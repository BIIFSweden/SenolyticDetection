print("Importing Python Modules")
from ctypes.wintypes import RGB
import numpy as np
from nd2reader import ND2Reader
import os
import matplotlib.pyplot as plt
from skimage.measure import label, regionprops
from skimage.morphology import disk,binary_opening
from skimage.filters import threshold_otsu,gaussian
from time import time
import pandas as pd
from time import time, localtime, strftime
import csv
from skimage.exposure import adjust_gamma


def find_images(folder_path):
    """Finds the paths of all .nd2 images within specified path. Normalizes
    image paths to work on any OS.

    Parameters
    ----------
    folder_path: Directory containing images or folders of images to be analyzed

    Returns
    -------
    image_paths: system paths to all .nd2 images within folder_path
    """
    folder_path = os.path.normpath(folder_path)

    image_paths = []

    for root, _, files in os.walk(folder_path):
        for name in files:
            if name.endswith(".nd2"):
                image_paths.append(os.path.join(root, name))
    return image_paths


def nd2_import(image_path):
    """Splits 3 channel .nd2 2D image into 3x 2D numpy arrays

    Parameters
    ----------
    image_path : the directory path of the .nd2 image to be imported

    Returns
    -------
    damaged: The first channel in the .nd2 image
    quiescent: The second channel in the .nd2 image
    blue: The third channel in the .nd2 image
    """

    with ND2Reader(image_path) as nd2_object:
        red, green, blue = nd2_object[0], nd2_object[1], nd2_object[2]

    return red, green, blue


def threshold_with_otsu(img):
    """Segmented 2D image using Otsu Thresholding

    Parameters
    ----------
    img : Grayscale input image

    Returns
    -------
    thresholded : Binary (Boolean) thresholded input image
    """

    thresh = threshold_otsu(img)
    thresholded = img > thresh

    # Zero out thresholding if over 50,000 nuclei detected
    # Done as if no nuclei present, otsu will background noise
    labelled = label(thresholded)
    if np.amax(labelled) > 50000:
        thresholded = np.zeros(thresholded.shape)

    return thresholded


def remove_objects_size(img, low_size=20000, high_size=900000):
    """Removes binary objects that have a pixel area between low_size and
        high_size. Used to remove well edges.

    Parameters
    ----------
    img : boolean,
                  thresholded 2D image
    low_size : int, optional
               the minimum pixel area of objects to be removed
    max_size : int, optional
               the maximum pixel area of objects to be removed

    Returns
    -------
    out : boolean,
          input image with objects between area thresholds removed
    """


    # Measure properties of each segmented region
    labelled = label(img)
    regions = regionprops(labelled)

    # Generate inverted mask of regions falling between the low_size and min_size
    removal_mask = np.ones(img.shape)
    for region in regions:
        if low_size < region.area < high_size:
            removal_mask[tuple(region.coords.T.tolist())] = 0
    out = removal_mask * img
    return out


def contained_within(centroid, red_channel):
    x = int(centroid[0])
    y = int(centroid[1])

    if red_channel[x, y] == 1:
        return True
    else:
        return False

def max_quiescent_size(img,max_size):

    labelled = label(img)
    regions = regionprops(labelled)

    removal_mask = np.ones(img.shape)
    for nuclei in regions:
        if nuclei.area > max_size:
            removal_mask[tuple(nuclei.coords.T.tolist())] = 0
    out = removal_mask * img

    return out

def autofluoresence_removal(red_channel_thresholded, green_channel_thresholded,max_quiescent_area = 1500):
    """The damaged senescent cells in the red channel have autofluorescence in
        the green channel. Since the green channel is used to detect the healthy
        cells, we must remove any green channel nuclei which also appear in the
        red channel.

    Parameters
    ----------
    red channel : boolean,
                  The thresholded red channel containing senescent cells.
    green channel : boolean,
                   The thresholded green channel, containing both healthy cells
                   tagged using green fluorescent probes, and senescent cells
                   present due to autofluorescense.
    max_quiescent_area: int,
                   Maximum allowable pixel area of quiescent nuclei. Nuclei over
                   this size will be counted as senescent nuclei.
    Returns
    -------
    healthy_only : boolean,
              Thresholded green channel excluding nuclei that are also present
              in the red channel.
    """

    labelled_green = label(green_channel_thresholded)
    regions_green = regionprops(labelled_green)

    red_coordinates = np.nonzero(red_channel_thresholded)
    red_coordinates = np.asarray(red_coordinates).T

    mask_large_nuclei = np.ones(green_channel_thresholded.shape)

    #Filter out large green nuclei which are senescent
    for nuclei in regions_green:
        if nuclei.area > max_quiescent_area:
            mask_large_nuclei[tuple(nuclei.coords.T)] = 0

    large_nuclei_removed = mask_large_nuclei*green_channel_thresholded
    labelled_large_nuclei_removed = label(large_nuclei_removed)
    regions_large_nuclei_removed = regionprops(labelled_large_nuclei_removed)

    # Check overlap between red/green channel, remove overlapping from green
    mask_overlap = np.ones(green_channel_thresholded.shape)
    for nuclei in regions_large_nuclei_removed:
        if contained_within(nuclei.centroid, red_channel_thresholded):
            mask_overlap[tuple(nuclei.coords.T)] = 0

    healthy_only = large_nuclei_removed * mask_overlap
    return healthy_only


def analyze_nuclei(img):
    """Labels nuclei objects in binary image and returns counts, mean size
    and std.

    Parameters
    ----------
    img: thresholded image.

    Returns
    -------
    number of objects/nuclei that do not touch

    """
    labelled = label(img)
    count = np.amax(labelled)

    region = regionprops(labelled)

    if len(region) > 0:
        areas = []
        for i in range(len(region)):
            areas.append(region[i].area)
        mean_size = round(np.mean(areas),2)
        std_size = round(np.std(areas),2)
    else:
        mean_size = 0
        std_size = 0

    return count, mean_size, std_size


def create_figure(
    RGB, RGB_gamma_corrected, red_thresholded, quiescent_nuclei, img_path, program_start_time,parameters
):
    """Saves .tiff file of nuclei segmentation results

    Parameters
    ----------

    red: dtype any (non-binary),
         red channel (senescent nuclei)
    red_thresolded: binary,
                    red channel segmententation mask
    green: dtype any (non-binary),
         green channel (Healthy nuclei + senescent nuclei caused by autofluorescence)
    quiescent_nuclei: binary,
                    green channel segmententation mask (with senescent nuclei removed)
    blue: dtype any (non-binary)
          contains
    img_path: str,
              Directory containing the image channels
    program_start_time: str,
                        time-stamp for when analysis began

    """
    zero_array = np.zeros(red_thresholded.shape)

    # Plot Images
    figure = plt.figure(figsize=(20, 10))

    if parameters.green_gamma == 1 and parameters.red_gamma == 1:
        title_string = 'Original Image, no gamma correction'
    
        plt.subplot(1, 2, 1)
        plt.imshow(RGB)
        plt.title(title_string)

        plt.subplot(1, 2, 2)

        RGB_segmentation = np.dstack((red_thresholded,quiescent_nuclei > 0,zero_array))
        plt.imshow(RGB_segmentation)
        plt.title("Segmentated Image")

    elif parameters.green_gamma != 1 or parameters.red_gamma != 1:

        plt.subplot(1, 3, 1)
        plt.imshow(RGB)
        plt.title('Orginal Image, no gamma correction')

        plt.subplot(1, 3, 2)
        plt.imshow(RGB_gamma_corrected)
        plt.title(f'Gamma corrected image, green:{parameters.green_gamma},red:{parameters.red_gamma}')

        plt.subplot(1, 3, 3)
        RGB_segmentation = np.dstack((red_thresholded,quiescent_nuclei > 0,zero_array))
        plt.imshow(RGB_segmentation)
        plt.title("Segmentated Image")


    img_dirname = os.path.dirname(img_path)
    img_name = os.path.split(img_path)[-1]
    img_name = os.path.splitext(img_name)[0]

    storage_directory = os.path.join(img_dirname, "Results " + program_start_time)
    if os.path.exists(storage_directory) is False:
        os.mkdir(storage_directory)

    plt.tight_layout()
    plt.savefig(os.path.join(storage_directory, img_name + ".tiff"), dpi=100)

    figure.clf()
    plt.close()

    return


def saveExcel(
    img_path,
    quiescent_count,
    quiescent_size_mean,
    quiescent_size_std,
    senescent_count,
    senescent_size_mean,
    senescent_size_std,
    ratio,
    program_start_time,
):

    """Saves nuclei counts and ratio between Quiescent and Senescent nucleis

    Parameters
    ----------
    img_path: str,
              directory name of image under analysis

    quiescent_count: int,
                   number of healthy nuclei
    senescent_count: int,
                   number of senescent nuclei
    ratio: float,
            ratio of healthy to senescent nuclei
    program_start_time: str,
                        time-stamp for when analysis began

    """

    img_dirname = os.path.dirname(img_path)
    img_name = os.path.split(img_path)[-1]
    img_name = os.path.splitext(img_name)[0]

    storage_directory = os.path.join(img_dirname, "Results " + program_start_time)
    if os.path.exists(storage_directory) is False:
        os.mkdir(storage_directory)

    excel_path = os.path.join(storage_directory, "Senescence_Results.xlsx")

    # Create Dataframe for current image
    scenescent_measures = f"{senescent_size_mean} \u00B1 {senescent_size_std}"
    quiescence_measures = f"{quiescent_size_mean} \u00B1 {quiescent_size_std}"

    storage_df = pd.DataFrame(
        [
            img_name,
            quiescent_count,
            senescent_count,
            ratio,
            quiescence_measures,
            scenescent_measures,
        ]
    ).transpose()

    storage_df.columns = [
        "Image",
        "quiescence count",
        "senescence count",
        "quiescence / senescence ratio",
        "quiescence mean area \u00B1 std (pixels^2)",
        "senescence mean area \u00B1 std(pixels^2)",
    ]

    if os.path.exists(excel_path):
        existing_excel = pd.read_excel(excel_path)
        new_excel = pd.concat([existing_excel, storage_df], axis=0, ignore_index=True)
        new_excel.to_excel(excel_path, index=False)

    else:
        storage_df.to_excel(excel_path, index=False)

    return


def save_user_parameters(parameters,program_start_time):
    user_variables = [
    ["Directory Analyzed", parameters.folder_path],
    ["Max quiescent area", parameters.max_quiescent_area],
    ["Green Channel Gamma correction",parameters.green_gamma],
    ["Red Channel Gamma correction",parameters.red_gamma],
]
    with open(
        os.path.join(parameters.folder_path, f"senolysis_parameters_{program_start_time}.csv"), "w", newline=""
    ) as csvfile:
        my_writer = csv.writer(csvfile)
        my_writer.writerows(user_variables)

    return


def main_analysis(parameters):
    """Main function to run the senescent analysis. Saves nuclei counts and
    image segmentation results.

    Parameters
    ----------
    directory: folder path which contains images/folders or images to be anaylyzed
    max_quiescent_area: int,
                        user-defined parameter for max quiescent nuclei area.
                        Nuclei in green channel larger than this value are removed.
    """

    img_paths = find_images(parameters.folder_path)

    num_images = len(img_paths)

    program_start_time = strftime("%Y-%m-%d %H-%M-%S", localtime())

    run_times = []

    for i, img_path in enumerate(img_paths):

        start = time()

        print("Analyzing image {0} of {1}:".format(i + 1, num_images), img_path)

        # #Split .nd2 image into seperate channels
        red, green, blue = nd2_import(img_path)
        RGB_orignal = np.dstack((red, green, blue))
        RGB_orignal = RGB_orignal / (2**16 - 1)

        #Adjust Image gamma if user specified gamma value != 1
        if parameters.green_gamma != 1:
            green  = adjust_gamma(green,gamma=parameters.green_gamma,gain=1)

        if parameters.red_gamma != 1:
            red  = adjust_gamma(green,gamma=parameters.red_gamma,gain=1)
        
        RGB_gamma_corrected = np.dstack((red, green, blue))
        RGB_gamma_corrected = RGB_gamma_corrected / (2**16 - 1)
        

        # Threshold guassian blurred images with Otsu
        green_thresholded = threshold_with_otsu(gaussian(green,1))
        red_thresholded = threshold_with_otsu(gaussian(red,1))

        # Remove Well Ring from images based on object size
        green_thresholded = remove_objects_size(green_thresholded)
        red_thresholded = remove_objects_size(red_thresholded)

        #Remove salt noise from thresholding results
        green_thresholded = binary_opening(green_thresholded,disk(2))
        red_thresholded = binary_opening(red_thresholded,disk(2))

        # Remove green nuclei that are present in red channel based on overlap and nuclei size
        quiescent_nuclei = autofluoresence_removal(red_thresholded, green_thresholded,parameters.max_quiescent_area)

        # Save Results Image
        print("     Saving Results...")
        create_figure(
            RGB_orignal,
            RGB_gamma_corrected,
            red_thresholded,
            quiescent_nuclei,
            img_path,
            program_start_time,
            parameters
        )

        # Count number of nuclei and nuclei sizes + std
        quiescent_count, quiescent_size_mean, quiescent_size_std = analyze_nuclei(
            quiescent_nuclei
        )
        senescent_count, senescent_size_mean, senescent_size_std = analyze_nuclei(
            red_thresholded
        )
        if senescent_count > 0:
            ratio = round(quiescent_count / senescent_count, 3)
        else:
            ratio = "inf"

        # Save Count Results in excel file
        saveExcel(
            img_path,
            quiescent_count,
            quiescent_size_mean,
            quiescent_size_std,
            senescent_count,
            senescent_size_mean,
            senescent_size_std,
            ratio,
            program_start_time,
        )


        # Save User Parameters
        save_user_parameters(parameters,program_start_time)

        end = time()
        run_time = end-start
        run_times.append(run_time)
        print(f"     Image analysis time: {round(run_time, 1)} seconds")

        if i != num_images-1:
            remaining_time = np.mean(run_times)*(num_images-(i+1))
            remaining_time = round(remaining_time/60,1)
            print(f"     Run time remaining: {remaining_time} minutes")

    total_time = round(np.sum(run_times)/60,1)
    print(f'Analysis Finished.Total run time: {total_time} minutes')
    return


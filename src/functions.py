print("Importing Python Modules")
import numpy as np
from nd2reader import ND2Reader
import os
import matplotlib.pyplot as plt
from skimage.measure import label, regionprops
from skimage.morphology import binary_dilation, disk
from skimage.filters import threshold_otsu
from time import time
import pandas as pd
from time import time, localtime, strftime


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
    healthy: The second channel in the .nd2 image
    all: The third channel in the .nd2 image
    """

    with ND2Reader(image_path) as nd2_object:
        damaged, healthy, all = nd2_object[0], nd2_object[1], nd2_object[2]

    return damaged, healthy, all


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

    return thresholded


def remove_objects_size(img, low_size=100000, high_size=800000, selem_size=8):
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

    selem_size : int, optional
            structuring element size for binary distilation used to fill in
            gaps of input binary image

    Returns
    -------
    out : boolean,
          input image with objects between area thresholds removed
    """

    # Perform Binary Dilation to close any small gaps in objects
    dilated = binary_dilation(img, disk(selem_size))

    # Measure properties of each segmented region
    labelled = label(dilated)
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


def autofluoresence_removal(red_channel_thresholded, green_channel_thresholded):
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

    mask = np.ones(green_channel_thresholded.shape)

    # If green nuclei centroid is within a red nuclei, mask it out
    for nuclei in regions_green:
        if contained_within(nuclei.centroid, red_channel_thresholded):
            mask[tuple(nuclei.coords.T)] = 0

    healthy_only = green_channel_thresholded * mask
    return healthy_only


def count_nuclei(img):
    """Counts nuclei objects in binary image.

    Parameters
    ----------
    img: thresholded image.

    Returns
    -------
    number of objects/nuclei that do not touch

    """
    labelled = label(img)
    regions = regionprops(labelled)

    return len(regions)


def mask_3D(RGB, mask):
    """Applies 2D Binary mask to RGB Image

    Parameters
    ----------
    RGB : 3D array, any type
    mask: Binary/Boolean,
          2D mask for segmenting RGB image

    Returns
    ------
    masked: segmented RGB image
    """
    masked = np.zeros(RGB.shape)
    for i in range(RGB.shape[2]):
        masked[:, :, i] = mask * RGB[:, :, i]
    return masked


def create_figure(
    red, red_thresholded, green, healthy_nuclei, blue, img_path, program_start_time
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
    green_thresolded: binary,
                    green channel segmententation mask (with senescent nuclei removed)
    blue: dtype any (non-binary)
          contains
    img_path: str,
              Directory containing the image channels
    program_start_time: str,
                        time-stamp for when analysis began

    """

    # Create RGB image [0...1]
    RGB = np.dstack((red, green, blue))
    RGB = RGB / (2**16 - 1)

    # Plot Images
    figure = plt.figure(figsize=(20, 10))

    plt.subplot(1, 3, 1)
    plt.imshow(RGB)
    plt.title("All nuclei")

    plt.subplot(1, 3, 2)
    masked = mask_3D(RGB, red_thresholded)
    plt.imshow(masked)
    plt.title("Senescent nuclei")

    plt.subplot(1, 3, 3)
    masked = mask_3D(RGB, (healthy_nuclei > 0))
    plt.imshow(masked)
    plt.title("Healthy nuclei")

    img_dirname = os.path.dirname(img_path)
    img_name = os.path.split(img_path)[-1].strip(".nd2")

    storage_directory = os.path.join(img_dirname, "Results " + program_start_time)
    if os.path.exists(storage_directory) is False:
        os.mkdir(storage_directory)

    plt.savefig(os.path.join(storage_directory, img_name + ".tiff"), dpi=200)

    figure.clf()
    plt.close()

    return


def saveExcel(img_path, healthy_count, senescent_count, ratio, program_start_time):

    """Saves nuclei counts and ratio between healthy and Senescent nucleis

    Parameters
    ----------
    img_path: str,
              directory name of image under analysis

    healthy_count: int,
                   number of healthy nuclei
    senescent_count: int,
                   number of senescent nuclei
    ratio: float,
            ratio of healthy to senescent nuclei
    program_start_time: str,
                        time-stamp for when analysis began

    """

    img_dirname = os.path.dirname(img_path)
    img_name = os.path.split(img_path)[-1].strip(".nd2")

    storage_directory = os.path.join(img_dirname, "Results " + program_start_time)
    if os.path.exists(storage_directory) is False:
        os.mkdir(storage_directory)

    excel_path = os.path.join(storage_directory, "Senescence_Results.xlsx")

    # Create Dataframe for current image
    storage_df = pd.DataFrame(
        [img_name, healthy_count, senescent_count, ratio]
    ).transpose()
    storage_df.columns = [
        "Image",
        "healthy count",
        "senescent count",
        "healthy / senescent ratio",
    ]

    if os.path.exists(excel_path):
        existing_excel = pd.read_excel(excel_path)
        new_excel = pd.concat([existing_excel, storage_df], axis=0, ignore_index=True)
        new_excel.to_excel(excel_path, index=False)

    else:
        storage_df.to_excel(excel_path, index=False)

    return


def main_analysis(directory):
    """Main function to run the senescent analysis. Saves nuclei counts and
    image segmentation results.

    Parameters
    ----------
    directory: folder path which contains images/folders or images to be anaylyzed
    """

    img_paths = find_images(directory)

    num_images = len(img_paths)

    program_start_time = strftime("%Y-%m-%d %H-%M-%S", localtime())

    for i, img_path in enumerate(img_paths):

        start = time()

        print("Analyzing {0} of {1} images:".format(i + 1, num_images), img_path)
        # #Split .nd2 image into seperate channels
        red, green, blue = nd2_import(img_path)

        # Threshold With Otsu
        green_thresholded = threshold_with_otsu(green)
        red_thresholded = threshold_with_otsu(red)

        # Remove Well Ring from images based on object size
        green_thresholded = remove_objects_size(green_thresholded)
        red_thresholded = remove_objects_size(red_thresholded)

        # Remove green nuclei that are present in red channel based on overlap
        healthy_nuclei = autofluoresence_removal(red_thresholded, green_thresholded)

        # Save Results Image
        print("     Saving Results...")
        create_figure(
            red,
            red_thresholded,
            green,
            healthy_nuclei,
            blue,
            img_path,
            program_start_time,
        )

        # Count number of nuclei
        healthy_count = count_nuclei(healthy_nuclei)
        senescent_count = count_nuclei(red_thresholded)
        ratio = round(healthy_count / senescent_count, 2)

        # Save Count Results in excel file
        saveExcel(img_path, healthy_count, senescent_count, ratio, program_start_time)

        end = time()
        print("     Processing time:", round(end - start, 1), "seconds")

    return

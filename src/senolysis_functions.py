import numpy as np
from nd2reader import ND2Reader
import os
import matplotlib.pyplot as plt
from skimage.measure import label, regionprops
from skimage.filters import threshold_otsu
import pandas as pd
from skimage.segmentation import mark_boundaries
from matplotlib.lines import Line2D
import warnings
from skimage.filters import threshold_mean
from skimage.morphology import remove_small_objects
from skimage.exposure import rescale_intensity

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

def standardize_strings(names):
        '''makes string or list of strings lowercase and removes extra spaces.
        '''
        if isinstance(names,list):
            names = [" ".join(x.strip().split()) for x in names]
            names = [x.lower() for x in names]
            return names
        elif isinstance(names,str):
            names = " ".join(names.strip().split())
            names = names.lower()
            return names
        else:
            raise ValueError('names should be a string or list of strings') 

def nd2_import(image_path):

        #List of possible image names
        hoechst_possbile_names = standardize_strings(['senolysis hoechst','hoechst','kinetix single hoechst'])
        senolysis_possible_names = standardize_strings(['senolysis',' Kinetix Single band tdTomato', 'tdTomato'])
        EGFP_possible_namess = standardize_strings(['senolysis egfp',' Kinetix Single band senolysis  EGFP1', 'egfp1','egfp'])

        with ND2Reader(image_path) as nd2_object:
            
            # Get channel names
            metadata = nd2_object.metadata
            channels = standardize_strings(metadata['channels'])

            # Return channels in correct order
            for i,channel in enumerate(channels):
               
                if channel in hoechst_possbile_names:
                    ind_hoechst = i
                elif channel.lower() in senolysis_possible_names:
                    ind_senolysis = i
                elif channel.lower() in EGFP_possible_namess:
                    ind_EGFP = i
                else:
                    ind_senolysis = 0
                    ind_EGFP = 1
                    ind_hoechst = 2

                    warnings.warn('''Naming of .nd2 channels cannot be resolved. Assuming the 
                                    channel order is Senescent, Quiescent then Nuclei stain.
                    ''')
                                   
            return nd2_object[ind_senolysis], nd2_object[ind_EGFP], nd2_object[ind_hoechst]


def normalize_img(img, low_per=1, high_per=99):
    low = np.percentile(img, low_per)
    high = np.percentile(img, high_per)
    rescaled = rescale_intensity(img, in_range=(low, high), out_range=(0, 1))
    return rescaled



def remove_well_rings(img,min_size=20000,max_size = 300):


    thresh = threshold_mean(img)
    binary = img > thresh
    regions = regionprops(label(binary))
    # Generate inverted mask of regions falling between the low_size and min_size
    removal_mask = np.ones(img.shape, dtype="bool")
    for region in regions:
        if max_size < region.area:
            removal_mask[tuple(region.coords.T.tolist())] = 0

    # Used to remove corners of images which sometimes remain
    removal_mask = remove_small_objects(removal_mask, min_size=min_size) #was 20000

    out = removal_mask * img
    return out


def remove_large_nuclei(binary, max_size=7000):

    regions = regionprops(label(binary))

    removal_mask = np.ones(binary.shape)
    for region in regions:
        if max_size < region.area:
            removal_mask[tuple(region.coords.T.tolist())] = 0
    
    return removal_mask * binary


def threshold_with_otsu(img):

    thresh = threshold_otsu(img)
    thresholded = img > thresh

    # Zero out thresholding if over 50,000 nuclei detected
    # Done as if no nuclei present, otsu will theshold noise
    labelled = label(thresholded)
    if np.amax(labelled) > 50000:
        thresholded = np.zeros(thresholded.shape)
        warnings.warn('No nuclei detected.')

    return thresholded


def determine_nuclei_type(mask, red, green, blue):

    nuclei_regions = regionprops(label(mask))

    scenescent = np.zeros(mask.shape)
    quiescent = np.zeros(mask.shape)
    for nuclei in nuclei_regions:
        nuclei_coordinates = nuclei.coords
        red_value = np.mean(red[tuple(nuclei_coordinates.T)])
        green_value = np.mean(green[tuple(nuclei_coordinates.T)])

        if red_value > green_value:
            scenescent[tuple(nuclei_coordinates.T)] = 1
        else:
            quiescent[tuple(nuclei_coordinates.T)] = 1

    return np.bool_(scenescent), np.bool_(quiescent)


def determine_count_and_area(mask):

    labelled = label(mask)
    count = np.amax(labelled)

    region = regionprops(labelled)

    if len(region) > 0:
        areas = []
        for i in range(len(region)):
            areas.append(region[i].area)
        mean_size = round(np.mean(areas), 2)
        std_size = round(np.std(areas), 2)
    else:
        mean_size = 0
        std_size = 0

    return count, mean_size, std_size


def analyze_nuclei(scenescent_mask, quiescent_mask, img_path):

    count_q, area_q, std_q = determine_count_and_area(quiescent_mask)
    count_s, area_s, std_s = determine_count_and_area(scenescent_mask)

    if count_s > 0:
        ratio = round(count_q / count_s, 3)
    else:
        ratio = "inf"
    scenescent_measures = f"{area_s} \u00B1 {std_s}"
    quiescence_measures = f"{area_q} \u00B1 {std_q}"

    img_name = os.path.basename(img_path)
    storage_df = pd.DataFrame(
        [
            img_name,
            count_q,
            count_s,
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

    return storage_df

#Uses matlplotlib to save image, pretty but very slow
def create_figure(RGB, scenescent, quinescent, save_path, img_name):

    # Plot Images
    plt.figure(figsize=(5, 5))

    marked = mark_boundaries(RGB, scenescent, color=(1, 1, 1), mode="thick")
    marked = mark_boundaries(marked, quinescent, color=(0, 0, 1), mode="thick")
    plt.imshow(marked)

    plt.title("Segmentation Results")
    custom_lines = [
        Line2D([0], [0], color=(1, 1, 1), lw=2),
        Line2D([0], [0], color=(0, 0, 1), lw=2),
    ]

    plt.legend(custom_lines, ["Senescent", "Quiescent"], prop={"size": 6})

    plt.tight_layout()
    plt.savefig(os.path.join(save_path, img_name + ".png"), dpi=500)

    plt.clf()
    plt.close()

    return


def write_csv(pandas_dataframe, directory):
    # Writes the CSV file of  pandas dataframe to specified directory
    if os.path.exists(directory) is False:
        with open(directory, "a") as f:
            pandas_dataframe.to_csv(f, header=True, index=False)
    else:
        existing = pd.read_csv(directory)
        new_file = pd.concat([existing, pandas_dataframe], axis=0, ignore_index=False)
        new_file.to_csv(directory, header=True, index=False)
    return

def saveExcel(pandas_dataframe,directory):

    if os.path.exists(directory):
        existing_excel = pd.read_excel(directory)
        new_excel = pd.concat([existing_excel, pandas_dataframe], axis=0, ignore_index=True)
        new_excel.to_excel(directory, index=False)

    else:
        pandas_dataframe.to_excel(directory, index=False)

    return

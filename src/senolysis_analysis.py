from skimage.transform import downscale_local_mean
from skimage.filters import gaussian
from senolysis_functions import *
from skimage.morphology import remove_small_objects, remove_small_holes
from skimage.transform import resize
from skimage import io


def senolysis_analysis(img_path, program_start_time, gui):

    red, green, blue = nd2_import(img_path, gui)

    # downscale the images for faster computation
    downscale_factor = 4
    blue_downscaled = downscale_local_mean(
        blue, factors=(downscale_factor, downscale_factor)
    )
    green_downscaled = downscale_local_mean(
        green, factors=(downscale_factor, downscale_factor)
    )
    red_downscaled = downscale_local_mean(
        red, factors=(downscale_factor, downscale_factor)
    )

    #rescale to 0 - 98th percentiles 
    red_normalized, green_normalized, blue_normalized = (
        normalize_img(red_downscaled, high_per=98),
        normalize_img(green_downscaled, high_per=98),
        normalize_img(blue_downscaled, high_per=98),
    )   

    blue_smoothed = gaussian(blue_downscaled, 1,preserve_range = True)

    if gui.remove_well_ring == 1:
            blue_smoothed = remove_well_rings(
                blue_normalized, max_size=gui.max_nuclei_size
            )
        
    # Threshold Nuclei
    if gui.thresholding_method == 'Otsu':
        
        nuclei_thresholded = threshold_with_otsu(blue_smoothed)

    elif gui.thresholding_method == 'Global':

        nuclei_thresholded = blue_smoothed >= gui.nuclei_threshold
    else: 
        raise ValueError('Could not identify nuclei thresholding method')

    nuclei_thresholded = remove_small_holes(nuclei_thresholded, area_threshold=100)

    # Size filter threshold nuclei
    min_nuclei_area = int(gui.min_nuclei_size / downscale_factor**2)
    max_nuclei_area = int(gui.max_nuclei_size / downscale_factor**2)
    nuclei_thresholded = remove_small_objects(
        nuclei_thresholded, min_size=min_nuclei_area
    )
    nuclei_thresholded = remove_large_nuclei(
        nuclei_thresholded, max_size=max_nuclei_area
    )

    # Determine if each nuclei belongs to scenescent or quiescent cell
    scenescent_downscaled, quiescent_downscaled = classify_nuclei(
        mask=nuclei_thresholded,
        red=red_downscaled,
        green=green_downscaled,
        red_threshold=gui.scenescent_threshold,
    )

    # Upsample segmentation results back to orignal image size
    scenescent_upscaled = resize(scenescent_downscaled, output_shape=red.shape)
    quiescent_upscaled = resize(quiescent_downscaled, output_shape=green.shape)

    # Measures counts and nuclei mean size + std
    results_dataframe = analyze_nuclei(
        scenescent_upscaled, quiescent_upscaled, img_path
    )

    img_dirname = os.path.dirname(img_path)
    save_path = os.path.join(img_dirname, f"Results_{program_start_time}")

    if os.path.exists(save_path) is False:
        os.mkdir(save_path)

    saveExcel(results_dataframe, os.path.join(save_path, "Senolysis_measures.xlsx"))

    #Save Image with no DAPI Channel
    zeros = np.zeros(blue_normalized.shape)
    RGB = np.dstack([red_normalized, green_normalized, zeros])

    img_name = os.path.split(img_path)[-1]
    img_name = os.path.splitext(img_name)[0]

    create_figure(
        RGB,
        scenescent_downscaled,
        quiescent_downscaled,
        save_path,
        img_name,
        gui.scenescent_threshold,
    )

    #Save Binary Mask as well
    scenescent_mask_path = os.path.join(save_path,img_name+'_scenescent_mask.png')
    quiescent_mask_path = os.path.join(save_path,img_name+'_quiescent_mask.png')

    io.imsave(scenescent_mask_path,np.uint8(scenescent_upscaled*255),check_contrast=False)
    io.imsave(quiescent_mask_path,np.uint8(quiescent_upscaled*255),check_contrast=False)

    return

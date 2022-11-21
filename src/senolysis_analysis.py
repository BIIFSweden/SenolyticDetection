from skimage.transform import downscale_local_mean
from skimage.filters import gaussian
from senolysis_functions import *
from skimage.morphology import binary_opening, remove_small_holes, disk,remove_small_objects
from skimage.transform import resize


def senolysis_analysis(img_path, program_start_time):

    red, green, blue = nd2_import(img_path)

     # downscale the images for faster computation
    downscale_factor = 4
    blue_downscaled = downscale_local_mean(
        blue_norm, factors=(downscale_factor, downscale_factor)
    )
    green_downscaled = downscale_local_mean(
        green_norm, factors=(downscale_factor, downscale_factor)
    )
    red_downscaled = downscale_local_mean(
        red_norm, factors=(downscale_factor, downscale_factor)
    )

    # normalize to [0,1] for 0 to 99th percentiles
    red_norm, green_norm, blue_norm = (
        normalize_img(red_downscaled, high_per=98),
        normalize_img(green_downscaled, high_per=98),
        normalize_img(blue_downscaled, high_per=98),
    )
   
    # Smooth the blue channel for nuclei segmentation
    blue_smoothed = gaussian(blue_norm, 1)  # smooth image

    # remove the well ring from the blue channel
    blue_no_well_ring = remove_well_rings(blue_smoothed)

    nuclei_thresholded = threshold_with_otsu(blue_no_well_ring)

    # Segment nuclei in blue channel and clean up results
    nuclei_thresholded = threshold_with_otsu(blue_no_well_ring)
    disk_factor = int(5 / downscale_factor)
    nuclei_thresholded = binary_opening(nuclei_thresholded, footprint=disk(disk_factor))
    nuclei_thresholded = remove_small_holes(nuclei_thresholded, area_threshold=500)
    nuclei_thresholded = remove_large_nuclei(
        nuclei_thresholded, max_size=int(7000 / downscale_factor**2)
    )

    # Determine if each nuclei belongs to scenescent or quiescent cell
    scenescent_downscaled, quiescent_downscaled = classify_nuclei(
        mask=nuclei_thresholded,
        red=red_downscaled,
        green=green_downscaled,
    )

    # Upsample segmentation results back to orignal image size
    scenescent_upscaled = resize(scenescent_downscaled, output_shape=red.shape)
    quiescent_upscaled = resize(quiescent_downscaled, output_shape=green.shape)

    #Remove any nuclei smaller than 150 pixels
    scenescent_upscaled = remove_small_objects(scenescent_upscaled,min_size=150)
    quiescent_upscaled = remove_small_objects(quiescent_upscaled,min_size=150)

    # Measures counts and nuclei mean size + std
    results_dataframe = analyze_nuclei(
        scenescent_upscaled, quiescent_upscaled, img_path
    )

    img_dirname = os.path.dirname(img_path)
    save_path = os.path.join(img_dirname, f"Results_{program_start_time}")

    if os.path.exists(save_path) is False:
        os.mkdir(save_path)

    saveExcel(results_dataframe, os.path.join(save_path, "Senolysis_measures.xlsx"))

    RGB = np.dstack([red_norm,green_norm,blue_norm])

    img_name = os.path.split(img_path)[-1]
    img_name = os.path.splitext(img_name)[0]
    create_figure(RGB, scenescent_upscaled, quiescent_upscaled, save_path, img_name)

    return

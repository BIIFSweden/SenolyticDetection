from skimage.transform import downscale_local_mean
from skimage.filters import gaussian
from senolysis_functions import *
from skimage.morphology import remove_small_objects, remove_small_holes
from skimage.transform import resize


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

    # normalize to [0,1] for 0 to 98th percentiles
    red_normalized, green_normalized, blue_normalized = (
        normalize_img(red_downscaled, high_per=98),
        normalize_img(green_downscaled, high_per=98),
        normalize_img(blue_downscaled, high_per=98),
    )

    # Smooth the blue channel for nuclei segmentation
    blue_smoothed = gaussian(blue_normalized, 1)  # smooth image

    # remove the well ring from the blue channel
    if gui.remove_well_ring == 1:
        blue_no_well_ring = remove_well_rings(
            blue_smoothed, max_size=gui.max_nuclei_size
        )
        nuclei_thresholded = threshold_with_otsu(blue_no_well_ring)
    else:
        nuclei_thresholded = threshold_with_otsu(blue_smoothed)

    # Segment nuclei in blue channel and small and large objects
    nuclei_thresholded = threshold_with_otsu(blue_no_well_ring)
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

    RGB = np.dstack([red_normalized, green_normalized, blue_normalized])

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

    return

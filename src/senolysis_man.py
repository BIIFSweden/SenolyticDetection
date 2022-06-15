print("Importing Modules...")
from senolysis_analysis import *
from time import strftime, localtime
from joblib import Parallel, delayed
from multiprocessing import cpu_count
from tqdm_joblib import tqdm_joblib
from tqdm import tqdm
from time import sleep


def main():

    program_start_time = strftime("%Y-%m-%d %H-%M-%S", localtime())

    dir = "/Users/robertwelch/Desktop/Test Images/Chiara3/All Images"

    img_paths = find_images(dir)

    num_images = len(img_paths)

    # Use parallel processing for larger image set
    if num_images > 9:
        cpus_to_use = cpu_count()
        if num_images < cpus_to_use:
            cpus_to_use = num_images
        print(f"Number of Images > 9.Using {cpus_to_use} CPUs for parallel processing.")

        # Parallelize image analsyis with progress bar
        print(f"Analyzing {len(img_paths)} images")
        with tqdm_joblib(tqdm(desc="Progress", total=len(img_paths))) as progress_bar:
            Parallel(n_jobs=cpus_to_use)(
                delayed(senolysis_analysis)(img_path, program_start_time)
                for img_path in img_paths
            )

    else:
        print(f"Number of Images less than 10, running analysis in series.")
        [
            senolysis_analysis(img_path, program_start_time)
            for img_path in tqdm(img_paths)
        ]

    sleep(1)

    print(f"Finished Analysis")
    return None


if __name__ == "__main__":
    main()

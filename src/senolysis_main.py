print("Importing Modules...")
from senolysis_analysis import *
from time import strftime, localtime
from joblib import Parallel, delayed
from multiprocessing import cpu_count
from tqdm_joblib import tqdm_joblib
from tqdm import tqdm
from time import sleep
from gui_senolysis import *


def main():

    gui = GUI()
    gui.mainloop()

    program_start_time = strftime("%Y-%m-%d %H-%M-%S", localtime())

    img_paths = find_images(gui.directory)

    num_images = len(img_paths)
    print(f"Total number of images to analyze: {num_images}")

    assert (
        gui.num_jobs > 0 and gui.num_jobs <= os.cpu_count()
    ), f"Number of jobs shoulder be integer value be between 1 and {os.cpu_count()}"
    print(f"Analyzing {gui.num_jobs} images in parallel")

    # Parallelize image analsyis with progress bar
    if gui.num_jobs > 1:
        with tqdm_joblib(tqdm(desc="Progress", total=len(img_paths))) as progress_bar:
            Parallel(n_jobs=gui.num_jobs)(
                delayed(senolysis_analysis)(img_path, program_start_time,red_threshold=gui.red_threshold)
                for img_path in img_paths
            )

    elif gui.num_jobs == 1:
        print(f"Number of jobs = 1, processing images in series.")
        [
            senolysis_analysis(img_path, program_start_time,scenescent_threshold=gui.red_threshold)
            for img_path in tqdm(img_paths)
        ]

    #Record folder path chosen and red-threshold used
    save_user_parameters(gui,program_start_time)

    print(f"Finished Analysis")
    return None


if __name__ == "__main__":
    main()

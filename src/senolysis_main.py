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

    # Use parallel processing for larger image set, save 2 cpus for background work...
    
    cpus_to_use = gui.num_jobs
    assert cpus_to_use > 0 and cpus_to_use <=os.cpu_count(), f'Number of jobs must integer value be between 1 and {os.cpu_count()}'
    print(f"Using {cpus_to_use} CPUs for parallel processing.")

    print(f"Analyzing {len(img_paths)} images")

    # Parallelize image analsyis with progress bar
    if cpus_to_use>1:
        with tqdm_joblib(tqdm(desc="Progress", total=len(img_paths))) as progress_bar:
            Parallel(n_jobs=cpus_to_use)(
                delayed(senolysis_analysis)(img_path, program_start_time)
                for img_path in img_paths
            )

    elif cpus_to_use==1:
        print(f"Number of jobs = 1, processing images in series.")
        [
            senolysis_analysis(img_path, program_start_time)
            for img_path in tqdm(img_paths)
        ]

    print(f"Finished Analysis")
    return None

if __name__ == "__main__":
    main()

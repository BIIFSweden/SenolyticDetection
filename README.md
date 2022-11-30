# Federico-Pietrocola2022-3

<p align="center">
<img width="700" alt="Screenshot 2022-11-22 at 12 14 22" src="https://user-images.githubusercontent.com/43760657/203300414-90941d88-ce7f-4729-a97e-73b2bc896896.png">
</p>



This python script is used for high-throughput analysis of 3-channel .nd2 fluorescent images. Otsu thresholding is used to segment the blue channel, which marks the nuclei of the cells.

To classify the cells, the mean intensity of the nucleus in the scenescent channel is calculated. If it is higher than the user-specified scenescent threshold, the cell is classified as scenescent. Some additional user-specified size filtering is used to retain nuclei within an area range.

The script saves csv files with counts of the scenescent and quiescent nuclei and size statistics. In addition, it saves .png images displaying the segmentation results.

## Installation

1. Create a conda virtual environment (example using virtual environment named senolysisenv). This will be used to run the program in. Afterwards activate the environment.
```bash
conda create -n senolysisenv python=3.9
conda activate senolysisenv
```

2. Open command prompt (windows) or terminal (mac) and change to a directory where you wish to store the program:

```bash
cd path/to/store/program
```

3. Download the github repository into this directory, change into the Federico-Pietrocola2022-3 directory and setup the environment:
```bash
git clone https://github.com/BIIFSweden/Federico-Pietrocola2022-3.git
cd Federico-Pietrocola2022-3
pip install -e .
```

## Running the program

1. With the conda environment activated, run the program senolysis_program.
```bash
conda activate senolysisenv
senolysisprogram
```
This will open a small GUI prompting you to select the directory containing the images to analyze. Select the directory and set the minium and maximum allowable areas of the nuclei. Nuclei outside of this range will not be counted.

The most important parameter to tune is the Senescent threshold. Nuclei with a mean intensity in the senescent channel above this threshold will be classified as senescent, otherwise quiescent.

The channel order can be modified if required, by default it is (senescent, quiescent, nuclei).

The user also has the option to choose how many images are analyzed in parallel.

Then, press Run Analysis and monitor the script's progress in the command prompt/terminal.

<p align="center">
<img width="693" alt="Screenshot 2022-11-30 at 09 28 48" src="https://user-images.githubusercontent.com/43760657/204745692-05520285-dba8-455c-9ac1-dda18f5bf8c7.png">
</p>



## Results
After the program has finished running, .png images with the segmentation results as well as .csv files with nuclei counts and areas will be saved in the corresponding directories containing the analyzed images.

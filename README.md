# Federico-Pietrocola2022-3

<p align="center">
<img src="https://user-images.githubusercontent.com/43760657/168568815-f88ab2f9-f87c-4223-8bf3-dc6c8b1f995c.jpg" width="400" height="400">
</p>

This python script is used for high-throughput analysis of senescence and quiescence cells. The senescent nuclei appear orange as they are tagged in the red channel and have autofluorescence in the green channel. Whereas the quiescent nuclei are only seen in the green channel. Otsu Thresholding is used to segment the red and green channels.

To overcome the autofluorescence of the senescent nuclei in the green channel, the nuclei that appear in both the green and red channel are removed from the quiescent nuclei thresholded results, leaving nuclei that are present only in the green channel. Additionally there is a user-defined quiescent nucleus area used to remove overly-large nuclei in the green channel.

The script saves excel files with counts of the scenescent and quiescent nuclei and size statistics. In addition, it saves .tiff images displaying the segmentation results.


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
python setup.py install
```

## Running the program

1. With the conda environment activated, run the program senolysis.
```bash
conda activate senolysisenv
senolysis
```
This will open a small GUI prompting you to select the directory containing the images to analyze. Select the directory and set the maximum allowable area of the quiescent nuclei. Most of the quescent nuclei will be properly detected, however if large nuclei are appearing in the green channel (indicated of senescent nuclei), they can be removed using this threshold. Then, press Run Analysis and monitor the script's progress in the command prompt/terminal.

<p align="center">
<img width="500" alt="Screen Shot 2022-05-24 at 3 27 40 PM" src="https://user-images.githubusercontent.com/43760657/170046498-79d23ed3-3934-4fe8-b461-52c5b5156b16.png">
</p>

## Results

After the program has finished running, .tiff images with the segmentation results as well as .xlsx files with nuclei counts and areas will be saved in the corresponding directories containing the analyzed images.

![WellE02_Channel Kinetix Single band tdTomato, Kinetix Single band senolysis  EGFP1, Kinetix Single  Hoechst_Seq0015](https://user-images.githubusercontent.com/43760657/170046965-f4a9b199-4ab4-4eb0-b804-e63de4adf3c7.jpg)



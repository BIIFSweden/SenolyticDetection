# Federico-Pietrocola2022-3

<p align="center">
<img src="https://user-images.githubusercontent.com/43760657/168568815-f88ab2f9-f87c-4223-8bf3-dc6c8b1f995c.jpg" width="400" height="400">
</p>

This python script is used for high-throughput screening of senescent nuclei. The senescent nuclei appear orange as they are tagged in the red channel but also have autofluorescence in the green channel. The quiescent nuclei are seen only in the green channel, while the blue channel labels both scenescent and quiescent nuclei. To count the nuclei, they are first segmented using Otsu Thresholding in the red and green channels.

To overcome the autofluorescence of the senescent nuclei in the green channel, the nuclei that appear in both the green and red channel are removed from the quiescent nuclei thresholded results, leaving nuclei that are present only in the green channel.

The script saves excel files with counts of the scenescent and quiescent nuclei. In addition, it saves .tiff images showing the segmentation results.


## Installation

1. Create a conda virtual environment (example using virtual environment named senescent). This will be used to run the program in. Afterwards activate the environment.
```bash
conda create -n senescent python=3.9
conda activate senescent
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

1. Change to the src directory inside Federico-Pietrocola2022-3
```bash
cd src
```
2. With the conda environment activated, run the program.
```bash
conda activate senescent
senolysis
```
3. This will open a small GUI prompting you to select the directory containing the images to analyze. Select the directory and press Run Analysis.

<img width="477" alt="Screen Shot 2022-05-16 at 5 41 03 PM" src="https://user-images.githubusercontent.com/43760657/168631403-fa4f1d85-8062-4be4-a77a-670f177e48a7.png">

4. Monitor the command prompt/terminal for updates on the program.

## Results

After the program has finished running, .tiff images with the segmentation results as well as .xlsx files with nuclei counts and areas will be saved in the corresponding directories containing the analyzed images.

![WellE02_Channel Kinetix Single band tdTomato, Kinetix Single band senolysis  EGFP1, Kinetix Single  Hoechst_Seq0015](https://user-images.githubusercontent.com/43760657/169508353-56c31fbf-d3d1-4fcd-a037-e56914d3960e.jpg)


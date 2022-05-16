# Federico-Pietrocola2022-3

<p align="center">
<img src="https://user-images.githubusercontent.com/43760657/168568815-f88ab2f9-f87c-4223-8bf3-dc6c8b1f995c.jpg" width="400" height="400">
</p>

This python script is used for high-throughput screening of senescent nuclei. The senescent nuclei appear orange as they are tagged in the red channel but also have autofluorescence in the green channel. The "healthy" nuclei are seen only in the green channel, while the blue channel labels both scenescent and "healthy" nuclei. To count the nuclei, they are first segmented using Otsu Thresholding. 

To overcome the autofluorescence of the senescent nuclei, nuclei that appear in both the green and red channel are removed from the "healthy" nuclei thresholded results, leaving nuclei that are present only in the green channel.

The script saves excel files with the scenescent and healthy counts of nuclei as well as .tiff images showing the segmentation results.






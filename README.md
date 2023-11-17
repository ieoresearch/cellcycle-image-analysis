# Cell Cycle Image Analysis
This repository contains two pipelines that can be used in association with a dedicated statistical analysis to profile the cell cycle phases in timelapses experiments. In our experiments cells were expressing the FUCCI(CA)2 technology. The analysis is divided into the following two step:

- Image processing <br> 
   The images are pre-processed through a custom-made Fiji macro in order to transform the original images into a dataset optimized for the subsequent steps of tracking and cell cycle phase assignment. In particular the pipeline generates, from the original acquired multichannel image, a final image stack with the add of a channel that will be used as tracking reference and a channel that will be used for the subsequent cell cycle profiling.
- Tracking Analysis <br>
   In the tracking analysis, the Fiji plugin TrackMate (Tinevez et al., 2017) was employed, adapting the example script available on the dedicated TrackMate website (https://imagej.net/plugins/trackmate/scripting/scripting), to ensure the automation of the tracking step. The related parameters were selected and tuned according to each experiment, as well as the proper filters to discard unreliable tracks


# Usage

**Image processing**

1)	Open the pre-processing macro (Image_processing_HSB_v1.ijm) in your Fiji <br>
Note: the execution of the macro requires the prior installation of the Basic plugin (https://github.com/marrlab/BaSiC) for flat-field correction
2)	Set the proper image filters and background subtraction processing for red and green channels at lines 58-78 and 85-94
3)	Choose the maximum values of the Brightness and Contrast for both red and green channels and set the found values at lines 116 (red) and 118 (green)
4)	Set the proper value of the Top Hat filter on the Brightness channel (HSB stack) at line 127
5)	 Set the correct position of red and green channels, depending on the experiment, at lines 173-174.
6)	Run the macro from the Fiji script editor
7)	Set in the dialog window the input directory (where original data are stored), the output directory (where you want to store processed images) and the original file format

**Tracking Analysis**

1)	Open the TrackMate script in the Fiji macro editor
2)	Adjust the parameters settings (from line 39 to 58) according to the experiment
3)	Run the script from the Fiji script editor
4)	Set in the dialog window the input directory (where the images processed with the previous pipeline are stored) and the output directory (where you want to store the results table)


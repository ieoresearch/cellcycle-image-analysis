# Cell Cycle Image Analysis

## Introduction

This repository contains two pipelines that can be used in association with a dedicated statistical analysis to profile the cell cycle phases of cells expressing the FUCCI(CA)2 technology. 
In our dataset, time-lapse images were composed by Red and Green channels, detecting respectively the mCherry and mVenus markers of the FUCCI(CA)2 indicator. During the experiment each cell alternatively switches between the expression of these two markers as it goes through the different cell cycle phases, causing the lack of a single fluorescence channel suitable for tracking. Furthermore, the automatic profiling of cell-cycle phases becomes cumbersome when dealing with two distinct channels that in the end give rise to two independent fluorescence time-series.

## Analysis description

The analysis is divided into the following two step:

- Image processing <br>
   The images are pre-processed through a custom-made Fiji (Schindelin et al., 2012) macro in order to transform the original images into a dataset optimized for the subsequent steps of tracking and cell cycle phase assignment. The color changes that occurs during the cell cycle are represented with the Hue scale, as described in (Graduate School of Information Science and Technology, Osaka University, Suita, Osaka, Japan et al., 2020) while the Brightness channel was kept as tracking reference. These two are merged to the Red and Green fluorescence channels to form the final stack used for the tracking process.

- Tracking Analysis <br>
   In the tracking analysis, the Fiji plugin TrackMate (Tinevez et al., 2017) was employed, adapting the example script available on the dedicated TrackMate website (https://imagej.net/plugins/trackmate/scripting/scripting), to ensure the automation of the tracking step. The related parameters were selected and tuned according to each experiment, as well as the proper filters to discard unreliable tracks

## Usage

*A test image dataset can be provided upon request, writing to the e-mail: chiara.soriani@ieo.it*

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


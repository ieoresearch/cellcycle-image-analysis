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
Note: the execution of the macro requires the prior installation of the Basic plugin (https://github.com/marrlab/BaSiC) for flat-field correction <br>

**Flat-field Correction**: this step corrects for uneven illumination across the field of view, preventing the potential loss of objects at the image borders. If not applied in the acquisition phase, we recommend employing the BaSic method for flat-field correction.<br>

***Suggested values range**: BaSic default settings*

2)	Set the proper image filters and background subtraction processing for red and green channels at lines 58-78 and 85-94 <br>

**Denoising**: to reduce noise and enhance image quality, denoising techniques are essential. We suggest applying either a Gaussian Blur filter or a Median filter to effectively suppress noise while preserving important image features.<br>

***Suggested values range**: Maximum filter sigma: 0.2 $`\times`$(Mean diameter of the object) in order to be able to suppress random noise and distinguish two adjacent cells as distinct spots in the tracking phase, as shown in the example below (Object’s diameter = 16 px).* 

<img width="1167" alt="Gaussian_Blur_example" src="https://github.com/ieoresearch/cellcycle-image-analysis/assets/86475646/bc199a00-fe42-4f7a-b83b-0d4943238352">


**Background Subtraction**: removing background signal is critical for isolating objects of interest. We inserted in our pipeline methods for background subtraction such as the rolling ball algorithm or, specifically for the green channel, the Mean Intensity Background Subtraction. This ensures the removal of background fluorescence or camera offset, enabling precise objects identification (for a helpful discussion about background subtraction, please see: https://forum.image.sc/t/consensus-on-subtract-background-built-in-or-other/7061).<br>

*NB!* We chose to implement Mean Intensity Background subtraction for the green channel due to its superior performance compared to the rolling ball algorithm in our experimental setup. The rolling ball algorithm failed to adequately remove camera noise and offset, resulting in residual spikes and impurities with periodicity matching the size of our objects. Therefore, Mean Intensity Background Subtraction emerged as the preferred approach for achieving optimal background removal and enhancing the precision of our analysis. <br>

**The BG subtraction step is mandatory if the images contain a background offset which is above 100. This is the case especially in widefield mode, while in confocal microscopy usually the background already has near to zero values.**<br>

In the example here below, it is shown an image of a field of view in hue scale without (left) and with (right) the prior execution of the BG subtraction in red and green channels. In the left image the background has a hue value that approaches the yellow color value. Brightness and Contrast values are set as 0-85.

![BG_subtraction_example](https://github.com/ieoresearch/cellcycle-image-analysis/assets/86475646/ef74a51f-4d8c-4fae-9dc2-3fe53102d058)

3)	Choose the maximum values of the Brightness and Contrast for both red and green channels and set the found values at lines 116 (red) and 118 (green). <br>

**Hue Saturation Brightness (HSB) Conversion**: to convert original images to the HSB stack, it is essential to include a step for histogram stretching. This contrast enhancement is particularly important for images with a low signal-to-noise ratio, as it ensures a proper range of values in the Brightness scale images, that are used as tracking reference (first image below, left image: Red rescaled between 0 and 3500, Green rescaled between 0 and 4000; right image: whole intensity range). Note that, if the green and red channels are acquired with similar intensity ranges, the Hue image is correctly extracted even if the image histogram is not rescaled, as shown in the second image below (left image: Red rescaled between 0 and 3500, Green rescaled between 0 and 4000; right image: whole intensity range).<br>

***Suggested values range**: Minimum = 0; Maximum = maximum intensity value of stack histogram*

Brightness image
![Brightness_example](https://github.com/ieoresearch/cellcycle-image-analysis/assets/86475646/13030ac8-3d57-47e3-ba22-7abf9adf2fbc)

Hue scale image
![Hue_example](https://github.com/ieoresearch/cellcycle-image-analysis/assets/86475646/ed5929d2-a009-4ace-9e81-668f324fb2da)

*NB!* If the original images are not acquired with a 16-bit camera range, change the commands at lines 128 and 132, indicating the correct camera bit-depth used for the experiment's acquisition


4)	Set the proper value of the Top Hat filter on the Brightness channel (HSB stack) at line 127 <br>

**Particle Enhancement**: enhancing the visibility of cellular structures is essential for accurate tracking. Utilizing a Top Hat filter, with the radius parameter set as the mean diameter of the objects of interest, facilitates effective particle enhancement, improving object separation and tracking accuracy.

***Suggested values range**: set as the mean diameter of the objects of interest*

5)	 Set the correct position of red and green channels, depending on the experiment, at lines 173-174.
6)	Run the macro from the Fiji script editor
7)	Set in the dialog window the input directory (where original data are stored), the output directory (where you want to store processed images) and the original file format

**Tracking Analysis**

1)	Open the TrackMate script in the Fiji macro editor
2)	Adjust the parameters settings (from line 39 to 58) according to the experiment
3)	Run the script from the Fiji script editor
4)	Set in the dialog window the input directory (where the images processed with the previous pipeline are stored) and the output directory (where you want to store the results table)

To set the tracking parameters, please refer to the guidelines contained into the Documentation and tutorial section of the TrackMate web page (https://imagej.net/plugins/trackmate/)

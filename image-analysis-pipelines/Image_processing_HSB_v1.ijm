//-----Macro for the preprocessing of Fucci timelapses images-----//
//---Author: Chiara Soriani
//---Created: May 2022
//---Last Modified:Sept 2023

//--DIALOG WINDOW TO SET INPUT, OUTPUT AND FILE TYPE

#@ File (label = "Input directory", style = "directory") input
#@ File (label = "Output directory", style = "directory") output
#@ String (label = "File suffix", value = ".nd2") suffix


//--FUNCTION DEFINITION

function processFile(input, output, file, ch_green, ch_red) {
	
	//--path definition
	path = input + File.separator + file;
	
	//--recall of Bio-Formats Macro Extensions to import proprietary files
	run("Bio-Formats Macro Extensions");
	
	Ext.setId(path);
	Ext.getCurrentFile(filename);
	Ext.getSeriesCount(seriesCount);
	
	for (s = 1; s <= seriesCount; s++) {

		// Leave the print statements until things work, then remove them.
		print("Processing: " + input + File.separator + file);
		run("Bio-Formats", "open=&path autoscale color_mode=Colorized rois_import=[ROI manager] view=Hyperstack stack_order=XYCZT series_"+s);
		title = getTitle();
		
		title_string = split(title, "/");
		image_title_temp = "";
		
		for (t = 0; t < title_string.length; t++) {
			
			new_title = image_title_temp+"_"+title_string[t];
			image_title_temp = new_title;
		}

		//this is to avoid the first _ symbol in the final name
		image_title = substring(image_title_temp, 1);
		Array.show(title_string);
		print(image_title);
		
		//--BASIC PROCESSING OF ORIGINAL FLUORESCENCE CHANNELS
		
		//--the Z-projection depends on the imaging settings (if necessary comment/uncomment the following lines)
		//run("Z Project...", "projection=[Max Intensity] all");
		//selectWindow(title);
		//close();
		//rename(title);
		run("Split Channels");
	
		//--processing of the green channel
		selectWindow(ch_green+title);
		
		//-flat-field correction with Basic plugin (https://biii.eu/basic)
		run("Re-order Hyperstack ...", "channels=[Channels (c)] slices=[Frames (t)] frames=[Slices (z)]");
		rename(ch_green+title+"forBasic");
		run("BaSiC ", "processing_stack=["+ch_green+title+"forBasic] flat-field=None dark-field=None shading_estimation=[Estimate shading profiles] shading_model=[Estimate flat-field only (ignore dark-field)] setting_regularisationparametes=Automatic temporal_drift=Ignore correction_options=[Compute shading and correct images] lambda_flat=0.50 lambda_dark=0.50");
		
		//-change processing steps according to the experiment
		run("Gaussian Blur...", "sigma=1 stack");
		run("Top Hat...", "radius=20 stack");
		
		//-background subtraction on green channel: per each frame the mean green fluorescence intensity is subtracted to the image (also Subtract background with rolling ball algorithm is good)
		getDimensions(width, height, channels, slices, frames);
		
	        for (n = 1; n <= slices; n++) {
	        	//Stack.setFrame(n);
	        	Stack.setSlice(n);
	        	getStatistics(area, mean, min, max, std, histogram);
	        	print(mean);
	        	run("Subtract...", "value="+mean+" slice");
	        }
	        
		//run("Subtract Background...", "rolling=50 stack");
		
		rename(ch_green+title);
		close(ch_green+title+"forBasic");
	
		//--processing of the red channel
		selectWindow(ch_red+title);
		run("Re-order Hyperstack ...", "channels=[Channels (c)] slices=[Frames (t)] frames=[Slices (z)]");
		rename(ch_red+title+"forBasic");
		run("BaSiC ", "processing_stack=["+ch_red+title+"forBasic] flat-field=None dark-field=None shading_estimation=[Estimate shading profiles] shading_model=[Estimate flat-field only (ignore dark-field)] setting_regularisationparametes=Automatic temporal_drift=Ignore correction_options=[Compute shading and correct images] lambda_flat=0.50 lambda_dark=0.50");
		
		//-change processing steps according to the experiment
		run("Gaussian Blur...", "sigma=1 stack");
		run("Subtract Background...", "rolling=50 stack");
		run("Top Hat...", "radius=20 stack");
		
		rename(ch_red+title);
		close(ch_red+title+"forBasic");
			
		run("Merge Channels...", "c1=["+ch_red+ title+"] c2=["+ch_green+ title+"] create ignore");
		run("Re-order Hyperstack ...", "channels=[Channels (c)] slices=[Frames (t)] frames=[Slices (z)]");
		
		//waitForUser("");
		
		title2 = getTitle();
		
		//--CREATION OF THE HUE SCALE
		
		run("Duplicate...", "duplicate channels=1-2");
		rename(title2+"_dup");
			
		selectWindow(title2);
		close();
		
		selectWindow(title2+"_dup");
		Stack.setChannel(1);
		setMinAndMax(0, 1400);//B&C RED parameters chosen by visual inspection (depends on the experiment)
		Stack.setChannel(2);
		setMinAndMax(0, 2000);//B&C GREEN parameters chosen by visual inspection (depends on the experiment)
		run("Duplicate...", "duplicate");
		rename(title2+"_duphsb");
		run("RGB Color", "frames");
		run("HSB Stack");
		run("Split Channels");
		
		//--processing of B (brightness) channel that will be used as a tracking channel
		selectWindow("C3-"+title2+"_duphsb");
		run("Top Hat...", "radius=20 stack");
		run("16-bit");
		
		//--processing of H (hue) channel that will be used as cell-cycle profiling channel
		selectWindow("C1-"+title2+"_duphsb");
		run("16-bit");
		
		//--recovering of red and green channels
		selectWindow(title2+"_dup");
		run("Split Channels");
		
		run("Merge Channels...", "c1=[C1-"+title2+"_dup] c2=[C2-"+title2+"_dup] c4=[C3-"+title2+"_duphsb] c6=[C1-"+title2+"_duphsb] create ignore");
		
		//--renaming of the resulting image according to the original name
		rename(image_title);
		saveAs("Tiff", output+File.separator + image_title);

		close("*");
		run("Collect Garbage");

	
		// Leave the print statements until things work, then remove them.
		//print("Processing: " + input + File.separator + file);
		print("Saving to: " + output);
	
}
    
}


// function to scan folders/subfolders/files to find files with correct suffix
function processFolder(input, ch_green, ch_red) {
	list = getFileList(input);
	list = Array.sort(list);
	for (i = 0; i < list.length; i++) {
		if(File.isDirectory(input + File.separator + list[i]))
			processFolder(input + File.separator + list[i]);
		if(endsWith(list[i], suffix))
			processFile(input, output, list[i], ch_green, ch_red);
	}
}


//---MAIN CODE

//--variable definition
ch_red = "C2-";
ch_green =  "C3-";

processFolder(input, ch_green, ch_red);

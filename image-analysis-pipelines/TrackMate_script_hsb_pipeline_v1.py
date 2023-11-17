#-----Script to execute TrackMate adapted from (https://imagej.net/plugins/trackmate/scripting/scripting)-----//
#---Author: Chiara Soriani
#---Created: May 2022
#---Last Modified: Sept 2023

#---DIALOG WINDOW TO SET INPUT AND OUTPUT FOLDERS

#@ File(label="Input directory", description="Select the directory with input images", style="directory") inputDir
#@ File(label="Output directory", description="Select the output directory", style="directory") outputFolder

#--PACKAGES IMPORT--
import sys
 
from ij import IJ
from ij import WindowManager
import os
import os.path
import csv
 
from fiji.plugin.trackmate import Model
from fiji.plugin.trackmate import Settings
from fiji.plugin.trackmate import TrackMate
from fiji.plugin.trackmate import SelectionModel
from fiji.plugin.trackmate import Logger
from fiji.plugin.trackmate.detection import LogDetectorFactory
#from fiji.plugin.trackmate.tracking import LAPUtils
from fiji.plugin.trackmate.tracking.jaqaman import SparseLAPTrackerFactory
from fiji.plugin.trackmate.providers import SpotAnalyzerProvider
from fiji.plugin.trackmate.providers import EdgeAnalyzerProvider
from fiji.plugin.trackmate.providers import TrackAnalyzerProvider
import fiji.plugin.trackmate.visualization.hyperstack.HyperStackDisplayer as HyperStackDisplayer
import fiji.plugin.trackmate.features.FeatureFilter as FeatureFilter
from fiji.plugin.trackmate.gui.displaysettings import DisplaySettingsIO
import fiji.plugin.trackmate.action.ExportStatsTablesAction as ExportStatsTablesAction
import fiji.plugin.trackmate.action.ExportAllSpotsStatsAction as ExportAllSpotsStatsAction
from ij.gui import WaitForUserDialog


#--TRACKING PARAMETERS SETTINGS--
#--Detector parameters
radius = 8.5; #put a Double number, no Integer!!
target_ch = 3;
spot_threshold = 0.1; #put a Double number, no Integer!!

#--Tracker parameters
max_dist = 50.0; #put a Double number, no Integer!!
gap_max_dist = 70.0; #put a Double number, no Integer!!
gap_frame = 3;

#--Add penalties for tracks creation
q_penalty = {
    'QUALITY' : 1.2
}

#--Track filters
track_displ = 10.0
track_duration = 70.0
track_start = 10

#--This reads the list of the files in the input folder
files_raw = []
for i in inputDir.listFiles():
	file_i = str(i)
	files_raw.append(i.getName())
	
n = len(files_raw)

#--We have to do the following to avoid errors with UTF8 chars generated in 
#--TrackMate that will mess with our Fiji Jython.
reload(sys)
sys.setdefaultencoding('utf-8')

#--Loop over images in folder input
for f in range(n):

	# Image preparation
	
	experiment = files_raw[f] # Get experiment file name
	imp = IJ.openImage(os.path.join(inputDir.getCanonicalPath(), experiment))
	print(experiment)

	# Get currently selected image
	#imp = WindowManager.getCurrentImage()
	#imp = IJ.openImage('https://fiji.sc/samples/FakeTracks.tif')
	#imp.show()
	 
	#----------------------------
	# Create the model object now
	#----------------------------
	 
	# Some of the parameters we configure below need to have
	# a reference to the model at creation. So we create an
	# empty model now.
	 
	model = Model()
	 
	# Send all messages to ImageJ log window.
	model.setLogger(Logger.IJ_LOGGER)
	 
	 
	 
	#------------------------
	# Prepare settings object
	#------------------------
	 
	#settings = Settings(imp)
	#for linux write two rows here below
	settings = Settings(imp)
	#settings.setFrom(imp)
	
	# Configure detector - We use the Strings for the keys
	settings.detectorFactory = LogDetectorFactory()
	settings.detectorSettings = {
	    'DO_SUBPIXEL_LOCALIZATION' : False,
	    'RADIUS' : radius,
	    'TARGET_CHANNEL' : target_ch,
	    'THRESHOLD' : spot_threshold,
	    'DO_MEDIAN_FILTERING' : True,
	}  
	 
	# Configure spot filters - Classical filter on quality
	#filter1 = FeatureFilter('QUALITY', 30, True)
	#settings.addSpotFilter(filter1)
	 
	# Configure tracker - We won't allow merges and fusions
	settings.trackerFactory = SparseLAPTrackerFactory()
	settings.trackerSettings = settings.trackerFactory.getDefaultSettings() # almost good enough
	settings.trackerSettings['ALLOW_TRACK_SPLITTING'] = False
	settings.trackerSettings['ALLOW_TRACK_MERGING'] = False
	
	settings.trackerSettings['LINKING_MAX_DISTANCE'] = max_dist
	settings.trackerSettings['LINKING_FEATURE_PENALTIES'] = q_penalty
	settings.trackerSettings['GAP_CLOSING_MAX_DISTANCE'] = gap_max_dist
	settings.trackerSettings['MAX_FRAME_GAP'] = gap_frame
	
	 
	# Add ALL the feature analyzers known to TrackMate. They will 
	# yield numerical features for the results, such as speed, mean intensity etc.
	#settings.addAllAnalyzers()
	
	spotAnalyzerProvider = SpotAnalyzerProvider(imp.getNChannels())
	trackAnalyzerProvider   = TrackAnalyzerProvider()
	for key in spotAnalyzerProvider.getKeys():
	    print( key )
	    settings.addSpotAnalyzerFactory( spotAnalyzerProvider.getFactory( key ) )
	
	for key in trackAnalyzerProvider.getKeys():
		#	print( key )
			settings.addTrackAnalyzer( trackAnalyzerProvider.getFactory( key ) )
	 
	# Configure track filters - We want to get rid of the two immobile spots at
	# the bottom right of the image. Track displacement must be above 10 pixels.
	 
	filter2 = FeatureFilter('TRACK_DISPLACEMENT', track_displ, True)
	settings.addTrackFilter(filter2)
	filter3 = FeatureFilter('TRACK_DURATION', track_duration, True)
	settings.addTrackFilter(filter3)
	#filter4 = FeatureFilter('TRACK_MEAN_SPEED', 5.0, True)
	#settings.addTrackFilter(filter4)
	filter5 = FeatureFilter('TRACK_START', track_start, False) #filter on tracks that start before "track_start" value
	settings.addTrackFilter(filter5)
	 

	 
	#-------------------
	# Instantiate plugin
	#-------------------
	
	trackmate = TrackMate(model, settings)
	trackmate.computeSpotFeatures( True )
	 
	#--------
	# Process
	#--------
	 
	ok = trackmate.checkInput()
	if not ok:
	    sys.exit(str(trackmate.getErrorMessage()))
	 
	ok = trackmate.process()
	if not ok:
	    sys.exit(str(trackmate.getErrorMessage()))
	 
	 
	#----------------
	# Display results
	#----------------
	
	selectionModel = SelectionModel( model )
	ds = DisplaySettingsIO.readUserDefault()
	displayer =  HyperStackDisplayer( model, selectionModel, imp, ds )
	displayer.render()
	displayer.refresh()
	 
	# Echo results with the logger we set at start:
	model.getLogger().log( str( model ) )
	
	 
	#----------------
	# Write results
	#----------------
	
	outpath = outputFolder.getPath() + "/"+ experiment + ".csv"
	with open(outpath, 'w') as resultFile:
		writer = csv.writer(resultFile)
		csvWriter = csv.writer(resultFile, delimiter=',', quotechar='|')
		#csvWriter.writerow(['SPOTS_ID', 'TRACK_ID','QUALITY','POSITION_X','POSITION_Y', 'FRAME', 'MEAN_INTENSITY_CH1', 'MEAN_INTENSITY_CH2', 'MEAN_INTENSITY_CH4'])
		csvWriter.writerow(['SPOTS_ID', 'TRACK_ID','QUALITY','POSITION_X','POSITION_Y', 'FRAME', 'MEAN_INTENSITY_CH1', 'MEAN_INTENSITY_CH2', 'MEAN_INTENSITY_CH3', 'MEAN_INTENSITY_CH4', 'MEAN_INTENSITY_CH5'])
	
	
		fm = model.getFeatureModel();
		for id in model.getTrackModel().trackIDs(True):
			#== Fetch the track feature from the feature model.
			v = fm.getTrackFeature(id, 'TRACK_MEAN_SPEED')
			model.getLogger().log('')
			model.getLogger().log('Track ' + str(id) + ': mean velocity = ' + str(v) + ' ' + model.getSpaceUnits() + '/' + model.getTimeUnits())
			track = model.getTrackModel().trackSpots(id)
			for spot in track:
				sid = spot.ID()
				#== Fetch spot features directly from spot. 
				x=spot.getFeature('POSITION_X')
				y=spot.getFeature('POSITION_Y')
				t=spot.getFeature('FRAME')
				q=spot.getFeature('QUALITY')
				track_id=id
				snr1=spot.getFeature('SNR_CH1') 
				mean1=spot.getFeature('MEAN_INTENSITY_CH1')
				snr2=spot.getFeature('SNR_CH2') 
				mean2=spot.getFeature('MEAN_INTENSITY_CH2')
				snr3=spot.getFeature('SNR_CH3') 
				mean3=spot.getFeature('MEAN_INTENSITY_CH3')
				snr4=spot.getFeature('SNR_CH4') 
				mean4=spot.getFeature('MEAN_INTENSITY_CH4')
				snr5=spot.getFeature('SNR_CH5') 
				mean5=spot.getFeature('MEAN_INTENSITY_CH5')
				model.getLogger().log('\tspot ID = ' + str(sid) + ': x='+str(x)+', y='+str(y)+', t='+str(t)+', q='+str(q)+', track_id='+str(track_id)+', snr_ch1='+str(snr1)+', mean_ch1 ='+str(mean1)+', snr_ch2='+str(snr2)+', mean_ch2 ='+ str(mean2)+', mean_ch3 ='+ str(mean3)+', mean_ch4 ='+ str(mean4)+', mean_ch5 ='+ str(mean5))
				csvWriter.writerow([str(sid), str(id), str(q), str(x),str(y), str(t), str(mean1), str(mean2), str(mean3), str(mean4), str(mean5)])
		
		#myWait = WaitForUserDialog ("myTitle", "myMessage")
		#myWait.show()
		resultFile.close()
		IJ.run("Close All", "")

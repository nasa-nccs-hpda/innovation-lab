#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import csv
from collections import namedtuple
import os
import shutil
import random
from osgeo.osr import SpatialReference

from model.MasRequest import MasRequest
from model.MaxEntRequest import MaxEntRequest
from model.ObservationFile import ObservationFile
from model.GeospatialImageFile import GeospatialImageFile

# -----------------------------------------------------------------------------
# class MmxRequest
# -----------------------------------------------------------------------------
class MmxRequest(object):
    
    Trial = namedtuple('Trial', ['directory', 'obsFile', 'images'])
    
    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    #    def __init__(self, observationFile, dateRange, numTrials=10,
    #                 outputDirectory):

    def __init__(self, observationFile, dateRange, collection, variables,
                 operation, numTrials, outputDirectory):

        if not os.path.exists(outputDirectory):
            raise RuntimeError(str(outputDirectory)) + ' does not exist.'
            
        if not os.path.isdir(outputDirectory):
            raise RuntimeError(str(outputDirectory) + ' must be a directory.')
            
        # ---
        # The top-level directory structure.
        # - outputDirectory
        #   - merra: raw merra files from requestMerra()
        #   - asc: merra files prepared for maxent.jar
        #   - trials: contains trial-n directories, one for each trial.
        # ---
        self._outputDirectory = outputDirectory
        self._merraDir = os.path.join(self._outputDirectory, 'merra')
        #self._ascDir = os.path.join(self._outputDirectory, 'asc')
        self._trialsDir = os.path.join(self._outputDirectory, 'trials')
        self._numTrials = numTrials
        self._observationFile = observationFile
        self._dateRange = dateRange
        self._collection = collection
        self._variables = variables
        self._operation = operation

        if not os.path.exists(self._merraDir):
            os.mkdir(self._merraDir)
        #if not os.path.exists(self._ascDir):
        #    os.mkdir(self._ascDir)
        if not os.path.exists(self._trialsDir):
            os.mkdir(self._trialsDir)

    # -------------------------------------------------------------------------
    # compileContributions
    # -------------------------------------------------------------------------
    def _compileContributions(self, trials):
        
        #---
        # Loop through the trials creating a dictionary like:
        # {predictor: [contribution, contribution, ...],
        #  predictor: [contribution, contribution, ...]} 
        #---
        contributions = {}
        CONTRIB_KWD = 'permutation'
        
        for trial in trials:
            
            resultsFile = os.path.join(trial.directory, 
                                       'maxentResults.csv')
                                       
            results = csv.reader(open(resultsFile))
            header = None
            
            try:
                header = results.next()

            except:
                raise RuntimeError('Error reading ' + str(resultsFile))

            for row in results:

                rowDict = dict(zip(header, row))
                
                for key in rowDict.iterkeys():
                    
                    if CONTRIB_KWD in key:
                        
                        newKey = key.split(CONTRIB_KWD)[0].strip()
                        
                        if newKey not in contributions:
                            contributions[newKey] = []

                        contributions[newKey].append(float(rowDict[key]))

            return contributions

    # -------------------------------------------------------------------------
    # getListofMerraImages
    # -------------------------------------------------------------------------
    def getListofMerraImages(self, files):

        # Convert the list of NetCDF files to GeospatialImageFiles
        list = []
        tgt_srs = SpatialReference()
        tgt_srs.ImportFromEPSG(4326)
        for file in files:
            list.append(GeospatialImageFile
                        (os.path.join(self._merraDir, file),tgt_srs))
        return list

    # -------------------------------------------------------------------------
    # getTopTen
    # -------------------------------------------------------------------------
    def getTopTen(self, trials):
        
        # Get the contributions of each predictor over all trials.
        contributions = self._compileContributions(trials)
        
        # Compute the average contribution of each predictor over all trials.
        averages = {}
        
        for key in contributions.iterkeys():
            
            samples = contributions[key]
            averages[key] = float(sum(samples) / max(len(samples), 1))
            
        # ---
        # Sort the averages to get the most significant contributors at the
        # top of the list.
        # ---
        sortedAvgs = sorted(averages.items(), 
                            key = lambda x:x[1], 
                            reverse = True)[:10]
                            
        topTen = []
        
        for k, v in sortedAvgs:
            pred = k+'.nc'
            topTen.append(pred)

        list = self.getListofMerraImages(topTen)
        return list
        
    # -------------------------------------------------------------------------
    # getTrialImageIndexes
    #
    # This method returns a list of lists.  Each inner list contains ten
    # randomly-chosen indexes into the set of MERRA input images.
    #
    # [[1, 3, 8, 4, ...], [31, 4, 99, ...], ...]
    # -------------------------------------------------------------------------
    def getTrialImagesIndexes(self, images):
        
        # Generate lists of random indexes in the files.
        indexesInEachTrial = []
        PREDICTORS_PER_TRIAL = 10  #10
        
#        for i in range(1, self.config.numTrials + 1):
        for i in range(1, int(self._numTrials) + 1):
            
            indexesInEachTrial.append(random.sample(range(0, len(images) - 1),
                                                    PREDICTORS_PER_TRIAL))
        
        return indexesInEachTrial
        
    # -------------------------------------------------------------------------
    # prepareOneTrial
    # -------------------------------------------------------------------------
    def prepareOneTrial(self, images, trialImageIndexes, trialNum):
        
        # Create a directory for this trial.
        TRIAL_NAME = 'trial-' + str(trialNum)
        TRIAL_DIR = os.path.join(self._trialsDir, TRIAL_NAME)
        
        if not os.path.exists(TRIAL_DIR):
            os.mkdir(TRIAL_DIR)
        
        # Get this trial's constituents.
        trialPredictors = [images[i] for i in trialImageIndexes]
        
        # Copy the samples file to the trial.
        obsBaseName = os.path.basename(self._observationFile._filePath)
        trialObsPath = os.path.join(TRIAL_DIR, obsBaseName)
        shutil.copyfile(self._observationFile.fileName(), trialObsPath)

        trialObs = ObservationFile(trialObsPath, 
                                   self._observationFile.species())
        
        # Copy the images to the trial.
        trailAscDir = os.path.join(TRIAL_DIR, 'asc')
        if not os.path.exists(trailAscDir):
           os.mkdir(trailAscDir)

        # Build the Trial structure to use later.
        trial = MmxRequest.Trial(directory=TRIAL_DIR,
                                 images=trialPredictors,
                                 obsFile=trialObs)

        return trial

    # -------------------------------------------------------------------------
    # requestMerra
    # -------------------------------------------------------------------------
    def requestMerra(self):

        masRequest = MasRequest(self._observationFile.envelope(),
                                self._dateRange,
                                self._collection,
                                self._variables,
                                self._operation,
                                self._merraDir)

        masRequest.run()

    # -------------------------------------------------------------------------
    # run
    # -------------------------------------------------------------------------
    def run(self):
        # ---
        # Get MERRA images.
        #
        # - outputDirectory
        #   - merra
        # ---
        # Check if required NetCDFs already existing,
        #       then skip data preparation
        existedVars = os.listdir(self._merraDir)
        requiredVars = [v+'.nc' for v in self._variables]
        if not all(elem in existedVars for elem in requiredVars):
            self.requestMerra()

        images = self.getListofMerraImages(requiredVars)

        # Get the random lists of indexes into Images for each trial.
        listOfIndexesInEachTrial = self.getTrialImagesIndexes(images)

        # ---
        # Prepare the trials.
        #
        # - outputDirectory
        #   - trials
        #     - trial-1
        #       - observation file
        #       - asc
        #         - asc image 1
        #         - asc image 2
        #         ...
        #     - trial-2
        #     ...
        # ---
        trialNum = 0
        trials = []

        for trialImageIndexes in listOfIndexesInEachTrial:
            trials.append(self.prepareOneTrial(images,
                                               trialImageIndexes,
                                               trialNum+1))
            trialNum += 1

        # Run the trials.
        for trial in trials:

            mer = MaxEntRequest(trial.obsFile, trial.images, trial.directory)
            mer.run()

        # Compile trial statistics and select the top-ten predictors.
        topTen = self.getTopTen(trials)

        # Run the final model.
        final = self.prepareOneTrial(topTen, range(0, len(topTen)-1), 'final')
        finalMer = MaxEntRequest(final.obsFile, final.images, final.directory)
        finalMer.run()



###############################################################################
###############################################################################
#       FUNCTIONS TO BE TESTED & INTEGRATED
###############################################################################
###############################################################################

    # -------------------------------------------------------------------------
    # requestMerra
    # -------------------------------------------------------------------------
    def requestMerraTest(self):
        variables = ['TSURF', 'BASEFLOW', 'ECHANGE']
        variablesY = ['BASEFLOW', 'ECHANGE', 'EVLAND', 'EVPINTR', 'EVPSBLN',
                      'EVPSOIL', 'FRSAT', 'FRSNO', 'FRUNST', 'FRWLT', 'GHLAND',
                      'GRN', 'GWETPROF', 'GWETROOT', 'GWETTOP', 'LAI',
                      'LHLAND', 'LWLAND', 'PARDFLAND', 'PARDRLAND',
                      'PRECSNOLAND', 'PRECTOTLAND', 'PRMC', 'QINFIL', 'RUNOFF',
                      'RZMC', 'SFMC', 'SHLAND', 'SMLAND', 'SNODP', 'SNOMAS',
                      'SPLAND', 'SPSNOW', 'SPWATR', 'SWLAND', 'TELAND',
                      'TPSNOW', 'TSAT', 'TSOIL1', 'TSOIL2', 'TSOIL3', 'TSOIL4',
                      'TSOIL5', 'TSOIL6', 'TSURF', 'TUNST', 'TWLAND', 'TWLT',
                      'WCHANGE']

        masRequest = MasRequest(self._observationFile.envelope(),
                                self._dateRange,
                                'tavg1_2d_lnd_Nx',
                                variablesY,
                                'avg',
                                self._merraDir)

        masRequest.run()
        return masRequest

    # -------------------------------------------------------------------------
    # runBatch
    #
    #  This method executes a batch of images - Quick test while we sort out run() granularity
    # -------------------------------------------------------------------------
    def runBatch(self):

        # ---
        # Get MERRA images.
        #
        # - outputDirectory
        #   - merra
        # ---
#        masRequest = self.requestMerra()
#        images = masRequest.getListOfImages()

        # simulate masRequest call for now
        self._tgt_srs = SpatialReference()
        self._tgt_srs.ImportFromEPSG(4326)
        srs = self._tgt_srs

        self._ncImages = list()
        self._ncImages.append(
            GeospatialImageFile(os.path.join(self._outputDirectory, '/home/jli/SystemTesting/testMasRequest/TSURF.nc'),
                                         srs))
        #self._ncImages.append(
        #    GeospatialImageFile(os.path.join(self._outputDirectory, '/home/jli/SystemTesting/testMasRequest/BASEFLOW.nc'),
        #                        srs))
        preparedImages = self._ncImages

        # GT - quick test to exercise batch of images
        #maxEntReq = MaxEntRequest(self._observationFile, self._ncImages, self._outputDirectory)
        #maxEntReq.run()
        #exit()

        for image in preparedImages:

            ascImagePath = MaxEntRequest.prepareImage(image, srs, self._observationFile.envelope(), self._ascDir)
            preparedImages.append(GeospatialImageFile(ascImagePath, srs))
#            preparedImages.append(GeospatialImageFile(image, srs))

        # Get the random lists of indexes into preparedImages for each trial.
        listOfIndexesInEachTrial = self.getTrialImagesIndexes(preparedImages)

    # -------------------------------------------------------------------------
    # runBatch
    #
    #  This method executes a batch of images - Quick test while we sort out run() granularity
    # -------------------------------------------------------------------------
    def runSimple(self):

        # ---
        # Get MERRA images.
        #
        # - outputDirectory
        #   - merra
        # ---
        masRequest = self.requestMerra()
        images = masRequest.getListOfImages()

        # simulate masRequest call for now
        #self._tgt_srs = SpatialReference()
        #self._tgt_srs.ImportFromEPSG(4326)
        #srs = self._tgt_srs

        #self._ncImages = list()
        #self._ncImages.append(
        #    GeospatialImageFile(os.path.join(self._outputDirectory, '/home/jli/SystemTesting/testMasRequest/TSURF.nc'),
        #                        srs))
        #self._ncImages.append(
        #    GeospatialImageFile(os.path.join(self._outputDirectory, '/home/jli/SystemTesting/testMasRequest/BASEFLOW.nc'),
        #                        srs))

        #preparedImages = self._ncImages
        preparedImages = images

        # GT - quick test to exercise batch of images
        maxEntReq = MaxEntRequest(self._observationFile, preparedImages, self._outputDirectory)
        maxEntReq.run()

    # -------------------------------------------------------------------------
    # runBatch
    #
    #  This method executes a batch of images - Quick test while we sort out run() granularity
    # -------------------------------------------------------------------------
    def runEdas(self):

        # ---
        # Get MERRA images.
        #
        # - outputDirectory
        #   - merra
        # ---
        masRequest = self.requestMerra()
        images = masRequest.getListOfImages()

        # simulate masRequest call for now
        #self._tgt_srs = SpatialReference()
        #self._tgt_srs.ImportFromEPSG(4326)
        #srs = self._tgt_srs

        #self._ncImages = list()
        #self._ncImages.append(
        #    GeospatialImageFile(os.path.join(self._outputDirectory, '/home/jli/SystemTesting/testMasRequest/TSURF.nc'),
        #                        srs))
        #self._ncImages.append(
        #    GeospatialImageFile(os.path.join(self._outputDirectory, '/home/jli/SystemTesting/testMasRequest/BASEFLOW.nc'),
        #                        srs))

        #preparedImages = self._ncImages
        preparedImages = images

        # GT - quick test to exercise batch of images
        maxEntReq = MaxEntRequest(self._observationFile, preparedImages, self._outputDirectory)
        maxEntReq.run()





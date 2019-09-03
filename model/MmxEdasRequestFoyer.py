#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import time
import csv
from collections import namedtuple
import os
import glob
import shutil
import random
from osgeo.osr import SpatialReference
from osgeo import gdal

from model.EdasRequestFoyer import EdasRequest
from model.MaxEntRequest import MaxEntRequest
from model.ObservationFile import ObservationFile
from model.GeospatialImageFile import GeospatialImageFile

from multiprocessing import Process

threadCatalog = dict({})
# Aggregate process to prepare for and run a trial using MaxEnt
def runTrial(observationFile, listOfImages, outputDirectory):

    mer = MaxEntRequest(observationFile, listOfImages, outputDirectory)
    mer.run()
# -----------------------------------------------------------------------------
# class MmxRequest
# -----------------------------------------------------------------------------
class MmxEdasRequest(object):
    Trial = namedtuple('Trial', ['directory', 'obsFile', 'images'])

    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    #    def __init__(self, observationFile, dateRange, numTrials=10,
    #                 outputDirectory):

    def __init__(self, observationFile, dateRange, collection, variables,
                 operation, numTrials, numPredictors, outputDirectory):

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
        self._trialsDir = os.path.join(self._outputDirectory, 'trials')
        self._numTrials = numTrials
        self._numPredictors = numPredictors
        self._observationFile = observationFile
        self._dateRange = dateRange
        self._collection = collection
        self._variables = variables
        self._operation = operation

        self._orgWCDir = "/att/nobackup/jli30/SystemTesting/worldClim/origin/5m/wc2.0_5m_bio"
        self._M2WCDir = "/att/nobackup/jli30/SystemTesting/worldClim/M2WdClim/5m"

        if not os.path.exists(self._merraDir):
            os.mkdir(self._merraDir)
        if not os.path.exists(self._trialsDir):
            os.mkdir(self._trialsDir)

    # -------------------------------------------------------------------------
    # compileContributions
    # -------------------------------------------------------------------------
    def _compileContributions(self, trials):

        # ---
        # Loop through the trials creating a dictionary like:
        # {predictor: [contribution, contribution, ...],
        #  predictor: [contribution, contribution, ...]} 
        # ---
        contributions = {}
        CONTRIB_KWD = 'permutation'

        for trial in trials:

            resultsFile = os.path.join(trial.directory,
                                       'maxentResults.csv')

            results = csv.reader(open(resultsFile))

            try:
                header = results.__next__()

            except:
                raise RuntimeError('Error reading ' + str(resultsFile))

            for row in results:

                rowDict = dict(zip(header, row))

                for key in rowDict.keys():

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
                        (os.path.join(self._merraDir, file), tgt_srs))
        return list

    # -------------------------------------------------------------------------
    # getTopTen
    # -------------------------------------------------------------------------
    def getTopTen(self, trials, images):

        # Get the contributions of each predictor over all trials.
        contributions = self._compileContributions(trials)

        # Compute the average contribution of each predictor over all trials.
        averages = {}

        for key in contributions.keys():
            samples = contributions[key]
            averages[key] = float(sum(samples) / max(len(samples), 1))

        # ---
        # Sort the averages to get the most significant contributors at the
        # top of the list.
        # ---
        sortedAvgs = sorted(averages.items(),
                            key=lambda x: x[1],
                            reverse=True)[:self._numPredictors]

        topTen = []

        for x in images:
            if (k in x._filePath for k, v in sortedAvgs):
                topTen.append(x)

        return topTen

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
        PREDICTORS_PER_TRIAL = self._numPredictors

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
        trial = MmxEdasRequest.Trial(directory=TRIAL_DIR,
                                     images=trialPredictors,
                                     obsFile=trialObs)

        return trial

    # -------------------------------------------------------------------------
    # requestMerra
    # -------------------------------------------------------------------------
    def requestMerra(self):

        existed = [os.path.basename(x) for x in glob.glob(f'{self._merraDir}/[!bio]*.nc')]
        required = [v + '.nc' for v in self._variables]

        if not all(elem in existed for elem in required):
            edasRequest = EdasRequest(self._observationFile.envelope(),
                                      self._dateRange,
                                      self._collection,
                                      self._variables,
                                      self._operation,
                                      self._merraDir)

            edasRequest.run()

        return required

    def requestWorldClim(self):

        collection = 'cip_merra2_mth'
        year = self._dateRange[0].year
        list = []

        existed = [os.path.basename(x) for x in glob.glob(f'{self._merraDir}/*bio*.nc')]
        required = [f'bio-{i+1}_{collection}_worldClim_{year}.nc' for i in range(0, 19)]

        if not all(elem in existed for elem in required):
            req = EdasRequest(self._observationFile.envelope(),
                                  self._dateRange,
                                  collection,
                                  'None',
                                  self._operation,
                                  self._merraDir)
            domain = [req.addDomain("d0", self._observationFile.envelope(), self._dateRange)]
            input = [req.addInput(collection, "tasmin", "minTemp", "d0"),
                    req.addInput(collection, "tasmax", "maxTemp", "d0"),
                     req.addInput(collection, "pr",  "moist", "d0")]
            operation = [dict(name="edas:worldClim", input="minTemp, maxTemp, moist")]
            requestSpec = dict(domain=domain, input=input, operation=operation)
            rsltdata=req.runEdas(requestSpec)
            dsets = rsltdata.getDataset()
            for var in dsets:
                s = var.split('[')[0]
                resultFile = f"{s}_{collection}_worldClim_{year}.nc"
                dsets[var].to_netcdf(f"{self._merraDir}/{resultFile}")
                list.append(resultFile)

        return required

    def getListofWorldClim(self, dir, files):
        tgt_srs = SpatialReference()
        required = []
        for file in files:
            prj = gdal.Open(os.path.join(dir, file)).GetProjection()
            tgt_srs.ImportFromWkt(prj)
            required.append(GeospatialImageFile(os.path.join(dir, file), tgt_srs))
        return required

    # -------------------------------------------------------------------------
    # requestMerraTest
    # -------------------------------------------------------------------------
    def requestMerraTest(self):

        collection = "merra2_t1nxslv"
        vars = ['T10M', 'U10M', 'V10M', 'QV10M', 'SLP']
        operation = 'ave'
        existed = [os.path.basename(x) for x in glob.glob(f'{self._merraDir}/[!bio]*.nc')]
        required = [v + '.nc' for v in vars]

        if not all(elem in existed for elem in required):
            edasRequest = EdasRequest(self._observationFile.envelope(),
                                      self._dateRange,
                                      collection,
                                      vars,
                                      operation,
                                      self._merraDir)

            edasRequest.run()

        return required

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

        ncFileList= []
        images = []

        if 'originWorldClim' in self._variables:
            fileList = glob.glob(f"{self._orgWCDir}/*bio*.tif")
            images += self.getListofWorldClim(self._orgWCDir, fileList)
            self._variables.remove('originWorldClim')

        if 'M2WorldClim' in self._variables:
            fileList = glob.glob(f"{self._M2WCDir}/*bio*.tif")
            images += self.getListofWorldClim(self._M2WCDir, fileList)
            self._variables.remove('M2WorldClim')

        if 'worldClim' in self._variables:
            ncFileList += self.requestWorldClim()
            self._variables.remove('worldClim')

#        ncFileList += self.requestMerra()
        ncFileList += self.requestMerraTest()
        if ncFileList:
            images += self.getListofMerraImages(ncFileList)

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
                                               trialNum + 1))
            trialNum += 1

        # Run the trials.
        # Run the trials in parallel using process multi-threading
        trialNum = 0
        for trial in trials:
            p = Process(target=runTrial, args=(trial.obsFile, trial.images, trial.directory))
            p.start()
            trialNum += 1
            threadCatalog[trialNum] = p

        # wait for the threads to complete
        keylist = threadCatalog.keys()
        for key in keylist:
            p = threadCatalog[key]
            p.join()

        # Compile trial statistics and select the top-ten predictors.
        topTen = self.getTopTen(trials, images)

#        topTenV = self.getListofWorldClim(self._orgWCDir, [s+".tif" for s in topTen])
#        topTenX = self.getListofWorldClim(self._M2WCDir, [s+".tif" for s in topTen])

        # Run the final model.
        final = self.prepareOneTrial(topTen, range(0, len(topTen) - 1),'final')

        s = time.time()
        finalMer = MaxEntRequest(final.obsFile, final.images, final.directory)

        finalMer.run()
        print(f"Executing time is {time.time()-s}")
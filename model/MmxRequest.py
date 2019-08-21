#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import csv
from collections import namedtuple
import os
import shutil
import random
from osgeo.osr import SpatialReference
import pandas

from model.MaxEntRequest import MaxEntRequest
from model.ObservationFile import ObservationFile
from model.GeospatialImageFile import GeospatialImageFile

from model.MultiThreader import MultiThreader
from model.RetrieverFactory import RetrieverFactory

# -------------------------------------------------------------------------
# runMaxEnt
# -------------------------------------------------------------------------
# Aggregate process to prepare for and run a trial using MaxEnt
def runMaxEnt(observationFile, listOfImages, outputDirectory):

    mer = MaxEntRequest(observationFile, listOfImages, outputDirectory)
    mer.run()

# -----------------------------------------------------------------------------
# class MmxRequest
# -----------------------------------------------------------------------------
class MmxRequest(object):
    Trial = namedtuple('Trial', ['directory', 'obsFile', 'images'])

    def __init__(self, context, source = "Edas"):

        # save source and context
        self._source = source
        self._context = context

        # validate incoming parameters
        self._validate(context)

        self._outputDirectory = context['outDir']
        self._merraDir = os.path.join(self._outputDirectory, 'merra')
        self._trialsDir = os.path.join(self._outputDirectory, 'trials')
        self._numTrials = context['numTrials']
        self._observationFilePath = context['observationFilePath']
        self._species = context['species']
        self._startDate = context['startDate']
        self._endDate = context['endDate']
        self._collection = context['collection']
        self._variables = context['listOfVariables']
        self._operation = context['operation']

        self._observationFile = ObservationFile(self._observationFilePath, self._species)
        self._dateRange = pandas.date_range(self._startDate, self._endDate)

        if not os.path.exists(self._outputDirectory):
            raise RuntimeError(str(self._outputDirectory)) + ' does not exist.'

        if not os.path.isdir(self._outputDirectory):
            raise RuntimeError(str(self._outputDirectory) + ' must be a directory.')

        if not os.path.exists(self._merraDir):
            os.mkdir(self._merraDir)
        if not os.path.exists(self._trialsDir):
            os.mkdir(self._trialsDir)

    # -------------------------------------------------------------------------
    # validate incoming parameters
    # -------------------------------------------------------------------------
    def _validate(self, context):
        requiredParms = {
            "observationFilePath", "species", "startDate", "endDate", "collection", \
            "listOfVariables", "operation", "numTrials", "startDate", "outDir"
        }
        for key in requiredParms:
            if not key in context.keys():
                raise RuntimeError(str(key)) + ' parameter does not exist.'

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
    def getTopTen(self, trials):

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
                            reverse=True)[:10]

        topTen = []

        for k, v in sortedAvgs:
            pred = k + '.nc'
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
        PREDICTORS_PER_TRIAL = 10

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
        trial = self.Trial(directory=TRIAL_DIR,
                                     images=trialPredictors,
                                     obsFile=trialObs)

        return trial

    # -------------------------------------------------------------------------
    # determineRequiredImages
    # -------------------------------------------------------------------------
    def selectRequiredImages(self):
        # ---
        # Get MERRA images.
        #
        # - outputDirectory
        #   - merra
        # ---
        # Check if required NetCDFs already existing,
        #       then skip data preparation
        existedVars = os.listdir(self._merraDir)
        requiredVars = [v + '.nc' for v in self._variables]
        if not all(elem in existedVars for elem in requiredVars):
            self.requestMerra()
        images = self.getListofMerraImages(requiredVars)
        return images

    # -------------------------------------------------------------------------
    # prepareTrials
    # -------------------------------------------------------------------------
    def prepareTrials(self, images, listOfIndexesInEachTrial):
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

        # Run the trials concurrently
        MultiThreader().runTrials(runMaxEnt, trials)
        return trials

    # -------------------------------------------------------------------------
    # runAggregateModel
    # -------------------------------------------------------------------------
    def runAggregateModel(self, topTen):

        # Run the model that aggregates the trials.
        final = self.prepareOneTrial(topTen, range(0, len(topTen) - 1),
                                     'final')
        runMaxEnt(final.obsFile, final.images, final.directory)

    # -------------------------------------------------------------------------
    # requestMerra
    # -------------------------------------------------------------------------
    def requestMerra(self):

        #  Get the proper Retriever from the factory and use it to execute the retrieval process
        retrieverInstance =  RetrieverFactory.retrieveRequest(self, self._source)
        retriever = retrieverInstance(self._context)
        retriever.retrieve(self._context)

    # -------------------------------------------------------------------------
    # run - refactored workflow
    # -------------------------------------------------------------------------
    def runMmxWorkflow(self):

        # Get MERRA images.
        images = self.selectRequiredImages()

        # Get the random lists of indexes into Images for each trial.
        listOfIndexesInEachTrial = self.getTrialImagesIndexes(images)

        # Prepare the trial infrastructure for MaxEnt output
        trials = self.prepareTrials(images, listOfIndexesInEachTrial)

        # Compile trial statistics and select the top-ten predictors.
        topTen = self.getTopTen(trials)

        # Run the final model.
        self.runAggregateModel(topTen)

    # -------------------------------------------------------------------------
    # run - run default MMX workflow, specify functions should be overridden here
    # -------------------------------------------------------------------------
    def run(self):
        self.runMmxWorkflow()

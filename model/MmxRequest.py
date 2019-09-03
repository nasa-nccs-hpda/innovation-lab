#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys, csv
from collections import namedtuple
import os
import shutil
import random
import glob
from osgeo.osr import SpatialReference
from osgeo import gdal

from model.MaxEntRequest import MaxEntRequest
from model.ObservationFile import ObservationFile
from model.GeospatialImageFile import GeospatialImageFile

from model.MultiThreader import MultiThreader

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

    def __init__(self, context):

        # validate incoming parameters
        self._validate(context)

        # save source and context
        self._context = context

        self._outputDirectory = context['outDir']
        self._trialsDir = os.path.join(self._outputDirectory, 'trials')
        self._numTrials = context['numTrials']
        self._numPredictors = context['numPredictors']
        self._observationFilePath = context['observation']
        self._species = context['species']

        self._observationFile = ObservationFile(self._observationFilePath, self._species)

        if not os.path.exists(self._outputDirectory):
            raise RuntimeError(str(self._outputDirectory)) + ' does not exist.'

        if not os.path.isdir(self._outputDirectory):
            raise RuntimeError(str(self._outputDirectory) + ' must be a directory.')

        if not os.path.exists(self._trialsDir):
            os.mkdir(self._trialsDir)

    # -------------------------------------------------------------------------
    # validate incoming parameters
    # -------------------------------------------------------------------------
    def _validate(self, context):
        requiredParms = [
            "observation", "species", "numTrials", "numPredictors", "outDir"
        ]
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
                # Skip 1st record to get to actual data
                # Don't like it, but we need different reader per Python 2 (binary) and 3 (text)
                if sys.version_info[0] < 3:
                    header = results.next()
                else:
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
                            reverse=True)[:10]

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
    def getTrialImagesIndexes(self, images, numPredictors):

        # Generate lists of random indexes in the files.
        indexesInEachTrial = []
        for i in range(1, int(self._numTrials) + 1):
            indexesInEachTrial.append(random.sample(range(0, len(images) - 1),
                                                    numPredictors))

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
        # final = self.prepareOneTrial(topTen, range(0, len(topTen) - 1),
        final = self.prepareOneTrial(topTen, range(0, len(topTen)),
                                     'final')
        runMaxEnt(final.obsFile, final.images, final.directory)

    # -------------------------------------------------------------------------
    # determineRequiredImages
    # -------------------------------------------------------------------------
    def getExistingImages(self, filepath):
        existingFiles = glob.glob(filepath)
        if existingFiles is None:
            raise RuntimeError(' Required image files missing from: ' + filepath )

        tgt_srs = SpatialReference()
        images = []
        for file in existingFiles:
            prj = gdal.Open(os.path.join(filepath, file)).GetProjection()
            tgt_srs.ImportFromWkt(prj)
            images.append(GeospatialImageFile(os.path.join(filepath, file), tgt_srs))
        return images

    # -------------------------------------------------------------------------
    # run - refactored workflow
    # -------------------------------------------------------------------------
    def runMaxEnt(self, images):

        # Get the random lists of indexes into Images for each trial.
        listOfIndexesInEachTrial = self.getTrialImagesIndexes(images, self._numPredictors)

        # Prepare the trial infrastructure for MaxEnt output
        trials = self.prepareTrials(images, listOfIndexesInEachTrial)

        # Compile trial statistics and select the top-ten predictors.
        topTen = self.getTopTen(trials, images)

        # Run the final model.
        self.runAggregateModel(topTen)

    # -------------------------------------------------------------------------
    # run - refactored workflow
    # -------------------------------------------------------------------------
    def runMmxWorkflow(self):
        # Get Existing Images
        images = self.getExistingImages(self._context['imageDir'])
        # Run Maximum Entropy workflow.
        self.runMaxEnt(images)

    # -------------------------------------------------------------------------
    # run - run default MMX workflow, specify functions should be overridden here
    # -------------------------------------------------------------------------
    def run(self):
        self.runMmxWorkflow()

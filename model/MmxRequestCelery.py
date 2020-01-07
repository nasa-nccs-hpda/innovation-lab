#!/usr/bin/env python2
# -*- coding: utf-8 -*-


from CeleryConfiguration import app

from model.MaxEntRequestCelery import MaxEntRequestCelery
from model.MmxRequest import MmxRequest


# -----------------------------------------------------------------------------
# class MmxRequestCelery
# -----------------------------------------------------------------------------
class MmxRequestCelery(MmxRequest):

    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self, observationFile, dateRange, collection, variables,
                 operation, numTrials, outputDirectory):

        # Initialize the base class.
        super(MmxRequestCelery, self).__init__(observationFile, 
                                               dateRange, 
                                               collection, 
                                               variables,
                                               operation, 
                                               numTrials, 
                                               outputDirectory)
                                               
        self._trialNum = 0

    # -------------------------------------------------------------------------
    # prepareOneTrial
    #
    # Serialization:
    #
    # - images is a list of GeospatialImageFiles.  Pickle can serialize lists
    #   when they are comprised of objects Pickle can serialize.  
    #   GeospatialImageFile is serializable with Pickle because it has 
    #   __getstate__ and __setstate__.
    #
    # - trialImageIndexes is a list of integers.  Pickle can serialise lists
    #   and integers.
    #
    # - trialNum is an integer, which Pickle can serialize.
    # -------------------------------------------------------------------------
    @app.task(serializer='pickle')
    def prepareOneTrial(self, images, trialImageIndexes, trialNum):
        
        self._trialNum += 1
        
        trial = super(MmxRequestCelery, self.). \
                     prepareOneTrial(images, trialImageIndexes, self._trialNum)
                     
        return trial

    # -------------------------------------------------------------------------
    # prepareTrials
    # -------------------------------------------------------------------------
    def prepareTrials(self, images, listOfIndexesInEachTrial):

        wpi = group(MmxRequestCelery.prepareOneTrial.s(
                        images,
                        trialImageIndexes) 
                        for trialImageIndexes in listOfIndexesInEachTrial

        result = wpi.apply_async()
        
        #---
        # This returns a list of results from each subtask in the group.
        # See "Group Results" at
        # http://docs.celeryproject.org/en/latest/userguide/canvas.html#groups
        #---
        trials = result.get()    # Waits for wpi to finish.

        return trials

    # -------------------------------------------------------------------------
    # runOneTrial
    #
    # Serialization:
    #
    # The trial argument, defined in MmxRequest, is a named tuple consisting of
    # directory, observation file and list of images.  As long as Pickle can
    # serialize the components, it can serialize the named tuple.
    #
    # - Tuple name is a string, natively serializable.
    # - Directory is a string, natively serializable.
    # - ObservationFile has __getstate__ and __setstate__
    # -------------------------------------------------------------------------
    @app.task(serializer='pickle')
    def runOneTrial(self, trial):
        
        mer = MaxEntRequestCelery(trial.obsFile, trial.images, trial.directory)
        
    # -------------------------------------------------------------------------
    # runPartiallyDistributed
    #
    # This is mostly for experimentation.  A proper run method will complete
    # all MMX steps through Celery.
    # -------------------------------------------------------------------------
    def runPartiallyDistributed(self):

        # Get MERRA images.        
        existingVars = os.listdir(self._merraDir)
        requiredVars = [v + '.nc' for v in self._variables]
        
        if not all(elem in existingVars for elem in requiredVars):
            self.requestMerra()

        images = self.getGeospatialImageFiles(requiredVars)

        # Get the random lists of indexes into Images for each trial.
        listOfIndexesInEachTrial = self.getTrialImagesIndexes(images)

        # Prepare trials.
        trials = self.prepareTrials(images, listOfIndexesInEachTrial)
        
        # Run trials.
        wpi = group(MmxRequestCelery.runOneTrial.s(trial) for trial in trials
        result = wpi.apply_async()
        result.get()    # Waits for wpi to finish.        
        
        # Compile trial statistics and select the top-ten predictors.
        topTen = self.getTopTen(trials)

        # Run the final model.
        final = self.prepareOneTrial(topTen, 
                                     range(0, len(topTen) - 1),
                                     'final')

        mer = MaxEntRequestCelery(final.obsFile, final.images, final.directory)
        mer.run()
        
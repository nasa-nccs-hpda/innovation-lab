#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#from multiprocessing import Process
from billiard.context import Process

# -----------------------------------------------------------------------------
# class MultiThreader
# -----------------------------------------------------------------------------
class MultiThreader(object):

    # -------------------------------------------------------------------------
    # runTrials - run trials concurrently (convenience method with knowledge of trial parms)
    # -------------------------------------------------------------------------
    def runTrials(self, process, trials):

        # create a thread for each trial
        trialNum = 0
        threadCatalog = dict({})
        for trial in trials:
            p = Process(target=process, args=(trial.obsFile, trial.images, trial.directory, trial.maxEntPath))
            p.start()
            trialNum += 1
            threadCatalog[trialNum] = p

        # wait for the threads to complete
        keylist = threadCatalog.keys()
        for key in keylist:
            p = threadCatalog[key]
            p.join()

    # -------------------------------------------------------------------------
    # runThread - generalized method to run threads concurrently
    # -------------------------------------------------------------------------
    def runThreads(self, process, processArgs):

        # create a thread for each trial
        threadNum = 0
        threadCatalog = dict({})
        for parms in processArgs:
            p = Process(target=process, args=(parms))
            p.start()
            threadNum += 1
            threadCatalog[threadNum] = p

        # wait for the threads to complete
        keylist = threadCatalog.keys()
        for key in keylist:
            p = threadCatalog[key]
            p.join()

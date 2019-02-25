#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os

from model.MaxEntRequest import MaxEntRequest


# -----------------------------------------------------------------------------
# class MmxRequest
# -----------------------------------------------------------------------------
class MmxRequest(object):
    
    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self, observationFilePath, species, dateRange, numTrials=10, 
                 outputDirectory):
                 
        self._numTrials = numTrials
        
        self._masRequest =
                
        # Defer validation to MasRequest and MaxEntRequest.
        maxEntDir = os.path.join(outputDirectory, 'maxEnt')
        
        self._maxEntRequest = MaxEntRequest(observationFilePath,
                                            species,
                                            ***listOfImages,
                                            maxEntDir)


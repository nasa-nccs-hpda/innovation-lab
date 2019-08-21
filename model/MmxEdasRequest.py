#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from model.MmxRequest import MmxRequest

# -----------------------------------------------------------------------------
# class MmxRequest
# -----------------------------------------------------------------------------
class MmxEdasRequest(MmxRequest):

    def __init__(self, context, source = "Edas"):
        MmxRequest.__init__(self, context)

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
    # run - run default MMX workflow, specify functions should be overridden here
    # -------------------------------------------------------------------------
    def run(self):
       self.runMmxWorkflow()

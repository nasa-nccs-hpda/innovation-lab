#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import glob

from model.MmxRequest import MmxRequest
from model.EdasRequest import EdasRequest

# -----------------------------------------------------------------------------
# class MmxRequest
# -----------------------------------------------------------------------------
class MmxRmRequest(MmxRequest):
    def __init__(self, context, source = "Edas"):
        MmxRequest.__init__(self, context, source)

    # -------------------------------------------------------------------------
    # validate incoming parameters
    # -------------------------------------------------------------------------
    def _validate(self, context):
        requiredParms = {
            "observationFilePath", "species", "startDate", "endDate", "collection", \
            "listOfVariables", "operation", "numTrials", "numPredictors", "startDate", "outDir"
        }
        for key in requiredParms:
            if not key in context.keys():
                raise RuntimeError(str(key)) + ' parameter does not exist.'

    # -------------------------------------------------------------------------
    # getMerra
    # -------------------------------------------------------------------------
    def getMerra(self):

        existed = [os.path.basename(x) for x in glob.glob(f'{self._merraDir}/[!bio]*.nc')]
        required = [v + '.nc' for v in self._variables]

        if not all(elem in existed for elem in required):
            self.requestMerra()

        return required

    # -------------------------------------------------------------------------
    # requestMerra
    # -------------------------------------------------------------------------
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

    # -------------------------------------------------------------------------
    # run
    # -------------------------------------------------------------------------
    def run(self):
        # ---
        # Get MERRA images.
        # Check if required NetCDFs already existing,
        #       then skip data preparation
        ncFileList= []

        if 'inDir' not in self._context.keys():
            # Get MERRA images.
            if 'worldClim' in self._variables:
                ncFileList += self.requestWorldClim()
                self._variables.remove('worldClim')

            ncFileList += self.getMerra()
            images = self.getListofMerraImages(ncFileList)
        else:
            # Get MERRA images.
            existedVars = os.listdir(self._inputDirectory)
            images = self.getListofMerraImages(existedVars)


        # Run Maximum Entropy workflow.
        self.runMaxEnt(images)
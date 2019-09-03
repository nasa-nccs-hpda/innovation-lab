#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
from osgeo.osr import SpatialReference
from osgeo import gdal

import pandas
import glob

from model.MmxRequest import MmxRequest
from model.GeospatialImageFile import GeospatialImageFile
from model.RetrieverFactory import RetrieverFactory

# -----------------------------------------------------------------------------
# class MmxRequest
# -----------------------------------------------------------------------------
class MmxRmRequest(MmxRequest):

    def __init__(self, context, source="EdasFoyer"):
        super(MmxRmRequest, self)._validate(context)
        super(MmxRmRequest, self).__init__(context)

        self._source = source
        self._dateRange = pandas.date_range(context['startDate'], context['endDate'])
        self._imageDir = os.path.join(context['outDir'], 'merra')
        if not os.path.exists(self._imageDir):
            os.mkdir(self._imageDir)

    # -------------------------------------------------------------------------
    # validate incoming parameters
    # -------------------------------------------------------------------------
    def _validate(self, context):

        requiredParms = [
            'startDate', 'endDate', 'collection', 'vars', 'operation', 'outDir'
        ]
        for key in requiredParms:
            if key not in context.keys():
                raise RuntimeError(str(key)) + ' parameter does not exist.'

        keys = ['operation', 'collection', 'vars']
        if not len(context['collection']) == len(context['operation']) == len(context['vars']):
            raise RuntimeError('Number of '+' '.join(keys)+' are not consistent.')

    def requestMerra(self, context):
        #  Get the proper Retriever from the factory and use it to execute the retrieval process
        retrieverInstance = RetrieverFactory.retrieveRequest(self, self._source)
        retriever = retrieverInstance(context, self._observationFile.envelope(), self._dateRange)
        return retriever.retrieve(context)

    # -------------------------------------------------------------------------
    # get lis of MERRA images
    # -------------------------------------------------------------------------
    def getListofMerraImages(self, files):
        # Convert the list of NetCDF files to GeospatialImageFiles
        list = []
        tgt_srs = SpatialReference()
        tgt_srs.ImportFromEPSG(4326)
        for file in files:
            list.append(GeospatialImageFile
                        (os.path.join(self._imageDir, file), tgt_srs))
        return list

    # -------------------------------------------------------------------------
    # get lis of WorldClim images
    # -------------------------------------------------------------------------
    def getListofWorldClim(self, dir, files):
        # Convert the list of WorldClim files to GeospatialImageFiles
        tgt_srs = SpatialReference()
        list = []
        for file in files:
            prj = gdal.Open(os.path.join(dir, file)).GetProjection()
            tgt_srs.ImportFromWkt(prj)
            list.append(GeospatialImageFile(os.path.join(dir, file), tgt_srs))
        return list

    # -------------------------------------------------------------------------
    # run
    # -------------------------------------------------------------------------
    def runMmxWorkflow(self):
        # Execute the EDAS retrieval process
        ncFileList= []
        if self._context['EdasWorldClim']:
            c = self._context
            c['imageDir'] = self._imageDir
            ncFileList += self.requestMerra(c)

        subcontext = {k: self._context[k] for k in ('operation', 'vars', 'collection')}
        contextlist = [{k: v[i] for k, v in subcontext.items()} for i in range(max(map(len, subcontext.values())))]
        for c in contextlist:
            c['imageDir'] = self._imageDir
            ncFileList += self.requestMerra(c)

        images = []
        # Convert NetCDF files to GeoSpatialImages
        images += self.getListofMerraImages(ncFileList)

        # Convert WorldClim files, if present, to GeoSpatialImages
        if self._context['WorldClim'] is not None:
            worldClimDir = self._context['WorldClim']
            files = glob.glob(f"{worldClimDir}/*")
            images += self.getListofWorldClim(worldClimDir, files)

        if self._context['MERRAClim'] is not None:
            worldClimDir = self._context['WorldClim']
            files = glob.glob(f"{worldClimDir}/*")
            images += self.getListofWorldClim(worldClimDir, files)

        # Run Maximum Entropy workflow.
        self.runMaxEnt(images)
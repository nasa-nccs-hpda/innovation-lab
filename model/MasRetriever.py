#!/usr/bin/python

import os
import glob
import pandas as pd
from multiprocessing import Process
from osgeo.osr import SpatialReference

from CDSLibrary import CDSApi
from model.RetrieverInterface import RetrieverInterface

cds_lib = CDSApi()


# -----------------------------------------------------------------------------
# class MasRequest
# -----------------------------------------------------------------------------
class MasRetriever(RetrieverInterface):
    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self, context, envelope=None, dateRange=None):

        self.envelope = envelope
        self.dateRange = dateRange
        self._listOfVars = context['vars']
        self._outDir = context['imageDir']

        self._ds = {
            'job_name': 'MMX_MasRequest',
            'service': 'M2AS',
            'service_request': 'GetVariableByCollection_Operation_TimeRange_' +
                               'SpatialExtent_VerticalExtent',
            'start_level': 1,
            'end_level': 1,
            'operation': context['operation'],
            'collection': context['collection'],
            }
        self._tgt_srs = SpatialReference()
        self._tgt_srs.ImportFromEPSG(4326)

    # -------------------------------------------------------------------------
    # retrieve analytic results
    # -------------------------------------------------------------------------
    def _getResult(self, sessionId, filename):
        response = cds_lib.poll(self._ds['service'], sessionId, filename,
                                cds_lib.cds_ws.config)
        sessionStatus = cds_lib.getElement(response, "sessionStatus")
        if sessionStatus == 'Completed':
            cds_lib.downloadResult(sessionStatus, self._ds['service'],
                                   sessionId, self._outDir, filename)

    # -------------------------------------------------------------------------
    # set date range for MAS operation
    # -------------------------------------------------------------------------
    def _setDateRange(self, dateRange):
        fmt = '%Y%m%d'
        m2DateRange = pd.date_range('1980-1-1', '2018-11-27')

        if len(dateRange) < 2:
            raise RuntimeError('Date range must contain start and end dates')

        if not dateRange.isin(m2DateRange).all():
            raise RuntimeError('MERRA2 data are available between ' +
                               m2DateRange.strftime(fmt)[0] + ' and ' +
                               m2DateRange.strftime(fmt)[-1])

        self._ds['start_date'] = dateRange.strftime(fmt)[0]
        self._ds['end_date'] = dateRange.strftime(fmt)[-1]

    # -------------------------------------------------------------------------
    # set spatial domain for MAS operation
    # -------------------------------------------------------------------------
    def _setDomain(self, env):

        env.TransformTo(self._tgt_srs)

        self._ds['min_lon'] = env.ulx()
        self._ds['max_lon'] = env.lrx()
        self._ds['min_lat'] = env.lry()
        self._ds['max_lat'] = env.uly()

    # -------------------------------------------------------------------------
    # run MAS operation
    # -------------------------------------------------------------------------
    def run(self):
        existed = [os.path.basename(x) for x in glob.glob(f'{self._outDir}/*.nc')]
        required = [f'{v}.nc' for v in self.listOfVariables]

        if not all(elem in existed for elem in required):

            sessionCatalog = {}

            for var in self._listOfVars:
                self._ds['variable_list'] = var
                sessionId = cds_lib.placeOrder(self._ds['service'],
                                               self._ds['service_request'],
                                               self._ds)
                if "Failed" in sessionId:
                    raise RuntimeError("{0}".format(sessionId))
                else:
                    sessionCatalog[var] = sessionId

            keylist = sessionCatalog.keys()
            keylist.sort()
            jobs = []
            for key in keylist:
                filename = key + '.nc'
                p = Process(target=self._getResult,
                            args=(sessionCatalog[key], filename))
                p.start()
                jobs.append(p)

            for j in jobs:
                j.join()

        return required

    # -------------------------------------------------------------------------
    # perform retrieval
    # -------------------------------------------------------------------------
    def retrieve(self, context):
        return self.run()
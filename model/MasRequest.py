#!/usr/bin/python

import pandas as pd
from multiprocessing import Process
from osgeo.osr import SpatialReference
from CDSLibrary import CDSApi

cds_lib = CDSApi()


# -----------------------------------------------------------------------------
# class MasRequest
# -----------------------------------------------------------------------------
class MasRequest(object):
    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self, envelope, dateRange,
                 collection, listOfVariables, operation, outDir):

        self._ds = {
            'job_name': 'MMX_MasRequest',
            'service': 'M2AS',
            'service_request': 'GetVariableByCollection_Operation_TimeRange_'+
                               'SpatialExtent_VerticalExtent',
            'start_level': 1,
            'end_level': 1,
            'operation': operation,
            'collection': collection,
        }

        self._setDateRange(dateRange)
        self._setDomain(envelope)

        self._listOfVars = listOfVariables
        self._outDir = outDir

    # -------------------------------------------------------------------------
    # retrieve analytic results
    # -------------------------------------------------------------------------
    def _getResult(self, service, sessionId, filename):
        response = cds_lib.poll(service, sessionId, filename,
                                cds_lib.cds_ws.config)
        sessionStatus = cds_lib.getElement(response, "sessionStatus")
        if sessionStatus == "Completed":
            cds_lib.downloadResult(sessionStatus, service, sessionId,
                                   self._outDir, filename)

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
        tgt_srs = SpatialReference()
        tgt_srs.ImportFromEPSG(4326)

        env.transformTo(tgt_srs)

        self._ds['min_lon'] = env.ulx()
        self._ds['max_lon'] = env.lrx()
        self._ds['min_lat'] = env.lry()
        self._ds['max_lat'] = env.uly()

    # -------------------------------------------------------------------------
    # run MAS operation
    # -------------------------------------------------------------------------
    def run(self):
        sessionCatalog = {}
        threadCatalog = {}

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
        for key in keylist:
            filename = key + '.nc'
            p = Process(target=self._getResult,
                      args=(self._ds['service'], sessionCatalog[key],filename))
            p.start()
            threadCatalog[sessionCatalog[key]] = p

        keylist = threadCatalog.keys()
        keylist.sort()
        for key in keylist:
            p = threadCatalog[key]
            p.join()
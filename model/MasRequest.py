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
        self._envelope = envelope
        self._dateRange = dateRange
        self._collection = collection
        self._listOfVars = listOfVariables
        self._operation = operation
        self._outDir = outDir
        self._ds = dict({})

    # -------------------------------------------------------------------------
    # retrieve analytic results
    # -------------------------------------------------------------------------
    @staticmethod
    def _getResult(service, sessionId, filename, outDir):
        response = cds_lib.poll(service, sessionId, filename,
                                cds_lib.cds_ws.config)
        sessionStatus = cds_lib.getElement(response, "sessionStatus")
        if sessionStatus == "Completed":
            cds_lib.downloadResult(sessionStatus, service, sessionId,
                                   outDir, filename)

    # -------------------------------------------------------------------------
    # set date range for MAS operation
    # -------------------------------------------------------------------------
    def _setDateRange(self, dateRange):
        fmt = '%Y%m%d'
        m2DateRange = pd.date_range('1980-1-1', '2018-11-27', periods=2)

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
        if not env:
            raise RuntimeError('Envelope was not provided')

        tgt_srs = SpatialReference()
        tgt_srs.ImportFromEPSG(4326)

        if not tgt_srs.IsSame(env.srs()):
            env.transformTo(tgt_srs)

        self._ds['min_lon'] = env.ulx()
        self._ds['max_lon'] = env.lrx()
        self._ds['min_lat'] = env.lry()
        self._ds['max_lat'] = env.uly()

    # -------------------------------------------------------------------------
    # set parameters for MAS operation
    # -------------------------------------------------------------------------
    def _formDict(self):
        self._ds = {
            'job_name': 'MMX_MasRequest',
            'service': 'M2AS',
            'service_request': 'GetVariableByCollection_Operation_TimeRange_SpatialExtent_VerticalExtent',
            'start_level': 1,
            'end_level': 1,
            'operation': self._operation,
            'collection': self._collection,
        }
        self._setDateRange(self._dateRange)

        self._setDomain(self._envelope)

    # -------------------------------------------------------------------------
    # run MAS operation
    # -------------------------------------------------------------------------
    def run(self):
        sessionCatalog = dict({})
        threadCatalog = dict({})
        self._formDict()
        ds = self._ds
        listOfVars = self._listOfVars.split(',')
        for var in listOfVars:
            ds['variable_list'] = var
            sessionId = cds_lib.placeOrder(ds['service'],
                                           ds['service_request'], ds)
            if "Failed" in sessionId:
                raise RuntimeError("{0}".format(sessionId))
            else:
                sessionCatalog[var] = sessionId

        keylist = sessionCatalog.keys()
        keylist.sort()
        for key in keylist:
            filename = key + '.nc'
            p = Process(target=self._getResult,
                        args=(ds['service'], sessionCatalog[key],
                              filename, self._outDir))
            p.start()
            threadCatalog[sessionCatalog[key]] = p

        keylist = threadCatalog.keys()
        keylist.sort()
        for key in keylist:
            p = threadCatalog[key]
            p.join()

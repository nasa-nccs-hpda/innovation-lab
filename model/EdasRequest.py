#!/usr/bin/python
import os
import shutil
from osgeo.osr import SpatialReference

from model.GeospatialImageFile import GeospatialImageFile

from stratus.app.core import StratusCore
from stratus_endpoint.handler.base import TaskHandle


# -----------------------------------------------------------------------------
# class EdasRequest
# -----------------------------------------------------------------------------
class EdasRequest(object):
    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self, edasCfgFile, envelope, dateRange, collection, listOfVariables, operation, outDir):

        self.envelop = envelope
        self.dateRange = dateRange

        self.collection = collection
        self.listOfVariables = listOfVariables
        self.operation = operation

        self._tgt_srs = SpatialReference()
        self._tgt_srs.ImportFromEPSG(4326)

        self._outDir = outDir
        self._ncImages = list()
        self.client = self._setClient()
        self._edasCfgFile = edasCfgFile

    # -------------------------------------------------------------------------
    # initialize Edas Client
    # -------------------------------------------------------------------------
    def _setClient(self):
        settings = dict(
            stratus=dict(type="rest",
                         API="wps",
                         host_address="https://edas.nccs.nasa.gov/wps/cwt")
        )
        core = StratusCore(settings)
        return core.getClient()

    # -------------------------------------------------------------------------
    # set spatial and temporal domain
    # -------------------------------------------------------------------------
    def addDomain(self, domainname, env, date):
        env.TransformTo(self._tgt_srs)

        return dict(name=domainname,
            lat=dict(start=env.lry()-0.5, end=env.uly()+0.5, system="values"),
            lon=dict(start=env.ulx()-0.5, end=env.lrx()+0.5, system="values"),
            time=dict(start=f"{date[0]}", end=f"{date[-1]}",crs="timestamps"),)

    # -------------------------------------------------------------------------
    # set target variable
    # -------------------------------------------------------------------------
    def addInput(self, col, var, varname, domainname):
        return dict(uri=f"collection://{col}", name=f"{var}:{varname}",
                    domain=f"{domainname}")

    # -------------------------------------------------------------------------
    # set Edas operation
    # -------------------------------------------------------------------------
    def addOperation(self, varname, opr, axes):
        return dict(name=f"xarray.{opr}", axes=f"{axes}", input=f"{varname}")

    # -------------------------------------------------------------------------
    # execute Edas request
    # -------------------------------------------------------------------------
    def runEdas(self, edas_request):
        task: TaskHandle = self.client.request(edas_request)
        result = task.getResult(block=True)
        return result.header.get('file')

    # -------------------------------------------------------------------------
    # run
    # -------------------------------------------------------------------------
    def run(self):
        domain = [self.addDomain("d0", self.envelop, self.dateRange)]
        operation = [self.addOperation("v0", self.operation, "t")]

        for var in self.listOfVariables:
            edas_request = dict(
                domain=domain,
                operation=operation,
                input=[self.addInput(self.collection, var, "v0", "d0")],
            )

            rstfile = self.runEdas(edas_request)
            outfile = var + '.nc'

            outPath = os.path.join(self._outDir, outfile)
            shutil.copy(rstfile, outPath)
            self._ncImages.append(
                GeospatialImageFile(outPath, self._tgt_srs))

    # -------------------------------------------------------------------------
    # SRS for output NC files
    # -------------------------------------------------------------------------
    def getSRS(self):
        return self._tgt_srs

    # -------------------------------------------------------------------------
    # list of output NC images
    # -------------------------------------------------------------------------
    def getListOfImages(self):
        if not self._ncImages:
            raise RuntimeError('No images exist')
        else:
            return self._ncImages

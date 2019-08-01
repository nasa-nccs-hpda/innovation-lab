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
    def __init__(self, envelope, dateRange,
                 collection, listOfVariables, operation, outDir):

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

    # -------------------------------------------------------------------------
    # initialize Edas Client
    # -------------------------------------------------------------------------
    def _setClient(self):
        settings = dict(
            stratus=dict(type="zeromq",
                         client_address = "foyer101",
                         request_port = "4556",
                         response_port = "4557")
        )
        core = StratusCore(settings)
        return core.getClient()

    # -------------------------------------------------------------------------
    # set spatial and temporal domain
    # -------------------------------------------------------------------------
    def addDomain(self, domainname, env, date):
        env.TransformTo(self._tgt_srs)
        sd = date[0].strftime("%Y-%m-%dT%HZ")
        ed = date[-1].strftime("%Y-%m-%dT%HZ")
        return dict(name=domainname,
            lat=dict(start=env.lry()-1.5, end=env.uly()+1.5, system="values"),
            lon=dict(start=env.ulx()-1.5, end=env.lrx()+1.5, system="values"),
            time=dict(start=f"{sd}", end=f"{ed}",system="timestamps"),)

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
        return dict(name=f"edas:{opr}", axes=f"{axes}", input=f"{varname}")

    # -------------------------------------------------------------------------
    # execute Edas request
    # -------------------------------------------------------------------------
    def runEdas(self, edas_request):
        task: TaskHandle = self.client.request(edas_request)
        result = task.getResult(block=True)
        return result

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

            rstdata = self.runEdas(edas_request)
            outfile = var + '.nc'

            outPath = os.path.join(self._outDir, outfile)
            rstdata.getDataset().to_netcdf(outPath)

#!/usr/bin/python
import os
import shutil
import glob
from osgeo.osr import SpatialReference

from stratus.app.core import StratusCore
from stratus_endpoint.handler.base import TaskHandle

from model.RetrieverInterface import RetrieverInterface

# -----------------------------------------------------------------------------
# class EdasProdRetriever
# -----------------------------------------------------------------------------
class EdasProdRetriever(RetrieverInterface):

    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self, context, envelope=None, dateRange=None):

        self.envelope = envelope
        self.dateRange = dateRange

        self.collection = context['collection']
        self.listOfVariables = context['vars']
        self.operation = context['operation']

        self._outDir = context['imageDir']
        self._tgt_srs = SpatialReference()
        self._tgt_srs.ImportFromEPSG(4326)
        self.client = None
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
        domain = [self.addDomain("d0", self.envelope, self.dateRange)]
        operation = [self.addOperation("v0", self.operation, "t")]

        existed = [os.path.basename(x) for x in glob.glob(f'{self._outDir}/*.nc')]
        required = [f'{v}.nc' for v in self.listOfVariables]

        if not all(elem in existed for elem in required):
            self.client = self._setClient()
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

        return required

    # -------------------------------------------------------------------------
    # perform retrieval
    # -------------------------------------------------------------------------
    def retrieve(self, context):
        return self.run()

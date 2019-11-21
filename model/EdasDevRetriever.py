#!/usr/bin/python
import os
import glob
import pandas
from osgeo.osr import SpatialReference

from stratus.app.core import StratusCore
from stratus_endpoint.handler.base import TaskHandle

from model.RetrieverInterface import RetrieverInterface

# -----------------------------------------------------------------------------
# class EdasDevRetriever
# -----------------------------------------------------------------------------
class EdasDevRetriever(RetrieverInterface):
    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self, context, envelope=None, dateRange=None):

        self.collection = context['collection'] if 'collection' in context.keys() else None
        self.listOfVariables = context['vars'] if 'vars' in context.keys() else None
        self.operation = context['operation'] if 'operation' in context.keys() else None
        self._outDir = context['imageDir']

        self.envelope = envelope
        self.dateRange = dateRange

        self._worldClim = context['EdasWorldClim'] if 'EdasWorldClim' in context.keys() else False

        self._tgt_srs = SpatialReference()
        self._tgt_srs.ImportFromEPSG(4326)
        self.client = None


    # -------------------------------------------------------------------------
    # initialize Edas-Slurm Client
    # -------------------------------------------------------------------------
    def _setClient(self):
        settings = dict(
            stratus=dict(type="endpoint",
                         module="edas.stratus.endpoint",
                         object="EDASEndpoint"
                         )
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

                rstdata = self.runEdas(edas_request)
                outfile = var + '.nc'

                outPath = os.path.join(self._outDir, outfile)
                rstdata.getDataset().to_netcdf(outPath)

        return required

    def getWorldClim(self):

        collection = 'cip_merra2_mth'
        year = self.dateRange[0].year

        existed = [os.path.basename(x) for x in glob.glob(f'{self._outDir}/*bio*.nc')]
        required = [f'bio-{i+1}_{collection}_worldClim_{year}.nc' for i in range(0, 19)]

        if not all(elem in existed for elem in required):
            self.client = self._setClient()
            #Adding extra months for worldClim request
            offset = pandas.DateOffset(months=1)
            period = pandas.date_range(self.dateRange[0]-offset, self.dateRange[-1]+offset, freq='MS')

            domain = [self.addDomain("d0", self.envelope, period)]

            inputs = [self.addInput(collection, "tasmin", "minTemp", "d0"),
                      self.addInput(collection, "tasmax", "maxTemp", "d0"),
                      self.addInput(collection, "pr",  "moist", "d0")]
            operation = [dict(name="edas:worldClim", input="minTemp, maxTemp, moist")]
            requestSpec = dict(domain=domain, input=inputs, operation=operation)

            rsltdata=self.runEdas(requestSpec)

            dsets = rsltdata.getDataset()
            for var in dsets:
                s = var.split('[')[0]
                resultFile = f"{s}_{collection}_worldClim_{year}.nc"
                dsets[var].to_netcdf(f"{self._outDir}/{resultFile}")

        return required

    def retrieve(self, context):
        if self._worldClim:
            return self.getWorldClim()
        else:
            return self.run()

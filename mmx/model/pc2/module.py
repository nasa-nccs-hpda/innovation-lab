from pc2base.module.handler.base import Module, TaskResult, TaskHandle, Status
from mmx.model.MmxRequest import MmxRequest
import string, traceback, atexit, os
from typing import List, Dict, Any, Sequence, BinaryIO, TextIO, ValuesView, Tuple, Optional, Iterable
HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(HERE)), "data")

class MMXModule(Module):

    def __init__( self, **kwargs ):
        Module.__init__( self, **kwargs )
        self._epas = [ "mmx*" ]
        self.obsDir = kwargs.get( "observation.dir", os.path.join(DATA_DIR,"csv") )
        self.imageDir = kwargs.get("image.dir", os.path.join(DATA_DIR,"merra") )
        self.outDir = kwargs.get("result.dir", os.path.join(DATA_DIR,"trials") )
        atexit.register( self.shutdown, "ShutdownHook Called" )

    def epas( self ) -> List[str]: return self._epas

    def init( self ):
        pass

    def capabilities(self, type: str, **kwargs  ) -> Dict:
        if type == "epas": return dict( epas = self._epas )

    def getObservations(self, requestSpec: Dict ):
        observations: str = self.getRequestParameter(requestSpec, "observations")
        if not observations.endswith(".csv"): observations = observations + ".csv"
        return os.path.join(self.obsDir, observations)

    def getOutDir(self, opSpec: Dict ):
        outDir: str = opSpec.get( 'outDir', self.outDir )
        try: os.makedirs( outDir )
        except: pass
        return outDir

    def request(self, requestSpec: Dict, inputs: List[TaskResult] = None, **kwargs ) -> "TaskHandle":
        operations = requestSpec["operation"]
        context = {}
        context['rid']: str = kwargs.get('rid', self.randomStr(4))
        context['cid']: str = kwargs.get('cid', self.randomStr(4))
        self.logger.info(f"MMXModule--> processing rid {context['rid']}")
        try:
            for opSpec in operations:
                context['imageDir'] = opSpec.get( 'imageDir', self.imageDir )
                context['outDir']   = self.getOutDir( opSpec )
                context['observation'] = self.getObservations( opSpec )
                context['species']     = self.getRequestParameter( opSpec, "species" )
                context['numTrials']   = int( self.getRequestParameter( opSpec, "numTrials" ) )
                context['numPredictors'] = int( self.getRequestParameter( opSpec, "numPredictors" ) )
                mmxr = MmxRequest(context)
                mmxr.run()

        except Exception as err:
            self.logger.error( "Caught execution error: " + str(err) )
            traceback.print_exc()
            return TaskHandle(rid=context['rid'], cid=context['cid'], status = Status.ERROR, error = self.getErrorReport(err) )

        return TaskHandle(rid=context['rid'], cid=context['cid'], status=Status.COMPLETED )

    def shutdown(self, *args, **kwargs ): pass

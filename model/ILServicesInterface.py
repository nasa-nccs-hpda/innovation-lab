
import abc
#from typing import Dict

class ILServicesInterface:
    __metaclass__ = abc.ABCMeta

    def __init__( self, **kwargs ):
        self.parms = kwargs

    @abc.abstractmethod
    def order(self, context) -> dict: pass
#    def order(self, service, request, context) -> dict: pass

    @abc.abstractmethod
    def status(self, context) -> dict: pass

    @abc.abstractmethod
    def download(self, context) -> dict: pass


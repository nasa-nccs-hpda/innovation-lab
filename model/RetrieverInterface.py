'''
Created on August 18, 2019

@author: gtamkin
'''
import abc

class RetrieverInterface(object):
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, config):
        super(RetrieverInterface, self).__init__()
        self.config = config
        if self.__class__ is RetrieverInterface:
            raise NotImplementedError

    @abc.abstractmethod
    def retrieve(self, context):
        """The Retrieve method provides a generic way of providing submission information packages (SIP) to a service provider."""
        return

    @abc.abstractmethod
    def validate(self, context):
        """The Retrieve method provides a generic way of providing submission information packages (SIP) to a service provider."""
        return
    

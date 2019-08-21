'''
Created on August 18, 2019

@author: gtamkin
'''
import abc

class RetrieverFactory(object):
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, config):
        super(RetrieverFactory, self).__init__()
        self.config = config
        if self.__class__ is RetrieverFactory:
            raise NotImplementedError

    def retrieveRequest(self, source):
        """This method returns the context-sensitive retriever."""
        clazzName = "{0}Request".format(source)
        # import the class from module
        mod = __import__("model.{0}".format(clazzName), globals(), locals(), [clazzName])
        classobj = getattr(mod, clazzName)
        return classobj

    

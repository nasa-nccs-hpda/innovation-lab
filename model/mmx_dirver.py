import sys,os
from model.MmxRequest import MmxRequest

def main():
    context = {}
    localpath = '/home/jli/SystemTesting/testMmxAlone'

    context['observation']=os.path.join(localpath, 'obs','ebd_Cassins_2016.csv')
    context['species']='Cassins Sparrow'
    context['outDir']=localpath
    context['numTrials']=3
    context['numPredictors']=2

    #path to NetCDF files
    context['imageDir']=os.path.join(localpath, 'merra')

    mmxr = MmxRequest(context)
    mmxr.run()

if __name__ == "__main__":
    sys.exit(main())

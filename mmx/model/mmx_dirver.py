import sys,os
from mmx.model.MmxRequest import MmxRequest
HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join( os.path.dirname(HERE), "data" )

def main():

    context = {}
    context['observation']=os.path.join( DATA_DIR, 'csv','ebd_Cassins_2016.csv' )
    context['species']='Cassins Sparrow'
    context['outDir']=DATA_DIR
    context['numTrials']=3
    context['numPredictors']=2
    context['imageDir']=os.path.join( DATA_DIR, 'merra' )    #path to NetCDF files

    mmxr = MmxRequest(context)
    mmxr.run()

if __name__ == "__main__":
    sys.exit(main())

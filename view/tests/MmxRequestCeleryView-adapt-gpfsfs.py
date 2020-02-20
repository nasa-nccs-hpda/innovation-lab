import requests
from celery import Celery
from celery import chain
from celery.utils.log import get_task_logger
import json
import subprocess
import os

#from IPython.display import IFrame

logger = get_task_logger(__name__)

from view.MmxRequestTranslationView import order, status, download

app = Celery('MmxRequestCeleryView', broker='redis://localhost:6379/0')

@app.task
def _order(context):
    resp = order(context)
    return resp

@app.task
def _status(context):
    resp = status(context)
    print('\nStatus -> Service: ', context['service'], ' Request: ', context['request'] , ' Status: ', context['status'])
    return resp

@app.task
def _download(context):
    resp = download(context)
    return resp

def _nextStep(context, service, request):
    context['service'] = service
    context['request'] = request
    context['status'] = 'PENDING'
    print('\nExercise -> Service: ', service, ' Request: ', request, ' \nContext: ', context)
    #logger.info('Execute: %s %s %s', service, request, context)
    os.system("rm -rf /att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/testWorldClim/TMworldClim_fac/trials/*")
    return context

def asynch_func(context):
         _order.delay(context)

def chain_func(context):
    resp = context
    try:
        resp = chain(
                _nextStep(context,'IL','subsetData'),
                _order(context),

                _nextStep(context, 'MMX','prepareImages'),
                _order(context),

                _nextStep(context, 'MMX','runTrials'),
                _order(context),

                _nextStep(context,'MMX','getTopPredictors'),
                _order(context),

                _nextStep(context,'MMX','runFinalModel'),
                _order(context),
                )
        print(resp)

    except Exception as e:
        print (e)
        print("\nMmx chain finished.  Final Context:", resp)

    return resp

if __name__ == "__main__":

        json_string = "{\"observation\":\"/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/CassinSparrowData/ebd_Cassins_2006.csv\", " \
                        "\"species\":\"Cassins Sparrow\", \"startDate\":\"2006-01-01\", \"endDate\":\"2007-01-01\", \"collection\":\"merra2_t1nxslv\", " \
                        "\"vars\":\"U10M V10M\", \"operation\":\"ave\", \"EdasWorldClim\":\"True\", " \
                        "\"outDir\":\"/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/testWorldClim/TMworldClim_fac\", \"numTrials\":\"2\", \"numPredictors\":\"3\", " \
                        "\"workflow\":\"Rm\"}"
        context = json.loads(json_string)
        print("\nMmx chain starting.  Initial Context:", context)
#        print(json.dumps(context))
#        asynch_func(context)
        chain_func(context)

#        IFrame(src='../../../../../SystemTesting/testWorldClim/TMworldClim_fac/trials/trial-final/Cassins_Sparrow.html', width=700, height=600)
#        IFrame(src='../../../../../SystemTesting/testWorldClim/TMworldClim_fac/trials/trial-final/Cassins_Sparrow.png', width=700, height=600)

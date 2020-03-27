from celery import Celery
from celery import chain
from celery.utils.log import get_task_logger
import json
import os

logger = get_task_logger(__name__)

from view.MmxRequestTranslationView import order, status, download

app = Celery('MmxRequestJSONView', broker='redis://localhost:6379/0')

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
    deletStr = "rm -rf " + context['outDir'] + "/trials/*"
    os.system(deletStr)
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

        json_string = "{\"observation\":\"/att/nobackup/iluser/mmx/input/ebd_Cassins_2006.csv\", " \
                        "\"species\":\"Cassins Sparrow\", \"startDate\":\"2006-01-01\", \"endDate\":\"2007-01-01\", \"collection\":\"merra2_t1nxslv\", " \
                        "\"vars\":\"U10M V10M\", \"operation\":\"ave\", \"EdasWorldClim\":\"True\", " \
                        "\"outDir\":\"/att/nobackup/iluser/mmx/output\", \"numTrials\":\"2\", \"numPredictors\":\"3\", " \
                        "\"workflow\":\"Rm\"}"
        context = json.loads(json_string)
        context['inDir'] = "/att/nobackup/iluser/mmx/input"
        context['outDir'] = "/att/nobackup/iluser/mmx/output"
        print("\nMmx chain starting.  Initial Context:", context)
        chain_func(context)


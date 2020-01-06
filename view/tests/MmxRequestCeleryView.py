import requests
from celery import Celery
from celery import chain
from celery.utils.log import get_task_logger
import json
import subprocess
import os

# -----------------------------------------------------------------------------
#  MmxRequestCeleryView
# -----------------------------------------------------------------------------

logger = get_task_logger(__name__)

from view.MmxRequestTranslationView import order, status, download

app = Celery('MmxRequestCeleryView', broker='redis://localhost:6379/0')

# -------------------------------------------------------------------------
    _order - place order for Mmx processing
# -------------------------------------------------------------------------
@app.task
def _order(context):
    resp = order(context)
    return resp

# -------------------------------------------------------------------------
    _status - determine status of order for Mmx processing
# -------------------------------------------------------------------------
@app.task
def _status(context):
    resp = status(context)
    print('\nStatus -> Service: ', context['service'], ' Request: ', context['request'] , ' Status: ', context['status'])
#    os.system("rm -rf /att/nobackup/gtamkin/SystemTesting/testWorldClim/TMworldClim_fac/trials/*")
    return resp

# -------------------------------------------------------------------------
    _download - download result
# -------------------------------------------------------------------------
@app.task
def _download(context):
    resp = download(context)
    return resp

# -------------------------------------------------------------------------
    _nextStep - prepare context for next stage of workflow
# -------------------------------------------------------------------------
def _nextStep(context, service, request):
    context['service'] = service
    context['request'] = request
    context['status'] = 'PENDING'
    print('\nExercise -> Service: ', service, ' Request: ', request, ' \nContext: ', context)
    #logger.info('Execute: %s %s %s', service, request, context)
    os.system("rm -rf /att/nobackup/gtamkin/SystemTesting/testWorldClim/TMworldClim_fac/trials/*")
    return context

# -------------------------------------------------------------------------
    _chain_func - chain together dependent stages of workflow
# -------------------------------------------------------------------------
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
        print("\nMmx chain finished.  Final Context:", resp)

    return resp

    except Exception as e:
#        print(e)
        n = 1

    print("\nMmx chain finished.  Final Context:", resp)

    return resp

# -----------------------------------------------------------------------------
# main
#
# cd innovation-lab/view/tests
# export PYTHONPATH=`pwd`
# mkdir ~/SystemTesting/testMmx
# mkdir ~/SystemTesting/testMaxEnt/merra
# view/MmxRequestCeleryView.py
#--json_string="{\"observationFilePath\":\"/home/jli/SystemTesting/MaxEntData/GSENM/CSV_Field_Data/GSENM_cheat_pres_abs_2001.csv\", \"species\":\"Cheat Grass\", \"startDate\":\"1985-02-01\", \"endDate\":\"1985-04-01\", \"collection\":\"cip_merra2_mth\", \"listOfVariables\":\"tas ps uas vas tasmax tasmin pr prc hfls hfss rlus rsus\", \"operation\":\"ave\", \"outDir\":\"/home/jli/SystemTesting/testEdasReq/\", \"numTrials\":\"10\"}"

if __name__ == "__main__":

        json_string = "{\"observation\":\"/att/nobackup/gtamkin/SystemTesting/CassinSparrowData/ebd_Cassins_2006.csv\", " \
                        "\"species\":\"Cassins Sparrow\", \"startDate\":\"2006-01-01\", \"endDate\":\"2007-01-01\", \"collection\":\"merra2_t1nxslv\", " \
                        "\"vars\":\"U10M V10M\", \"operation\":\"ave\", \"EdasWorldClim\":\"True\", " \
                        "\"outDir\":\"/att/nobackup/gtamkin/SystemTesting/testWorldClim/TMworldClim_fac\", \"numTrials\":\"2\", \"numPredictors\":\"3\", " \
                        "\"workflow\":\"Rm\"}"
        context = json.loads(json_string)
        print("\nMmx chain starting.  Initial Context:", context)
#        print(json.dumps(context))
        chain_func(context)

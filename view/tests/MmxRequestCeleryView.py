from celery import Celery
from celery import chain
from celery.utils.log import get_task_logger
import json
import os
import argparse

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
    # Process command-line args.
    desc = 'This application runs Maximum Entropy.'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-f',
                        required=True,
                        help='Path to observation file')

    parser.add_argument('-i',
                        required=True,
                        help='Path to directory of input image files')

    parser.add_argument('-o',
                        required=True,
                        help='Path to output directory')

    parser.add_argument('-s',
                        default='Cassins Sparrow',
                        help='Name of species in observation file')

    parser.add_argument('-sd',
                        default='2006-01-01',
                        help='Start date')

    parser.add_argument('-ed',
                        default='2007-01-01',
                        help='End date')

    parser.add_argument('-c',
                        default='merra2_t1nxslv',
                        help='Collection')

    parser.add_argument('-v',
                        default='U10M V10M',
                        help='Variables')

    parser.add_argument('-op',
                        default='ave',
                        help='Operation')

    parser.add_argument('-ewc',
                        default='True',
                        help='EdasWorldClim on')

    parser.add_argument('-t',
                        default='2',
                        help='Number of trials')

    parser.add_argument('-p',
                        default='3',
                        help='Number of predictors')

    parser.add_argument('-w',
                        default='Rm',
                        help='Workflow')

    '''
    # Example CLI/API invocation
    -f
    "/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/CassinSparrowData/ebd_Cassins_2006.csv"
    -i
    "/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/testWorldClim/TMworldClim_fac/merra"
    -o
    "/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/testWorldClim/TMworldClim_fac"
    -s
    "Cassins Sparrow"
    -sd
    "2006-01-01"
    -ed
    "2007-01-01"
    -c
    "merra2_t1nxslv"
    -v
    "U10M V10M"
    -op
    "ave"
    -ewc
    "True"
    -t
    "2"
    -p
    "3"
    -w
    "Rm"
'''
    args = parser.parse_args()
    print(args.s)

    # format key value pairs for json
    observation = "\"observation\"" + ":\"" + args.f + "\""
    inDir = "\"inDir\"" + ":\"" + args.i + "\""
    outDir = "\"outDir\"" + ":\"" + args.o + "\""
    species = "\"species\"" + ":\"" + args.s + "\""
    startDate = "\"startDate\"" + ":\"" + args.sd + "\""
    endDate = "\"endDate\"" + ":\"" + args.ed + "\""
    collection = "\"collection\"" + ":\"" + args.c + "\""
    vars = "\"vars\"" + ":\"" + args.v + "\""
    operation = "\"operation\"" + ":\"" + args.op + "\""
    edasWorldClim = "\"EdasWorldClim\"" + ":\"" + args.ewc + "\""
    numTrials = "\"numTrials\"" + ":\"" + args.t + "\""
    numPredictors = "\"numPredictors\"" + ":\"" + args.p + "\""
    workflow = "\"workflow\"" + ":\"" + args.w + "\""

    json_string = "{" + observation + "," + \
        inDir +  "," + \
        outDir +  "," + \
        species +  "," + \
        startDate + "," + \
        endDate + "," + \
        collection + "," + \
        vars + "," + \
        operation + "," + \
        edasWorldClim + "," + \
        numTrials + "," + \
        numPredictors + "," + \
        workflow + "}"

    json_string_ = "{" + observation + "," + \
                        inDir +  "," + \
                        outDir +  "," + \
                        species +  "," + \
                        "\"startDate\":\"2006-01-01\", \"endDate\":\"2007-01-01\", \"collection\":\"merra2_t1nxslv\", " \
                        "\"vars\":\"U10M V10M\", \"operation\":\"ave\", \"EdasWorldClim\":\"True\", " \
                        "\"numTrials\":\"2\", \"numPredictors\":\"3\", " \
                        "\"workflow\":\"Rm\"}"
    context = json.loads(json_string)
    print("\nMmx chain starting.  Initial Context:", context)
    chain_func(context)

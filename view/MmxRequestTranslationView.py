#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import argparse
import sys

from model.MmxRequest import MmxRequest
import json

# -----------------------------------------------------------------------------
# main
#
# cd innovation-lab
# export PYTHONPATH=`pwd`
# mkdir ~/SystemTesting/testMmx
# mkdir ~/SystemTesting/testMaxEnt/merra
# view/MmxRequestTranslationView.py
#--json_string="{\"observationFilePath\":\"/home/jli/SystemTesting/MaxEntData/GSENM/CSV_Field_Data/GSENM_cheat_pres_abs_2001.csv\", \"species\":\"Cheat Grass\", \"startDate\":\"1985-02-01\", \"endDate\":\"1985-04-01\", \"collection\":\"cip_merra2_mth\", \"listOfVariables\":\"tas ps uas vas tasmax tasmin pr prc hfls hfss rlus rsus\", \"operation\":\"ave\", \"outDir\":\"/home/jli/SystemTesting/testEdasReq/\", \"numTrials\":\"10\"}"

# -----------------------------------------------------------------------------
def createList(string):
    innerList = []
    outerList = []
    splitString = string.split()
    for i in splitString:
            innerList.append(i)
    outerList.append(innerList)
    return outerList

def order(context):

    # convert space-delimited string to list for consistency with CLI view and set defaults
    orig_collection = context['collection']
    orig_vars = context['vars']
    orig_operation = context['operation']

    context['collection'] = createList(context['collection'])
    context['vars'] = createList(context['vars'])
    context['operation'] = createList(context['operation'])

    if 'numTrials' not in context.keys():  context['numTrials'] = 10
    if 'numPredictors' not in context.keys():  context['numPredictors'] = 10
    if 'inDir' not in context.keys():  context['inDir'] = '.'
    if 'outDir' not in context.keys():  context['outDir'] = '.'
    if 'source' not in context.keys():  context['source'] = 'EdasDev'
    if 'workflow' not in context.keys():  context['workflow'] = ''
    if 'service' not in context.keys():  context['service'] = ''
    if 'request' not in context.keys():  context['request'] = ''
    if 'images' not in context.keys():  context['images'] = ''

    # Dynamically select workflow request (defaults to MmxRequest)
    clazzName = "Mmx{0}Request".format(context['workflow'])
    # import the class from module
    mod = __import__("model.{0}".format(clazzName), globals(), locals(), [clazzName])
    requestInstance = getattr(mod, clazzName)
    mmxr = requestInstance(context, context['source'])

    context = mmxr.order(context)

    context['collection'] = orig_collection
    context['vars'] = orig_vars
    context['operation'] = orig_operation
    return context

def status(context):
    orig_collection = context['collection']
    orig_vars = context['vars']
    orig_operation = context['operation']

    context['collection'] = createList(context['collection'])
    context['vars'] = createList(context['vars'])
    context['operation'] = createList(context['operation'])

    # Dynamically select workflow request (defaults to MmxRequest)
    clazzName = "Mmx{0}Request".format(context['workflow'])
    # import the class from module
    mod = __import__("model.{0}".format(clazzName), globals(), locals(), [clazzName])
    requestInstance = getattr(mod, clazzName)
    mmxr = requestInstance(context, context['source'])

    context = mmxr.status(context)
    context['collection'] = orig_collection
    context['vars'] = orig_vars
    context['operation'] = orig_operation

    return context

def download(context):
    orig_collection = context['collection']
    orig_vars = context['vars']
    orig_operation = context['operation']

#    context['collection'] = createList(context['collection'])
#    context['vars'] = createList(context['vars'])
#    context['operation'] = createList(context['operation'])

    # Dynamically select workflow request (defaults to MmxRequest)
    clazzName = "Mmx{0}Request".format(context['workflow'])
    # import the class from module
    mod = __import__("model.{0}".format(clazzName), globals(), locals(), [clazzName])
    requestInstance = getattr(mod, clazzName)
    mmxr = requestInstance(context, context['source'])

    context = mmxr.download(context)
    context['collection'] = orig_collection
    context['vars'] = orig_vars
    context['operation'] = orig_operation

    return context


# ------------------------------------------------------------------------------
# Invoke the main
# ------------------------------------------------------------------------------
if __name__ == "__main__":

    # Process command-line args.  Example:
    # --json_string="{\"observationFilePath\":\"/home/jli/SystemTesting/MaxEntData/GSENM/CSV_Field_Data/GSENM_cheat_pres_abs_2001.csv\", \"species\":\"Cheat Grass\", \"startDate\":\"1985-02-01\", \"endDate\":\"1985-04-01\", \"collection\":\"cip_merra2_mth\", \"listOfVariables\":\"tas ps uas vas tasmax tasmin pr prc hfls hfss rlus rsus\", \"operation\":\"ave\", \"outDir\":\"/home/jli/SystemTesting/testEdasReq/\", \"numTrials\":\"10\"}"
    desc = 'This application runs MMX with JSON as input.'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('--json_string',
                        required=True,
                        help='JSON input')
    args = parser.parse_args()
    json_data = args.json_string
    context = json.loads(json_data)
    sys.exit(order(context))


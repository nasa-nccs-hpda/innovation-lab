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
def main():

    # Process command-line args.  Example:
    #--json_string="{\"observationFilePath\":\"/home/jli/SystemTesting/MaxEntData/GSENM/CSV_Field_Data/GSENM_cheat_pres_abs_2001.csv\", \"species\":\"Cheat Grass\", \"startDate\":\"1985-02-01\", \"endDate\":\"1985-04-01\", \"collection\":\"cip_merra2_mth\", \"listOfVariables\":\"tas ps uas vas tasmax tasmin pr prc hfls hfss rlus rsus\", \"operation\":\"ave\", \"outDir\":\"/home/jli/SystemTesting/testEdasReq/\", \"numTrials\":\"10\"}"
    desc = 'This application runs MMX with JSON as input.'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('--json_string',
                        required=True,
                        help='JSON input')
    args = parser.parse_args()
    json_data = args.json_string
    context = json.loads(json_data)

    # convert space-delimited string to list for consistency with CLI view and set defaults
    context['listOfVariables'] =  str(context['listOfVariables']).split()
    if 'numTrials' not in context.keys():  context['numTrials'] = 10
    if 'numPredictors' not in context.keys():  context['numPredictors'] = 10
    if 'outDir' not in context.keys():  context['outDir'] = '.'
    if 'source' not in context.keys():  context['source'] = 'Edas'
    if 'workflow' not in context.keys():  context['workflow'] = ''

    # Dynamically select workflow request (defaults to MmxRequest)
    clazzName = "Mmx{0}Request".format(context['workflow'])
    # import the class from module
    mod = __import__("model.{0}".format(clazzName), globals(), locals(), [clazzName])
    requestInstance = getattr(mod, clazzName)
    mmxr = requestInstance(context, context['source'])
    mmxr.run()

# ------------------------------------------------------------------------------
# Invoke the main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(main())


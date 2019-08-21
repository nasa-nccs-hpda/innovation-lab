#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import argparse
import sys

from model.MmxEdasRequest import MmxEdasRequest
import json

# -----------------------------------------------------------------------------
# main
#
# cd innovation-lab
# export PYTHONPATH=`pwd`
# mkdir ~/SystemTesting/testMmx
# mkdir ~/SystemTesting/testMaxEnt/merra
# view/MmxRequestTranslationView.py
# -f ~/SystemTesting/MaxEntData/GSENM_cheat_pres_abs_2001.csv
# -s "Cheat Grass" --start_date 2013-02-03 --end_date 2013-03-12
# -o ~/SystemTesting/testMaxEnt/
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

    # Process json args.
    mmxr = MmxEdasRequest(context)
    mmxr.run()


# ------------------------------------------------------------------------------
# Invoke the main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(main())


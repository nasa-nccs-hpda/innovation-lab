#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import argparse
import sys

from model.MmxRmRequest import MmxRmRequest

# -----------------------------------------------------------------------------
# main
#
# cd innovation-lab
# export PYTHONPATH=`pwd`
# mkdir ~/SystemTesting/testMmx
# mkdir ~/SystemTesting/testMaxEnt/merra
# view/MmxRequestCommandLineView.py
# -f ~/SystemTesting/MaxEntData/GSENM_cheat_pres_abs_2001.csv
# -s "Cheat Grass" --start_date 2013-02-03 --end_date 2013-03-12
# -o ~/SystemTesting/testMaxEnt/
# -----------------------------------------------------------------------------
def main():

    # Process command-line args.
    desc = 'This application runs MMX.'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-f',
                        required=True,
                        help='Path to observation file')

    parser.add_argument('-s',
                        required=True,
                        help='Name of species in observation file')

    parser.add_argument('--start_date',
                        required=True,
                        help='YYYY-MM-DD')

    parser.add_argument('--end_date',
                        required=True,
                        help='YYYY-MM-DD')

    parser.add_argument('-c',
                        required=True,
                        help='Name of collection of MERRA2')

    parser.add_argument('--vars',
                        required=True,
                        nargs='+',
                        help='List of variables in M2 collection')

    parser.add_argument('--opr',
                        required=True,
                        help='Type of analysis')

    parser.add_argument('-n',
                        default=10,
                        help='Number of trials to run')

    parser.add_argument('-k',
                        default=10,
                        type=int,
                        help='Number of predictors for each trial')
                        
    parser.add_argument('-o',
                        default='.',
                        help='Path to output directory')
    
    args = parser.parse_args()

    # Prepare context - convert CLI parameters to context-sensitive dictionary
    context = {}
    context['outDir'] = args.o
    context['numTrials'] = args.n
    context['observationFilePath'] = args.f
    context['species'] = args.s
    context['startDate'] = args.start_date
    context['endDate'] = args.end_date
    context['collection'] = args.c
    context['listOfVariables'] = args.vars
    context['operation'] = args.opr
    context['numPredictors'] = args.k
    context['source'] = "Rm"

    # Run MMX
    mmxr = MmxRmRequest(context)
    mmxr.run()

# ------------------------------------------------------------------------------
# Invoke the main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(main())


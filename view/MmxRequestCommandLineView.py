#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import argparse
import sys

from model.MmxRequest import MmxRequest

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

    parser.add_argument('-i',
                        default=None,
                        help='Path to input directory')

    parser.add_argument('--source',
                        default='Edas',
                        help='Data source')

    parser.add_argument('--workflow',
                        default='',
                        help='Type of analysis')

    args = parser.parse_args()

    # prepare context - convert CLI parameters to context-sensitive dictionary
    context = {}
    if args.o is not None: context['outDir'] = args.o
    if args.i is not None: context['inDir'] = args.i
    if args.n is not None: context['numTrials'] = args.n
    if args.f is not None: context['observationFilePath'] = args.f
    if args.s is not None: context['species'] = args.s
    if args.start_date is not None: context['startDate'] = args.start_date
    if args.end_date is not None: context['endDate'] = args.end_date
    if args.c is not None: context['collection'] = args.c
    if args.vars is not None: context['listOfVariables'] = args.vars
    if args.opr is not None: context['operation'] = args.opr
    if args.k is not None: context['numPredictors'] = args.k
    if args.source is not None: context['source'] = args.source
    if args.workflow is not '': context['workflow'] = args.workflow

    # Dynamically select workflow request (defaults to MmxRequest)
    clazzName = "Mmx{0}Request".format(args.workflow)
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


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

    parser.add_argument('--imageDir',
                        default=argparse.SUPPRESS,
                        help='Path to input directory of environmental images')

    parser.add_argument('--outDir',
                        required=True,
                        default='.',
                        help='Path to output directory')

    parser.add_argument('--observation',
                        required=True,
                        help='Path to observation file')

    parser.add_argument('--species',
                        required=True,
                        help='Name of species in observation file')

    parser.add_argument('--numTrials',
                        default=10,
                        help='Number of trials to run')

    parser.add_argument('--numPredictors',
                        default=10,
                        type=int,
                        help='Number of predictors for each trial')

    parser.add_argument('--workflow',
                        default='',
                        help='Type of analysis')

    parser.add_argument('--startDate',
                        default=argparse.SUPPRESS,
                        help='YYYY-MM-DD')

    parser.add_argument('--endDate',
                        default=argparse.SUPPRESS,
                        help='YYYY-MM-DD')

    parser.add_argument('--collection',
                        action='append',
                        default=argparse.SUPPRESS,
                        help='Name of collection of MERRA2')

    parser.add_argument('--vars',
                        action='append',
                        nargs='+',
                        default=argparse.SUPPRESS,
                        help='List of variables in M2 collection')

    parser.add_argument('--operation',
                        action='append',
                        default=argparse.SUPPRESS,
                        help='Type of analysis')

    parser.add_argument('--EdasWorldClim',
                        type=bool,
                        default=False,
                        help='Activate EDAS WorldClim request')

    parser.add_argument('--WorldClim',
                        default=argparse.SUPPRESS,
                        help='Path to directory of WorldClim images')

    parser.add_argument('--MERRAClim',
                        default=argparse.SUPPRESS,
                        help='Path to directory of MERRAClim images')

    # prepare context - convert CLI parameters to context-sensitive dictionary
    context = vars(parser.parse_args())

    # Dynamically select workflow request (defaults to MmxRequest)
    clazzName = "Mmx{0}Request".format(context['workflow'])
    # import the class from module
    mod = __import__("model.{0}".format(clazzName), globals(), locals(), [clazzName])
    requestInstance = getattr(mod, clazzName)
    mmxr = requestInstance(context)
    mmxr.run()


# ------------------------------------------------------------------------------
# Invoke the main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(main())

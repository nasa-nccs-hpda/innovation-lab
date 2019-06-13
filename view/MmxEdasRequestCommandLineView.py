#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import argparse
import sys
import pandas
from osgeo.osr import SpatialReference
from model.Envelope import Envelope

from model.MmxEdasRequest import MmxEdasRequest
from model.ObservationFile import ObservationFile

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

    parser.add_argument('-e',
                        required=True,
                        nargs='+',
                        help='ulx uly lrx lry')

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
                        
    parser.add_argument('-o',
                        default='.',
                        help='Path to output directory')
    
    args = parser.parse_args()
    
    observationFile = ObservationFile(args.f, args.s)
    dateRange = pandas.date_range(args.start_date, args.end_date)

    # Envelope
    srs = SpatialReference()
#    srs.ImportFromEPSG(args.epsg)
    srs.ImportFromEPSG(4326)
    env = Envelope()
    env.addPoint(float(args.e[0]), float(args.e[1]), 0, srs)
    env.addPoint(float(args.e[2]), float(args.e[3]), 0, srs)
    observationFile._envelope = env

    mmxr = MmxEdasRequest(observationFile, dateRange, args.c, args.vars, args.opr, args.n, args.o)
#    mmxr.runBatch()
#    mmxr.runSimple()
    mmxr.runEdas()
#    mmxr.run()
# ------------------------------------------------------------------------------
# Invoke the main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(main())


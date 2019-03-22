#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import argparse

import pandas

from model.MmxRequest import MmxRequest
from model.ObservationFile import ObservationFile

# TBD - Placeholder for translation view

# -----------------------------------------------------------------------------
# main
#
# cd innovation-lab
# export PYTHONPATH=`pwd`
# mkdir ~/SystemTesting/testMmx
# view/MmxRequestCommandLineView.py 
# -f ~/SystemTesting/MaxEntData/GSENM_cheat_pres_abs_2001.csv
# -s "Cheat Grass" --start_date 2013-02-03 --end_date 2013-03-12
# -o ~/SystemTesting/testMaxEnt/
# -----------------------------------------------------------------------------
def main():

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

    parser.add_argument('-n',
                        default=10,
                        help='Number of trials to run')
                        
    parser.add_argument('-o',
                        default='.',
                        help='Path to output directory')
    
    args = parser.parse_args()
    
    observationFile = ObservationFile(args.f, args.s)
    dateRange = pandas.date_range(args.start_date, args.end_date)

    mmxr = MmxRequest(observationFile, dateRange, args.n, args.o)
    
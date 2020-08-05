#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import sys
import pandas

from model.MmxRequest import MmxRequest
from model.MmxRequestCelery import MmxRequestCelery
from model.ObservationFile import ObservationFile

# -----------------------------------------------------------------------------
# main
#
# cd innovation-lab
# export PYTHONPATH=`pwd`
# view/MmxRequestCommandLineView.py -f /att/nobackup/rlgill/maxEntData/ebd_Cassins_1989.csv -s "Cassin's Sparrow" --start_date 2013-02-03 --end_date 2013-12-31 -c m2t1nxslv --vars QV2M TS --opr avg -o /att/nobackup/rlgill/testMmx --celery
#
# Container execution:
# cd innovation-lab
# singularity run -B /att /att/nobackup/iluser/containers/ilab-core-5.0.0.simg python view/MmxRequestCommandLineView.py -f /att/nobackup/rlgill/maxEntData/ebd_Cassins_1989.csv -s "Cassin's Sparrow" --start_date 2013-02-03 --end_date 2013-12-31 -c m2t1nxslv --vars QV2M TS --opr avg -o /att/nobackup/rlgill/testMmx --celery
# -----------------------------------------------------------------------------
def main():

    # Process command-line args.
    desc = 'This application runs MMX.'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('--celery',
                        action='store_true',
                        help='Use Celery for distributed processing.')

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

    if args.celery:
        
        mmxr = MmxRequestCelery(observationFile, dateRange, args.c, args.vars,
                                args.opr, args.n, args.o)

    else:

        mmxr = MmxRequest(observationFile, dateRange, args.c, args.vars,
                          args.opr, args.n, args.o)

    mmxr.run()

# ------------------------------------------------------------------------------
# Invoke the main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(main())


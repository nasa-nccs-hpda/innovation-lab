#!/usr/bin/python
import argparse
import sys

from model.MasRequest import MasRequest


# -----------------------------------------------------------------------------
# main
#
# cd innovation-lab
# export PYTHONPATH=`pwd`
# mkdir ~/SystemTesting/testMasReq
#
# view/MasRequestCommandLineView.py
# -e -125 50 -66 24
# --epsg 4326
# --start_date 2013-02-03
# --end_date 2013-03-12
# -c tavg1_2d_lnd_Nx
# --vars TSURF BASEFLOW ECHANGE
# --opr avg
# -o ~/SystemTesting/testMasReq/
# -----------------------------------------------------------------------------
def main():
    # Process command-line args.
    desc = 'This application runs MAS Request for MMX.'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-e',
                        required=True,
                        nargs='+',
                        help='ulx uly lrx lry')

    parser.add_argument('--epsg',
                        required=True,
                        type=int,
                        help='EPSG code')

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

    parser.add_argument('-o',
                        default='.',
                        help='Path to output directory')

    args = parser.parse_args()

    # Mas Request
    masReq = MasRequest(args.e, args.epsg, args.start_date, args.end_date,
                        args.c, args.vars, args.opr, args.o)
    masReq.run()


# ------------------------------------------------------------------------------
# Invoke the main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/python
import argparse
import sys
import pandas
from osgeo.osr import SpatialReference
from model.Envelope import Envelope
from model.EdasRequest import EdasRequest


# -----------------------------------------------------------------------------
# main
#
# cd innovation-lab
# export PYTHONPATH=`pwd`
# mkdir ~/SystemTesting/testEdasReq
#
# view/EdasRequestCommandLineView.py
# -e -125 50 -66 24
# --epsg 4326
# --start_date 1985-02-01
# --end_date 1985-04-01
# -c cip_merra2_mth
# --vars tas uas vas
# --opr ave
# -o ~/SystemTesting/testEdasReq/
# -----------------------------------------------------------------------------
def main():
    # Process command-line args.
    desc = 'This application runs EDAS Request for MMX.'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-e',
                        required=True,
                        nargs='+',
                        help='ulx uly lrx lry')

    parser.add_argument('-edas',
                        required=True,
                        help='Path to EDAS config file')

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

    # Envelope
    srs = SpatialReference()
    srs.ImportFromEPSG(args.epsg)
    env = Envelope()
    env.addPoint(float(args.e[0]), float(args.e[1]), 0, srs)
    env.addPoint(float(args.e[2]), float(args.e[3]), 0, srs)

    # Date Range
    dateRange = pandas.date_range(args.start_date, args.end_date)

    # Mas Request
    masReq = EdasRequest( args.edas, env, dateRange, args.c, args.vars, args.opr, args.o)
    masReq.run()


# ------------------------------------------------------------------------------
# Invoke the main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(main())

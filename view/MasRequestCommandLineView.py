#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import argparse
import sys

from model.MasRequest import MasRequest


# -----------------------------------------------------------------------------
# main
#
# cd innovation-lab
# export PYTHONPATH=`pwd`
# mkdir ~/SystemTesting/testMaxEnt
# view/MasRequestCommandLineView.py -e Envelope_obj -d Pandas_date_range_obj
# -c tavg1_2d_lnd_Nx --vars "TSURF,BASEFLOW,ECHANGE" --opr "avg"
# -o ~/SystemTesting/testMaxEnt/
# -----------------------------------------------------------------------------
def main():

    # Process command-line args.
    desc = 'This application runs MAS Request for MMX.'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-e',
                        required=True,
                        help='Envelope object')

    parser.add_argument('-d',
                        required=True,
                        help = 'Pandas date_range object')

    parser.add_argument('-c',
                        required=True,
                        help = 'Name of collection of MERRA2')

    parser.add_argument('--vars',
                        required=True,
                        help = 'List of variables in M2 collection')

    parser.add_argument('--opr',
                        required=True,
                        help = 'Type of analysis')

    parser.add_argument('-o',
                        default='.',
                        help='Path to output directory')

    args = parser.parse_args()
    masReq = MasRequest(args.e, args.d, args.c, args.vars, args.opr, args.o)
    masReq.run()

# ------------------------------------------------------------------------------
# Invoke the main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(main())

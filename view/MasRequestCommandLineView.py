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
# view/MasRequestCommandLineView.py -f ~/SystemTesting/MaxEntData/GSENM_cheat_pres_abs_2001.csv -s "Cheat Grass"
# --startDate "20030205" --endDate "20030211" -c tavg1_2d_lnd_Nx --vars "TSURF,BASEFLOW,ECHANGE" --opr "avg"
# -o ~/SystemTesting/testMaxEnt/
# -----------------------------------------------------------------------------
def main():

    # Process command-line args.
    desc = 'This application runs MAS Request for MMX.'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-f',
                        required=True,
                        help='Path to observation file')

    parser.add_argument('-o',
                        default='.',
                        help='Path to output directory')

    parser.add_argument('-s',
                        required=True,
                        help='Name of species in observation file')

    parser.add_argument('--startDate',
                        required=True,
                        help = 'YYYYMMDD')

    parser.add_argument('--endDate',
                        required=True,
                        help = 'YYYYMMDD')

    parser.add_argument('-c',
                        required=True,
                        help = 'Name of collection of MERRA2')

    parser.add_argument('--vars',
                        required=True,
                        help = 'List of variables in M2 collection')

    parser.add_argument('--opr',
                        required=True,
                        help = 'Type of analysis')

    args = parser.parse_args()
    masReq = MasRequest(args.f, args.s, args.startDate, args.endDate,
                        args.c, args.vars, args.opr, args.o)
    masReq.run()

# ------------------------------------------------------------------------------
# Invoke the main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(main())

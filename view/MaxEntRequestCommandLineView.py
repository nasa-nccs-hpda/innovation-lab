#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import argparse
import glob
import sys

from model.MaxEntRequest import MaxEntRequest


# -----------------------------------------------------------------------------
# main
#
# cd innovation-lab
# export PYTHONPATH=`pwd`
# mkdir ~/SystemTesting/testMaxEnt
# view/MaxEntRequestCommandLineView.py -f ~/SystemTesting/MaxEntData/GSENM_cheat_pres_abs_2001.csv -s "Cheat Grass" -i ~/SystemTesting/MaxEntData/ -o ~/SystemTesting/testMaxEnt/
# -----------------------------------------------------------------------------
def main():

    # Process command-line args.
    desc = 'This application runs Maximum Entropy.'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-f',
                        required=True,
                        help='Path to observation file')

    parser.add_argument('-i',
                        default='.',
                        help='Path to directory of image files')

    parser.add_argument('-o',
                        default='.',
                        help='Path to output directory')

    parser.add_argument('-s',
                        required=True,
                        help='Name of species in observation file')

    args = parser.parse_args()
    images = glob.glob(args.i + '/*')
    maxEntReq = MaxEntRequest(args.f, args.s, images, args.o)
    maxEntReq.run()


# ------------------------------------------------------------------------------
# Invoke the main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import argparse
import glob
import sys

from projects.aviris_regression_algorithms.model.ApplyAlgorithm \
    import ApplyAlgorithm


# -----------------------------------------------------------------------------
# main
#
# docker run -it -v /Users/rlgill/Desktop/Source/innovation-lab:/home/ilUser/hostFiles -v /Users/rlgill/Desktop/SystemTesting:/home/ilUser/SystemTesting innovation-lab:1.0
# cd ~/hostFiles
# export PYTHONPATH=`pwd`
# projects/aviris_regression_algorithms/view/AvirisCommandLineView.py
# -----------------------------------------------------------------------------
def main():

    # Process command-line args.
    desc = 'This application runs the AVIRIS algorithm prototype.'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-a',
                        required=True,
                        help='Name of algorithm in coefficient file to apply')

    parser.add_argument('-c',
                        required=True,
                        help='Path to coefficient CSV file')

    parser.add_argument('-d',
                        nargs=2,
                        type=int,
                        help='Produce debugging output for the given ' + \
                             'pixel, defined as "x y".')

    parser.add_argument('-i',
                        default='.',
                        help='Path to image file')

    parser.add_argument('-o',
                        default='.',
                        help='Path to output directory')

    args = parser.parse_args()
    
    aa = ApplyAlgorithm(args.c, args.i, args.o)
    
    if d in args:
        aa.debug(args.d[0], args.d[1])
        
    aa.applyAlgorithm(args.a)
    

# ------------------------------------------------------------------------------
# Invoke the main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(main())

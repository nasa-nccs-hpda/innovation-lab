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
# cd /att/nobackup/rlgill/innovation-lab/
# export PYTHONPATH=`pwd`
# projects/aviris_regression_algorithms/view/AvirisCommandLineView.py -a 'Avg Chl' -c /att/nobackup/rlgill/AVIRIS/Chl_Coeff_input.csv -i /att/nobackup/rlgill/AVIRIS/test/ang20170624t181530_rdn_v2p9/clipTest.img -o /att/nobackup/rlgill/AVIRIS/test/output -d 1 1
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
    
    if args.d:
        aa.debug(args.d[0], args.d[1])
        
    aa.applyAlgorithm(args.a)
    

# ------------------------------------------------------------------------------
# Invoke the main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(main())

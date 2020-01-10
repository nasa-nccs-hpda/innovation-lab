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
# /att/pubrepo/ABoVE/archived_data/ORNL/ABoVE_Airborne_AVIRIS_NG/data
#
# cd /att/nobackup/rlgill/innovation-lab/
# export PYTHONPATH=`pwd`
# projects/aviris_regression_algorithms/view/AvirisCommandLineView.py -a 'Avg Chl' -c /att/nobackup/rlgill/AVIRIS/Chl_Coeff_input.csv -i /att/nobackup/rlgill/AVIRIS/test/ang20170624t181530_rdn_v2p9/clipTest.img -o /att/nobackup/rlgill/AVIRIS/test/output
#
# projects/aviris_regression_algorithms/view/AvirisCommandLineView.py -a 'Avg Chl' -c /att/nobackup/rlgill/AVIRIS/Chl_Coeff_input.csv -i /att/pubrepo/ABoVE/archived_data/ORNL/ABoVE_Airborne_AVIRIS_NG/data/ang20180819t010027/ang20180819t010027_rdn_v2r2/ang20180819t010027_rdn_v2r2_img -o /att/nobackup/rlgill/AVIRIS/test/output
#
# To screen
# projects/aviris_regression_algorithms/view/AvirisCommandLineView.py -a 'Avg Chl' -c /att/nobackup/rlgill/AVIRIS/Chl_Coeff_input.csv -i /att/pubrepo/ABoVE/archived_data/ORNL/ABoVE_Airborne_AVIRIS_NG/data/ang20180819t010027/ang20180819t010027_rdn_v2r2/ang20180819t010027_rdn_v2r2_img -s
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

    parser.add_argument('-i',
                        default='.',
                        help='Path to image file')

    group = parser.add_mutually_exclusive_group()

    group.add_argument('-o',
                       default='.',
                       help='Path to output directory')

    import pdb
    pdb.set_trace()
    
    group.add_argument('-s',
                       nargs='?',
                       default=0.1,
                       help='Screen the image to determine if it has ' + 
                            'pixels that are not masked and not ' +
                            'no-data valued.  The value for this argument ' +
                            'is a percentage, expressed as a decimal, ' +
                            'indicating the threshold to stop screening ' + 
                            'and declare the image useful.  This does not ' +
                            'produce an output file.')

    args = parser.parse_args()
    aa = ApplyAlgorithm(args.c, args.i, args.o)

    if args.s > 0:
        aa.screen(args.s)
        
    else:
        aa.applyAlgorithm(args.a)


# ------------------------------------------------------------------------------
# Invoke the main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(main())

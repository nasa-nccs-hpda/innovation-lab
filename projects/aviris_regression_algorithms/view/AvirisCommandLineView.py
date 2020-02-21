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
# gdal_translate -srcwin 333 983 5 5 -of ENVI /att/pubrepo/ABoVE/archived_data/ORNL/ABoVE_Airborne_AVIRIS_NG_CORRUPT/data/ang20170714t213741rfl/ang20170714t213741_rfl_v2p9/ang20170714t213741_corr_v2p9_img /att/nobackup/rlgill/AVIRIS/test/ang20170714t213741/clip
#
# gdallocationinfo /att/pubrepo/ABoVE/archived_data/ORNL/ABoVE_Airborne_AVIRIS_NG_CORRUPT/data/ang20170714t213741rfl/ang20170714t213741_rfl_v2p9/ang20170714t213741_corr_v2p9_img 333 983
#
# cd /att/nobackup/rlgill/innovation-lab/
# export PYTHONPATH=`pwd`
#
# projects/aviris_regression_algorithms/view/AvirisCommandLineView.py -a 'Avg Chl' -c /att/nobackup/rlgill/AVIRIS/Chl_Coeff_input.csv -i /att/nobackup/rlgill/AVIRIS/test/ang20170714t213741/ang20170714t213741-clip -o /att/nobackup/rlgill/AVIRIS/test/output
#
# projects/aviris_regression_algorithms/view/AvirisCommandLineView.py -a 'Avg Chl' -c /att/nobackup/rlgill/AVIRIS/Chl_Coeff_input.csv -i /att/pubrepo/ABoVE/archived_data/ORNL/ABoVE_Airborne_AVIRIS_NG_CORRUPT/data/ang20170714t213741rfl/ang20170714t213741_rfl_v2p9/ang20170714t213741_corr_v2p9_img -o /att/nobackup/rlgill/AVIRIS/test/output
#
# To screen
# export PYTHONPATH=`pwd`
# projects/aviris_regression_algorithms/view/AvirisCommandLineView.py -a 'Avg Chl' -c /att/nobackup/rlgill/AVIRIS/Chl_Coeff_input.csv -i /att/nobackup/rlgill/AVIRIS/test/ang20170714t213741/clip -s
#
# projects/aviris_regression_algorithms/view/AvirisCommandLineView.py -a 'Avg Chl' -c /att/nobackup/rlgill/AVIRIS/Chl_Coeff_input.csv -i /att/pubrepo/ABoVE/archived_data/ORNL/ABoVE_Airborne_AVIRIS_NG_CORRUPT/data/ang20170714t213741rfl/ang20170714t213741_rfl_v2p9/ang20170714t213741_corr_v2p9_img -s
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

    parser.add_argument('-n',
                        action='store_true',
                        help='Use normalized pixel values')

    group = parser.add_mutually_exclusive_group()

    group.add_argument('-o',
                       default='.',
                       help='Path to output directory')

    group.add_argument('-s',
                       nargs='?',
                       const=0.1,
                       default=0.0,
                       help='Screen the image to determine if it has ' +
                            'pixels that are not masked and not ' +
                            'no-data valued.  The value for this argument ' +
                            'is a percentage, expressed as a decimal, ' +
                            'indicating the threshold of valid pixels ' +
                            'at which to stop screening and declare the ' +
                            'image useful.  This does not produce an ' +
                            'output file.')

    args = parser.parse_args()
    aa = ApplyAlgorithm(args.c, args.i, args.o)

    if args.s > 0:

        aa.screen(args.s)

    else:
        aa.applyAlgorithm(args.a, args.n)


# ------------------------------------------------------------------------------
# Invoke the main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(main())

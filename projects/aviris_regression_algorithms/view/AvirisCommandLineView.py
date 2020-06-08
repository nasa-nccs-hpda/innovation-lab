#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import glob
import sys

from projects.aviris_regression_algorithms.model.ApplyAlgorithm \
    import ApplyAlgorithm

from projects.aviris_regression_algorithms.model.ApplyAlgorithmCelery \
    import ApplyAlgorithmCelery

from projects.aviris_regression_algorithms.model.AvirisSpecFile \
    import AvirisSpecFile


# -----------------------------------------------------------------------------
# main
#
# gdal_translate -srcwin 333 983 5 5 -of ENVI /att/pubrepo/ABoVE/archived_data/ORNL/ABoVE_Airborne_AVIRIS_NG_CORRUPT/data/ang20170714t213741rfl/ang20170714t213741_rfl_v2p9/ang20170714t213741_corr_v2p9_img /att/nobackup/rlgill/AVIRIS/test/ang20170714t213741/clip
#
# gdallocationinfo /att/pubrepo/ABoVE/archived_data/ORNL/ABoVE_Airborne_AVIRIS_NG_CORRUPT/data/ang20170714t213741rfl/ang20170714t213741_rfl_v2p9/ang20170714t213741_corr_v2p9_img 333 983
#
# cd /att/nobackup/rlgill/innovation-lab/
# export PYTHONPATH=`pwd`
#
# -----
# Run from command-line parameters
# projects/aviris_regression_algorithms/view/AvirisCommandLineView.py -c /att/nobackup/rlgill/AVIRIS/PLSR_Coeff_NoVN_v2.csv -o /att/nobackup/rlgill/AVIRIS/test -a AVG-CHL -i /att/pubrepo/ABoVE/archived_data/ORNL/ABoVE_Airborne_AVIRIS_NG_CORRUPT/data/ang20180729t210144rfl/ang20180729t210144_rfl_v2r2/ang20180729t210144_corr_v2r2_img
#
# -----
# Run from spec. file
# projects/aviris_regression_algorithms/view/AvirisCommandLineView.py -o /att/nobackup/rlgill/AVIRIS/test/output --spec /att/nobackup/rlgill/AVIRIS/sample.spec
#
# -----
# Screen from command-line parameters
# projects/aviris_regression_algorithms/view/AvirisCommandLineView.py -a 'Avg Chl' -c /att/nobackup/rlgill/AVIRIS/Chl_Coeff_input.csv -i /att/pubrepo/ABoVE/archived_data/ORNL/ABoVE_Airborne_AVIRIS_NG_CORRUPT/data/ang20170714t213741rfl/ang20170714t213741_rfl_v2p9/ang20170714t213741_corr_v2p9_img -s
# -----
# Screen from spec. file
# projects/aviris_regression_algorithms/view/AvirisCommandLineView.py -s --spec /att/nobackup/rlgill/AVIRIS/sample.spec
#
# -----
# Docker
# projects/aviris_regression_algorithms/view/AvirisCommandLineView.py -c ~/SystemTesting/aviris/PLSR_Coeff_NoVN_v2.csv -o ~/SystemTesting/aviris/output -a AVG-CHL -i ~/SystemTesting/aviris/ang20180729t210144_corr_v2r2_img --celery
# -----------------------------------------------------------------------------
def main():

    # Process command-line args.
    desc = 'This application runs the AVIRIS algorithm prototype.'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-a',
                        help='Name of algorithm in coefficient file to apply')

    parser.add_argument('-c',
                        help='Path to coefficient CSV file')

    # parser.add_argument('--celery',
    #                     action='store_true',
    #                     help='Use Celery for distributed processing.')

    parser.add_argument('-i',
                        default='.',
                        help='Path to image file')

    parser.add_argument('-n',
                        action='store_true',
                        help='Use normalized pixel values')

    parser.add_argument('-o',
                        default='.',
                        help='Path to output directory')

    parser.add_argument('-s',
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

    parser.add_argument('--spec',
                        help='Path to specification file.  Using a ' +
                             'specification file means the parameters ' +
                             '"a", "c", "i" and "n" will be ignored.  ' +
                             'Specification files are created or updated ' +
                             'when this application runs.')

    args = parser.parse_args()

    if args.spec:

        algorithm, csvFile, imageFile, normalize = argsFromSpec(args.spec)

    else:

        algorithm = args.a
        csvFile = args.c
        imageFile = args.i
        normalize = args.n

    if args.s > 0:

        aa = ApplyAlgorithm(csvFile, imageFile)
        aa.screen(args.s)

    else:

        if args.celery:
            
            aa = ApplyAlgorithmCelery(csvFile, imageFile)

        else:
            aa = ApplyAlgorithm(csvFile, imageFile)
        
        aa.applyAlgorithm(algorithm, args.o, normalize)


# ------------------------------------------------------------------------------
# argsFromSpec
# ------------------------------------------------------------------------------
def argsFromSpec(specFile):

    asf = AvirisSpecFile(specFile)

    return (asf.getField(AvirisSpecFile.PLANT_TYPE_KEY),
            asf.getField(AvirisSpecFile.COEFS_FILE_KEY),
            asf.getField(AvirisSpecFile.IMAGE_FILE_KEY),
            asf.getField(AvirisSpecFile.NORMALIZE_KEY))

# ------------------------------------------------------------------------------
# Invoke the main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(main())

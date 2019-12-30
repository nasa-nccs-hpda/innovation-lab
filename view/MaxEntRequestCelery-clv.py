#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import argparse
import glob
import sys

from osgeo.osr import SpatialReference

from model.GeospatialImageFile import GeospatialImageFile
from model.MaxEntRequestCelery import MaxEntRequestCelery
from model.ObservationFile import ObservationFile


# -----------------------------------------------------------------------------
# main
#
# cd innovation-lab
# export PYTHONPATH=`pwd`
# mkdir ~/SystemTesting/testMaxEnt
# view/MaxEntRequestCelery-clv.py -e 4326 -f ~/SystemTesting/maxEntData/ebd_Cassins_1989.csv -s "Cheat Grass" -i ~/SystemTesting/maxEntData/images/ -o ~/SystemTesting/testMaxEnt/
# -----------------------------------------------------------------------------
def main():

    # Process command-line args.
    desc = 'This application runs Maximum Entropy.'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-e',
                        required=True,
                        type=int,
                        help='Integer EPSG code representing the spatial ' +
                             'reference system of the input images.')

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

    srs = SpatialReference()
    srs.ImportFromEPSG(args.e)

    imageFiles = glob.glob(args.i + '/*.nc')
    geoImages = [GeospatialImageFile(i, srs) for i in imageFiles]
    observationFile = ObservationFile(args.f, args.s)
    maxEntReq = MaxEntRequestCelery(observationFile, geoImages, args.o)
    maxEntReq.run()

# ------------------------------------------------------------------------------
# Invoke the main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(main())

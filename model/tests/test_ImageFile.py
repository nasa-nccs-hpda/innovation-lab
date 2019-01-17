#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import shutil
import tempfile
import unittest

from osgeo import gdal
from osgeo import gdalconst

from model.Envelope import Envelope
from model.ImageFile import ImageFile


# -----------------------------------------------------------------------------
# class ImageFileTestCase
#
# python -m unittest discover model/tests/
# python -m unittest model.tests.test_ImageFile
# -----------------------------------------------------------------------------
class ImageFileTestCase(unittest.TestCase):

    # -------------------------------------------------------------------------
    # testClip
    # -------------------------------------------------------------------------
    def testClip(self):

        ulx = 367080
        uly = 4209230
        lrx = 509200
        lry = 4095100
        epsg = 32612
        env = Envelope()
        env.addPoint(ulx, uly, 0, epsg)
        env.addPoint(lrx, lry, 0, epsg)

        testFile = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'gsenm_250m_eucl_dist_streams.tif')

        workingCopy = tempfile.mkstemp(suffix='.tif')[1]
        shutil.copyfile(testFile, workingCopy)

        imageFile = ImageFile(workingCopy)
        imageFile.clip(env)

        # Check the corners.
        dataset = gdal.Open(workingCopy, gdalconst.GA_ReadOnly)

        if not dataset:
            raise RuntimeError('Unable to read ' + workingCopy + '.')

        xform = dataset.GetGeoTransform()
        xScale = xform[1]
        yScale = xform[5]
        width = dataset.RasterXSize
        height = dataset.RasterYSize
        clippedUlx = xform[0]
        clippedUly = xform[3]
        clippedLrx = ulx + width * xScale
        clippedLry = uly + height * yScale

        self.assertEqual(clippedUlx, ulx)
        self.assertEqual(clippedUly, uly)
        self.assertEqual(clippedLrx, lrx)
        self.assertEqual(clippedLry, lry)

        # Delete the test file.
        os.remove(workingCopy)

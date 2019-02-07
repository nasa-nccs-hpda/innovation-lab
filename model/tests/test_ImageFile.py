#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import shutil
import tempfile
import unittest

from osgeo import gdal
from osgeo import gdalconst
from osgeo.osr import SpatialReference

from model.Envelope import Envelope
from model.ImageFile import ImageFile


# -----------------------------------------------------------------------------
# class ImageFileTestCase
#
# python -m unittest discover model/tests/
# python -m unittest model.tests.test_ImageFile
# -----------------------------------------------------------------------------
class ImageFileTestCase(unittest.TestCase):

    TEST_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'gsenm_250m_eucl_dist_streams.tif')

    # -------------------------------------------------------------------------
    # testClipReprojectResample
    # -------------------------------------------------------------------------
    def testClipReprojectResample(self):

        # Build the test file.
        workingCopy = tempfile.mkstemp(suffix='.tif')[1]
        shutil.copyfile(ImageFileTestCase.TEST_FILE, workingCopy)
        imageFile = ImageFile(workingCopy)

        # Build the envelope.
        ulx = 367080
        uly = 4209230
        lrx = 509200
        lry = 4095100
        srs = SpatialReference()
        srs.ImportFromEPSG(32612)
        env = Envelope()
        env.addPoint(ulx, uly, 0, srs)
        env.addPoint(lrx, lry, 0, srs)

        # Reprojection parameter
        targetSRS = SpatialReference()
        targetSRS.ImportFromEPSG(4326)

        # Resample parameter
        targetX_Scale = 0.002
        targetY_Scale = -0.002

        # Clip, reproject and resample.
        imageFile.clipReprojectResample(env,
                                        targetSRS,
                                        (targetX_Scale, targetY_Scale))

        # Check the results.
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
        clippedLrx = clippedUlx + width * xScale
        clippedLry = clippedUly + height * yScale

        self.assertAlmostEqual(clippedUlx, -112.49369402670872, places=12)
        self.assertAlmostEqual(clippedUly, 38.03073206024332, places=11)
        self.assertAlmostEqual(clippedLrx, -110.89569402670872, places=12)
        self.assertAlmostEqual(clippedLry, 36.99273206024332, places=11)

        outSRS = SpatialReference()
        outSRS.ImportFromWkt(dataset.GetProjection())
        self.assertTrue(outSRS.IsSame(targetSRS))

        self.assertEqual(xform[1], targetX_Scale)
        self.assertEqual(xform[5], targetY_Scale)

        # Delete the test file.
        os.remove(workingCopy)

    # -------------------------------------------------------------------------
    # testClip
    # -------------------------------------------------------------------------
    def testClip(self):

        # Build the test file.
        workingCopy = tempfile.mkstemp(suffix='.tif')[1]
        shutil.copyfile(ImageFileTestCase.TEST_FILE, workingCopy)
        imageFile = ImageFile(workingCopy)

        # Build the envelope and clip.
        ulx = 367080
        uly = 4209230
        lrx = 509200
        lry = 4095100
        srs = SpatialReference()
        srs.ImportFromEPSG(32612)
        env = Envelope()
        env.addPoint(ulx, uly, 0, srs)
        env.addPoint(lrx, lry, 0, srs)
        imageFile.clipReprojectResample(env)

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

    # -------------------------------------------------------------------------
    # testGetFormatName
    # -------------------------------------------------------------------------
    def testGetFormatName(self):

        # Create a test image.
        workingCopy = tempfile.mkstemp(suffix='.tif')[1]
        shutil.copyfile(ImageFileTestCase.TEST_FILE, workingCopy)
        imageFile = ImageFile(workingCopy)

        # Test getFormatName.
        self.assertEqual('GTiff', imageFile.getFormatName())

        # Delete the test file.
        os.remove(workingCopy)

    # -------------------------------------------------------------------------
    # test_getDataset
    # -------------------------------------------------------------------------
    def test_getDataset(self):

        # Create a test image.
        workingCopy = tempfile.mkstemp(suffix='.tif')[1]
        shutil.copyfile(ImageFileTestCase.TEST_FILE, workingCopy)
        imageFile = ImageFile(workingCopy)

        # Test _getDataset.
        self.assertIsNotNone(imageFile._getDataset())

        # Delete the test file.
        os.remove(workingCopy)

    # -------------------------------------------------------------------------
    # testGetSquareScale
    # -------------------------------------------------------------------------
    def testGetSquareScale(self):

        img = ImageFile(ImageFileTestCase.TEST_FILE)
        self.assertEqual(img.getSquareScale(), 246.0)

    # -------------------------------------------------------------------------
    # testNoOperation
    # -------------------------------------------------------------------------
    def testNoOperation(self):

        # Create a test image.
        workingCopy = tempfile.mkstemp(suffix='.tif')[1]
        shutil.copyfile(ImageFileTestCase.TEST_FILE, workingCopy)
        imageFile = ImageFile(workingCopy)

        # Test with no operation specified.
        with self.assertRaisesRegexp(RuntimeError, 'output SRS or scale'):
            imageFile.clipReprojectResample()

        # Delete the test file.
        os.remove(workingCopy)

    # -------------------------------------------------------------------------
    # testReproject
    # -------------------------------------------------------------------------
    def testReproject(self):

        # Build the test file.
        workingCopy = tempfile.mkstemp(suffix='.tif')[1]
        shutil.copyfile(ImageFileTestCase.TEST_FILE, workingCopy)
        imageFile = ImageFile(workingCopy)

        # Reproject.
        targetSRS = SpatialReference()
        targetSRS.ImportFromEPSG(4326)
        imageFile.clipReprojectResample(outputSRS=targetSRS)

        # Check the SRS.
        dataset = gdal.Open(workingCopy, gdalconst.GA_ReadOnly)

        if not dataset:
            raise RuntimeError('Unable to read ' + workingCopy + '.')

        outSRS = SpatialReference()
        outSRS.ImportFromWkt(dataset.GetProjection())
        self.assertTrue(outSRS.IsSame(targetSRS))

        # Delete the test file.
        os.remove(workingCopy)

    # -------------------------------------------------------------------------
    # testResample
    # -------------------------------------------------------------------------
    def testResample(self):

        # Build the test file.
        workingCopy = tempfile.mkstemp(suffix='.tif')[1]
        shutil.copyfile(ImageFileTestCase.TEST_FILE, workingCopy)
        imageFile = ImageFile(workingCopy)

        # Scale.  Original scale is (246, -246).
        targetX_Scale = 100
        targetY_Scale = -150

        imageFile.clipReprojectResample(scaleTuple=(targetX_Scale,
                                                    targetY_Scale))

        # Check the scale.
        dataset = gdal.Open(workingCopy, gdalconst.GA_ReadOnly)

        if not dataset:
            raise RuntimeError('Unable to read ' + workingCopy + '.')

        xform = dataset.GetGeoTransform()
        self.assertEqual(xform[1], targetX_Scale)
        self.assertEqual(xform[5], targetY_Scale)

        # Delete the test file.
        os.remove(workingCopy)

    # -------------------------------------------------------------------------
    # testScale
    # -------------------------------------------------------------------------
    def testScale(self):

        # Build the test file.
        workingCopy = tempfile.mkstemp(suffix='.tif')[1]
        shutil.copyfile(ImageFileTestCase.TEST_FILE, workingCopy)
        imageFile = ImageFile(workingCopy)

        # Check the scale.
        self.assertEqual(imageFile.scale()[0], 246)
        self.assertEqual(imageFile.scale()[1], -246)

        # Delete the test file.
        os.remove(workingCopy)

    # -------------------------------------------------------------------------
    # testSrs
    # -------------------------------------------------------------------------
    def testSrs(self):

        # Build the test file.
        workingCopy = tempfile.mkstemp(suffix='.tif')[1]
        shutil.copyfile(ImageFileTestCase.TEST_FILE, workingCopy)
        imageFile = ImageFile(workingCopy)

        # Check the srs.
        expectedSRS = SpatialReference()
        expectedSRS.ImportFromEPSG(32612)
        self.assertTrue(imageFile.srs().IsSame(expectedSRS))

        # Delete the test file.
        os.remove(workingCopy)

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
from model.GeospatialImageFile import GeospatialImageFile


# -----------------------------------------------------------------------------
# class GeospatialImageFileTestCase
#
# python -m unittest discover model/tests/
# python -m unittest model.tests.test_GeospatialImageFile
# -----------------------------------------------------------------------------
class GeospatialImageFileTestCase(unittest.TestCase):

    # -------------------------------------------------------------------------
    # createTestFile
    # -------------------------------------------------------------------------
    def _createTestFile(self):

        testFile = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'TSURF.nc')

        workingCopy = tempfile.mkstemp(suffix='.nc')[1]
        shutil.copyfile(testFile, workingCopy)
        srs = SpatialReference()
        srs.ImportFromEPSG(4326)
        return GeospatialImageFile(workingCopy, srs)

    # -------------------------------------------------------------------------
    # testClipReproject
    # -------------------------------------------------------------------------
    def testClipReproject(self):

        # Build the test file.
        imageFile = self._createTestFile()

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

        # Clip, reproject and resample.
        imageFile.clipReproject(env, targetSRS,)

        # Check the results.
        dataset = gdal.Open(imageFile.fileName(), gdalconst.GA_ReadOnly)

        if not dataset:
            raise RuntimeError('Unable to read ' + imageFile.fileName() + '.')

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
        self.assertAlmostEqual(clippedLrx, -110.89516946364738, places=12)
        self.assertAlmostEqual(clippedLry, 36.99265291293727, places=11)

        outSRS = SpatialReference()
        outSRS.ImportFromWkt(dataset.GetProjection())
        self.assertTrue(outSRS.IsSame(targetSRS))

        # Delete the test file.
        os.remove(imageFile.fileName())

    # -------------------------------------------------------------------------
    # testClip
    # -------------------------------------------------------------------------
    def testClip(self):

        # Build the test file.
        imageFile = self._createTestFile()

        # Build the envelope and clip.
        ulx = -100
        uly = 40
        lrx = -70
        lry = 30
        srs = SpatialReference()
        srs.ImportFromEPSG(4326)
        env = Envelope()
        env.addPoint(ulx, uly, 0, srs)
        env.addPoint(lrx, lry, 0, srs)
        imageFile.clipReproject(env)

        # Check the corners.
        dataset = gdal.Open(imageFile.fileName(), gdalconst.GA_ReadOnly)

        if not dataset:
            raise RuntimeError('Unable to read ' + imageFile.fileName() + '.')

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
        os.remove(imageFile.fileName())

    # -------------------------------------------------------------------------
    # testEnvelope
    # -------------------------------------------------------------------------
    def testEnvelope(self):

        # Create a test image.
        imageFile = self._createTestFile()

        # Test envelope.
        srs = SpatialReference()
        srs.ImportFromEPSG(4326)
        expectedEnvelope = Envelope()
        expectedEnvelope.addPoint(-125.3125000,  50.25, 0, srs)
        expectedEnvelope.addPoint(-65.9375000,  23.75, 0, srs)

        self.assertTrue(imageFile.envelope().Equals(expectedEnvelope))

        # Delete the test file.
        os.remove(imageFile.fileName())

    # -------------------------------------------------------------------------
    # testGetSquareScale
    # -------------------------------------------------------------------------
    def testGetSquareScale(self):

        imageFile = self._createTestFile()
        self.assertEqual(imageFile.getSquareScale(), 0.625)
        os.remove(imageFile.fileName())

    # -------------------------------------------------------------------------
    # testInvalidSpatialReference
    # -------------------------------------------------------------------------
    def testInvalidSpatialReference(self):

        testFile = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'TSURF.nc')

        workingCopy = tempfile.mkstemp(suffix='.nc')[1]
        shutil.copyfile(testFile, workingCopy)

        with self.assertRaisesRegexp(RuntimeError, 'Spatial reference for '):
            GeospatialImageFile(workingCopy, SpatialReference())

        os.remove(workingCopy)

    # -------------------------------------------------------------------------
    # testNoOperation
    # -------------------------------------------------------------------------
    def testNoOperation(self):

        # Create a test image.
        imageFile = self._createTestFile()

        # Test with no operation specified.
        with self.assertRaisesRegexp(RuntimeError, 'envelope or output SRS'):
            imageFile.clipReproject()

        # Delete the test file.
        os.remove(imageFile.fileName())

    # -------------------------------------------------------------------------
    # testReproject
    # -------------------------------------------------------------------------
    def testReproject(self):

        # Build the test file.
        imageFile = self._createTestFile()

        # Reproject.
        targetSRS = SpatialReference()
        targetSRS.ImportFromEPSG(4326)
        imageFile.clipReproject(outputSRS=targetSRS)

        # Check the SRS.
        dataset = gdal.Open(imageFile.fileName(), gdalconst.GA_ReadOnly)

        if not dataset:
            raise RuntimeError('Unable to read ' + imageFile.fileName() + '.')

        outSRS = SpatialReference()
        outSRS.ImportFromWkt(dataset.GetProjection())
        self.assertTrue(outSRS.IsSame(targetSRS))

        # Delete the test file.
        os.remove(imageFile.fileName())

    # -------------------------------------------------------------------------
    # testResample
    # -------------------------------------------------------------------------
    def testResample(self):

        # Build the test file.
        imageFile = self._createTestFile()

        # Scale.  Original scale is (246, -246).
        targetX_Scale = 0.25
        targetY_Scale = -0.35

        imageFile.resample(targetX_Scale, targetY_Scale)

        # Check the scale.
        dataset = gdal.Open(imageFile.fileName(), gdalconst.GA_ReadOnly)

        if not dataset:
            raise RuntimeError('Unable to read ' + imageFile.fileName() + '.')

        xform = dataset.GetGeoTransform()
        self.assertEqual(xform[1], targetX_Scale)
        self.assertAlmostEqual(xform[5], targetY_Scale, places=2)

        # Delete the test file.
        os.remove(imageFile.fileName())

    # -------------------------------------------------------------------------
    # testScale
    # -------------------------------------------------------------------------
    def testScale(self):

        # Build the test file.
        imageFile = self._createTestFile()

        # Check the scale.
        self.assertEqual(imageFile.scale()[0], 0.625)
        self.assertEqual(imageFile.scale()[1], -0.5)

        # Delete the test file.
        os.remove(imageFile.fileName())

    # -------------------------------------------------------------------------
    # testSrs
    # -------------------------------------------------------------------------
    def testSrs(self):

        # Build the test file.
        imageFile = self._createTestFile()

        # Check the srs.
        expectedSRS = SpatialReference()
        expectedSRS.ImportFromEPSG(4326)
        self.assertTrue(imageFile.srs().IsSame(expectedSRS))

        # Delete the test file.
        os.remove(imageFile.fileName())

#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import unittest

from osgeo import ogr
from osgeo.osr import SpatialReference

from model.Envelope import Envelope


# -----------------------------------------------------------------------------
# class EnvelopeTestCase
#
# python -m unittest discover model/tests/
# python -m unittest model.tests.test_Envelope
# -----------------------------------------------------------------------------
class EnvelopeTestCase(unittest.TestCase):

    # -------------------------------------------------------------------------
    # testAccessors
    # -------------------------------------------------------------------------
    def testAccessors(self):

        ulx = 374187
        uly = 4202663
        lrx = 501598
        lry = 4100640
        srs = SpatialReference()
        srs.ImportFromEPSG(32612)
        env = Envelope()
        env.addPoint(ulx, uly, 0, srs)
        env.addPoint(lrx, lry, 0, srs)

        self.assertEqual(ulx, env.ulx())
        self.assertEqual(uly, env.uly())
        self.assertEqual(lrx, env.lrx())
        self.assertEqual(lry, env.lry())

    # -------------------------------------------------------------------------
    # testAddPoint
    # -------------------------------------------------------------------------
    def testAddPoint(self):

        env = Envelope()

        # Invalid x.  Invalid ordinates are undetected by GDAL, so no error.
        srs = SpatialReference()
        srs.ImportFromEPSG(4326)
        env.addPoint(100, 100, 0, srs)

        # Invalid ordinate type.
        with self.assertRaises(TypeError):
            env.addPoint('abc', 100, 0, srs)

        # Add a second point with a different SRS than the first.
        with self.assertRaisesRegexp(RuntimeError, 'must be in the SRS'):

            utm = SpatialReference()
            utm.ImportFromEPSG(32612)
            env.addPoint(374187, 4202663, 0, utm)

        # Add a couple valid points.
        env.addPoint(80, 10, 10, srs)
        env.addPoint(43.5, 79.3, 0, srs)

    # -------------------------------------------------------------------------
    # testAddOgrPoint
    # -------------------------------------------------------------------------
    def testAddOgrPoint(self):

        # ---
        # Several of the tests are covered by testAddPoint because addPoint
        # uses addOgrPoint.
        # ---
        env = Envelope()

        with self.assertRaises(AttributeError):
            env.addOgrPoint('abc')

        with self.assertRaisesRegexp(RuntimeError, 'must be of type wkbPoint'):
            env.addOgrPoint(ogr.Geometry(ogr.wkbPolygon))

    # -------------------------------------------------------------------------
    # testEquals
    # -------------------------------------------------------------------------
    def testEquals(self):

        ulx = 374187
        uly = 4202663
        lrx = 501598
        lry = 4100640
        srs = SpatialReference()
        srs.ImportFromEPSG(32612)
        env = Envelope()
        env.addPoint(ulx, uly, 0, srs)
        env.addPoint(lrx, lry, 0, srs)

        unequalEnv = Envelope()
        unequalEnv.addPoint(ulx+1, uly, 0, srs)
        self.assertFalse(env.equals(unequalEnv))

        equalEnv = Envelope()
        equalEnv.addPoint(ulx, uly, 0, srs)
        equalEnv.addPoint(lrx, lry, 0, srs)
        self.assertTrue(env.equals(equalEnv))

    # -------------------------------------------------------------------------
    # testExpansion
    # -------------------------------------------------------------------------
    def testExpansion(self):

        ulx = 374187
        uly = 4202663
        lrx = 501598
        lry = 4100640
        srs = SpatialReference()
        srs.ImportFromEPSG(32612)
        env = Envelope()
        env.addPoint(ulx, uly, 0, srs)
        env.addPoint(lrx, lry, 0, srs)

        self.assertEqual(ulx, env.ulx())
        self.assertEqual(uly, env.uly())
        self.assertEqual(lrx, env.lrx())
        self.assertEqual(lry, env.lry())

        lry = 4100000
        env.addPoint(lrx, lry, 0, srs)

        self.assertEqual(ulx, env.ulx())
        self.assertEqual(uly, env.uly())
        self.assertEqual(lrx, env.lrx())
        self.assertEqual(lry, env.lry())

    # -------------------------------------------------------------------------
    # testSrs
    # -------------------------------------------------------------------------
    def testSrs(self):

        ulx = 374187
        uly = 4202663
        lrx = 501598
        lry = 4100640
        srs = SpatialReference()
        srs.ImportFromEPSG(32612)
        env = Envelope()
        env.addPoint(ulx, uly, 0, srs)
        env.addPoint(lrx, lry, 0, srs)

        srs = SpatialReference()
        srs.ImportFromEPSG(32612)

        self.assertTrue(srs.IsSame(env.srs()))

    # -------------------------------------------------------------------------
    # testTransformTo
    # -------------------------------------------------------------------------
    def testTransformTo(self):

        ulx = 374187
        uly = 4202663
        lrx = 501598
        lry = 4100640
        srs = SpatialReference()
        srs.ImportFromEPSG(32612)
        env = Envelope()
        env.addPoint(ulx, uly, 0, srs)
        env.addPoint(lrx, lry, 0, srs)

        targetSRS = SpatialReference()
        targetSRS.ImportFromEPSG(4326)
        env.transformTo(targetSRS)

        expectedUlx = -112.43223503554906
        expectedUly = 37.962871687712536
        expectedLrx = -110.98202787057967
        expectedLry = 37.051990304130925

        self.assertAlmostEqual(expectedUlx, env.ulx(), 10)
        self.assertAlmostEqual(expectedUly, env.uly(), 8)
        self.assertAlmostEqual(expectedLrx, env.lrx(), 10)
        self.assertAlmostEqual(expectedLry, env.lry(), 8)
        self.assertTrue(targetSRS.IsSame(env.srs()))

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
        env = Envelope()
        env.addPoint(ulx, uly, 0, 32612)
        env.addPoint(lrx, lry, 0, 32612)

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
        env.addPoint(100, 100, 0, 4326)

        # Invalid ordinate type.
        with self.assertRaises(TypeError):
            env.addPoint('abc', 100, 0, 4326)

        # Add a second point with a different SRS than the first.
        with self.assertRaisesRegexp(RuntimeError, 'must be in the SRS'):
            env.addPoint(374187, 4202663, 0, 32612)

        # Add a couple valid points.
        env.addPoint(80, 10, 10, 4326)
        env.addPoint(43.5, 79.3, 0, 4326)

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
        env = Envelope()
        env.addPoint(ulx, uly, 0, 32612)
        env.addPoint(lrx, lry, 0, 32612)

        unequalEnv = Envelope()
        unequalEnv.addPoint(ulx+1, uly, 0, 32612)
        self.assertFalse(env.equals(unequalEnv))

        equalEnv = Envelope()
        equalEnv.addPoint(ulx, uly, 0, 32612)
        equalEnv.addPoint(lrx, lry, 0, 32612)
        self.assertTrue(env.equals(equalEnv))

    # -------------------------------------------------------------------------
    # testExpansion
    # -------------------------------------------------------------------------
    def testExpansion(self):

        ulx = 374187
        uly = 4202663
        lrx = 501598
        lry = 4100640
        env = Envelope()
        env.addPoint(ulx, uly, 0, 32612)
        env.addPoint(lrx, lry, 0, 32612)

        self.assertEqual(ulx, env.ulx())
        self.assertEqual(uly, env.uly())
        self.assertEqual(lrx, env.lrx())
        self.assertEqual(lry, env.lry())

        lry = 4100000
        env.addPoint(lrx, lry, 0, 32612)

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
        epsg = 32612
        env = Envelope()
        env.addPoint(ulx, uly, 0, epsg)
        env.addPoint(lrx, lry, 0, epsg)

        srs = SpatialReference()
        srs.ImportFromEPSG(epsg)

        self.assertTrue(srs.IsSame(env.srs()))

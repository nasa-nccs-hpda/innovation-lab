#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import unittest

from osgeo import ogr
from osgeo.osr import SpatialReference

from model.Envelope import Envelope


# -----------------------------------------------------------------------------
# class EnvelopeTestCase
#
# docker run -it -v /Users/rlgill/Desktop/Source/innovation-lab:/home/ilUser/hostFiles -v /Users/rlgill/Desktop/SystemTesting:/home/ilUser/SystemTesting innovation-lab:1.0
# cd ~/hostFiles
# export PYTHONPATH=`pwd`
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

        srs = SpatialReference()
        srs.ImportFromEPSG(4326)
        ogrPt = ogr.Geometry(ogr.wkbPoint)
        ogrPt.AddPoint(20.0, 30.0, 40)
        ogrPt.AssignSpatialReference(srs)
        env.addOgrPoint(ogrPt)

        self.assertEqual(env.ulx(), 20.0)
        self.assertEqual(env.uly(), 30.0)

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
    # testGetSetState
    # -------------------------------------------------------------------------
    def testGetSetState(self):

        ulx = 374187
        uly = 4202663
        lrx = 501598
        lry = 4100640
        srs = SpatialReference()
        srs.ImportFromEPSG(32612)
        env = Envelope()
        env.addPoint(ulx, uly, 0, srs)
        env.addPoint(lrx, lry, 0, srs)

        state = env.__reduce__()
        env2 = Envelope()
        env2.__setstate__(state[2])

        self.assertEqual(env.ulx(), env2.ulx())
        self.assertEqual(env.uly(), env2.uly())
        self.assertEqual(env.lrx(), env2.lrx())
        self.assertEqual(env.lry(), env2.lry())

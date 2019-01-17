#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import csv
import os
import tempfile
import unittest

from osgeo.osr import SpatialReference

from model.Envelope import Envelope
from model.ObservationFile import ObservationFile


# -----------------------------------------------------------------------------
# class ObservationFileTestCase
#
# python -m unittest discover model/tests/
# python -m unittest model.tests.test_ObservationFile
# -----------------------------------------------------------------------------
class ObservationFileTestCase(unittest.TestCase):

    _testObsFile = None

    # -------------------------------------------------------------------------
    # setUpClass
    # -------------------------------------------------------------------------
    @classmethod
    def setUpClass(cls):

        ObservationFileTestCase._testObsFile = \
            tempfile.mkstemp(suffix='.csv')[1]

        print '_testObsFile: ' + str(ObservationFileTestCase._testObsFile)

        with open(ObservationFileTestCase._testObsFile, 'w') as csvFile:

            fields = ['x', 'y', 'z', 'epsg', 'pres/abs']
            writer = csv.writer(csvFile, fields)
            writer.writerow(fields)
            writer.writerow((374187, 4124593, 0, 32612, 1))
            writer.writerow((393543, 4100640, 0, 32612, 0))
            writer.writerow((395099, 4130094, 0, 32612, 0))
            writer.writerow((486130, 4202663, 0, 32612, 1))
            writer.writerow((501598, 4142175, 0, 32612, 0))

    # -------------------------------------------------------------------------
    # tearDownClass
    # -------------------------------------------------------------------------
    @classmethod
    def tearDownClass(cls):

        os.remove(ObservationFileTestCase._testObsFile)

    # -------------------------------------------------------------------------
    # testCRS
    # -------------------------------------------------------------------------
    def testCRS(self):

        testCRS = SpatialReference()
        testCRS.ImportFromEPSG(32612)
        obs = ObservationFile(ObservationFileTestCase._testObsFile)
        self.assertTrue(obs.crs().IsSame(testCRS))

    # -------------------------------------------------------------------------
    # testEnvelope
    # -------------------------------------------------------------------------
    def testEnvelope(self):

        testEnv = Envelope()
        testEnv.addPoint(374187, 4202663, 0, 32612)
        testEnv.addPoint(501598, 4100640, 0, 32612)
        obs = ObservationFile(ObservationFileTestCase._testObsFile)
        self.assertTrue(testEnv.equals(obs.envelope()))

    # -------------------------------------------------------------------------
    # testNotA_CSV_File
    # -------------------------------------------------------------------------
    def testNotA_CSV_File(self):

        with self.assertRaises(RuntimeError):
            ObservationFile('Common/tests/test_BaseFile.py')

    # -------------------------------------------------------------------------
    # testInvalidFile
    # -------------------------------------------------------------------------
    def testInvalidFile(self):

        # Create a file with multiple CRSs.
        invalidFile = tempfile.mkstemp(suffix='.csv')[1]
        print 'invalidFile: ' + str(invalidFile)

        with open(invalidFile, 'w') as csvFile:

            fields = ['x', 'y', 'z', 'epsg', 'pres/abs']
            writer = csv.writer(csvFile, fields)
            writer.writerow(fields)
            writer.writerow((374187, 4124593, 0, 32612, 1))
            writer.writerow((88.8, 21.12, 301, 4326, 0))

        with self.assertRaisesRegexp(RuntimeError, 'same CRS'):
            ObservationFile(invalidFile)

        os.remove(invalidFile)

    # -------------------------------------------------------------------------
    # testValidFile
    # -------------------------------------------------------------------------
    def testValidFile(self):

        obs = ObservationFile(ObservationFileTestCase._testObsFile)
        self.assertEqual(obs.numObservations(), 5)
        self.assertEqual(obs.observation(0)[0].GetX(), 374187)
        self.assertEqual(obs.observation(1)[1], False)
        self.assertEqual(obs.observation(2)[0].GetY(), 4130094)
        self.assertEqual(obs.observation(3)[1], True)

        # Test a spatial reference.
        crs = SpatialReference()
        crs.ImportFromEPSG(32612)

        self.assertTrue(obs.observation(4)[0].
                        GetSpatialReference().
                        IsSame(crs))

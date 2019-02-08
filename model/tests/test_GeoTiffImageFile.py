#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import tempfile
import unittest


from model.GeoTiffImageFile import GeoTiffImageFile


# -----------------------------------------------------------------------------
# class GeoTiffImageFileTestCase
#
# python -m unittest discover model/tests/
# python -m unittest model.tests.test_GeoTiffImageFile
# -----------------------------------------------------------------------------
class GeoTiffImageFileTestCase(unittest.TestCase):

    TEST_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'gsenm_250m_eucl_dist_streams.tif')

    # -------------------------------------------------------------------------
    # testNotGeoTiffImageFile
    # -------------------------------------------------------------------------
    def testNotGeoTiffImageFile(self):

        notGeoTiffImageFile = tempfile.mkstemp(suffix='.csv')[1]

        with self.assertRaisesRegexp(RuntimeError, 'not in .tif format'):
            GeoTiffImageFile(notGeoTiffImageFile)

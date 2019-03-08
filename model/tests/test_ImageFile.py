#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import unittest

from model.ImageFile import ImageFile


# -----------------------------------------------------------------------------
# class ImageFileTestCase
#
# python -m unittest discover model/tests/
# python -m unittest model.tests.test_ImageFile
# -----------------------------------------------------------------------------
class ImageFileTestCase(unittest.TestCase):

    TEST_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'TSURF.nc')

    # -------------------------------------------------------------------------
    # test_getDataset
    # -------------------------------------------------------------------------
    def test_getDataset(self):

        # Create a test image.
        imageFile = ImageFile(ImageFileTestCase.TEST_FILE)

        # Test _getDataset.
        self.assertIsNotNone(imageFile._getDataset())

    # -------------------------------------------------------------------------
    # testInvalidImageType
    # -------------------------------------------------------------------------
    def testInvalidImageType(self):

        testFile = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'invalid.tif')

        with self.assertRaisesRegexp(RuntimeError, 'is not in .nc'):
            ImageFile(testFile)

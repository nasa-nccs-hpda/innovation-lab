#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import tempfile
import unittest

from model.NC_File import NC_File


# -----------------------------------------------------------------------------
# class NC_FileTestCase
#
# python -m unittest discover model/tests/
# python -m unittest model.tests.test_NC_File
# -----------------------------------------------------------------------------
class NC_FileTestCase(unittest.TestCase):

    # -------------------------------------------------------------------------
    # testNotNC_File
    # -------------------------------------------------------------------------
    def testNotNC_File(self):

        notNC_File = tempfile.mkstemp(suffix='.csv')[1]

        with self.assertRaisesRegexp(RuntimeError, 'not in Net CDF format'):
            NC_File(notNC_File)

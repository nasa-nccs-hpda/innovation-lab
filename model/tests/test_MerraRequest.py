#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import unittest

import pandas

from model.MerraRequest import MerraRequest


# -----------------------------------------------------------------------------
# class MerraRequestTestCase
#
# python -m unittest discover model/tests/
# python -m unittest model.tests.test_MerraRequest
# -----------------------------------------------------------------------------
class MerraRequestTestCase(unittest.TestCase):

    # -------------------------------------------------------------------------
    # testQueryFiles
    # -------------------------------------------------------------------------
    def testQueryFiles(self):

        import pdb
        pdb.set_trace()
        dateRange = pandas.date_range('2010-10-10', '2012-12-12')
        files = MerraRequest.queryFiles(dateRange, 'tavgM_2d_slv_Nx')

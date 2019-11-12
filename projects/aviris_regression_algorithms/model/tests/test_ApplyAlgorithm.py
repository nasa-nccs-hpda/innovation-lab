#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import tempfile
import unittest

from projects.aviris_regression_algorithms.model.ApplyAlgorithm \
    import ApplyAlgorithm


# -----------------------------------------------------------------------------
# class ApplyAlgorithmTestCase
#
# python -m unittest projects.aviris_regression_algorithms.model.tests.test_ApplyAlgorithm
# -----------------------------------------------------------------------------
class ApplyAlgorithmTestCase(unittest.TestCase):

    TEST_FILE = '/att/pubrepo/ORNL/ABoVE_Archive/daac.ornl.gov/daacdata/' \
                'above/ABoVE_Airborne_AVIRIS_NG/data/' \
                'ang20170709t224839_rfl_v2p9/ang20170709t224839_corr_v2p9_img'
    
    # -------------------------------------------------------------------------
    # testInit
    # -------------------------------------------------------------------------
    def testInit(self):

        coefFile = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'Chl_Coeff_input.csv')

        aa = ApplyAlgorithm(coefFile, 
                            ApplyAlgorithmTestCase.TEST_FILE, 
                            tempfile.gettempdir())

#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import logging
import os
import sys
import tempfile
import unittest

from projects.aviris_regression_algorithms.model.ApplyAlgorithm \
    import ApplyAlgorithm


logger = logging.getLogger()
logger.level = logging.DEBUG

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
    # test
    # -------------------------------------------------------------------------
    def test(self):

        streamHandler = logging.StreamHandler(sys.stdout)
        logger.addHandler(streamHandler)

        coefFile = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'Chl_Coeff_input.csv')

        aa = ApplyAlgorithm(coefFile, 
                            ApplyAlgorithmTestCase.TEST_FILE, 
                            tempfile.gettempdir())
                            
        aa.applyAlgorithm('Avg Chl')

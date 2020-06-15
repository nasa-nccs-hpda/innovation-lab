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
#
# /att/nobackup/rlgill/innovation-lab$ python -m unittest projects.aviris_regression_algorithms.model.tests.test_ApplyAlgorithm.ApplyAlgorithmTestCase.testScreen
# -----------------------------------------------------------------------------
class ApplyAlgorithmTestCase(unittest.TestCase):

    # -------------------------------------------------------------------------
    # test
    # -------------------------------------------------------------------------
    def test(self):

        streamHandler = logging.StreamHandler(sys.stdout)
        logger.addHandler(streamHandler)

        coefFile = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'PLSR_Coeff_NoVN_v2.csv')

        # Image is 653 x 7074 x 425
        testImage = '/att/pubrepo/ABoVE/archived_data/ORNL/' + \
                    'ABoVE_Airborne_AVIRIS_NG_CORRUPT/data/' + \
                    'ang20180729t210144rfl/ang20180729t210144_rfl_v2r2/' + \
                    'ang20180729t210144_corr_v2r2_img'

        aa = ApplyAlgorithm(coefFile, testImage, logger)
        print('Testing without normalization.')
        aa.applyAlgorithm('AVG-CHL', tempfile.gettempdir())
        print('Testing with normalization.')
        aa.applyAlgorithm('AVG-CHL', tempfile.gettempdir(), True)

    # -------------------------------------------------------------------------
    # testScreen
    # -------------------------------------------------------------------------
    def testScreen(self):
        
        streamHandler = logging.StreamHandler(sys.stdout)
        logger.addHandler(streamHandler)

        coefFile = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'PLSR_Coeff_NoVN_v2.csv')

        # Image is 653 x 7074 x 425
        testImage = '/att/pubrepo/ABoVE/archived_data/ORNL/' + \
                    'ABoVE_Airborne_AVIRIS_NG_CORRUPT/data/' + \
                    'ang20180729t210144rfl/ang20180729t210144_rfl_v2r2/' + \
                    'ang20180729t210144_corr_v2r2_img'

        aa = ApplyAlgorithm(coefFile, testImage, logger)
        aa.screen()
        
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
# gdal_translate -of ENVI -srcwin 41 96 5 5 /att/pubrepo/ABoVE/archived_data/ORNL/ABoVE_Airborne_AVIRIS_NG_CORRUPT/data/ang20180729t210144rfl/ang20180729t210144_rfl_v2r2/ang20180729t210144_corr_v2r2_img clip.img
#
# python -m unittest projects.aviris_regression_algorithms.model.tests.test_ApplyAlgorithm
# -----------------------------------------------------------------------------
class ApplyAlgorithmTestCase(unittest.TestCase):

    # -------------------------------------------------------------------------
    # test
    # -------------------------------------------------------------------------
    def test(self):

        streamHandler = logging.StreamHandler(sys.stdout)
        logger.addHandler(streamHandler)

        coefFile = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'Chl_Coeff_input.csv')

        testImage = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 'clip.img')

        aa = ApplyAlgorithm(coefFile, testImage, logger)
        aa.applyAlgorithm('Avg Chl', tempfile.gettempdir())
        aa.applyAlgorithm('Avg Chl', tempfile.gettempdir(), True)

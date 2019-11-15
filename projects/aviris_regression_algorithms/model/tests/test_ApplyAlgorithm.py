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

        aa = ApplyAlgorithm(coefFile, testImage, tempfile.gettempdir(),logger)
        aa.applyAlgorithm('Avg Chl')

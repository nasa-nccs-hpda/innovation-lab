#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import unittest

from model.BaseFile import BaseFile


# -----------------------------------------------------------------------------
# class BaseFileTestCase
#
# python -m unittest discover model/tests/
# python -m unittest model.tests.test_BaseFile
# -----------------------------------------------------------------------------
class BaseFileTestCase(unittest.TestCase):

    # -------------------------------------------------------------------------
    # testFileDoesNotExist
    # -------------------------------------------------------------------------
    def testFileDoesNotExist(self):

        with self.assertRaises(RuntimeError):
            BaseFile('/this/does/not/exist')

    # -------------------------------------------------------------------------
    # testFileExists
    # -------------------------------------------------------------------------
    def testFileExists(self):

        BaseFile('model/tests/test_BaseFile.py')

    # -------------------------------------------------------------------------
    # testNoFileSpecified
    # -------------------------------------------------------------------------
    def testNoFileSpecified(self):

        with self.assertRaises(TypeError):
            BaseFile()

        with self.assertRaises(RuntimeError):
            BaseFile(None)

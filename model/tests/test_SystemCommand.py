#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import logging
import unittest

from model.SystemCommand import SystemCommand


# -----------------------------------------------------------------------------
# class SystemCommandTestCase
#
# python -m unittest discover model/tests/
# python -m unittest model.tests.test_SystemCommand
# -----------------------------------------------------------------------------
class SystemCommandTestCase(unittest.TestCase):

    # -------------------------------------------------------------------------
    # testInvalidCommand
    # -------------------------------------------------------------------------
    def testInvalidCommand(self):

        with self.assertRaisesRegexp(RuntimeError, 'A system command error'):

            SystemCommand('notA_Cmd', None, True)

    # -------------------------------------------------------------------------
    # testValidUnsuccessfulCommand
    # -------------------------------------------------------------------------
    def testValidUnsuccessfulCommand(self):

        scmd = SystemCommand('ls abc.txt')

        self.assertEqual(scmd.msg,
                         'ls: cannot access \'abc.txt\': ' +
                         'No such file or directory\n')

        scmd = SystemCommand('gdal_merge.py abc.txt', logging.getLogger())
        self.assertTrue('ERROR 4: abc.txt: No such file' in scmd.msg)

        with self.assertRaisesRegexp(RuntimeError, 'A system command error'):

            scmd = SystemCommand('gdal_merge.py abc.txt',
                                 logging.getLogger(),
                                 True)

    # -------------------------------------------------------------------------
    # testValidSuccessfulCommand
    # -------------------------------------------------------------------------
    def testValidSuccessfulCommand(self):

        SystemCommand('ls')
        SystemCommand('ls', logging.getLogger())
        SystemCommand('ls', logging.getLogger(), True)

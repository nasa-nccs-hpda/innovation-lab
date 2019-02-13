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

        with self.assertRaisesRegexp(RuntimeError, 'not in .nc format'):
            NC_File(notNC_File)

    # -------------------------------------------------------------------------
    # testNC_FileExtension
    # -------------------------------------------------------------------------
    def testNC_FileExtension(self):
        file = tempfile.mkstemp(suffix='.nc')[1]
        self.assertEqual(NC_File(file).extension(), '.nc')
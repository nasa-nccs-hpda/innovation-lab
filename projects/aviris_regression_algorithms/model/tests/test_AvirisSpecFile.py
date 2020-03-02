# -*- coding: utf-8 -*-

from datetime import datetime
import os
import unittest

from model.ImageFile import ImageFile

from projects.aviris_regression_algorithms.model.AvirisSpecFile \
    import AvirisSpecFile


# -----------------------------------------------------------------------------
# class AvirisSpecFileTestCase
#
# export PYTHONPATH='pwd'
# python -m unittest projects.aviris_regression_algorithms.model.tests.test_AvirisSpecFile
# -----------------------------------------------------------------------------
class AvirisSpecFileTestCase(unittest.TestCase):

    # -------------------------------------------------------------------------
    # testInit
    # -------------------------------------------------------------------------
    def testInit(self):

        asf = AvirisSpecFile()

        specFile = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'sample.spec')

        asf = AvirisSpecFile(specFile)

    # -------------------------------------------------------------------------
    # testWrite
    # -------------------------------------------------------------------------
    def testWrite(self):

        # Basic set and write test.
        asf = AvirisSpecFile()
        asf.setField(AvirisSpecFile.CLOUD_MASK_KEY, (1, '<', 2))

        coefs = {'Intercept': 66.11285, 381.87: 0}
        asf.setField(AvirisSpecFile.COEFS_KEY, coefs)

        csvFile = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'Chl_Coeff_input.csv')

        asf.setField(AvirisSpecFile.COEFS_FILE_KEY, csvFile)

        asf.setField(AvirisSpecFile.IMAGE_FILE_KEY,
                     '/att/pubrepo/ABoVE/archived_data/ORNL/' +
                     'ABoVE_Airborne_AVIRIS_NG_CORRUPT/data/' +
                     'ang20170714t213741rfl/' +
                     'ang20170714t213741_rfl_v2p9/' +
                     'ang20170714t213741_corr_v2p9_img')

        asf.setField(AvirisSpecFile.MASK_VALUE_KEY, -9999.0)
        asf.setField(AvirisSpecFile.NORMALIZE_KEY, False)
        asf.setField(AvirisSpecFile.NO_DATA_KEY, -9999.0)
        asf.setField(AvirisSpecFile.PLANT_TYPE_KEY, 'Robert')
        asf.setField(AvirisSpecFile.PROCESS_DATE_KEY, datetime.today())
        asf.setField(AvirisSpecFile.CLOUD_MASK_KEY, '416.929993 > 0.8')
        asf.setField(AvirisSpecFile.WATER_MASK_KEY, '1598.98 < 0.01')

        asf.write('/tmp')
        os.remove(asf.specFileName())

        # Write it again, to test writing an existing file.
        asf.write()
        os.remove(asf.specFileName())

    # -------------------------------------------------------------------------
    # testRoundTrip
    # -------------------------------------------------------------------------
    def testRoundTrip(self):

        # Read from a spec. file.
        specFile = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'sample.spec')

        asf = AvirisSpecFile(specFile)

        # Create a new file using accessors.
        asf2 = AvirisSpecFile()

        asf2.setField(AvirisSpecFile.BBL_KEY,
                      asf.getField(AvirisSpecFile.BBL_KEY))

        asf2.setField(AvirisSpecFile.CLOUD_MASK_KEY,
                      asf.getField(AvirisSpecFile.CLOUD_MASK_KEY))

        asf2.setField(AvirisSpecFile.COEFS_FILE_KEY,
                      asf.getField(AvirisSpecFile.COEFS_FILE_KEY))

        asf2.setField(AvirisSpecFile.COEFS_KEY,
                      asf.getField(AvirisSpecFile.COEFS_KEY))

        asf2.setField(AvirisSpecFile.CORRECTION_FACTORS_KEY,
                      asf.getField(AvirisSpecFile.CORRECTION_FACTORS_KEY))

        asf2.setField(AvirisSpecFile.FWHM_KEY,
                      asf.getField(AvirisSpecFile.FWHM_KEY))

        asf2.setField(AvirisSpecFile.IMAGE_FILE_KEY,
                      asf.getField(AvirisSpecFile.IMAGE_FILE_KEY))

        asf2.setField(AvirisSpecFile.MASK_VALUE_KEY,
                      asf.getField(AvirisSpecFile.MASK_VALUE_KEY))

        asf2.setField(AvirisSpecFile.NORMALIZE_KEY,
                      asf.getField(AvirisSpecFile.NORMALIZE_KEY))

        asf2.setField(AvirisSpecFile.NO_DATA_KEY,
                      asf.getField(AvirisSpecFile.NO_DATA_KEY))

        asf2.setField(AvirisSpecFile.PLANT_TYPE_KEY,
                      asf.getField(AvirisSpecFile.PLANT_TYPE_KEY))

        asf2.setField(AvirisSpecFile.PROCESS_DATE_KEY,
                      asf.getField(AvirisSpecFile.PROCESS_DATE_KEY))

        asf2.setField(AvirisSpecFile.RADIANCE_VERSION_KEY,
                      asf.getField(AvirisSpecFile.RADIANCE_VERSION_KEY))

        asf2.setField(AvirisSpecFile.SMOOTHING_FACTORS_KEY,
                      asf.getField(AvirisSpecFile.SMOOTHING_FACTORS_KEY))

        asf2.setField(AvirisSpecFile.WATER_MASK_KEY,
                      asf.getField(AvirisSpecFile.WATER_MASK_KEY))

        asf2.setField(AvirisSpecFile.WAVELENGTH_KEY,
                      asf.getField(AvirisSpecFile.WAVELENGTH_KEY))

        # Write the spec. file.
        asf2.write('/tmp')

        # Read it and test the values.
        asf3 = AvirisSpecFile(asf2.specFileName())
        os.remove(asf2.specFileName())

        self.assertEqual(asf2.getField(AvirisSpecFile.BBL_KEY),
                         asf3.getField(AvirisSpecFile.BBL_KEY))

        self.assertEqual(asf2.getField(AvirisSpecFile.CLOUD_MASK_KEY),
                         asf3.getField(AvirisSpecFile.CLOUD_MASK_KEY))

        self.assertEqual(asf2.getField(AvirisSpecFile.COEFS_FILE_KEY),
                         asf3.getField(AvirisSpecFile.COEFS_FILE_KEY))

        self.assertEqual(asf2.getField(AvirisSpecFile.COEFS_KEY),
                         asf3.getField(AvirisSpecFile.COEFS_KEY))

        self.assertEqual(asf2.getField(AvirisSpecFile.CORRECTION_FACTORS_KEY),
                         asf3.getField(AvirisSpecFile.CORRECTION_FACTORS_KEY))

        self.assertEqual(asf2.getField(AvirisSpecFile.FWHM_KEY),
                         asf3.getField(AvirisSpecFile.FWHM_KEY))

        self.assertEqual(asf2.getField(AvirisSpecFile.IMAGE_FILE_KEY),
                         asf3.getField(AvirisSpecFile.IMAGE_FILE_KEY))

        self.assertEqual(asf2.getField(AvirisSpecFile.MASK_VALUE_KEY),
                         asf3.getField(AvirisSpecFile.MASK_VALUE_KEY))

        self.assertEqual(asf2.getField(AvirisSpecFile.NORMALIZE_KEY),
                         asf3.getField(AvirisSpecFile.NORMALIZE_KEY))

        self.assertEqual(asf2.getField(AvirisSpecFile.NO_DATA_KEY),
                         asf3.getField(AvirisSpecFile.NO_DATA_KEY))

        self.assertEqual(asf2.getField(AvirisSpecFile.PLANT_TYPE_KEY),
                         asf3.getField(AvirisSpecFile.PLANT_TYPE_KEY))

        self.assertEqual(asf2.getField(AvirisSpecFile.PROCESS_DATE_KEY),
                         asf3.getField(AvirisSpecFile.PROCESS_DATE_KEY))

        self.assertEqual(asf2.getField(AvirisSpecFile.RADIANCE_VERSION_KEY),
                         asf3.getField(AvirisSpecFile.RADIANCE_VERSION_KEY))

        self.assertEqual(asf2.getField(AvirisSpecFile.SMOOTHING_FACTORS_KEY),
                         asf3.getField(AvirisSpecFile.SMOOTHING_FACTORS_KEY))

        self.assertEqual(asf2.getField(AvirisSpecFile.WATER_MASK_KEY),
                         asf3.getField(AvirisSpecFile.WATER_MASK_KEY))

        self.assertEqual(asf2.getField(AvirisSpecFile.WAVELENGTH_KEY),
                         asf3.getField(AvirisSpecFile.WAVELENGTH_KEY))

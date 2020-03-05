# -*- coding: utf-8 -*-

import collections
from datetime import datetime
import json
import os

from model.BaseFile import BaseFile


# -----------------------------------------------------------------------------
# class AvirisSpecFile
#
# This class defines the parameters for an aviris modeling run, serving as the
# input to the application.  It also serves as contextual metadata for the
# output images.
# -----------------------------------------------------------------------------
class AvirisSpecFile(BaseFile):

    # ---
    # These keys designate each item in the spec. file.  They are used to read
    # and write spec. files.
    # ---
    BBL_KEY = 'bbl'
    CLOUD_MASK_KEY = 'Cloud mask'
    COEFS_KEY = 'Coefficients'
    COEFS_FILE_KEY = 'Coefficients file'
    CORRECTION_FACTORS_KEY = 'correction factors'
    FWHM_KEY = 'fwhm'
    IMAGE_FILE_KEY = 'Image file'
    MASK_VALUE_KEY = 'Mask value'
    NORMALIZE_KEY = 'Normalize'
    NO_DATA_KEY = 'No-data value'
    PLANT_TYPE_KEY = 'Plant type'
    PROCESS_DATE_KEY = 'Process date'
    RADIANCE_VERSION_KEY = 'radiance version'
    SMOOTHING_FACTORS_KEY = 'smoothing factors'
    WATER_MASK_KEY = 'Water mask'
    WAVELENGTH_KEY = 'wavelength'

    # These are the keys of the fields that are parameters for AVIRIS runs.
    PARAMETER_KEYS = [COEFS_FILE_KEY, IMAGE_FILE_KEY, MASK_VALUE_KEY,
                      NORMALIZE_KEY, NO_DATA_KEY, PLANT_TYPE_KEY]

    # ---
    # These are the fields that are read from the image header file.  The
    # private method, _readImageHeaderField, uses this list to test that the
    # requested field is expected to be in the header.
    # ---
    META_KEYS = [BBL_KEY, CORRECTION_FACTORS_KEY, FWHM_KEY,
                 RADIANCE_VERSION_KEY, SMOOTHING_FACTORS_KEY, WAVELENGTH_KEY]

    # These are all other field.
    OTHER_KEYS = [CLOUD_MASK_KEY, COEFS_KEY, PROCESS_DATE_KEY, WATER_MASK_KEY]

    SEPARATOR = ':'

    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self, specFileName=None):

        self._imageHeader = None
        self._specFileName = specFileName
        self._specDict = {}

        if specFileName:

            BaseFile(specFileName)  # Simply to validate the file.

            with open(self._specFileName, 'r') as fp:

                for line in fp:

                    line = line.strip()

                    if line and line[0] != '#':

                        key, value = line.split(AvirisSpecFile.SEPARATOR, 1)
                        self._specDict[key.strip()] = value.strip()

    # -------------------------------------------------------------------------
    # _createSpecFile
    # -------------------------------------------------------------------------
    def _createSpecFile(self, outDir):

        # Validate the output directory.
        if not outDir:
            raise RuntimeError('An output directory must be specified.')

        if not os.path.isdir(outDir):
            raise RuntimeError(str(outDir) + ' is not a directory.')

        # Create a unique output file name.
        outFileName = \
            os.path.join(outDir,
                         self.getField(AvirisSpecFile.PLANT_TYPE_KEY) +
                         '.spec')

        uniqueName = outFileName
        count = 0

        while os.path.exists(uniqueName):

            count += 1
            uniqueName = outFileName.replace('.spec', str(count) + '.spec')

        self._specFileName = uniqueName

    # -------------------------------------------------------------------------
    # getField
    # -------------------------------------------------------------------------
    def getField(self, key):

        if not key:
            raise RuntimeError('A key must be provided.')

        if key not in AvirisSpecFile.PARAMETER_KEYS and \
           key not in AvirisSpecFile.META_KEYS and \
           key notin AvirisSpecFile.OTHER_KEYS:

            raise RuntimeError('Invalid key: ' + str(key))

        return self._specDict[key]

    # -------------------------------------------------------------------------
    # _imageHeaderName
    # -------------------------------------------------------------------------
    def _imageHeaderName(self):

        return self.getField(AvirisSpecFile.IMAGE_FILE_KEY) + '.hdr'

    # -------------------------------------------------------------------------
    # _openImageHeader
    # -------------------------------------------------------------------------
    def _openImageHeader(self):

        if self._imageHeader:

            return self._imageHeader

        else:
            hdrName = self._imageHeaderName()
            return open(hdrName, 'r')

    # -------------------------------------------------------------------------
    # _readImageHdrField
    # -------------------------------------------------------------------------
    def _readImageHdrField(self, field):

        if field not in AvirisSpecFile.META_KEYS:

            raise RuntimeError('Field, ' +
                               str(field) +
                               ', is not a valid metadata key.')

        fp = self._openImageHeader()
        keyLen = len(field)

        for line in fp:

            if line[0:keyLen] == field:
                return line

        raise RuntimeError('Key, ' +
                           str(field) +
                           ', not found in header, ' +
                           self._imageHeaderName())

    # -------------------------------------------------------------------------
    # setField
    # -------------------------------------------------------------------------
    def setField(self, key, value):

        if not key:
            raise RuntimeError('A key must be provided.')

        if key not in AvirisSpecFile.PARAMETER_KEYS and \
           key not in AvirisSpecFile.META_KEYS and \
           key not in AvirisSpecFile.OTHER_KEYS:

            raise RuntimeError('Invalid key: ' + str(key))

        self._specDict[key] = value

    # -------------------------------------------------------------------------
    # specFileName
    # -------------------------------------------------------------------------
    def specFileName(self):

        return self._specFileName

    # -------------------------------------------------------------------------
    # write
    # -------------------------------------------------------------------------
    def write(self, outDir=None):

        if not self._specFileName:
            self._createSpecFile(outDir)

        # Get the metadata items that are not already populated.
        for key in AvirisSpecFile.META_KEYS:

            if key not in self._specDict:

                value = self._readImageHdrField(key).split('=')[1].strip()
                self.setField(key, value)

        self.setField(AvirisSpecFile.PROCESS_DATE_KEY, str(datetime.today()))

        # Write the file.
        with open(self._specFileName, 'w') as fp:

            # ---
            # A specific field ordering was requested, so we cannot simply
            # iterate over the keys.
            # ---
            self._writeField(fp, AvirisSpecFile.PROCESS_DATE_KEY)
            self._writeField(fp, AvirisSpecFile.IMAGE_FILE_KEY)
            self._writeField(fp, AvirisSpecFile.PLANT_TYPE_KEY)
            self._writeField(fp, AvirisSpecFile.NORMALIZE_KEY)
            self._writeField(fp, AvirisSpecFile.NO_DATA_KEY)
            self._writeField(fp, AvirisSpecFile.MASK_VALUE_KEY)
            self._writeField(fp, AvirisSpecFile.CLOUD_MASK_KEY)
            self._writeField(fp, AvirisSpecFile.WATER_MASK_KEY)
            self._writeField(fp, AvirisSpecFile.COEFS_FILE_KEY)

            # self._writeField(fp, AvirisSpecFile.COEFS_KEY)
            sortedCoefs = collections.\
                OrderedDict(sorted(self.getField(AvirisSpecFile.COEFS_KEY).
                                   items()))

            fp.write(AvirisSpecFile.COEFS_KEY +
                     AvirisSpecFile.SEPARATOR +
                     ' ' +
                     json.dumps(sortedCoefs) +
                     '\n')

            fp.write('#************************************\n')
            fp.write('# Metadata from input image\n')

            self._writeField(fp, AvirisSpecFile.RADIANCE_VERSION_KEY)
            self._writeField(fp, AvirisSpecFile.WAVELENGTH_KEY)
            self._writeField(fp, AvirisSpecFile.FWHM_KEY)
            self._writeField(fp, AvirisSpecFile.SMOOTHING_FACTORS_KEY)
            self._writeField(fp, AvirisSpecFile.CORRECTION_FACTORS_KEY)
            self._writeField(fp, AvirisSpecFile.BBL_KEY)

    # -------------------------------------------------------------------------
    # _writeField
    # -------------------------------------------------------------------------
    def _writeField(self, fp, key):

        fp.write(key +
                 AvirisSpecFile.SEPARATOR +
                 ' ' +
                 str(self.getField(key)) +
                 '\n')

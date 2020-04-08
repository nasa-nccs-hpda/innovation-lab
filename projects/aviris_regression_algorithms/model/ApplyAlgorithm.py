# -*- coding: utf-8 -*-

import csv
import math
import os
import re
import struct

from osgeo import gdal
from osgeo import gdalconst

from model.BaseFile import BaseFile
from model.Chunker import Chunker
from model.GeospatialImageFile import GeospatialImageFile

from projects.aviris_regression_algorithms.model.AvirisSpecFile \
    import AvirisSpecFile


# -----------------------------------------------------------------------------
# class ApplyAlgorithm
#
# gdallocationinfo -b 10
#     projects/aviris_regression_algorithms/model/tests/clip.img 0 0
# -----------------------------------------------------------------------------
class ApplyAlgorithm(object):

    NO_DATA_VALUE = -9999.0
    QA_COMPUTED = struct.pack('i', 0)
    QA_CLOUD = struct.pack('i', 1)
    QA_WATER = struct.pack('i', 2)
    QA_NO_DATA = struct.pack('i', 3)

    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self, csvFile, avirisImage, logger=None):

        self.logger = logger
        # self.imageFile = GeospatialImageFile(avirisImage, None, None)

        # ---
        # Set up a chunker to move through the image by row.  This makes no
        # difference for the single-thread version of this class, but the 
        # Celery version will create a task from each row.
        # ---
        self._chunker = Chunker(avirisImage)
        self._chunker.setChunkAsRow()
        
        self.coefs = []

        coefFile = BaseFile(csvFile, '.csv')

        with open(coefFile.fileName()) as csvFile:

            reader = csv.DictReader(csvFile)

            for row in reader:
                self.coefs.append(row)

        self._specFile = self._createSpecFile(coefFile)

    # -------------------------------------------------------------------------
    # applyAlgorithm
    #
    # P = a0 + a1b1 + a2b2 …
    # -------------------------------------------------------------------------
    def applyAlgorithm(self, algorithmName, outDir, normalizePixels=False):

        if not outDir:
            raise RuntimeError('An output directory must be provided.')

        if not os.path.exists(outDir) or not os.path.isdir(outDir):
            raise RuntimeError(str(outDir) + ' is not an existing directory.')

        self._coefsToSpec(algorithmName)
        self._specFile.setField(AvirisSpecFile.NORMALIZE_KEY, normalizePixels)
        self._specFile.setField(AvirisSpecFile.PLANT_TYPE_KEY, algorithmName)
        self._specFile.write(outDir)

        # Ensure the algorithm name is valid.
        if algorithmName not in self.coefs[0]:

            raise RuntimeError('Algorithm ' +
                               str(algorithmName) +
                               ' not in coeffients.')

        # Create the output raster and QA image.
        outDs, qa = self._createOutputImages(algorithmName, outDir)

        # Iterate through the raster.
        while True:
            
            loc, chunk = self._chunker.getChunk()
            
            if chunk == None:
                break
                
            # Provide a hint of the progress.
            if loc[0] % 100 == 0:

                print 'Row ' + str(row) + ' of ' + \
                    str(self._chunker._imageFile._getDataset().RasterYSize)

            self._processRow(loc, chunk, outDs, qa)

        outDs = None
        qa = None

    # -------------------------------------------------------------------------
    # _associateValuesWithCoefs
    # -------------------------------------------------------------------------
    def _associateValuesWithCoefs(self, pixelStack, algorithmName):

        bandCoefValueDict = {}

        for coefRow in self.coefs:

            bandIndex = \
                int(re.search(r'\d{0,3}$', coefRow['Band Number']).group())

            coef = float(coefRow[algorithmName] or 0)
            value = pixelStack[bandIndex-1] if bandIndex > 0 else 0.0
            bandCoefValueDict[bandIndex] = (coef, value)

        return bandCoefValueDict

    # -------------------------------------------------------------------------
    # _coefsToSpec
    # -------------------------------------------------------------------------
    def _coefsToSpec(self, plantType):

        filteredCoefs = {}

        for coef in self.coefs:

            wavelength = coef['AVIRIS Band Center'] or 'Intercept'
            filteredCoefs[wavelength] = coef[plantType]

        self._specFile.setField(AvirisSpecFile.COEFS_KEY, filteredCoefs)

    # -------------------------------------------------------------------------
    # _computeDivisor
    # -------------------------------------------------------------------------
    def _computeDivisor(self, bandCoefValueDict):

        tally = 0.0

        for band in bandCoefValueDict.iterkeys():
            if band >= 5 and band <= 105:
                tally += bandCoefValueDict[band][1]**2

        return math.sqrt(tally)

    # -------------------------------------------------------------------------
    # createOutputImages
    # -------------------------------------------------------------------------
    def _createOutputImages(self, algorithmName, outDir):

        outBaseName = \
            os.path.basename(self._chunker._imageFile.fileName()).split('_')[0]

        outName = os.path.join(outDir,
                               outBaseName +
                               '_' +
                               algorithmName.replace(' ', '-') +
                               '.tif')

        driver = gdal.GetDriverByName('GTiff')

        outDs = driver.Create(outName,
                              self.imageFile._getDataset().RasterXSize,
                              self.imageFile._getDataset().RasterYSize,
                              1,
                              gdalconst.GDT_Float32)

        outDs.SetProjection(self._chunker._imageFile._getDataset().\
                            GetProjection())
        
        outDs.SetGeoTransform(self.imageFile._getDataset().GetGeoTransform())

        # ---
        # Create the quality assurance (QA) layer.  At each pixel location:
        # 0: expect a computed output value
        # 1: expect a no-data value due to clouds
        # 2: expect a no-data value due to water
        # 3: expect a no-data value due to a no-data value in the input
        # ---
        qaName = os.path.join(outDir, algorithmName + '_qa.tif')

        qaName = os.path.join(outDir,
                              outBaseName +
                              '_' +
                              algorithmName.replace(' ', '-') +
                              '-qa.tif')

        qa = driver.Create(qaName,
                           self._chunker._imageFile._getDataset().RasterXSize,
                           self._chunker._imageFile._getDataset().RasterYSize,
                           1,
                           gdalconst.GDT_Int16)

        qa.SetProjection(self._chunker._imageFile._getDataset().GetProjection())
        
        qa.SetGeoTransform(self._chunker._imageFile._getDataset().\
                           GetGeoTransform())

        return outDs, qa

    # -------------------------------------------------------------------------
    # _createSpecFile
    # -------------------------------------------------------------------------
    def _createSpecFile(self, coefFile):

        asf = AvirisSpecFile()
        asf.setField(AvirisSpecFile.COEFS_FILE_KEY, coefFile)
        
        asf.setField(AvirisSpecFile.IMAGE_FILE_KEY, 
                     self._chunker._imageFile.fileName())

        asf.setField(AvirisSpecFile.MASK_VALUE_KEY,
                     ApplyAlgorithm.NO_DATA_VALUE)

        asf.setField(AvirisSpecFile.NO_DATA_KEY, ApplyAlgorithm.NO_DATA_VALUE)

        asf.setField(AvirisSpecFile.WATER_MASK_KEY,
                     ApplyAlgorithm.NO_DATA_VALUE)

        asf.setField(AvirisSpecFile.CLOUD_MASK_KEY, 'B10 > 0.8')
        asf.setField(AvirisSpecFile.WATER_MASK_KEY, 'B246 < 0.01')
        return asf

    # -------------------------------------------------------------------------
    # _isCloudMask
    # -------------------------------------------------------------------------
    def _isCloudMask(self, value):

        return value > 0.8

    # -------------------------------------------------------------------------
    # _isNoData
    # -------------------------------------------------------------------------
    def _isNoData(self, value):

        return value == ApplyAlgorithm.NO_DATA_VALUE

    # -------------------------------------------------------------------------
    # _isWaterMask
    # -------------------------------------------------------------------------
    def _isWaterMask(self, value):

        return value < 0.01

    # -------------------------------------------------------------------------
    # processRow
    # -------------------------------------------------------------------------
    def _processRow(self, loc, row, outDs, qa):
        
        for col in range(row.shape[0]):

            # Read the stack of pixels at this col, row location.
            # pixelStack = self._readStack(col, row)
            pixelStack = row[col]

            # Check for no-data in the first pixel of the stack.
            if self._isNoData(pixelStack[0]):

                hexValue = struct.pack('f', ApplyAlgorithm.NO_DATA_VALUE)
                outDs.WriteRaster(col, row, 1, 1, hexValue)
                qa.WriteRaster(col, row, 1, 1, ApplyAlgorithm.QA_NO_DATA)
                continue

            # ---
            # Associate the pixel values in the stack with the band
            # and coefficient information.
            # {bandNumber: (coefficient, pixel value)}
            # ---
            bandCoefValueDict = \
                self._associateValuesWithCoefs(pixelStack, algorithmName)

            # Apply masks.
            if self._isCloudMask(bandCoefValueDict[9][1]) or \
               self._isWaterMask(bandCoefValueDict[245][1]):

                hexValue = struct.pack('f', ApplyAlgorithm.NO_DATA_VALUE)
                outDs.WriteRaster(col, row, 1, 1, hexValue)

                if bandCoefValueDict[9][1] > 0.8:

                    qa.WriteRaster(col, row, 1, 1, ApplyAlgorithm.QA_CLOUD)

                else:
                    qa.WriteRaster(col, row, 1, 1, ApplyAlgorithm.QA_WATER)

                continue

            qa.WriteRaster(col, row, 1, 1, ApplyAlgorithm.QA_COMPUTED)

            # ---
            # Compute the square root of the sum of the squares of all band
            # reflectances between 397nm and 898nm.  Those reflectances
            # translate to bands 6 - 105.
            # ---
            if normalizePixels:
                divisor = self._computeDivisor(bandCoefValueDict)

            # Compute the result, normalizing pixel values as we go.
            p = 0.0

            for band in bandCoefValueDict.iterkeys():

                coefValue = bandCoefValueDict[band]
                coef = coefValue[0]

                if band == 0:

                    p = coef

                elif coef != 0:

                    if normalizePixels:

                        normalizedValue = coefValue[1] / divisor
                        p += coef * normalizedValue

                    else:
                        p += coef * coefValue[1]

            hexValue = struct.pack('f', p)
            outDs.WriteRaster(col, row, 1, 1, hexValue)
        
    # -------------------------------------------------------------------------
    # _readStack
    # -------------------------------------------------------------------------
    # def _readStack(self, col, row):
    #
    #     numpyPixels = self.imageFile._getDataset().ReadAsArray(col, row, 1, 1)
    #     pixelsAsFloats = [p[0][0] for p in numpyPixels]
    #
    #     return pixelsAsFloats

    # -------------------------------------------------------------------------
    # screen
    # -------------------------------------------------------------------------
    # def screen(self, pctThreshold=0.1):
    #
    #     rows = self._chunker._imageFile._getDataset().RasterYSize
    #     cols = self._chunker._imageFile._getDataset().RasterXSize
    #     numPixels = rows * cols
    #
    #     # ---
    #     # Count both the valid and invalid pixels and compare their number
    #     # against the threshold and its inverse, so this method can quit as
    #     # soon as possible.  For example, if the validity threshold is 90% and
    #     # the first 10% of the image contains invalid pixels, quit because the
    #     # invalidity threshold is met.  Otherwise, the validity threshold
    #     # would not be met until the entire image was scanned.
    #     # ---
    #     validityThreshold = numPixels * pctThreshold
    #     invalidityThreshold = numPixels - validityThreshold
    #     validPixels = 0
    #     invalidPixels = 0
    #
    #     for row in range(rows):
    #         for col in range(cols):
    #
    #             if row % 100 == 0 and col == 0:
    #                 print 'Row ' + str(row) + ' of ' + str(rows)
    #
    #             # ---
    #             # Every band will contain the no-data value, if the pixel
    #             # is designated "no data".  To eliminated a read operation,
    #             # read bands that will be used later to screen for masks.
    #             # ---
    #             bValues = self.imageFile._getDataset(). \
    #                 ReadRaster(col,
    #                            row,
    #                            1,
    #                            1,
    #                            None,
    #                            None,
    #                            gdalconst.GDT_Float32,
    #                            [9, 245])
    #
    #             b10Value = struct.unpack('f', bValues[0:4])[0]
    #             b246Value = struct.unpack('f', bValues[4:8])[0]
    #
    #             if self._isNoData(b10Value) or \
    #                self._isCloudMask(b10Value) or \
    #                self._isWaterMask(b246Value):
    #
    #                 invalidPixels += 1
    #
    #                 if invalidPixels >= invalidityThreshold:
    #
    #                     print 'The invalidity threshold, ' + \
    #                           str(invalidityThreshold) + \
    #                           ' is met.'
    #
    #                     return
    #
    #             else:
    #
    #                 validPixels += 1
    #
    #                 if validPixels >= validityThreshold:
    #
    #                     print 'The validity threshold, ' + \
    #                           str(validityThreshold) + \
    #                           ' is met.'
    #
    #                     return

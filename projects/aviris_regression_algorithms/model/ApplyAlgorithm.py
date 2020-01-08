# -*- coding: utf-8 -*-

import csv
import math
import os
import re
import struct

from osgeo import gdal
from osgeo import gdalconst

from model.BaseFile import BaseFile
from model.GeospatialImageFile import GeospatialImageFile


# -----------------------------------------------------------------------------
# class ApplyAlgorithm
#
# gdallocationinfo -b 10
#     projects/aviris_regression_algorithms/model/tests/clip.img 0 0
# -----------------------------------------------------------------------------
class ApplyAlgorithm(object):

    NO_DATA_VALUE = -9999.0
    QA_COMPUTED = '0'
    QA_CLOUD = '1'
    QA_WATER = '2'
    QA_NO_DATA = '3'

    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self, coefFile, avirisImage, outDir, logger=None):

        if not outDir:
            raise RuntimeError('An output directory must be provided.')

        if not os.path.exists(outDir) or not os.path.isdir(outDir):
            raise RuntimeError(str(outDir) + ' is not an existing directory.')

        self.logger = logger
        self.outDir = outDir
        self.coefFile = BaseFile(coefFile, '.csv')
        self.imageFile = GeospatialImageFile(avirisImage, None, None)
        self.coefs = []

        with open(self.coefFile.fileName()) as csvFile:

            reader = csv.DictReader(csvFile)

            for row in reader:
                self.coefs.append(row)

    # -------------------------------------------------------------------------
    # applyAlgorithm
    #
    # P = a0 + a1b1 + a2b2 …
    # -------------------------------------------------------------------------
    def applyAlgorithm(self, algorithmName):

        # Ensure the algorithm name is valid.
        if algorithmName not in self.coefs[0]:

            raise RuntimeError('Algorithm ' +
                               str(algorithmName) +
                               ' not in coeffient file, ' +
                               self.coefFile)

        # Create the output raster and QA image.
        outDs, qa = self._createOutputImages(algorithmName)
        
        # ---
        # Iterate through the raster, pixel by pixel.
        # ---
        for row in range(self.imageFile._getDataset().RasterYSize):
            for col in range(self.imageFile._getDataset().RasterXSize):

                # Read the stack of pixels at this col, row location.
                pixelStack = self._readStack(col, row)

                # Check for no-data in the first pixel of the stack.
                if pixelStack[0] == ApplyAlgorithm.NO_DATA_VALUE:

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
                if bandCoefValueDict[9][1] > 0.8 or \
                   bandCoefValueDict[245][1] < 0.01:

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
                divisor = self._computeDivisor(bandCoefValueDict)

                # Compute the result, normalizing pixel values as we go.
                p = 0.0

                for band in bandCoefValueDict.iterkeys():

                    coefValue = bandCoefValueDict[band]
                    coef = coefValue[0]
                    normalizedValue = coefValue[1] / divisor

                    if band == 0:

                        p = normalizedValue

                    else:

                        p += coef * normalizedValue

                hexValue = struct.pack('f', p)
                outDs.WriteRaster(col, row, 1, 1, hexValue)

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

            coef = float(coefRow[algorithmName])
            value = pixelStack[bandIndex-1] if bandIndex > 0 else 0.0
            bandCoefValueDict[bandIndex] = (coef, value)

        return bandCoefValueDict

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
    def _createOutputImages(self, algorithmName):
        
        outName = os.path.join(self.outDir, algorithmName + '.tif')
        driver = gdal.GetDriverByName('GTiff')

        outDs = driver.Create(outName,
                              self.imageFile._getDataset().RasterXSize,
                              self.imageFile._getDataset().RasterYSize,
                              1,
                              gdalconst.GDT_Float32)

        outDs.SetProjection(self.imageFile._getDataset().GetProjection())
        outDs.SetGeoTransform(self.imageFile._getDataset().GetGeoTransform())

        # ---
        # Create the quality assurance (QA) layer.  At each pixel location:
        # 0: expect a computed output value
        # 1: expect a no-data value due to clouds
        # 2: expect a no-data value due to water
        # 3: expect a no-data value due to a no-data value in the input
        # ---
        qaName = os.path.join(self.outDir, algorithmName + '_qa.tif')
        driver = gdal.GetDriverByName('GTiff')

        qa = driver.Create(outName,
                           self.imageFile._getDataset().RasterXSize,
                           self.imageFile._getDataset().RasterYSize)
        
        return outDs, qa
        
    # -------------------------------------------------------------------------
    # _readStack
    # -------------------------------------------------------------------------
    def _readStack(self, col, row):

        numpyPixels = self.imageFile._getDataset().ReadAsArray(col, row, 1, 1)
        pixelsAsFloats = [p[0][0] for p in numpyPixels]

        return pixelsAsFloats

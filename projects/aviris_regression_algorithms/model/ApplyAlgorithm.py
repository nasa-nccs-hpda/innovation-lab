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

        # Set up debugging.
        self.debugRow = None
        self.debugCol = None
        self.debugDict = None   # {'Band': [0, value]}

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

        # Create the output raster.
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

                    if self.debugRow == row and self.debugCol == col:
                        self.debugDict[0] = 'No data'

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

                    if self.debugRow == row and self.debugCol == col:

                        self.debugDict[0] = 'Mask'
                        self.debugDict[10] = bandCoefValueDict[9][1]
                        self.debugDict[246] = bandCoefValueDict[245][1]

                    continue

                # ---
                # Compute the square root of the sum of the squares of all band
                # reflectances between 397nm and 898nm.  Those reflectances
                # translate to bands 6 - 105.
                # ---
                divisor = self._computeDivisor(bandCoefValueDict)

                if debugKey:

                    for band in bandCoefValueDict.iterkeys():

                        value = bandCoefValueDict[band][1]
                        self._addDebugDictItem(band, debugKey, value)

                    if self.debugRow == row and self.debugCol == col:
                        self.debugDict['Divisor'] = divisor

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
        self._writeDebugDict()

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
    # debug
    # -------------------------------------------------------------------------
    def debug(self, row, col):

        if row < 0 or row >= self.imageFile._getDataset().RasterYSize:
            raise RuntimeError('Debug row value is not within the image.')

        if col < 0 or col >= self.imageFile._getDataset().RasterXSize:
            raise RuntimeError('Debug column value is not within the image.')

        self.debugRow = row
        self.debugCol = col
        self.debugDict = {}

    # -------------------------------------------------------------------------
    # _pixelStackToCsv
    # -------------------------------------------------------------------------
    def _pixelStackToCsv(self, key, pixelStack):

        band = -1

        for pixel in pixelStack:

            band += 1
            self.debugWriter.writerow({'Band': band, key: pixel})

        return writer

    # -------------------------------------------------------------------------
    # _readStack
    # -------------------------------------------------------------------------
    def _readStack(self, col, row):

        numpyPixels = self.imageFile._getDataset().ReadAsArray(col, row, 1, 1)
        pixelsAsFloats = [p[0][0] for p in numpyPixels]

        return pixelsAsFloats

    # -------------------------------------------------------------------------
    # _writeDebugDict
    # -------------------------------------------------------------------------
    def _writeDebugDict(self):

        fieldNames = ['Band', 'Value']

        outFile = \
            os.path.join(self.outDir,
                         os.path.basename(self.imageFile.fileName()) + '.csv')

        with open(outFile, 'w') as f:

            writer = csv.writer(f)

            for bandKey in self.debugDict:
                writer.writerow([bandKey, self.debugDict[bandKey]])

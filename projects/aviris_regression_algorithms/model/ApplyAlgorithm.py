# -*- coding: utf-8 -*-

import csv
import math
import os
import re
import struct

from osgeo import gdal

from model.BaseFile import BaseFile
from model.GeospatialImageFile import GeospatialImageFile


# -----------------------------------------------------------------------------
# class ApplyAlgorithm
#
# /att/pubrepo/ORNL/ABoVE_Archive/daac.ornl.gov/daacdata/above/ABoVE_Airborne_AVIRIS_NG/data/ang20170709t224839_rfl_v2p9/ang20170709t224839_corr_v2p9_img
# -----------------------------------------------------------------------------
class ApplyAlgorithm(object):

    DEBUG_START = (0, 0)  # Set to (-1, -1) to debug no pixels.
    DEBUG_END = (-1, -1)  # Set to (-1, -1) to debug all pixels from start.
    
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
                
        # ---
        # Set up debugging.
        #
        # Band      (Row, Col)  (Row, Col)
        # Band      Value       Value
        # ...
        # No Data   True    False
        # P         p           p
        # Hex       hex         hex
        # ---
        if ApplyAlgorithm.DEBUG_START[0] != -1 and \
            ApplyAlgorithm.DEBUG_END != -1:
            
            fieldNames = ['Band']
            
            for row in range(ApplyAlgorithm.DEBUG_START[0],
                             ApplyAlgorithm.DEBUG_END[0] + 1):
                for col in range(ApplyAlgorithm.DEBUG_END[1],
                                 ApplyAlgorithm.DEBUG_END[1] + 1):
                                 
                    fieldNames.append(self._makeRowColKey(row, col))
                                 
            outFile = \
                os.path.join(self.outDir, 
                             os.path.basename(self.imageFile.fileName()) + \
                                              '.csv')

            f = open(outFile, 'w')
            self.debugWriter = csv.DictWriter(f, fieldnames=fieldNames)
        
    # -------------------------------------------------------------------------
    # applyAlgorithm
    #
    # P = a0 + a1b1 + a2b2 …
    # -------------------------------------------------------------------------
    def applyAlgorithm(self, algorithmName):
        
        # Ensure the algorithm name is valid.
        if algorithmName not in self.coefs[0]:

            raise RuntimeError('Algorithm ' + \
                               str(algorithmName) + \
                               ' not in coeffient file, ' + \
                               self.coefFile)
           
        # Create the output raster.
        outName = os.path.join(self.outDir, algorithmName + '.tif')
        driver = gdal.GetDriverByName('GTiff')
        
        outDs = driver.Create(outName,
                              self.imageFile._getDataset().RasterXSize,
                              self.imageFile._getDataset().RasterYSize)

        outDs.SetProjection(self.imageFile._getDataset().GetProjection())
        outDs.SetGeoTransform(self.imageFile._getDataset().GetGeoTransform())
        
        # ---
        # Iterate through the raster, pixel by pixel.
        # ---
        for row in range(self.imageFile._getDataset().RasterYSize):
            for col in range(self.imageFile._getDataset().RasterXSize):

                # Read the stack of pixels at this col, row location.
                pixelStack = self._readStack(col, row)
                
                debugKey = self._makeRowColKey(row, col) \
                    if self._isDebugPixel(row, col) else None
                    
                if debugKey:
                    self._pixelStackToCsv(key, pixelStack)
                
                # Check for no-data in the first pixel of the stack.
                if pixelStack[0] == ApplyAlgorithm.NO_DATA_VALUE:

                    hexValue = struct.pack('f', ApplyAlgorithm.NO_DATA_VALUE)
                    outDs.WriteRaster(col, row, 1, 1, hexValue)

                    if debugKey:
                        self.debugWriter.writerow({'Band': 'No data'})
                        
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

                    if debugKey:
                        self.debugWriter.writerow({'Band': 'Mask'})
                        
                    continue

                # ---
                # Compute the square root of the sum of the squares of all band
                # reflectances between 397nm and 898nm.  Those reflectances 
                # translate to bands 6 - 105.
                # ---
                divisor = self._computeDivisor(bandCoefValueDict)
                
                if writer:
                    writer.writerow({'Band': 'divisor', 'Value': divisor})             
                        
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
                
                if writer:

                    writer.writerow({'Band': 'p', 'Value': p})
                    writer.writerow({'Band': 'hex', 'Value': hexValue})
                
        outDs = None
        
        if debugWriter:
            debugWriter = None
                
    # -------------------------------------------------------------------------
    # _associateValuesWithCoefs
    # -------------------------------------------------------------------------
    def _associateValuesWithCoefs(self, pixelStack, algorithmName):
        
        bandCoefValueDict = {}

        for coefRow in self.coefs:
            
            bandIndex = \
                int(re.search(r'\d{0,3}$', coefRow['Band Number']).group()) - 1

            coef = float(coefRow[algorithmName])
            value = pixelStack[bandIndex]
            bandCoefValueDict[bandIndex] = (coef, value)
            
        return bandCoefValueDict

    # -------------------------------------------------------------------------
    # _computeDivisor
    # -------------------------------------------------------------------------
    def _computeDivisor(self, bandCoefValueDict):
        
        tally = 0.0
        
        for band in bandCoefValueDict.iterkeys():
            
            if band > 5 and band < 106:
                        
                coefValue = bandCoefValueDict[band]
            
                if coefValue[0] != 0:
                    tally += coefValue[1]**2
                
        return math.sqrt(tally)
        
    # -------------------------------------------------------------------------
    # _isDebugPixel
    # -------------------------------------------------------------------------
    def _isDebugPixel(self, row, col):
        
        if self.debugWriter and \
            row >= ApplyAlgorithm.DEBUG_START[0] and \
            row <= ApplyAlgorithm.DEBUG_END[0] and \
            col >= ApplyAlgorithm.DEBUG_START[1] and \
            col <= ApplyAlgorithm.DEBUG_END[1]:
            
            return True
            
        return False
        
    # -------------------------------------------------------------------------
    # _makeRowColKey
    # -------------------------------------------------------------------------
    def _makeRowColKey(self, row, col):
        
        return '(' + str(row) + ', ' + str(col) + ')'
        
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
        

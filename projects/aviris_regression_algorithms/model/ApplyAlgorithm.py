# -*- coding: utf-8 -*-

import csv
import math
import os
import re
import struct

from osgeo import gdal

from model.BaseFile import BaseFile
from model.ImageFile import ImageFile


# -----------------------------------------------------------------------------
# class ApplyAlgorithm
#
# /att/pubrepo/ORNL/ABoVE_Archive/daac.ornl.gov/daacdata/above/ABoVE_Airborne_AVIRIS_NG/data/ang20170709t224839_rfl_v2p9/ang20170709t224839_corr_v2p9_img
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
        self.imageFile = ImageFile(avirisImage, None)
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

        # ---
        # Iterate through the raster, pixel by pixel.
        # ---
        for row in range(self.imageFile._getDataset().RasterYSize):
            for col in range(self.imageFile._getDataset().RasterXSize):

                # Read the stack of pixels at this col, row location.
                pixelStack = self.readStack(col, row)
                
                # Check for no-data in the first pixel of the stack.
                if pixelStack[0] == ApplyAlgorithm.NO_DATA_VALUE:

                    hexValue = struct.pack('f', ApplyAlgorithm.NO_DATA_VALUE)
                    outDs.WriteRaster(col, row, 1, 1, hexValue)
                    continue

                # ---
                # Associate the pixel values in the stack with the band
                # and coefficient information.  
                # {bandNumber: (coefficient, pixel value)}
                # ---
                bandCoefValueDict = \
                    self.associateValuesWithCoefs(pixelStack, algorithmName)
                
                # Apply masks.
                if bandCoefValueDict[9][1] > 0.8 or \
                    bandCoefValueDict[425][1] < 0.01:

                    hexValue = struct.pack('f', ApplyAlgorithm.NO_DATA_VALUE)
                    outDs.WriteRaster(col, row, 1, 1, hexValue)
                    continue

                # ---
                # Compute the square root of the sum of the squares of all band
                # reflectances between 397nm and 898nm.  Those reflectances 
                # translate to bands 6 - 105.
                # ---
                import pdb
                pdb.set_trace()
                divisor = self.computeDivisor(bandCoefValueDict)
                        
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
                
    # -------------------------------------------------------------------------
    # associateValuesWithCoefs
    # -------------------------------------------------------------------------
    def associateValuesWithCoefs(self, pixelStack, algorithmName):
        
        bandCoefValueDict = {}

        for coefRow in self.coefs:
            
            bandIndex = \
                int(re.search(r'\d{0,3}$', coefRow['Band Number']).group()) - 1

            coef = float(coefRow[algorithmName])
            value = pixelStack[bandIndex]
            bandCoefValueDict[bandIndex] = (coef, value)
            
        return bandCoefValueDict

    # -------------------------------------------------------------------------
    # computeDivisor
    # -------------------------------------------------------------------------
    def computeDivisor(self, bandCoefValueDict):
        
        tally = 0.0
        
        for band in bandCoefValueDict.iterkeys():
            
            if band > 5 and band < 106:
                        
                coefValue = bandCoefValueDict[band]
            
                if coefValue[1] != 0:
                    tally += coefValue[2]**2
                
        return math.sqrt(tally)
        
    # -------------------------------------------------------------------------
    # readStack
    # -------------------------------------------------------------------------
    def readStack(self, col, row):
        
        numpyPixels = self.imageFile._getDataset().ReadAsArray(col, row, 1, 1)
        pixelsAsFloats = [p[0][0] for p in numpyPixels]

        return pixelsAsFloats
        

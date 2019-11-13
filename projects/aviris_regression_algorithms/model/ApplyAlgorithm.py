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

                # ---
                # Test for masks and no-data values.
                # ---
                if self.isMaskedOrNoData(col, row): 
                    
                    hexValue = struct.pack('f', ApplyAlgorithm.NO_DATA_VALUE)
                    outDs.WriteRaster(col, row, 1, 1, hexValue)
                    next
                
                # ---
                # Read the stack of pixels at this col, row location.
                # ---
                pixelStack = self.readStack(col, row)
                
                # ---
                # Compute the square root of the sum of the squares of all band
                # reflectances between 397nm and 898nm.  Those reflectances 
                # translate to bands 6 - 105.
                # ---
                divisor = math.sqrt(sum([p**2 for p in pixelStack[6:105] \
                                              if pixelStack[p] != 0]))
                
                # # The first term is the y intercept.
                # P = float(self.coefs[0][algorithmName])
                #
                #
                #
                #
                # hexValue = struct.pack('f', P)
                # outDs.WriteRaster(col, row, 1, 1, hexValue)
                
        outDs.close()
                
    # -------------------------------------------------------------------------
    # isMaskedOrNoData
    # -------------------------------------------------------------------------
    def isMaskedOrNoData(self, col, row):
                
        # ---
        # Mask: band 10 > 0.8
        # Also check for a no-data value.  When found the output value is
        # no data.
        # ---
        bandValue = self.readOnePixelToFloat(col, row, 9)  
        
        if bandValue > 0.8 or bandValue == ApplyAlgorithm.NO_DATA_VALUE:
            return True

        # Mask: band 426 < 0.01
        bandValue = self.readOnePixelToFloat(col, row, 425)  
        if bandValue < 0.01: return True
        
        return False
        
    # -------------------------------------------------------------------------
    # readOnePixelToFloat
    # -------------------------------------------------------------------------
    def readOnePixelToFloat(self, col, row, band):
        
        pixelAsString = self. \
                        imageFile. \
                        _getDataset(). \
                        ReadRaster(col,
                                   row,
                                   1, # x read size
                                   1, # y read size
                                   1, # buf_xsize
                                   1, # buf_ysize
                                   None, # buf_type read from image
                                   [band])

        pixelAsFloat = struct.unpack('f', pixelAsString)[0]

        if self.logger:

            msg = '(band, value) = (' + \
                  str(band) + ', ' + \
                  str(pixelAsFloat) + ')'

            self.logger.info(msg)
            
        return pixelAsFloat
        
    # -------------------------------------------------------------------------
    # readStack
    # -------------------------------------------------------------------------
    def readStack(self, col, row):
        
        pixelsAsStrings = \
            self.imageFile._getDataset().ReadAsArray(col, row, 1, 1)
            
        pixelsAsFloats = [struct.unpack('f', p)[0] for p in pixelsAsStrings]

        return pixelsAsFloats
        
    # -------------------------------------------------------------------------
    # applyAlgorithm
    #
    # P = a0 + a1b1 + a2b2 …
    # -------------------------------------------------------------------------
    # def applyAlgorithmOrig(self, algorithmName):
    #
    #     # Ensure the algorithm name is valid.
    #     if algorithmName not in self.coefs[0]:
    #
    #         raise RuntimeError('Algorithm ' + \
    #                            str(algorithmName) + \
    #                            ' not in coeffient file, ' + \
    #                            self.coefFile)
    #
    #     # Create the output raster.
    #     outName = os.path.join(self.outDir, algorithmName + '.tif')
    #     driver = gdal.GetDriverByName('GTiff')
    #
    #     outDs = driver.Create(outName,
    #                           self.imageFile._getDataset().RasterXSize,
    #                           self.imageFile._getDataset().RasterYSize)
    #
    #     # ---
    #     # Remove the coefficients that are zero.  Only the bands for non-zero
    #     # terms will be extracted.
    #     # ---
    #     coefs = [coef for coef in self.coefs if coef[algorithmName] != 0]
    #
    #     # The first term is the y intercept.
    #     P = float(self.coefs[0][algorithmName])
    #
    #     # ---
    #     # Iterate through the raster, extracting the pixel for each non-zero
    #     # band, and computing the output pixel value.
    #     # ---
    #     for row in range(self.imageFile._getDataset().RasterYSize):
    #         for col in range(self.imageFile._getDataset().RasterXSize):
    #             for coefRow in coefs[1:]:
    #
    #                 coef = float(coefRow[algorithmName])
    #
    #                 if coef != 0:
    #
    #                     bandIndex = \
    #                         int(re.search(r'\d{0,3}$',
    #                                       coefRow['Band Number']).group())
    #
    #                     pixelStrValue = \
    #                         self. \
    #                         imageFile. \
    #                         _getDataset(). \
    #                         ReadRaster(col,
    #                                    row,
    #                                    1, # x read size
    #                                    1, # y read size
    #                                    1, # buf_xsize
    #                                    1, # buf_ysize
    #                                    None, # buf_type read from image
    #                                    [bandIndex])
    #
    #                     pixelValue = struct.unpack('f', pixelStrValue)[0]
    #
    #                     if pixelValue != ApplyAlgorithm.NO_DATA_VALUE:
    #                         P += pixelValue * coef
    #
    #                     if self.logger:
    #
    #                         msg = '(band, value, P) = (' + \
    #                               str(bandIndex) + ', ' + \
    #                               str(floatValue) + ', ' + \
    #                               str(P) + ')'
    #
    #                         self.logger.info(msg)
    #
    #             hexValue = struct.pack('f', P)
    #             outDs.WriteRaster(col, row, 1, 1, hexValue)
    #
    #     outDs.close()
    #

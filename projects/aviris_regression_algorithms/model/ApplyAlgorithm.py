# -*- coding: utf-8 -*-

import csv
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
        # Remove the coefficients that are zero.  Only the bands for non-zero
        # terms will be extracted.
        # ---
        coefs = [coef for coef in self.coefs if coef[algorithmName] != 0]

        # The first term is the y intercept.
        P = float(self.coefs[0][algorithmName])
        
        # ---
        # Iterate through the raster, extracting the pixel for each non-zero
        # band, and computing the output pixel value.
        # ---
        for row in range(self.imageFile._getDataset().RasterYSize):
            for col in range(self.imageFile._getDataset().RasterXSize):
                for coef in coefs[1:]:

                    bandIndex = int(re.search(r'\d{0,3}$', 
                                              coef['Band Number']).group())
                    
                    bandValue = self. \
                                imageFile. \
                                _getDataset(). \
                                ReadRaster(col,
                                           row,
                                           1, # x read size
                                           1, # y read size
                                           1, # buf_xsize
                                           1, # buf_ysize
                                           None, # buf_type read from image
                                           [bandIndex])
                                            
                    floatValue = struct.unpack('f', bandValue)[0]
                    
                    if floatValue != ApplyAlgorithm.NO_DATA_VALUE:
                        P += floatValue * float(coef[algorithmName])

                    msg = '(band, value, P) = (' + \
                          str(bandIndex) + ', ' + \
                          str(floatValue) + ', ' + \
                          str(P) + ')'
                    
                    if self.logger:
                        self.logger.info(msg)

                hexValue = struct.pack('f', P)
                outDs.WriteRaster(col, row, 1, 1, hexValue)
                
        outDs.close()
                

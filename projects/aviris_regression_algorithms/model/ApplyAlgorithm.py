# -*- coding: utf-8 -*-

import csv
import os

from osgeo import gdal

from model.BaseFile import BaseFile
from model.ImageFile import ImageFile


# -----------------------------------------------------------------------------
# class ApplyAlgorithm
#
# /att/pubrepo/ORNL/ABoVE_Archive/daac.ornl.gov/daacdata/above/ABoVE_Airborne_AVIRIS_NG/data/ang20170709t224839_rfl_v2p9/ang20170709t224839_corr_v2p9_img
# -----------------------------------------------------------------------------
class ApplyAlgorithm(object):

    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self, coefFile, avirisImage, outDir):
        
        if not outDir:
            raise RuntimeError('An output directory must be provided.')
            
        if not os.path.exists(outDir) or not os.path.isdir(outDir):
            raise RuntimeError(str(outDir) + ' is not an existing directory.')
            
        self.outDir = outDir
        self.coefFile = BaseFile(coefFile, '.csv')
        self.imageFile = ImageFile(avirisImage, None)
        self.coefs = []
        
        with open(self.coefFile.fileName()) as csvFile:
            
            reader = csv.DictReader(csvFile)
            
            for row in reader:
                self.coefs.append(row)

        # self.csvFd = open(self.coefFile.fileName())
        # self.coefs = csv.DictReader(self.csvFd)
        
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
        P = self.coefs[0][algorithmName]
        
        # ---
        # Iterate through the raster, extracting the pixel for each non-zero
        # band, and computing the output pixel value.
        # ---
        for row in range(self.imageFile._getDataset().RasterYSize):
            for col in range(self.imageFile._getDataset().RasterXSize):
                for coef in coefs[1:]:

                    bandName = 'Band ' + str(coef['Band Number'])
                    
                    # bandValue = self. \
                    #             imageFile. \
                    #             _getDataset(). \
                    #             ReadRaster(col,
                    #                        row,
                    #                        1,
                    #                        1,
                    #                        None, # buf_xsize
                    #                        None, # buf_ysize
                    #                        gdal.GDT_CFloat32, # buf_type
                    #                        [bandName])

                    self. \
                                imageFile. \
                                _getDataset(). \
                                ReadRaster(col,
                                           row,
                                           1,
                                           1,
                                           None, # buf_xsize
                                           None, # buf_ysize
                                           gdal.GDT_CFloat32)

                #     P += bandValue * coef[algorithm]
                #
                # outDs.WriteRaster(col, row, 1, 1, P)
                
        outDs.close()
                

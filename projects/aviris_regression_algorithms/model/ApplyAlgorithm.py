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
# The applyAlgorithm() is the method to use.  It sets up to run, then calls
# processRaster().  ProcessRaster() works its way through the entire raster,
# collects results and writes them to the output and quality-assurance images.
# This gives derived classes, like ApplyAlgorithmCelery, an opportunity to
# divide the image in other ways, rather than row by row.  Eventually, one row
# at a time is processed by processRow().
#
# gdallocationinfo -b 10 projects/aviris_regression_algorithms/model/tests/clip.img 0 0
#
# projects/aviris_regression_algorithms/view/AvirisCommandLineView.py -c /att/nobackup/rlgill/AVIRIS/PLSR_Coeff_NoVN_v2.csv -o /att/nobackup/rlgill/AVIRIS/test -a AVG-CHL -i /att/pubrepo/ABoVE/archived_data/ORNL/ABoVE_Airborne_AVIRIS_NG_CORRUPT/data/ang20180729t210144rfl/ang20180729t210144_rfl_v2r2/ang20180729t210144_corr_v2r2_img
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
        self._imagePath = avirisImage
        self.coefs = []

        coefFile = BaseFile(csvFile)

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

        self._processRaster(outDs, qa, algorithmName, normalizePixels)
        
        while True:
            
            loc, chunk = self._chunker.getChunk()

            if self._chunker.isComplete():
                break
                
            # Provide a hint of the progress.
            if curRow != loc[1] and loc[1] % 100 == 0:

                print('Row ' + str(loc[1]) + ' of ' + \
                    str(self._chunker._imageFile._getDataset().RasterYSize))

            curRow = loc[1]

            self._processRow(curRow, chunk, outDs, qa, algorithmName,
                             normalizePixels)

        outDs = None
        qa = None

    # -------------------------------------------------------------------------
    # _associateValuesWithCoefs
    # -------------------------------------------------------------------------
    @staticmethod
    def _associateValuesWithCoefs(pixelStack, algorithmName, coefs):

        bandCoefValueDict = {}

        for coefRow in coefs:

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
    # computeDivisor
    # -------------------------------------------------------------------------
    @staticmethod
    def computeDivisor(bandCoefValueDict):

        tally = 0.0

        for band in bandCoefValueDict.keys():
            if band >= 5 and band <= 105:
                tally += bandCoefValueDict[band][1]**2

        return math.sqrt(tally)

    # -------------------------------------------------------------------------
    # createOutputImages
    # -------------------------------------------------------------------------
    def _createOutputImages(self, algorithmName, outDir):

        outBaseName = \
            os.path.basename(self._imagePath).split('_')[0]

        outName = os.path.join(outDir,
                               outBaseName +
                               '_' +
                               algorithmName.replace(' ', '-') +
                               '.tif')

        driver = gdal.GetDriverByName('GTiff')

        imageFile = GeospatialImageFile(self._imagePath)
        
        outDs = \
            driver.Create(outName,
                          imageFile._getDataset().RasterXSize,
                          imageFile._getDataset().RasterYSize,
                          1,
                          gdalconst.GDT_Float32)

        outDs.SetProjection(imageFile._getDataset().GetProjection())
        outDs.SetGeoTransform(imageFile._getDataset().GetGeoTransform())

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
                           imageFile._getDataset().RasterXSize,
                           imageFile._getDataset().RasterYSize,
                           1,
                           gdalconst.GDT_Int16)

        qa.SetProjection(imageFile._getDataset().GetProjection())
        qa.SetGeoTransform(imageFile._getDataset().GetGeoTransform())

        return outDs, qa

    # -------------------------------------------------------------------------
    # _createSpecFile
    # -------------------------------------------------------------------------
    def _createSpecFile(self, coefFile):

        asf = AvirisSpecFile()
        asf.setField(AvirisSpecFile.COEFS_FILE_KEY, coefFile)
        
        asf.setField(AvirisSpecFile.IMAGE_FILE_KEY, 
                     self._imagePath)

        asf.setField(AvirisSpecFile.MASK_VALUE_KEY,
                     ApplyAlgorithm.NO_DATA_VALUE)

        asf.setField(AvirisSpecFile.NO_DATA_KEY, ApplyAlgorithm.NO_DATA_VALUE)

        asf.setField(AvirisSpecFile.WATER_MASK_KEY,
                     ApplyAlgorithm.NO_DATA_VALUE)

        asf.setField(AvirisSpecFile.CLOUD_MASK_KEY, 'B10 > 0.8')
        asf.setField(AvirisSpecFile.WATER_MASK_KEY, 'B246 < 0.01')
        return asf

    # -------------------------------------------------------------------------
    # isCloudMask
    # -------------------------------------------------------------------------
    @staticmethod
    def isCloudMask(value):

        return value > 0.8

    # -------------------------------------------------------------------------
    # isNoData
    # -------------------------------------------------------------------------
    @staticmethod
    def isNoData(value):

        return value == ApplyAlgorithm.NO_DATA_VALUE

    # -------------------------------------------------------------------------
    # isWaterMask
    # -------------------------------------------------------------------------
    @staticmethod
    def isWaterMask(value):

        return value < 0.01

    # -------------------------------------------------------------------------
    # processRaster
    # -------------------------------------------------------------------------
    def _processRaster(self, outDs, qa, algorithmName, normalizePixels):
        
        # ---
        # Set up a chunker to move through the image by row.  This makes no
        # difference for the single-thread version of this class, but the 
        # Celery version will create a task from each row.
        # ---
        chunker = Chunker(self._imagePath)
        chunker.setChunkAsRow()
        curRow = -1
        
        while True:
            
            loc, chunk = chunker.getChunk()

            if chunker.isComplete():
                break
                
            # Provide a hint of the progress.
            if curRow != loc[1] and loc[1] % 100 == 0:

                print ('Row ', loc[1], ' of ',
                       chunker._imageFile._getDataset().RasterYSize)

            curRow = loc[1]

            outArray, qaArray = \
                self._processRow(chunk, algorithmName, normalizePixels,
                                 self.coefs)
            
            xSize = len(outArray)
            
            if xSize != chunker._imageFile._getDataset().RasterXSize:
                
                raise RuntimeError('Less than a full row returned from ' + \
                                   'processRow().')
                                   
            hexArray = b''
            
            for num in outArray:
                hexArray += struct.pack('f', num)
                
            outDs.WriteRaster(0, curRow, xSize, 1, hexArray)

    # -------------------------------------------------------------------------
    # processRow
    # -------------------------------------------------------------------------
    @staticmethod
    def _processRow(rowArray, algorithmName, normalizePixels, coefs):

        outArray = []
        qaArray = b''
        
        for col in range(rowArray.shape[0]):
            
            # Read the stack of pixels at this col, row location.
            pixelStack = rowArray[col][0]

            # Check for no-data in the first pixel of the stack.
            if ApplyAlgorithm.isNoData(pixelStack[0]):

                # hexValue = struct.pack('f', ApplyAlgorithm.NO_DATA_VALUE)
                # outArray += hexValue
                outArray.append(ApplyAlgorithm.NO_DATA_VALUE)
                qaArray += ApplyAlgorithm.QA_NO_DATA
                continue

            # ---
            # Associate the pixel values in the stack with the band
            # and coefficient information.
            # {bandNumber: (coefficient, pixel value)}
            # ---
            bandCoefValueDict = \
                ApplyAlgorithm._associateValuesWithCoefs(pixelStack,
                                                         algorithmName,
                                                         coefs)

            # Apply masks.
            if ApplyAlgorithm.isCloudMask(bandCoefValueDict[9][1]) or \
               ApplyAlgorithm.isWaterMask(bandCoefValueDict[245][1]):

                # hexValue = struct.pack('f', ApplyAlgorithm.NO_DATA_VALUE)
                # outArray += hexValue
                outArray.append(ApplyAlgorithm.NO_DATA_VALUE)

                if bandCoefValueDict[9][1] > 0.8:

                    qaArray += ApplyAlgorithm.QA_CLOUD

                else:
                    qaArray += ApplyAlgorithm.QA_WATER

                continue

            qaArray += ApplyAlgorithm.QA_COMPUTED

            # ---
            # Compute the square root of the sum of the squares of all band
            # reflectances between 397nm and 898nm.  Those reflectances
            # translate to bands 6 - 105.
            # ---
            if normalizePixels:
                divisor = ApplyAlgorithm._computeDivisor(bandCoefValueDict)

            # Compute the result, normalizing pixel values as we go.
            p = 0.0

            for band in bandCoefValueDict.keys():

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

            # hexValue = struct.pack('f', p)
            # outArray += hexValue
            outArray.append(p)

        return outArray, qaArray
        
    # -------------------------------------------------------------------------
    # screen
    # -------------------------------------------------------------------------
    def screen(self, pctThreshold=0.1):

        chunker = Chunker(self._imagePath)
        chunker.setChunkAsRow()
        rows = chunker._imageFile._getDataset().RasterYSize
        cols = chunker._imageFile._getDataset().RasterXSize
        numPixels = rows * cols

        # ---
        # Count both the valid and invalid pixels and compare their number
        # against the threshold and its inverse, so this method can quit as
        # soon as possible.  For example, if the validity threshold is 90% and
        # the first 10% of the image contains invalid pixels, quit because the
        # invalidity threshold is met.  Otherwise, the validity threshold
        # would not be met until the entire image was scanned.
        # ---
        validityThreshold = numPixels * pctThreshold
        invalidityThreshold = numPixels - validityThreshold
        validPixels = 0
        invalidPixels = 0

        for row in range(rows):
            for col in range(cols):

                if row % 100 == 0 and col == 0:
                    print ('Row ', row, ' of ', rows)

                # ---
                # Every band will contain the no-data value, if the pixel
                # is designated "no data".  To eliminated a read operation,
                # read bands that will be used later to screen for masks.
                # ---
                bValues = chunker._imageFile._getDataset(). \
                    ReadRaster(col,
                               row,
                               1,
                               1,
                               None,
                               None,
                               gdalconst.GDT_Float32,
                               [9, 245])

                b10Value = struct.unpack('f', bValues[0:4])[0]
                b246Value = struct.unpack('f', bValues[4:8])[0]

                if ApplyAlgorithm.isNoData(b10Value) or \
                   ApplyAlgorithm.isCloudMask(b10Value) or \
                   ApplyAlgorithm.isWaterMask(b246Value):

                    invalidPixels += 1

                    if invalidPixels >= invalidityThreshold:

                        print('The invalidity threshold, ',
                              invalidityThreshold,
                              ' is met.')

                        return

                else:

                    if validPixels == 0:
                        
                        print ('First valid pixel is at row ',
                               row,
                               ', column ',
                               col,
                               '.')
                              
                    validPixels += 1

                    if validPixels >= validityThreshold:

                        print ('The validity threshold, ',
                               validityThreshold,
                               ', is met.')

                        return

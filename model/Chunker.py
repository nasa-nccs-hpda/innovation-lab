#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import numpy as np

from osgeo import gdal_array
from osgeo import gdalconst

from model.ImageFile import ImageFile


# -----------------------------------------------------------------------------
# class Chunker
#
# This works on GDAL image files, so GDAL can perform the partial reads from
# the raster.  The alternative would be to read an entire image into an array.
# While this would allow a Chunker to be created from a chunk of another 
# Chunker, it is probably not worth the memory consumption.
# -----------------------------------------------------------------------------
class Chunker(object):

    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self, _imageFileName):

        self._imageFile = ImageFile(_imageFileName)
        self._xSize = None
        self._ySize = None
        self._curChunkLoc = (0, 0)
        self._complete = False

        # ---
        # The data type is for building a buffer into which chunks are read.
        # Refer to the comment in getChunk() about a GDAL buf.  This code
        # is from gdal_array.BandReadAsArray, where the error occurs.
        # ---
        dataType = \
            self._imageFile._getDataset().GetRasterBand(1).DataType
            
        typeCode = gdal_array.GDALTypeCodeToNumericTypeCode(dataType)
        dataType = gdal_array.NumericTypeCodeToGDALTypeCode(typeCode)
        
        if not typeCode:
            
            dataType = gdalconst.GDT_Float32
            typeCode = np.float32

        else:
            dataType = gdal_array.NumericTypeCodeToGDALTypeCode(typeCode)

        if dataType == gdalconst.GDT_Byte and \
            self._imageFile._getDataset().\
                GetMetadataItem('PIXELTYPE', 'IMAGE_STRUCTURE') == \
             'SIGNEDBYTE':
             
            typecode = np.int8
            
        self._dataType = typeCode
        
    # -------------------------------------------------------------------------
    # getChunk
    # -------------------------------------------------------------------------
    def getChunk(self):

        if self._complete:
            return (None, None)
            
        if not self._xSize:
            raise RuntimeError('The chunk x size must be set.')
            
        if not self._ySize:
            raise RuntimeError('The chunk y size must be set.')
            
        xStart = self._curChunkLoc[0]
        yStart = self._curChunkLoc[1]
        xLen = self._xSize
        yLen = self._ySize
        next_xStart = xStart + xLen
        next_yStart = yStart
        xExceeded = False
        yExceeded = False

        # X dimension exceeded?
        if xStart + xLen > self._imageFile._getDataset().RasterXSize:

            # Limit the read in the X dimension.
            xLen = self._imageFile._getDataset().RasterXSize - xStart

            # Move to next chunk row.
            next_xStart = 0
            next_yStart = yStart + self._ySize
            
            # When X and Y are exceeded, chunking is complete.
            xExceeded = True

        # Y dimension exceeded?  Must be the last row of the image.
        if yStart + yLen > self._imageFile._getDataset().RasterYSize:

            # Limit the read in the Y dimension.
            yLen = self._imageFile._getDataset().RasterYSize - yStart

            # Last row, so Y start stays the same.
            next_yStart = yStart
            
            # When X and Y are exceeded, chunking is complete.
            yExceeded = True

        # ---
        # Read chunk as a two-dimensional Numpy array.  Deep in the GDAL code,
        # where the final call is made, the X and Y length arguments of the 
        # output buffer are backwards.  This causes the rectangle of return
        # pixels to have incorrect dimensions.  To work around this, create the
        # output buffer here.
        # ---
        buf = np.empty([xLen, yLen], dtype=self._dataType)
        
        chunk = self._imageFile._getDataset().ReadAsArray(xStart,
                                                          yStart,
                                                          xLen,
                                                          yLen,
                                                          buf)

        # Set position of next chunk.
        self._curChunkLoc = (next_xStart, next_yStart)
        
        # When X and Y are exceeded, chunking is complete.
        if xExceeded and yExceeded:
            self._complete = True
                                          
        return ((xStart, yStart), chunk)
        
    # -------------------------------------------------------------------------
    # setChunkAsColumn
    # -------------------------------------------------------------------------
    def setChunkAsColumn(self):
        
        self.setChunkSize(1, self._imageFile._getDataset().RasterYSize)
        
    # -------------------------------------------------------------------------
    # setChunkAsRow
    # -------------------------------------------------------------------------
    def setChunkAsRow(self):
        
        self.setChunkSize(self._imageFile._getDataset().RasterXSize, 1)
        
    # -------------------------------------------------------------------------
    # setChunkSize
    # -------------------------------------------------------------------------
    def setChunkSize(self, _xSize, _ySize):
        
        if _xSize < 1:
            raise RuntimeError('The sample size of a chunk must be greater ' +
                               'than zero.')
                               
        if _xSize > self._imageFile._getDataset().RasterXSize:
            
            raise RuntimeError('Sample size, ' + 
                               str(_xSize) +
                               ', must be less than or equal to the image ' +
                               'sample size, ' +
                               str(self._imageFile._getDataset().RasterXSize))
                               
        if _ySize < 1:
            raise RuntimeError('The line size of a chunk must be greater ' +
                               'than zero.')                               
                               
        if _ySize > self._imageFile._getDataset().RasterYSize:
            
            raise RuntimeError('Line size, ' + 
                               str(_ySize) +
                               ', must be less than or equal to the image ' +
                               'line size, ' +
                               str(self._imageFile._getDataset().RasterYSize))
                               
        self._xSize = _xSize
        self._ySize = _ySize
        
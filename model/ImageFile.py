#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from osgeo import gdal
from osgeo import gdalconst

from model.BaseFile import BaseFile


# -----------------------------------------------------------------------------
# class ImageFile
#
# This class represents our single image format, NetCDF.
# -----------------------------------------------------------------------------
class ImageFile(BaseFile):

    EXTENSIONS = ['.nc', '.tif']

    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self, pathToFile):

        # Initialize the base class.
        super(ImageFile, self).__init__(pathToFile, ImageFile.EXTENSIONS)

        self._dataset = None

    # -------------------------------------------------------------------------
    # _getDataset
    # -------------------------------------------------------------------------
    def _getDataset(self):

        if not self._dataset:

            self._dataset = gdal.Open(self._filePath, gdalconst.GA_ReadOnly)

            if not self._dataset:
                raise RuntimeError('Unable to read ' + self._filePath + '.')

        return self._dataset

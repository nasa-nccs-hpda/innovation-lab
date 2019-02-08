#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from model.ImageFile import ImageFile


# -----------------------------------------------------------------------------
# class GeoTiffImageFile
# -----------------------------------------------------------------------------
class GeoTiffImageFile(ImageFile):

    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self, pathToFile):

        # Initialize the base class.
        super(GeoTiffImageFile, self).__init__(pathToFile, '.tif')

#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os

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
        super(GeoTiffImageFile, self).__init__(pathToFile)

        if os.path.splitext(pathToFile)[1].lower() != '.tif':

            raise RuntimeError(str(pathToFile) +
                               ' is not in GeoTiff image format.')

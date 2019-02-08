# -*- coding: utf-8 -*-

from model.ImageFile import ImageFile


# -----------------------------------------------------------------------------
# class NC_File
# -----------------------------------------------------------------------------
class NC_File(ImageFile):

    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self, pathToFile):

        # Initialize the base class.
        super(NC_File, self).__init__(pathToFile, '.nc')

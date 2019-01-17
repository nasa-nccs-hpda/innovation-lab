# -*- coding: utf-8 -*-

import os

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
        super(NC_File, self).__init__(pathToFile)

        if os.path.splitext(pathToFile)[1].lower() != '.nc':
            raise RuntimeError(str(pathToFile) + ' is not in Net CDF format.')

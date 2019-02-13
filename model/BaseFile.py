# -*- coding: utf-8 -*-

import os


# -----------------------------------------------------------------------------
# class BaseFile
# -----------------------------------------------------------------------------
class BaseFile(object):

    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self, pathToFile, expectedExtension=None):

        if not pathToFile:
            raise RuntimeError('A fully-qualified path to a file must be \
                               specified.')

        if not os.path.exists(pathToFile):
            raise RuntimeError(str(pathToFile) + ' does not exist.')

        if expectedExtension and \
           os.path.splitext(pathToFile)[1].lower() != expectedExtension:

            raise RuntimeError(str(pathToFile) +
                               ' is not in ' +
                               str(expectedExtension) +
                               ' format.')

        self._filePath = pathToFile


    # -------------------------------------------------------------------------
    # fileName
    # -------------------------------------------------------------------------
    def fileName(self):
        return self._filePath
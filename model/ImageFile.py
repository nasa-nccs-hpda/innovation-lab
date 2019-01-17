#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from abc import ABCMeta
import shutil
import tempfile

from model.BaseFile import BaseFile
from model.Envelope import Envelope
from model.SystemCommand import SystemCommand


# -----------------------------------------------------------------------------
# class ImageFile
#
# We currently have one common image class, NC_File.  In case we use others,
# image references can use this base Image class.  As new image classes are
# derived from this, references will not need to be changed.
# -----------------------------------------------------------------------------
class ImageFile(BaseFile):

    __metaclass__ = ABCMeta

    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self, pathToFile):

        # Initialize the base class.
        super(ImageFile, self).__init__(pathToFile)

    # -------------------------------------------------------------------------
    # clip
    # -------------------------------------------------------------------------
    def clip(self, envelope):

        if not isinstance(envelope, Envelope):
            raise RuntimeError('The first parameter must be an Envelope.')

        outFile = tempfile.mkstemp()[1]

        cmd = ('gdalwarp -te' +
               ' ' + str(envelope.ulx()) +
               ' ' + str(envelope.lry()) +
               ' ' + str(envelope.lrx()) +
               ' ' + str(envelope.uly()) +
               ' ' + self._filePath +
               ' ' + outFile)

        SystemCommand(cmd, None, True)

        shutil.move(outFile, self._filePath)

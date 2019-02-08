#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from abc import ABCMeta
import math
import shutil
import tempfile

from osgeo import gdal
from osgeo import gdalconst
from osgeo.osr import SpatialReference

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
    def __init__(self, pathToFile, expectedExtension=None):

        # Initialize the base class.
        super(ImageFile, self).__init__(pathToFile, expectedExtension)
        self._dataset = None

    # -------------------------------------------------------------------------
    # clipReprojectResample
    #
    # These three operations, clipping, reprojection and resampling can be
    # combined into a single GDAL call.  This must be more efficient than
    # invoking them individually.
    #
    # ScaleTuple is of the form (xScale, yScale).
    #
    # OutputFormat is the GDAL image format name, which defaults to GeoTiff.
    # See https://gdal.org/formats_list.html.
    # -------------------------------------------------------------------------
    def clipReprojectResample(self, envelope=None, outputSRS=None,
                              scaleTuple=None):

        # At least one operation must be configured.
        if not envelope and not outputSRS and not scaleTuple:

            raise RuntimeError('A clip envelope, output SRS or ' +
                               'scale tuple must be specified.')

        # ---
        # Configure the base command.  Specify the output format.  Otherwise,
        # gdalwarp automatically converts to GeoTiff.
        # ---
        cmd = 'gdalwarp -of ' + self.getFormatName()

        # Clip?
        if envelope:

            if not isinstance(envelope, Envelope):
                raise TypeError('The first parameter must be an Envelope.')

            cmd += (' -te' +
                    ' ' + str(envelope.ulx()) +
                    ' ' + str(envelope.lry()) +
                    ' ' + str(envelope.lrx()) +
                    ' ' + str(envelope.uly()) +
                    ' -te_srs' +
                    ' "' + envelope.srs().ExportToProj4() + '"')

        # Reproject?
        if outputSRS:
            cmd += ' -t_srs "' + outputSRS.ExportToProj4() + '"'

        # Resample?
        if scaleTuple:
            cmd += ' -tr ' + str(scaleTuple[0]) + ' ' + str(scaleTuple[1])

        # Finish the command.
        outFile = tempfile.mkstemp()[1]
        cmd += ' ' + self._filePath + ' ' + outFile
        SystemCommand(cmd, None, True)
        shutil.move(outFile, self._filePath)

    # -------------------------------------------------------------------------
    # _getDataset
    # -------------------------------------------------------------------------
    def _getDataset(self):

        if not self._dataset:

            self._dataset = gdal.Open(self._filePath, gdalconst.GA_ReadOnly)

            if not self._dataset:
                raise RuntimeError('Unable to read ' + self._filePath + '.')

        return self._dataset

    # -------------------------------------------------------------------------
    # getFormatName
    # -------------------------------------------------------------------------
    def getFormatName(self):

        ds = self._getDataset()
        return ds.GetDriver().ShortName

    # -------------------------------------------------------------------------
    # getSquareScale
    #
    # Some ASCII image variants cannot represent pixel size in two dimensions.
    # When an ASCII image with rectangular pixels is represented with a
    # single-dimension variant, it introduces a ground shift.  This method
    # returns a single value suitable for resampling the pixels to be square.
    # The image must be resampled using this value.
    # -------------------------------------------------------------------------
    def getSquareScale(self):

        xScale = self.scale()[0]
        yScale = self.scale()[1]

        if math.fabs(xScale) > math.fabs(yScale):
            return xScale * -1  # xScale is bigger, so increase yScale

        return yScale * -1

    # -------------------------------------------------------------------------
    # scale
    # -------------------------------------------------------------------------
    def scale(self):

        xform = self._getDataset().GetGeoTransform()
        return xform[1], xform[5]

    # -------------------------------------------------------------------------
    # srs
    # -------------------------------------------------------------------------
    def srs(self):

        outSrs = SpatialReference()
        outSrs.ImportFromWkt(self._getDataset().GetProjection())
        return outSrs

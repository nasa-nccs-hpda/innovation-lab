#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import math
import shutil
import tempfile

from model.Envelope import Envelope
from model.ImageFile import ImageFile
from model.SystemCommand import SystemCommand


# -----------------------------------------------------------------------------
# class GeospatialImageFile
# -----------------------------------------------------------------------------
class GeospatialImageFile(ImageFile):

    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self, pathToFile, spatialReference):

        # Initialize the base class.
        super(GeospatialImageFile, self).__init__(pathToFile)

        if spatialReference.Validate() != 0:

            raise RuntimeError('Spatial reference for ' +
                               pathToFile,
                               ' is invalid.')

        self._srs = spatialReference

        self._BASE_GDAL_CMD = 'gdalwarp ' + \
                              ' -of netCDF' + \
                              ' -s_srs "' + self.srs().ExportToProj4() + '"'

    # -------------------------------------------------------------------------
    # clipReproject
    #
    # These  operations, clipping and reprojection can be combined into a
    # single GDAL call.  This must be more efficient than invoking them
    # individually.
    # -------------------------------------------------------------------------
    def clipReproject(self, envelope=None, outputSRS=None):

        # At least one operation must be configured.
        if not envelope and not outputSRS:

            raise RuntimeError('Clip envelope or output SRS must be ' +
                               'specified.')

        # ---
        # Configure the base command.  Specify the output format.  Otherwise,
        # gdalwarp automatically converts to GeoTiff.
        # ---
        cmd = self._BASE_GDAL_CMD

        # Clip?
        if envelope:

            if not isinstance(envelope, Envelope):
                raise TypeError('The first parameter must be an Envelope.')

            if not self.envelope().Intersection(envelope):

                raise RuntimeError('The clip envelope does not intersect ' +
                                   'the image.')

            cmd += (' -te' +
                    ' ' + str(envelope.ulx()) +
                    ' ' + str(envelope.lry()) +
                    ' ' + str(envelope.lrx()) +
                    ' ' + str(envelope.uly()) +
                    ' -te_srs' +
                    ' "' + envelope.GetSpatialReference().ExportToProj4() +
                    '"')

        # Reproject?
        if outputSRS and not self.srs().IsSame(outputSRS):

            cmd += ' -t_srs "' + outputSRS.ExportToProj4() + '"'
            self._srs = outputSRS

        # Finish the command.
        outFile = tempfile.mkstemp()[1]
        cmd += ' ' + self._filePath + ' ' + outFile
        SystemCommand(cmd, None, True)
        shutil.move(outFile, self._filePath)

        # Update the dataset.
        self._getDataset()

    # -------------------------------------------------------------------------
    # envelope
    # -------------------------------------------------------------------------
    def envelope(self):

        dataset = self._getDataset()
        xform = dataset.GetGeoTransform()
        xScale = xform[1]
        yScale = xform[5]
        width = dataset.RasterXSize
        height = dataset.RasterYSize
        ulx = xform[0]
        uly = xform[3]
        lrx = ulx + width * xScale
        lry = uly + height * yScale

        envelope = Envelope()
        envelope.addPoint(ulx, uly, 0, self.srs())
        envelope.addPoint(lrx, lry, 0, self.srs())

        return envelope

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
            return math.fabs(xScale * -1)  # xScale bigger, so increase yScale

        return math.fabs(yScale * -1)

    # -------------------------------------------------------------------------
    # resample
    # -------------------------------------------------------------------------
    def resample(self, xScale, yScale):

        cmd = self._BASE_GDAL_CMD + ' -tr ' + str(xScale) + ' ' + \
              str(yScale)

        # Finish the command.
        outFile = tempfile.mkstemp(suffix='.nc')[1]
        cmd += ' ' + self._filePath + ' ' + outFile
        SystemCommand(cmd, None, True)
        shutil.move(outFile, self._filePath)

        # Update the dataset.
        self._getDataset()

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

        return self._srs

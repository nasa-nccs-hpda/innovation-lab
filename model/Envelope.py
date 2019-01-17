#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from osgeo import ogr
from osgeo.osr import SpatialReference


# -----------------------------------------------------------------------------
# class Envelope
# -----------------------------------------------------------------------------
class Envelope(object):

    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self):

        self._envelope = None
        self._points = []
        self._srs = None

    # -------------------------------------------------------------------------
    # addPoint
    #
    # NOTE:  The underlying GDAL OGR Geometry class is unable to detect invalid
    # ordinates.  For example, it is possible to set a latitude to 91.  As
    # these values are relative to a point's SRS, it is difficult to check each
    # case.  A Point class would help, but could lead to extensive wrapping of
    # GDAL, which we should avoid--or at least strongly resist.
    # -------------------------------------------------------------------------
    def addPoint(self, x, y, z, epsg):

        ogrPt = ogr.Geometry(ogr.wkbPoint)
        srs = SpatialReference()
        srs.ImportFromEPSG(epsg)
        ogrPt.AssignSpatialReference(srs)

        # ---
        # The next line causes the GetGeometryType() to become -2147483647,
        # although GetGeometryName() remains 'POINT'.
        # ---
        ogrPt.AddPoint(x, y, z)

        self.addOgrPoint(ogrPt)

    # -------------------------------------------------------------------------
    # addOgrPoint
    # -------------------------------------------------------------------------
    def addOgrPoint(self, ogrPoint):

        # GetGeometryType() is sometimes corrupt, so check it's name, too.
        if ogrPoint.GetGeometryType() != ogr.wkbPoint and \
           ogrPoint.GetGeometryName() != 'POINT':

            raise RuntimeError('Added points must be of type wkbPoint.')

        if not self._srs:
            self._srs = ogrPoint.GetSpatialReference().Clone()

        if not ogrPoint.GetSpatialReference().IsSame(self._srs):

            raise RuntimeError('Added points must be in the SRS: ' +
                               str(self._srs.ExportToPrettyWkt()))

        self._points.append(ogrPoint)
        self._computeEnvelope()

    # -------------------------------------------------------------------------
    # _computeEnvelope
    # -------------------------------------------------------------------------
    def _computeEnvelope(self):

        self._envelope = None

        multipoint = ogr.Geometry(ogr.wkbMultiPoint)
        multipoint.AssignSpatialReference(self._srs)

        for point in self._points:
            multipoint.AddGeometry(point)

        self._envelope = multipoint.GetEnvelope()

    # -------------------------------------------------------------------------
    # equals
    # -------------------------------------------------------------------------
    def equals(self, otherEnvelope):

        return self._envelope == otherEnvelope._envelope

    # -------------------------------------------------------------------------
    # _getOrdinate
    # -------------------------------------------------------------------------
    def _getOrdinate(self, index):

        if not self._envelope:
            raise RuntimeError('Envelope was not computed.')

        if index < 0 or index > 3:
            raise RuntimeError('Index must be between 0 and 3.')

        return self._envelope[index]

    # -------------------------------------------------------------------------
    # lrx
    # -------------------------------------------------------------------------
    def lrx(self):

        return self._getOrdinate(1)

    # -------------------------------------------------------------------------
    # lry
    # -------------------------------------------------------------------------
    def lry(self):

        return self._getOrdinate(2)

    # -------------------------------------------------------------------------
    # ulx
    # -------------------------------------------------------------------------
    def ulx(self):

        return self._getOrdinate(0)

    # -------------------------------------------------------------------------
    # uly
    # -------------------------------------------------------------------------
    def uly(self):

        return self._getOrdinate(3)

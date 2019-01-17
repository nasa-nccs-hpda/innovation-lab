# -*- coding: utf-8 -*-

import csv
import os

from osgeo import ogr
from osgeo.osr import SpatialReference

from model.BaseFile import BaseFile
from model.Envelope import Envelope


# -----------------------------------------------------------------------------
# class ObservationFile
#
# x, y, z, integer EPSG code, boolean presence or absence
#
# TIP: This class uses minimal abstractions.  The purest implementation would
# include an Observation class, a class representing a collection of
# observations with methods like envelope, and some sort of serialization
# class.  For now, keep it simple.  More decomposition might be helpful later,
# especially if we need to add or remove observations.  Things like the
# envelope and disk file would need to be updated.
#
# TIP: This class uses a Point abstraction implemented with GDAL.
# -----------------------------------------------------------------------------
class ObservationFile(BaseFile):

    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self, pathToFile):

        # Initialize the base class.
        super(ObservationFile, self).__init__(pathToFile)

        if os.path.splitext(pathToFile)[1].lower() != '.csv':
            raise RuntimeError(str(pathToFile) + ' is not in CSV format.')

        # ---
        # Parse the observations.
        # [(point, presence/absence), (point, presence/absence)]
        # ---
        self._crs = None
        self._envelope = Envelope()
        self._observations = []

        with open(self._filePath) as csvFile:

            fdReader = csv.reader(csvFile, delimiter=',')

            # x, y, z, integer EPSG code, boolean presence or absence
            for row in fdReader:

                # Skip header row, if detected.
                try:
                    float(row[0])

                except ValueError:
                    continue

                rowCrs = SpatialReference()
                rowCrs.ImportFromEPSG(int(row[3]))

                if not self._crs:
                    self._crs = rowCrs

                if not self._crs.IsSame(rowCrs):

                    raise RuntimeError('Observations must all be in the ' +
                                       'same CRS.')

                ogrPt = ogr.Geometry(ogr.wkbPoint)
                ogrPt.AddPoint(float(row[0]), float(row[1]), float(row[2]))
                ogrPt.AssignSpatialReference(self._crs)
                self._observations.append((ogrPt, bool(int(row[4]))))
                self._envelope.addOgrPoint(ogrPt)

    # -------------------------------------------------------------------------
    # crs
    # -------------------------------------------------------------------------
    def crs(self):

        return self._crs

    # -------------------------------------------------------------------------
    # envelope
    # -------------------------------------------------------------------------
    def envelope(self):

        return self._envelope

    # -------------------------------------------------------------------------
    # numObservations
    # -------------------------------------------------------------------------
    def numObservations(self):

        return len(self._observations)

    # -------------------------------------------------------------------------
    # observation
    # -------------------------------------------------------------------------
    def observation(self, index):

        if index >= self.numObservations():
            raise IndexError

        return self._observations[index]

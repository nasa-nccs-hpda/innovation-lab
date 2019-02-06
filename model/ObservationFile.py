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
    def __init__(self, pathToFile, species):

        if not species:
            raise RuntimeError('A species must be specified.')

        # Initialize the base class.
        super(ObservationFile, self).__init__(pathToFile)

        if os.path.splitext(pathToFile)[1].lower() != '.csv':
            raise RuntimeError(str(pathToFile) + ' is not in CSV format.')

        self._species = species

        # ---
        # Parse the observations.
        # [(point, presence/absence), (point, presence/absence)]
        # ---
        self._srs = None
        self._envelope = Envelope()
        self._observations = []

        with open(self._filePath) as csvFile:

            fdReader = csv.reader(csvFile, delimiter=',')
            epsgColumn = None
            obsColumn = None
            zColumn = None

            # x, y, z, integer EPSG code, boolean presence or absence
            for row in fdReader:

                # ---
                # If the first element is a float, there is no header row.  If
                # there is a header row, determine which column, if any
                # contains "Z" values or EPSG codes.  If the column header
                # begins with "epsg:", the code comes after the colon, not in
                # each row.  These things inform the parsing of rows.
                # ---
                try:
                    float(row[0])

                except ValueError:

                    for i in range(len(row)):

                        if row[i].lower() == 'z':
                            zColumn = i

                        elif 'epsg:' in row[i].lower():

                            self._srs = SpatialReference()

                            self._srs. \
                                ImportFromEPSG(int(row[i].split(':')[1]))

                        elif row[i].lower() == 'epsg':
                            epsgColumn = i

                        elif row[i] == 'pres/abs':
                            obsColumn = i

                    # ---
                    # We must know the file SRS or the column in which to find
                    # an EPSG code.
                    # ---
                    if not self._srs and not epsgColumn:

                        raise RuntimeError('An EPSG code or column was ' +
                                           'not identified in the header.')

                    continue

                # ---
                # If the EPSG code is specified in every column, ensure it is
                # the same for every row.  If self._srs has yet to be created,
                # create it.
                # ---
                if epsgColumn:

                    rowSrs = SpatialReference()
                    rowSrs.ImportFromEPSG(int(row[epsgColumn]))

                    if not self._srs:

                        self._srs = SpatialReference()
                        self._srs.ImportFromEPSG(int(row[epsgColumn]))

                    if not self._srs.IsSame(rowSrs):

                        raise RuntimeError('Observations must all be in ' +
                                           'the same SRS.')

                # Parse a row.
                z = float(row[zColumn]) if zColumn else 0
                ogrPt = ogr.Geometry(ogr.wkbPoint)
                ogrPt.AddPoint(float(row[0]), float(row[1]), z)
                ogrPt.AssignSpatialReference(self._srs)
                self._envelope.addOgrPoint(ogrPt)

                obs = int(row[obsColumn]) if obsColumn else 1
                self._observations.append((ogrPt, obs))

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

    # -------------------------------------------------------------------------
    # species
    # -------------------------------------------------------------------------
    def species(self):

        return self._species

    # -------------------------------------------------------------------------
    # srs
    # -------------------------------------------------------------------------
    def srs(self):

        return self._srs

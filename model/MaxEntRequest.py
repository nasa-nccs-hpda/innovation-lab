#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import csv
import fileinput
import os
import shutil

from model.ImageFile import ImageFile
from model.ObservationFile import ObservationFile
from model.SystemCommand import SystemCommand


# -----------------------------------------------------------------------------
# class MaxEntRequest
# -----------------------------------------------------------------------------
class MaxEntRequest(object):

    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self, observationFilePath, species, listOfImages,
                 outputDirectory):

        if not species:
            raise RuntimeError('A species must be specified.')

        if not os.path.exists(outputDirectory):

            raise RuntimeError('Output directory, ' +
                               str(outputDirectory) +
                               ' does not exist.')

        self._images = listOfImages
        self._outputDirectory = outputDirectory
        self._species = species

        self._observationFile = ObservationFile(observationFilePath,
                                                self._species)

    # -------------------------------------------------------------------------
    # _fixNaNs
    # -------------------------------------------------------------------------
    def _fixNaNs(self, ascFile, noData=-9999.0):

        for line in fileinput.FileInput(ascFile, inplace=1):

            line = line.replace('nan', str(noData))
            print line,

    # -------------------------------------------------------------------------
    # _formatObservations
    # -------------------------------------------------------------------------
    def _formatObservations(self):

        path, name = os.path.split(self._observationFile.fileName())
        samplesFile = os.path.join(self._outputDirectory, name)
        firstRow = True

        fdReader = csv.reader(open(self._observationFile.fileName()),
                              delimiter=',')

        for row in fdReader:

            if firstRow:

                firstRow = False
                meWriter = csv.writer(open(samplesFile, 'w'), delimiter=',')
                meWriter.writerow(['species', 'x', 'y'])

            else:

                meWriter.writerow([self._species, row[0], row[1]])

        return samplesFile

    # -------------------------------------------------------------------------
    # run
    # -------------------------------------------------------------------------
    def run(self):

        # ---
        # Clip the images to the AoI of the observations, resample the images
        # to the SRS of the observations, and resample the pixels so that they
        # are square.  The ASCII image format the maxent.jar uses represents
        # pixel in one dimension.  Unless the pixels are square, the results
        # will be shifted on the ground.  Once this is complete, convert the
        # input images to ASCII Grid format.  Also, replace NaNs with a float
        # and copy the ASC to a working directory.
        # ---
        obsEnvelope = self._observationFile.envelope()
        ascDir = os.path.join(self._outputDirectory, 'asc')

        try:
            os.mkdir(ascDir)

        except OSError:

            # Do not complain, if the directory exists.
            pass

        for image in self._images:

            # ---
            # First, to preserve the original files, copy the input file to the
            # output directory.
            # ---
            baseName = os.path.basename(image)
            copyPath = os.path.join(ascDir, baseName)
            print 'Processing ' + copyPath
            shutil.copy(image, copyPath)
            imageCopy = ImageFile(copyPath)
            squareScale = imageCopy.getSquareScale()

            imageCopy.clipReprojectResample(obsEnvelope,
                                            self._observationFile.srs(),
                                            (squareScale, squareScale))

            # Convert to ASCII Grid.
            nameNoExtension = os.path.splitext(baseName)[0]
            ascImagePath = os.path.join(ascDir, nameNoExtension + '.asc')

            cmd = 'gdal_translate -ot Float32 -of AAIGrid -a_nodata -9999.0' +\
                  ' "' + imageCopy.fileName() + '"' + \
                  ' "' + ascImagePath + '"'

            SystemCommand(cmd, None, True)
            self._fixNaNs(ascImagePath)

        # Reformat the observations for MaxEnt.
        speciesFile = self._formatObservations()

        # Invoke maxent.jar.
        maxentJar = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                 'libraries',
                                 'maxent.jar')

        baseCmd = 'java -Xmx1024m -jar ' + \
                  maxentJar + \
                  ' visible=false autorun -P -J writeplotdata ' + \
                  '"applythresholdrule=Equal training sensitivity and ' + \
                  'specificity" removeduplicates=false '

        cmd = baseCmd + \
            '-s "' + speciesFile + '" ' + \
            '-e "' + ascDir + '" ' + \
            '-o "' + self._outputDirectory + '"'

        SystemCommand(cmd, None, True)

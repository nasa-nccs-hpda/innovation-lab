#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import csv
import fileinput
import os
import shutil
import sys

from model.GeospatialImageFile import GeospatialImageFile
from model.ObservationFile import ObservationFile
from model.SystemCommand import SystemCommand


# -----------------------------------------------------------------------------
# class MaxEntRequest
# -----------------------------------------------------------------------------
class MaxEntRequest(object):

    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self, observationFile, listOfImages, outputDirectory):

        if not os.path.exists(outputDirectory):

            raise RuntimeError('Output directory, ' +
                               str(outputDirectory) +
                               ' does not exist.')

        # Ensure all the images are in the same SRS.
        self._images = listOfImages
        self._imageSRS = self._images[0].srs()
        
        for image in self._images:
            
            if not self._imageSRS.IsSame(image.srs()):
                
                raise RuntimeError('Image ' + \
                                   image.fileName() + \
                                   ' is not in the same SRS as the others.')

        self._imagesToProcess = self._images
        self._outputDirectory = outputDirectory

        self._observationFile = observationFile
        self._observationFile.transformTo(self._imageSRS)
        self._maxEntSpeciesFile = self._formatObservations()

        # Create a directory for the ASC files.
        self._ascDir = os.path.join(self._outputDirectory, 'asc')

        try:
            os.mkdir(self._ascDir)

        except OSError:

            # Do not complain, if the directory exists.
            pass

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

        meWriter = csv.writer(open(samplesFile, 'w'), delimiter=',')
        meWriter.writerow(['species', 'x', 'y'])

        for i in range(self._observationFile.numObservations()):

            obs = self._observationFile.observation(i)

            # Skip absence points.
            if obs[1] > 0:

                speciesNoBlank = self._observationFile. \
                                 species(). \
                                 replace(' ', '_')

                meWriter.writerow([speciesNoBlank,
                                   obs[0].GetX(),
                                   obs[0].GetY()])

        return samplesFile

    # -------------------------------------------------------------------------
    # prepareNextImage
    # -------------------------------------------------------------------------
    def prepareNextImage(self):

        # ---
        # Clip the images to the AoI of the observations, resample the images
        # to the SRS of the observations, and resample the pixels so that they
        # are square.  The ASCII image format the maxent.jar uses represents
        # pixel in one dimension.  Unless the pixels are square, the results
        # will be shifted on the ground.  Once this is complete, convert the
        # input images to ASCII Grid format.  Also, replace NaNs with a float
        # and copy the ASC to a working directory.
        # ---
        try:
            image = self._imagesToProcess.pop()

        except IndexError:
            return 0

        # ---
        # First, to preserve the original files, copy the input file to the
        # output directory.
        # ---
        baseName = os.path.basename(image.fileName())
        copyPath = os.path.join(self._ascDir, baseName)
        print 'Processing ' + copyPath
        shutil.copy(image.fileName(), copyPath)
        imageCopy = GeospatialImageFile(copyPath, self._imageSRS)
        imageCopy.clipReproject(self._observationFile.envelope())

        squareScale = imageCopy.getSquareScale()
        imageCopy.resample(squareScale, squareScale)

        # Convert to ASCII Grid.
        nameNoExtension = os.path.splitext(baseName)[0]
        ascImagePath = os.path.join(self._ascDir, nameNoExtension + '.asc')

        cmd = 'gdal_translate -ot Float32 -of AAIGrid -a_nodata -9999.0' +\
              ' "' + imageCopy.fileName() + '"' + \
              ' "' + ascImagePath + '"'

        SystemCommand(cmd, None, True)
        self._fixNaNs(ascImagePath)

        return len(self._imagesToProcess)

    # -------------------------------------------------------------------------
    # run
    # -------------------------------------------------------------------------
    def run(self):

        imagesLeft = sys.maxint

        while imagesLeft > 0:

            imagesLeft = self.prepareNextImage()
            print str(imagesLeft) + ' images remaining to process.'

        self.runMaxEntJar()

    # -------------------------------------------------------------------------
    # runMaxEntJar
    # -------------------------------------------------------------------------
    def runMaxEntJar(self):

        print 'Running MaxEnt.'

        # Invoke maxent.jar.
        MAX_ENT_JAR = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                   'libraries',
                                   'maxent.jar')

        baseCmd = 'java -Xmx1024m -jar ' + \
                  MAX_ENT_JAR + \
                  ' visible=false autorun -P -J writeplotdata ' + \
                  '"applythresholdrule=Equal training sensitivity and ' + \
                  'specificity" removeduplicates=false '

        cmd = baseCmd + \
            '-s "' + self._maxEntSpeciesFile + '" ' + \
            '-e "' + self._ascDir + '" ' + \
            '-o "' + self._outputDirectory + '"'

        SystemCommand(cmd, None, True)

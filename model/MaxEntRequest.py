#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import csv
import fileinput
import os
import shutil
import sys

from model.GeospatialImageFile import GeospatialImageFile
from model.SystemCommand import SystemCommand


# -----------------------------------------------------------------------------
# class MaxEntRequest
# -----------------------------------------------------------------------------
class MaxEntRequest(object):

    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self, observationFile, listOfImages, outputDirectory, maxEntPath):

        if not os.path.exists(outputDirectory):

            raise RuntimeError('Output directory, ' +
                               str(outputDirectory) +
                               ' does not exist.')

        # Ensure all the images are in the same SRS.
        self._images = listOfImages
        self._imageSRS = self._images[0].srs()

        for image in self._images:

            if not self._imageSRS.IsSame(image.srs()):

                raise RuntimeError('Image ' +
                                   image.fileName() +
                                   ' is not in the same SRS as the others.')

        self._imagesToProcess = self._images
        self._outputDirectory = outputDirectory

        self._observationFile = observationFile
        self._observationFile.transformTo(self._imageSRS)
        self._maxEntSpeciesFile = self._formatObservations()
        self._maxEntPath = maxEntPath

        # Create a directory for the ASC files.
        self._ascDir = os.path.join(self._outputDirectory, 'asc')

        try:
            os.mkdir(self._ascDir)

        except OSError:

            # Do not complain, if the directory exists.
            pass

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
    #
    # This method is used to prepare all images in this request.
    # -------------------------------------------------------------------------
    def prepareNextImage(self):

        try:
            image = self._imagesToProcess.pop()

            self.prepareImage(image,
                              self._imageSRS,
                              self._observationFile.envelope(),
                              self._ascDir)

        except IndexError:
            return 0

        return len(self._imagesToProcess)

    # -------------------------------------------------------------------------
    # prepareImage
    #
    # This method prepares one image for use with maxent.jar.  Clients can use
    # this to control the preparation of a batch of images outside a single
    # MaxEntRequest.  MmxRequest will use this to prepare all images once,
    # instead of preparing a new set for each trial.
    # -------------------------------------------------------------------------
    @staticmethod
    def prepareImage(image, srs, envelope, ascDir):

        # ---
        # First, to preserve the original files, copy the input file to the
        # output directory.
        # ---
        baseName = os.path.basename(image.fileName())
        copyPath = os.path.join(ascDir, baseName)
        print ('Processing ' + copyPath)
        shutil.copy(image.fileName(), copyPath)
        imageCopy = GeospatialImageFile(copyPath, srs)
        imageCopy.clipReproject(envelope)

        squareScale = imageCopy.getSquareScale()
        imageCopy.resample(squareScale, squareScale)

        # Convert to ASCII Grid.
        nameNoExtension = os.path.splitext(baseName)[0]
        ascImagePath = os.path.join(ascDir, nameNoExtension + '.asc')

        cmd = 'gdal_translate -ot Float32 -of AAIGrid -a_nodata -9999.0' +\
              ' "' + imageCopy.fileName() + '"' + \
              ' "' + ascImagePath + '"'

        SystemCommand(cmd, None, True)

        # Fix NaNs.
        for line in fileinput.FileInput(ascImagePath, inplace=1):

            line = line.replace('nan', '-9999')
            line = line.replace('-inf', '-9999')
            sys.stdout.write(line)

        return ascImagePath

    # -------------------------------------------------------------------------
    # run
    # -------------------------------------------------------------------------
    def run(self):

        imagesLeft = sys.maxsize
        while imagesLeft > 0:

            imagesLeft = self.prepareNextImage()
            print (str(imagesLeft) + ' images remaining to process.')

        self.runMaxEntJar()

    # -------------------------------------------------------------------------
    # runMaxEntJar
    # -------------------------------------------------------------------------
    def runMaxEntJar(self):

        print ('Running MaxEnt.')
        # Invoke maxent.jar.
        MAX_ENT_JAR = self._maxEntPath
        if self._maxEntPath == "":
            MAX_ENT_JAR = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                       'libraries',
                                       'maxent.jar')

        if not os.path.exists(MAX_ENT_JAR):
            raise RuntimeError('Maximim Entropy path, ' +
                               str(MAX_ENT_JAR) +
                               ' does not exist.')
        JAVA = os.path.join(os.getenv('JAVA_HOME', default=''), 'java')

        baseCmd = JAVA + ' -Xmx1024m -jar ' + \
                  MAX_ENT_JAR + \
                  ' visible=false autorun -P -J writeplotdata ' + \
                  '"applythresholdrule=Equal training sensitivity and ' + \
                  'specificity" removeduplicates=false '

        cmd = baseCmd + \
            '-s "' + self._maxEntSpeciesFile + '" ' + \
            '-e "' + self._ascDir + '" ' + \
            '-o "' + self._outputDirectory + '"'

        SystemCommand(cmd, None, True)

    # -------------------------------------------------------------------------
    # Print Model Picture
    # -------------------------------------------------------------------------
    def printModelPic(self, directory, file):

        MAX_ENT_JAR = self._maxEntPath

        GRID_FILE = os.path.join(directory,
                                 file)

        JAVA = os.path.join(os.getenv('JAVA_HOME', default=''), 'java')

        cmd = JAVA + ' -Xmx1024m -cp ' + \
                  MAX_ENT_JAR + \
                 ' density.Show ' + \
                 GRID_FILE + \
                 ' -o'
        SystemCommand(cmd, None, True)
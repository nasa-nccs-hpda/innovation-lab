#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from osgeo.osr import SpatialReference

from celery import group

from CeleryConfiguration import app
from model.MaxEntRequest import MaxEntRequest


# -----------------------------------------------------------------------------
# class MaxEntRequestCelery
# -----------------------------------------------------------------------------
class MaxEntRequestCelery(MaxEntRequest):

    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self, observationFile, listOfImages, outputDirectory):

        # Initialize the base class.
        super(MaxEntRequestCelery, self).__init__(observationFile,
                                                  listOfImages,
                                                  outputDirectory)

    # -------------------------------------------------------------------------
    # prepareImage
    #
    # See MaxEntRequest.prepareImage's comments.
    #
    # This method is distributed using Celery, which requires serialized
    # arguments.  The Innovation Lab serialized with Python's Pickle.  The
    # IL classes representing imageFile and envelope arguments were
    # modified for Pickle serialization.  The ascDir argument, a string, is
    # serialized natively by Pickle.  The SRS argument is neither natively
    # serializable or available for us to add serialization; therefore,
    # it is passed in proj4 form, a string.
    # -------------------------------------------------------------------------
    @staticmethod
    @app.task(serializer='pickle')
    def prepareImage(imageFile, srsProj4, envelope, ascDir):

        srs = SpatialReference()
        srs.ImportFromProj4(srsProj4)

        MaxEntRequest.prepareImage(imageFile, srs, envelope, ascDir)

    # -------------------------------------------------------------------------
    # prepareImages
    # -------------------------------------------------------------------------
    def prepareImages(self):

        wpi = group(MaxEntRequestCelery.prepareImage.s(
                                    image,
                                    self._imageSRS.ExportToProj4(),
                                    self._observationFile.envelope(),
                                    self._ascDir) for image in self._images)

        result = wpi.apply_async()
        result.get()    # Waits for wpi to finish.

        return result

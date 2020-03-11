#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import glob
import os
import shutil
import warnings

from osgeo.osr import SpatialReference

import pandas
from pandas.tseries.offsets import MonthEnd

from GeospatialImageFile import GeospatialImageFile


# -----------------------------------------------------------------------------
# class MerraRequest
#
# MERRA description:  https://gmao.gsfc.nasa.gov/pubs/docs/Bosilovich785.pdf
# -----------------------------------------------------------------------------
class MerraRequest(object):

    BASE_DIR = '/att/pubrepo/ILAB/data/MERRA2/'

    # ---
    # Collection attributes should be in their own class structure.  While
    # collections are few, keep it simple, as represented here.  Without
    # a class structure in which to encode the collections, frequencies,
    # date ranges and operations, invalid queries will fail in real time,
    # rather than being detected early.
    # ---
    COLLECTIONS = ['m2t1nxflx', 'm2t1nxslv']
    OPERATIONS = ['avg', 'max', 'min', 'sum']
    MONTHLY = 'monthly'
    WEEKLY = 'weekly'
    FREQUENCY = [MONTHLY, WEEKLY]

    # -------------------------------------------------------------------------
    # _adjustFrequency
    # -------------------------------------------------------------------------
    @staticmethod
    def _adjustFrequency(dateRange, frequency):

        if frequency not in MerraRequest.FREQUENCY:

            raise RuntimeError('Frequency, ' +
                               str(frequency) +
                               ', is invalid.')
        # ---
        # Reduce the input date range frequency from days to the specified
        # frequency.
        # ['2000-08-02', '2000-08-03', ...] becomes
        # ['2000-08-31', '2000-09-30', ...]
        #
        # When converting to months, Pandas will exclude the final month
        # unless the date is the last day of the month.  Round the end date
        # to be the last day of the month.
        # ---
        endDate = dateRange[-1] + MonthEnd(0)

        pandasFreq = {MerraRequest.MONTHLY: 'M', MerraRequest.WEEKLY: 'W'}

        adjustedRange = pandas.date_range(dateRange[0],
                                          endDate,
                                          None,
                                          pandasFreq[frequency])

        # ---
        # The query in which these dates are involved expresses dates as
        # yyyy_freq## (2008_week05, 1994_month03).  Reformat the date_range
        # to match the query format.
        # ---
        reformattedRange = []
        fileFreq = {MerraRequest.MONTHLY: 'month', MerraRequest.WEEKLY: 'week'}

        for d in adjustedRange:

            freq = d.week if frequency == MerraRequest.WEEKLY else d.month

            reformattedRange.append(str(d.year) +
                                    '_' +
                                    fileFreq[frequency] +
                                    str(freq).zfill(2))

        return reformattedRange

    # -------------------------------------------------------------------------
    # clip
    # -------------------------------------------------------------------------
    @staticmethod
    def _clip(files, envelope, outDir):

        srs = SpatialReference()
        srs.ImportFromEPSG(4326)
        clippedFiles = []

        for f in files:

            outFile = os.path.join(outDir, os.path.basename(f))
            shutil.copyfile(f, outFile)
            geoFile = GeospatialImageFile(outFile, srs)
            geoFile.clipReproject(envelope, srs)
            clippedFiles.append(outFile)

        return clippedFiles

    # -------------------------------------------------------------------------
    # query
    # -------------------------------------------------------------------------
    @staticmethod
    def queryFiles(dateRange, frequency, collections, operations):

        # ---
        # Images of different frequencies are stored in separate
        # subdirectories.  Set the correct subdirectory.
        # ---
        subdirs = {MerraRequest.MONTHLY: 'Monthly',
                   MerraRequest.WEEKLY: 'Weekly'}

        queryPath = os.path.join(MerraRequest.BASE_DIR + subdirs[frequency])

        # ---
        # There is a file for each frequency step in the date range, like
        # ...month02..., ...month03..., ...month04.... A date range object
        # has a default frequency of daily and is in a different format than
        # that of our MERRA file names.  Express the date range in the format
        # and frequency of our MERRA file names.
        # ---
        adjDateRange = MerraRequest._adjustFrequency(dateRange, frequency)

        # ---
        # Find the files.  We could use glob and build a regular expression to
        # return all the dates, variables and operations in one glob.  Instead,
        # find each file individually.  We must detect any missing files.
        # Finding files individually helps with this, and it is easier to read.
        # Using one glob, we would still need to loop through the results to
        # detect missing files.
        # ---
        existingFiles = []
        missingFiles = []

        for coll in collections:

            if coll not in MerraRequest.COLLECTIONS:
                raise RuntimeError('Invalid collection: ' + str(coll))

            for op in operations:

                if op not in MerraRequest.OPERATIONS:
                    raise RuntimeError('Invalid operation: ' + str(op))

                for date in adjDateRange:

                    fileName = os.path.join(queryPath,
                                            coll +
                                            '_' +
                                            op +
                                            '_' +
                                            date +
                                            '.nc')

                    if os.path.exists(fileName):

                        existingFiles.append(fileName)

                    else:
                        missingFiles.append(fileName)

        return existingFiles, missingFiles

    # -------------------------------------------------------------------------
    # run
    # -------------------------------------------------------------------------
    @staticmethod
    def run(envelope, dateRange, frequency, collections, operations,
            outDir):

        # Validate the input.
        MerraRequest._validateInput(outDir)

        # Get the raw files.
        results, missingFiles = \
            MerraRequest.queryFiles(dateRange, frequency, collections,
                                    operations)

        if not results:
            raise RuntimeError('No MERRA files satisfy the request.')

        if missingFiles:

            warnings.warn('The request parameters encompass the following ' +
                          'files; however, they do not exist.\n' +
                          str(missingFiles))

        # Extract the variables and clip.
        clippedFiles = MerraRequest._clip(results, envelope, outDir)

        return clippedFiles

    # -------------------------------------------------------------------------
    # _validateInput
    # -------------------------------------------------------------------------
    @staticmethod
    def _validateInput(outDir):

        # Validate outdir.
        if not os.path.exists(outDir):

            raise RuntimeError('Output directory' +
                               str(outDir) +
                               ' does not exist.')

        if not os.path.isdir(outDir):

            raise RuntimeError('Output directory' +
                               str(outDir) +
                               ' must be a directory.')

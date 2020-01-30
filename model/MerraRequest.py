#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import glob
import os

from osgeo.osr import SpatialReference

import pandas
from pandas.tseries.offsets import MonthEnd


# -----------------------------------------------------------------------------
# class MerraRequest
#
# MERRA description:  https://gmao.gsfc.nasa.gov/pubs/docs/Bosilovich785.pdf
#
# A request for a single month can return multiple files: one from each suite.
# - collection obe, variable only, maintain internal table of collections and 
# variables
# - Single geotiff output
# - New file name scheme indicating that it is a derivative, 
#   like MERRA_SUBSET_YYYY_MM.
# -----------------------------------------------------------------------------
class MerraRequest(object):
    
    BASE_DIR = '/att/pubrepo/ILAB/data/MERRA2/Monthly/M2TMNXSLV.5.12.4'
    MERRA_SRS = 'EPSG:4326'
    OPERATION = ENUM('Operation', ['average', 'max', 'min', 'sum'])
    
    # -------------------------------------------------------------------------
    # extractVariables
    # -------------------------------------------------------------------------
    @staticmethod
    def extractVariables(files, variables, envelope):
        
        merraSRS = SpatialReference()
        merraSRS.ImportFromEPSG(MerraRequest.MERRA_SRS)
        envelope.TransformTo(merraSRS)
        
        cmd = 'gdal_translate ' 
        
        pass
        
    # -------------------------------------------------------------------------
    # query
    # -------------------------------------------------------------------------
    @staticmethod
    def queryFiles(dateRange, variables):

        # ---
        # Reduce the input date range frequency from days to months.
        # ['2000-08-02', '2000-08-03', ...] becomes
        # ['2000-08-31', '2000-09-30', ...]
        #
        # When converting to months, Pandas will exclude the final month
        # unless the date is the last day of the month.  Round the end date
        # to be the last day of the month.
        # ---
        endDate = dateRange[-1] + MonthEnd(0)        
        monthlyRange = pandas.date_range(dateRange[0], endDate, None, 'M')
        
        # ---
        # Glob for each month in the requested range by building regular
        # expressions for the year, month, collection, variable and operation.
        # One level below the base directory is a set of annual directories.
        # ---
        files = []
        
        for oneDate in monthlyRange:
            
            yearStr = str(oneDate.year)
            
            globStr = '*' + \
                      collection + \
                      '.' + \
                      yearStr + \
                      str(oneDate.month).zfill(2) + \
                      '*'
            
            globStr = os.path.join(MerraRequest.BASE_DIR, yearStr, globStr)
            globFiles = glob.glob(globStr)
            
            if globFiles:
                files += globFiles
            
        return files
            
    # -------------------------------------------------------------------------
    # run
    # -------------------------------------------------------------------------
    @staticmethod
    def run(self, envelope, dateRange, variables, operation, outDir):
         
        # Validate the input.
        MerraRequest._validateInput(outDir)        

        # Get the raw files.
        files = MerraRequest.queryFiles(dateRange, variables)

        # Extract the variables and clip.
        MerraRequest.extractVariables(files, variables)
        
    # -------------------------------------------------------------------------
    # _validateInput
    # -------------------------------------------------------------------------
    @staticmethod
    def _validateInput(self, outDir):
        
        # Validate outdir.
        if not os.path.exists(outDir):
            
            raise RuntimeError('Output directory' + 
                               str(outDir) + 
                               ' does not exist.')
                               
        if not os.path.isdir(outDir):
            
            raise RuntimeError('Output directory' + 
                               str(outDir) + 
                               ' must be a directory.')
            
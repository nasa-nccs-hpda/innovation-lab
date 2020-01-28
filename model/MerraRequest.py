#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import glob
import os

import pandas


# -----------------------------------------------------------------------------
# class MerraRequest
#
# MERRA description:  https://gmao.gsfc.nasa.gov/pubs/docs/Bosilovich785.pdf
# -----------------------------------------------------------------------------
class MerraRequest(object):
    
    BASE_DIR = '/att/pubrepo/ILAB/data/MERRA2/Monthly/M2TMNXSLV.5.12.4'
    EPSG = 'EPSG:4326'

    # -------------------------------------------------------------------------
    # extractVariables
    # -------------------------------------------------------------------------
    @staticmethod
    def extractVariables(files, variables):
        
        pass
        
    # -------------------------------------------------------------------------
    # query
    # -------------------------------------------------------------------------
    @staticmethod
    def queryFiles(dateRange, collection):

        # ---
        # Reduce the input date range frequency from days to months.
        # ['2000-08-02', '2000-08-03', ...] becomes
        # ['2000-08-31', '2000-09-30', ...]
        # ---
        monthlyRange = \
            pandas.date_range(dateRange[0], dateRange[-1], None, 'M')
        
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
                      str(oneDate.month) + \
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
    def run(self, envelope, dateRange, collection, variables, operation, 
            outDir):
                 
        # Get the raw files.
        files = MerraRequest.queryFiles(dateRange, collection)

        # Extract the variables.
        MerraRequest.extractVariables(files, variables)
        
        # Perform the operation.
        

#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os


# -----------------------------------------------------------------------------
# class MerraFileName
#
# MERRA description:  https://gmao.gsfc.nasa.gov/pubs/docs/Bosilovich785.pdf
#
# collection_operation_yyyy_week#
# collection_operation_yyyy_month#
# -----------------------------------------------------------------------------
class MerraFileName(object):
    
    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self, fileName):
        
        components = os.path.splitext(os.path.basename(fileName))[0].split('_')
        
        self.collection = components[0]
        self.operation = components[1]
        self.year = components[2]
        
        if components[3][0:4] == 'week':
            
            self.period = 'week'
            self.periodNum = int(components[3][4:6])
        
        elif components[3][0:5] == 'month':

            self.period = 'month'
            self.periodNum = int(components[3][5:7])

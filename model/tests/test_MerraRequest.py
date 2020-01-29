#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import unittest

import pandas

from model.MerraRequest import MerraRequest


# -----------------------------------------------------------------------------
# class MerraRequestTestCase
#
# python -m unittest discover model/tests/
# python -m unittest model.tests.test_MerraRequest
# -----------------------------------------------------------------------------
class MerraRequestTestCase(unittest.TestCase):

    # -------------------------------------------------------------------------
    # testQueryFiles
    # -------------------------------------------------------------------------
    def testQueryFiles(self):

        dateRange = pandas.date_range('2010-10-10', '2012-12-12')
        files = MerraRequest.queryFiles(dateRange, 'tavgM_2d_slv_Nx')
        
        self.assertEqual(27, len(files))

        expectedFiles = ['/att/pubrepo/ILAB/data/MERRA2/Monthly/M2TMNXSLV.5.12.4/2010/MERRA2_300.tavgM_2d_slv_Nx.201010.nc4',
                         '/att/pubrepo/ILAB/data/MERRA2/Monthly/M2TMNXSLV.5.12.4/2010/MERRA2_300.tavgM_2d_slv_Nx.201011.nc4', 
                         '/att/pubrepo/ILAB/data/MERRA2/Monthly/M2TMNXSLV.5.12.4/2010/MERRA2_300.tavgM_2d_slv_Nx.201012.nc4', 
                         '/att/pubrepo/ILAB/data/MERRA2/Monthly/M2TMNXSLV.5.12.4/2011/MERRA2_400.tavgM_2d_slv_Nx.201101.nc4', 
                         '/att/pubrepo/ILAB/data/MERRA2/Monthly/M2TMNXSLV.5.12.4/2011/MERRA2_400.tavgM_2d_slv_Nx.201102.nc4', 
                         '/att/pubrepo/ILAB/data/MERRA2/Monthly/M2TMNXSLV.5.12.4/2011/MERRA2_400.tavgM_2d_slv_Nx.201103.nc4', 
                         '/att/pubrepo/ILAB/data/MERRA2/Monthly/M2TMNXSLV.5.12.4/2011/MERRA2_400.tavgM_2d_slv_Nx.201104.nc4', 
                         '/att/pubrepo/ILAB/data/MERRA2/Monthly/M2TMNXSLV.5.12.4/2011/MERRA2_400.tavgM_2d_slv_Nx.201105.nc4', 
                         '/att/pubrepo/ILAB/data/MERRA2/Monthly/M2TMNXSLV.5.12.4/2011/MERRA2_400.tavgM_2d_slv_Nx.201106.nc4', 
                         '/att/pubrepo/ILAB/data/MERRA2/Monthly/M2TMNXSLV.5.12.4/2011/MERRA2_400.tavgM_2d_slv_Nx.201107.nc4',
                         '/att/pubrepo/ILAB/data/MERRA2/Monthly/M2TMNXSLV.5.12.4/2011/MERRA2_400.tavgM_2d_slv_Nx.201108.nc4', 
                         '/att/pubrepo/ILAB/data/MERRA2/Monthly/M2TMNXSLV.5.12.4/2011/MERRA2_400.tavgM_2d_slv_Nx.201109.nc4', 
                         '/att/pubrepo/ILAB/data/MERRA2/Monthly/M2TMNXSLV.5.12.4/2011/MERRA2_400.tavgM_2d_slv_Nx.201110.nc4', 
                         '/att/pubrepo/ILAB/data/MERRA2/Monthly/M2TMNXSLV.5.12.4/2011/MERRA2_400.tavgM_2d_slv_Nx.201111.nc4', 
                         '/att/pubrepo/ILAB/data/MERRA2/Monthly/M2TMNXSLV.5.12.4/2011/MERRA2_400.tavgM_2d_slv_Nx.201112.nc4', 
                         '/att/pubrepo/ILAB/data/MERRA2/Monthly/M2TMNXSLV.5.12.4/2012/MERRA2_400.tavgM_2d_slv_Nx.201201.nc4', 
                         '/att/pubrepo/ILAB/data/MERRA2/Monthly/M2TMNXSLV.5.12.4/2012/MERRA2_400.tavgM_2d_slv_Nx.201202.nc4', 
                         '/att/pubrepo/ILAB/data/MERRA2/Monthly/M2TMNXSLV.5.12.4/2012/MERRA2_400.tavgM_2d_slv_Nx.201203.nc4', 
                         '/att/pubrepo/ILAB/data/MERRA2/Monthly/M2TMNXSLV.5.12.4/2012/MERRA2_400.tavgM_2d_slv_Nx.201204.nc4', 
                         '/att/pubrepo/ILAB/data/MERRA2/Monthly/M2TMNXSLV.5.12.4/2012/MERRA2_400.tavgM_2d_slv_Nx.201205.nc4', 
                         '/att/pubrepo/ILAB/data/MERRA2/Monthly/M2TMNXSLV.5.12.4/2012/MERRA2_400.tavgM_2d_slv_Nx.201206.nc4', 
                         '/att/pubrepo/ILAB/data/MERRA2/Monthly/M2TMNXSLV.5.12.4/2012/MERRA2_400.tavgM_2d_slv_Nx.201207.nc4', 
                         '/att/pubrepo/ILAB/data/MERRA2/Monthly/M2TMNXSLV.5.12.4/2012/MERRA2_400.tavgM_2d_slv_Nx.201208.nc4', 
                         '/att/pubrepo/ILAB/data/MERRA2/Monthly/M2TMNXSLV.5.12.4/2012/MERRA2_400.tavgM_2d_slv_Nx.201209.nc4', 
                         '/att/pubrepo/ILAB/data/MERRA2/Monthly/M2TMNXSLV.5.12.4/2012/MERRA2_400.tavgM_2d_slv_Nx.201210.nc4', 
                         '/att/pubrepo/ILAB/data/MERRA2/Monthly/M2TMNXSLV.5.12.4/2012/MERRA2_400.tavgM_2d_slv_Nx.201211.nc4', 
                         '/att/pubrepo/ILAB/data/MERRA2/Monthly/M2TMNXSLV.5.12.4/2012/MERRA2_400.tavgM_2d_slv_Nx.201212.nc4']
                         
        self.assertEqual(expectedFiles, files)
        
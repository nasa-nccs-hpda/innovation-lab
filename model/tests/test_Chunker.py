#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import unittest

import numpy as np

from model.Chunker import Chunker


# -----------------------------------------------------------------------------
# class ChunkerTestCase
#
# python -m unittest discover model/tests/
# python -m unittest model.tests.test_Chunker
# -----------------------------------------------------------------------------
class ChunkerTestCase(unittest.TestCase):

    # -------------------------------------------------------------------------
    # testInit
    # -------------------------------------------------------------------------
    def testInit(self):
        
        testFile = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'gsenm_250m_eucl_dist_streams.tif')
        
        c = Chunker(testFile)

    # -------------------------------------------------------------------------
    # testSetChunkDimensions
    # -------------------------------------------------------------------------
    def testSetChunkDimensions(self):

        testFile = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'gsenm_250m_eucl_dist_streams.tif')
        
        c = Chunker(testFile)
        
        with self.assertRaisesRegexp(RuntimeError, 
                                     'sample size of a chunk must be greater'):
            c.setChunkSize(-1, 10)
            
        with self.assertRaisesRegexp(RuntimeError, 
                                     'Sample size.*must be less'):
            c.setChunkSize(1000000000, 10)
            
        with self.assertRaisesRegexp(RuntimeError, 
                                     'line size of a chunk must be greater'):
            c.setChunkSize(10, -1)
            
        with self.assertRaisesRegexp(RuntimeError, 
                                     'Line size.*must be less'):
            c.setChunkSize(10, 1000000000)
            
        c.setChunkSize(10, 15)
        self.assertEqual(c._xSize, 10)
        self.assertEqual(c._ySize, 15)
        
    # -------------------------------------------------------------------------
    # testSetChunkAsColumn
    # -------------------------------------------------------------------------
    def testSetChunkAsColumn(self):

        testFile = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'gsenm_250m_eucl_dist_streams.tif')
        
        c = Chunker(testFile)
        c.setChunkAsColumn()
        self.assertEqual(c._xSize, 1)
        self.assertEqual(c._ySize, 464)

    # -------------------------------------------------------------------------
    # testSetChunkAsRow
    # -------------------------------------------------------------------------
    def testSetChunkAsRow(self):

        testFile = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'gsenm_250m_eucl_dist_streams.tif')
        
        c = Chunker(testFile)
        c.setChunkAsRow()
        self.assertEqual(c._xSize, 578)
        self.assertEqual(c._ySize, 1)

    # -------------------------------------------------------------------------
    # testGetChunk
    # -------------------------------------------------------------------------
    def testGetChunk(self):
        
        # 578, 464
        testFile = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'gsenm_250m_eucl_dist_streams.tif')
        
        c = Chunker(testFile)
        c.setChunkSize(250, 200)

        # ---
        # The image is 578 x 464, and it's type is byte.  Check each chunk's
        # progression through the image.
        # ---
        outBuffer = np.empty([578, 464], dtype=np.uintc)
        loc, chunk = c.getChunk()
        self.assertEqual(loc[0], 0)
        self.assertEqual(loc[1], 0)
        outBuffer[loc[0]:loc[0]+250, loc[1]:loc[1]+200] = chunk
        self.assertEqual(chunk[0][0], outBuffer[loc[0]][loc[1]])
        self.assertEqual(chunk[249][199], outBuffer[loc[0]+249][loc[1]+199])

        loc, chunk = c.getChunk()
        self.assertEqual(loc[0], 250)
        self.assertEqual(loc[1], 0)
        outBuffer[loc[0]:loc[0]+250, loc[1]:loc[1]+200] = chunk
        self.assertEqual(chunk[0][0], outBuffer[loc[0]][loc[1]])
        self.assertEqual(chunk[249][199], outBuffer[loc[0]+249][loc[1]+199])
        
        # This hits the end of the first chunk row.
        loc, chunk = c.getChunk()
        self.assertEqual(loc[0], 500)
        self.assertEqual(loc[1], 0)
        outBuffer[loc[0]:loc[0]+250, loc[1]:loc[1]+200] = chunk
        self.assertEqual(chunk[0][0], outBuffer[loc[0]][loc[1]])
        self.assertEqual(chunk[77][199], outBuffer[loc[0]+77][loc[1]+199])

        loc, chunk = c.getChunk()
        self.assertEqual(loc[0], 0)
        self.assertEqual(loc[1], 200)
        outBuffer[loc[0]:loc[0]+250, loc[1]:loc[1]+200] = chunk
        self.assertEqual(chunk[0][0], outBuffer[loc[0]][loc[1]])
        self.assertEqual(chunk[249][199], outBuffer[loc[0]+249][loc[1]+199])
        
        loc, chunk = c.getChunk()
        self.assertEqual(loc[0], 250)
        self.assertEqual(loc[1], 200)
        outBuffer[loc[0]:loc[0]+250, loc[1]:loc[1]+200] = chunk
        self.assertEqual(chunk[0][0], outBuffer[loc[0]][loc[1]])
        self.assertEqual(chunk[249][199], outBuffer[loc[0]+249][loc[1]+199])

        # This hits the end of the second chunk row.
        loc, chunk = c.getChunk()
        self.assertEqual(loc[0], 500)
        self.assertEqual(loc[1], 200)
        outBuffer[loc[0]:loc[0]+250, loc[1]:loc[1]+200] = chunk
        self.assertEqual(chunk[0][0], outBuffer[loc[0]][loc[1]])
        self.assertEqual(chunk[77][199], outBuffer[loc[0]+77][loc[1]+199])
        
        # This hits the end of the first chunk column.
        loc, chunk = c.getChunk()
        self.assertEqual(loc[0], 0)
        self.assertEqual(loc[1], 400)
        outBuffer[loc[0]:loc[0]+250, loc[1]:loc[1]+200] = chunk
        self.assertEqual(chunk[0][0], outBuffer[loc[0]][loc[1]])
        self.assertEqual(chunk[249][63], outBuffer[loc[0]+249][loc[1]+63])

        loc, chunk = c.getChunk()
        self.assertEqual(loc[0], 250)
        self.assertEqual(loc[1], 400)
        outBuffer[loc[0]:loc[0]+250, loc[1]:loc[1]+200] = chunk
        self.assertEqual(chunk[0][0], outBuffer[loc[0]][loc[1]])
        self.assertEqual(chunk[249][63], outBuffer[loc[0]+249][loc[1]+63])

        loc, chunk = c.getChunk()
        self.assertEqual(loc[0], 500)
        self.assertEqual(loc[1], 400)
        outBuffer[loc[0]:loc[0]+250, loc[1]:loc[1]+200] = chunk
        self.assertEqual(chunk[0][0], outBuffer[loc[0]][loc[1]])
        self.assertEqual(chunk[77][63], outBuffer[loc[0]+77][loc[1]+63])

        loc, chunk = c.getChunk()
        self.assertIsNone(loc)
        self.assertIsNone(chunk)
            
import pandas as pd
import numpy as np
import math
import numba
from scipy import ndimage
import peakutils
from otbApp import otbApp
from osgeo import gdal, ogr, osr


import os

class Segmentation(object):
    
    def __init__(self,
                 pathToFile,
                 imageFile, 
                 outPath):
        
        if not pathToFile:
            raise RuntimeError('A path to a file must be specified')
        
        if not os.path.exists(pathToFile):
            raise RuntimeError(str(pathToFile) + 'does no exist.')
        
        self.imgFile = os.path.join(pathToFile,imageFile)
        
        if not os.path.isfile(self.imgFile):
            raise RuntimeError('An image must be specified')
        
        nm = imageFile.split('.')[0]    
        self._fileName = nm[4:]
        self._img = self.imgFile
        self._outPath = outPath
        
    # Padding image 
    @staticmethod
    def padImage(input, size, mode='symmetric'):

        a = np.pad(input, size//2, mode)
        return a
    
    # Compute variance within 2D sliding windows
    @staticmethod
    @numba.jit('f4(u2[:,:], u2[:,:], i2)',nopython = True, fastmath=True)
    def mw_var_numba(in_arr, out_arr, win_size):
        xn, yn=out_arr.shape
        maxIndex = xn*yn

        for i in range(maxIndex):
            x = int(i / yn)
            y = i % yn
            out_arr[x,y] = in_arr[x:(x+win_size), y:(y+win_size)].var()

        return out_arr.mean()
    
    # Extract band data 
    def readRasterBand(self, imageFile, band=1):
        img =  gdal.Open(imageFile)
        bd =  img.GetRasterBand(band)
        return bd.ReadAsArray()
    
    # Compute Spatial Radius and Range Radius, that're used by OTB Segmentation
    def getRadius(self, imageFile, band, start=3, end=50, step=2):
        red =self.readRasterBand(imageFile, band)
                
        data = []
        hs = 5
        
        for size in range(start, end, step):
            red_pad = self.padImage(red, size)
            red_var = np.zeros_like(red)
            out = self.mw_var_numba(red_pad, red_var, size)
            data.append((size, out))
    
        cols=['ws','local_variance']
        df = pd.DataFrame(data,columns=cols)
        df_sort=df.sort_values(by=['ws'])
        df_sort['ROC'] = (df_sort['local_variance'] - df_sort['local_variance'].shift(1))/df_sort['local_variance'].shift(1)
        df_sort['SCROC'] = df_sort['ROC'].shift(1) - df_sort['ROC'] 
        df_sort['spatial_radius']=(df_sort['ws']-1)/2 
        roc=df_sort.loc[df_sort['ROC'] < 0.01]
        scroc=roc.loc[roc['SCROC'] < 0.001]
        if not scroc.empty:
            hs=scroc['spatial_radius'].iloc[0]
            hs=int(hs)
        #df_sort.to_csv("LV_"+name+".csv")

        var_image= ndimage.generic_filter(red, np.var, size=hs)
        maxvalue = var_image.max()

        counts, bins = np.histogram(var_image.flatten(),bins='auto')
        b=bins.shape
        weight = int(b[0])
        c=weight-1
        y=bins[0:c,]
        indexes = peakutils.indexes(counts, thres=0, min_dist=maxvalue)
        hr=math.sqrt(y[indexes[0]])
        hr=int(hr)
        
        return hs, hr
    
    # Convert segmentation result from geotiff to shape file
    def rasterToShape(self, raster, shp):
        src_ds = gdal.Open( raster )
        srcband = src_ds.GetRasterBand(1)
        srs = osr.SpatialReference()
        srs.ImportFromWkt(src_ds.GetProjection())
        drv = ogr.GetDriverByName("ESRI Shapefile")
        seg_ds = drv.CreateDataSource( shp )
        seg_layer = seg_ds.CreateLayer(shp, srs = srs )
        gdal.Polygonize( srcband, None, seg_layer, -1, [], callback=None )
        seg_ds = None
        
    # run    
    def run(self):
        
        segOut = os.path.join(self._outPath, "merg_"+self._fileName+".tif")
        shapeOut = os.path.join(self._outPath, "seg_"+self._fileName+".shp")
        
        print("Computing Radius")
        hs, hr = self.getRadius(self._img, band=3)
        
        print("Running OTB LSMS")
        otbApp.runLSMS(self._img,segOut,
                spatialr=hs, ranger=hr,
                tilesizex=500, tilesizey=500, 
                sm_thres=0.1, sm_maxiter=100,
                seg_minsize=0, merg_minsize=10)
        
        print("Writing Segmentation Result")
        self.rasterToShape(segOut, shapeOut)
        
        

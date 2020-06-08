# Compute zonal stats using segmented polygons and explanatory variables
import itertools
import multiprocessing
from rasterstats import zonal_stats
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import os
import fiona
import geopandas as gpd
from functools import partial

# break down polygons into chunks
def chunks(data, n):
    for i in range(0, len(data), n):
        yield data[i:i+n]

# wrapper for zonal_stats
def zonal_stats_wrapper(feats, tif, stats):
    return zonal_stats(feats, tif, stats, nodata=-999)

# compute zonal_stats in parallel
def zonal_stats_parallel(features, cores, raster, opr):
    p = multiprocessing.pool(cores)
    func = partial(zonal_stats_wrapper, tif=raster, stats=opr)
    stats_lists = p.map(func, chunks(features, cores))
    stat = list(itertools.chain(*stats_lists))
    p.close()
    return stat

class Detection(object):
    def __init__(self, pathToFile, training,
                 segFile, brightFile, ndviFile, 
                 slopeFile, homogFile, meanFile,
                 outPath, outFile): 
               
        if not pathToFile:
            raise RuntimeError('A path to a file must be specified')
        
        if not os.path.exists(pathToFile):
            raise RuntimeError(str(pathToFile) + 'does no exist.')
        
        if not os.path.isfile(self.training):
            raise RuntimeError('A training shape file must be specified')
        self.trainfile = os.path.join(pathToFile, training)
        
        if not os.path.isfile(self.segFile):
            raise RuntimeError('A segmented shape file must be specified')
        self.segfile = os.path.join(pathToFile, segFile) 
        
        if not os.path.isfile(self.brightFile):
            raise RuntimeError('A brightness file must be specified')
        self.brightfile = os.path.join(pathToFile, brightFile)
 
        if not os.path.isfile(self.ndviFile):
            raise RuntimeError('A NDVI file must be specified')
        self.ndvifile = os.path.join(pathToFile, ndviFile)       

        if not os.path.isfile(self.slopeFile):
            raise RuntimeError('A slope file must be specified')
        self.slopefile = os.path.join(pathToFile, slopeFile) 
 
        if not os.path.isfile(self.homogFile):
            raise RuntimeError('A GLCM Homogeneity file must be specified')
        self.homogfile = os.path.join(pathToFile, homogFile)
        
        if not os.path.isfile(self.meanFile):
            raise RuntimeError('A GLCM Mean file must be specified')
        self.meanfile = os.path.join(pathToFile, meanFile)
        
        self.outfile = os.path.join(outPath, outFile)
    
    # run
    def run(self):
        
        shp_file = self.segfile
        
        rasters = {'brightness' : self.brightfile,
                   'ndvi'       : self.ndvifile,
                   'slope'      : self.slopefile,
                   'glcmhomog'  : self.homogfile,
                   'glcmmean'   : self.meanfile}
        
        # dictionary to host output zonal stats
        out_stat = dict.fromkeys(rasters)

        # open shapefile and read features once
        shp_open=fiona.open(shp_file)
        with shp_open as src:
            features = list(src)
    
        cores = os.cpu_count()

        # loop through rasters for zonal stats
        for k in rasters.keys():
            tif = rasters[k]
            stat = zonal_stats_parallel(features, cores, tif, 'mean')
            out_stat[k] = list(d["mean"] for d in stat)
                
        # add feature back to shapefile
        df=gpd.read_file(shp_file)
        df["Meanbright"]=out_stat['brightness']
        df["Meanndvi"]=out_stat['ndvi']
        df["Meanslope"]=out_stat['slope']
        df["glcmhomog"]=out_stat['glcmhomog']
        df["glcmmean"]=out_stat['glcmmean']
        df_final = df.replace([np.inf, -np.inf], np.nan)
        df_final=df_final.fillna(0)

        # read training file
        df_train = gpd.read_file(self.trainfile)
        predictor_vars = ["Meanbright","Meanndvi","Meanslope","glcmhomog","glcmmean"]
        x,y = df_train[predictor_vars],df_train.landslide

        # fit random forest model
        modelRandom = RandomForestClassifier(n_estimators=5000)
        modelRandom.fit(x,y)
        
        # make prediction
        predictions=modelRandom.predict(df_final[predictor_vars])
        df_final["outcomes"]= predictions
        
        # write out
        crs=df.crs
        df_land=df_final[df_final['outcomes']>0]
        df_land_dissolve = gpd.geoseries.GeoSeries([geom for geom in df_land.unary_union.geoms])
        df_land_dissolve.crs=crs
        df_land_dissolve.to_file(self.outfile)

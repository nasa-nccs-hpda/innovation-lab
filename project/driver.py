import sys

from preprocessing import PreProcessing
from segmentation import Segmentation
from detection import Detection

rawDataPath = "./data"
processedPath = "./temp"

IMG = "rad_4551910_2016-01-02_RE4_3A_Analytic.tif"
DEM = "srtm_arniko.tif"
OUT = "./temp"

def main():
    #file id derived from raw data 
    tag = IMG.split('.')[0]
    fid = tag[4:]
    
    #preprocess generate 5 geotiff
    step1 = PreProcessing(pathToFile=rawDataPath, imageFile=IMG, demFile=DEM, outPath=processedPath)
    step1.run()
    homogfile = "homog_"+fid+".tif"
    meanfile = "mean_"+fid+".tif"
    slopefile = "slope_"+fid+".tif"
    brightfile = "bright_"+fid+".tif"
    ndvifile = "ndvi_"+fid+".tif" 
    
    #segmentation generate a shape file
    step2 = Segmentation(pathToFile=rawDataPath, imageFile=IMG, outPath=processedPath)
    step2.run()
    segfile = "seg_"+fid+".shp"  

    # random forest model to detect landslide
    outfile = "landslide_dissolve.shp"
    step3 = Detection(pathToFile=processedPath, training="training.shp",
                      segFile = segfile, brightFile=brightfile, ndviFile=ndvifile,                       
                      slopeFile=slopefile, homogFile=homogfile, meanFile=meanfile, 
                      outPath=processedPath, outFile=outfile)
    step3.run()

if __name__ == "__main__":
    sys.exit(main())
    
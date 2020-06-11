import os
from osgeo import gdal
import numpy as np
from otbApp import otbApp
import richdem as rd



class PreProcessing(object):
    
    def __init__(self,
                 pathToFile,
                 imageFile,
                 demFile, 
                 outPath):
        
        if not pathToFile:
            raise RuntimeError('A path to a file must be specified')
        
        if not os.path.exists(pathToFile):
            raise RuntimeError(str(pathToFile) + 'does no exist.')
        
        
        self.imgFile = os.path.join(pathToFile,imageFile)
        self.demFile = os.path.join(pathToFile, demFile)
        
        nm = imageFile.split('.')[0]
        self._fileName=nm[4:]
        
        if not os.path.isfile(self.imgFile):
            raise RuntimeError('An image must be specified')
        
        if not os.path.isfile(self.demFile):
            raise RuntimeError('A DEM must be specified')
        
        self._outPath = outPath

    # Extract meta data from geotiff    
    def getImgInfo(self, image, band=1):
        
        img = gdal.Open(image)
        if img is None:
            raise RuntimeError('Unable to open '+str(self.imagFile))
        
        self._rows = img.RasterYSize
        self._cols = img.RasterXSize
        
        bd = img.GetRasterBand(band)
        arr = bd.ReadAsArray()
        self._maxvalue = arr.max()
        
        self._geo=img.GetGeoTransform()
        self._proj=img.GetProjection()
                       
        img = None

    # Write geotiff
    def _writeTiff (self, filename, xsize, ysize, band, gdaltype, 
                    geo, proj,data):
        driver = gdal.GetDriverByName("GTiff")
        out = driver.Create(filename, xsize, ysize, band, gdaltype)
        out.SetGeoTransform(geo)
        out.SetProjection(proj)
        out.GetRasterBand(1).WriteArray(data)

    # Extract slope information from DEM       
    def _convertDEM(self):
       
        #Read slope
        dem = rd.LoadGDAL(self.demFile)
        slope = rd.TerrainAttribute(dem, attrib="slope_degrees")
        
        #Reformat slope
        self.getImgInfo(self.demFile,1)
        self._writeTiff("slope.tif", self._cols, self._rows, 1, gdal.GDT_Float32,
                        self._geo, self._proj, slope)
        slope_clip=gdal.Open("slope.tif")
             
#        os.remove("slope.tif")
        
        return slope_clip
    
    # Compute textural features using OTB application        
    def generateGLCM(self): 
               
        self.getImgInfo(self.imgFile, 3)
        
        mean_stack=np.zeros((4,self._rows,self._cols))
        homog_stack=np.zeros((4,self._rows,self._cols))
        
        for x in range(4):
            
            if x==0:
                cx=0
                cy=1
                dir=0
            elif x==1:
                cx=1
                cy=1
                dir=45
            elif x==2:
                cx=1
                cy=0
                dir=90
            else:
                cx=1
                cy=-1
                dir=135
            
            tmpfile = "mean_"+str(dir)+".tif"    
            otbApp.runTextureExtraction(self.imgFile, 3, tmpfile, 
                             cx, cy, 3, 3, 0, int(self._maxvalue), 'advanced')
            fd = gdal.Open( tmpfile )
            band = fd.GetRasterBand(1)
            arr = band.ReadAsArray()
            mean_stack[x,:] = arr
            
            tmpfile = "homog_"+str(dir)+".tif"
            otbApp.runTextureExtraction(self.imgFile, 3, tmpfile, 
                             cx, cy, 3, 3, 0, int(self._maxvalue), 'simple')
            fd = gdal.Open( tmpfile )
            band = fd.GetRasterBand(4)
            arr = band.ReadAsArray()
            homog_stack[x,:] = arr
                               
        glcm_mean = np.mean(mean_stack, axis=0)
        glcm_homog = np.mean(homog_stack, axis=0)
        
        name = "mean_"+self._fileName+".tif"
        mean_outfile = os.path.join(self._outPath, name)
        self._writeTiff(mean_outfile, self._cols, self._rows, 1, gdal.GDT_Float32,
                        self._geo, self._proj, glcm_mean)

        name = "homog_"+self._fileName+".tif"
        homog_outfile = os.path.join(self._outPath, name)
        self._writeTiff(homog_outfile, self._cols, self._rows, 1, gdal.GDT_Float32,
                        self._geo, self._proj, glcm_homog)

    # Clip and re-project slope
    def generateSlope(self):
        
        slope_clip = self._convertDEM()
        
        self.getImgInfo(self.imgFile, 1)      

        minx = self._geo[0]
        maxy = self._geo[3]
        maxx = minx + self._geo[1] * self._cols
        miny = maxy + self._geo[5] * self._rows

        name = "slope_"+self._fileName+".tif"
        slope_outfile = os.path.join(self._outPath, name)
        gdal.Translate(slope_outfile,
                       slope_clip,width=self._cols,height=self._rows,
                       resampleAlg=0,format='GTiff',projWin=[minx,maxy,maxx,miny],
                       outputSRS=self._proj)

        dem_open=None
        slope_clip=None
    
    # Compute Brightness and NDVI         
    def generateIndex(self):
        self.getImgInfo(self.imgFile, 3)
        
        img = gdal.Open(self.imgFile)
        
        blue_band = img.GetRasterBand(1)
        green_band = img.GetRasterBand(2)
        red_band = img.GetRasterBand(3)
        nir_band = img.GetRasterBand(5)

        red = red_band.ReadAsArray()
        blue = blue_band.ReadAsArray()
        green = green_band.ReadAsArray()
        nir = nir_band.ReadAsArray()

        red_flt = red.astype(np.float32)
        nir_flt = nir.astype(np.float32)

        np.seterr(divide='ignore', invalid='ignore')
        ndvi=(nir_flt-red_flt)/(nir_flt+red_flt)

        bright=(blue+green+red+nir)/4
        
        name = "ndvi_"+self._fileName+".tif"
        ndvi_outfile = os.path.join(self._outPath, name)
        self._writeTiff(ndvi_outfile, self._cols, self._rows, 1, gdal.GDT_Float32,
                        self._geo, self._proj, ndvi)        

        name = "bright_"+self._fileName+".tif"
        bright_outfile = os.path.join(self._outPath, name)
        self._writeTiff(bright_outfile, self._cols, self._rows, 1, gdal.GDT_Int16,
                        self._geo, self._proj, bright)
      
    # run    
    def run(self):
        print("Computing Textural Features")
        self.generateGLCM()
        print("Computing Slope")
        self.generateSlope()
        print("Computing NDVI and Brightness")
        self.generateIndex()
        


        
            
        
    
    
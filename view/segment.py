import otbApplication
import os
from osgeo import gdal, ogr, osr
import time
t0=time.time()
#set working directory
#path="/att/nobackup/pamatya/japancomp"
path='/att/nobackup/jli30/workspace/landslide/japan/input'
os.chdir(path)
image_file = "WV02N34_253750E132_project.tif"
case = "_ms_10g.tif"

os.environ["OTB_MAX_RAM_HINT"] = "10240"
# The following line creates an instance of the MeanShiftSmoothing application
MeanShiftSmoothing = otbApplication.Registry.CreateApplication("MeanShiftSmoothing")

# The following lines set all the application parameters:
MeanShiftSmoothing.SetParameterString("in", image_file)

MeanShiftSmoothing.SetParameterString("fout", "smooth"+case)

MeanShiftSmoothing.SetParameterInt("spatialr", 9)

MeanShiftSmoothing.SetParameterFloat("ranger", 70)

MeanShiftSmoothing.SetParameterFloat("thres", 0.1)

MeanShiftSmoothing.SetParameterInt("maxiter", 100)

MeanShiftSmoothing.SetParameterInt("modesearch", 1)

# The following line execute the application
MeanShiftSmoothing.ExecuteAndWriteOutput()
# calculate time
t1=time.time()
time1=t1-t0
hrs1=float(time1/60)


# The following line creates an instance of the LSMSSegmentation application
LSMSSegmentation = otbApplication.Registry.CreateApplication("LSMSSegmentation")

# The following lines set all the application parameters:
LSMSSegmentation.SetParameterString("in", "smooth"+case)

LSMSSegmentation.SetParameterString("out", "segmentation"+case)

LSMSSegmentation.SetParameterFloat("spatialr", 9)

LSMSSegmentation.SetParameterFloat("ranger", 70)

LSMSSegmentation.SetParameterInt("minsize", 0)

LSMSSegmentation.SetParameterInt("tilesizex", 500)

LSMSSegmentation.SetParameterInt("tilesizey", 500)

# The following line execute the application
LSMSSegmentation.ExecuteAndWriteOutput()
# calculate time
t2=time.time()
time2=t2-t1
hrs2=float(time2/60)


# The following line creates an instance of the LSMSSmallRegionsMerging application
LSMSSmallRegionsMerging = otbApplication.Registry.CreateApplication("LSMSSmallRegionsMerging")

# The following lines set all the application parameters:
LSMSSmallRegionsMerging.SetParameterString("in", image_file)

LSMSSmallRegionsMerging.SetParameterString("inseg", "segmentation"+case)

LSMSSmallRegionsMerging.SetParameterString("out", "merged"+case)

LSMSSmallRegionsMerging.SetParameterInt("minsize", 40)

LSMSSmallRegionsMerging.SetParameterInt("tilesizex", 500)

LSMSSmallRegionsMerging.SetParameterInt("tilesizey", 500)

# The following line execute the application
LSMSSmallRegionsMerging.ExecuteAndWriteOutput()
# calculate time
t3=time.time()
time3=t3-t2
hrs3=float(time3/60)


#Raster to polygon
#  get raster datasource
src_ds = gdal.Open( "merged"+case )

srcband = src_ds.GetRasterBand(1)


srs = osr.SpatialReference()
srs.ImportFromWkt(src_ds.GetProjection())


#  create output datasource
dst_layername = "segment_polygon"+case
drv = ogr.GetDriverByName("ESRI Shapefile")
dst_ds = drv.CreateDataSource( dst_layername + ".shp" )
dst_layername = dst_layername.encode("utf-8")
dst_layer = dst_ds.CreateLayer(dst_layername, srs = srs )

gdal.Polygonize( srcband, None, dst_layer, -1, [], callback=None )
dst_ds = None

# calculate time
t4=time.time()
time4=t4-t3
hrs4=float(time4/60)
print(" smoothing = %s min")%hrs1
print(" segment = %s min")%hrs2
print(" merging = %s min")%hrs3
print(" polygonizing = %s min")%hrs4
total=(hrs1+hrs2+hrs3+hrs4)
final=float(total/60)
print(" Total time = %s hr")%final


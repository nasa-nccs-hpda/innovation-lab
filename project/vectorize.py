'''
Vectorize, version 0.2.1
By Thomas Stanley USRA/GESTAR 2020-8-24
NASA Goddard Space Flight Center
Convert raster to polygons
'''

import xarray as xr
import affine
import rasterio.features
import shapely.geometry as sg
import geopandas as gpd

#PATH = '/att/nobackup/tastanle/LHASA2/vectorized/'
PATH = '../output/predictions/20200706'
day = '20160102'
file_name = f'nowcast{day}.shp'
threshold = 0.9

p = xr.open_dataarray(f'{PATH}/{day}.nc4')
nowcast = (p > threshold).where(p.notnull()).values.astype('uint8')
trnsfrm = affine.Affine(0.00833333333333333, 0.0, -180.0, 0.0, -0.00833333333333333, 60.00006000333327)
shapes = rasterio.features.shapes(nowcast, mask = nowcast, transform=trnsfrm)

polygons = [sg.shape(geom) for geom, value in shapes]

gdf = gpd.GeoDataFrame(geometry = polygons)
gdf.crs = {'init': 'epsg:4326', 'no_defs': True}
gdf['p'] = threshold
projected = gdf.to_crs(epsg=3857)
# This hack is required to get the polygons into AIM, because AIM can't take intersecting corners
projected = projected.buffer(-5)

projected.to_file(f'{PATH}/vectorized/'+file_name)

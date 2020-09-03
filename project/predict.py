'''
Predict 1 day, version 0.4.3
By Thomas Stanley USRA/GESTAR 2020-7-7
NASA Goddard Space Flight Center
Output the results of the trained model by day
'''

import logging
logging.basicConfig(filename='../log/test.log', level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%H:%M')
logging.info('logging started')
import numpy as np
import xarray as xr
import xgboost as xgb
import pandas as pd

# work around to read NSIDC datasets
from opendap_work_around import NSIDCdata
#

logging.info('loaded imports')


PATH = '/att/nobackup/tastanle/'
OUTPUTPATH = '../output/'

# Open trained model
model = xgb.Booster()
model.load_model(PATH + 'LHASA2/models/20200706')
model.set_param('nthread', 10)

# Open static variables
p99 = xr.open_rasterio(PATH + 'LHASA2/static/Daily_sum_99.tif').squeeze().drop('band')
p99.name = 'p99'
d2faults = xr.open_rasterio(PATH + 'LHASA2/static/faults.tif').squeeze().drop('band')
d2faults.name = 'Faults'
lithology = xr.open_rasterio(PATH + 'LHASA2/static/lithology.tif').squeeze().drop('band')
lithology.name = 'Lithology'
slope = xr.open_rasterio(PATH + 'LHASA2/static/maxSlope.tif').squeeze().drop('band')
slope.name = 'Slope'
# Crop to 60 N-S, 180 E-W
p99 = p99.sel(y=slice(60, -60))
d2faults = d2faults.sel(y=slice(60, -60))
lithology = lithology.sel(y=slice(60, -60))
slope = slope.sel(x=slice(-180, 180), y=slice(60, -60))
# Load file into memory
d2faults.load()
lithology.load()
slope.load()
logging.info('opened static variables')

days = pd.date_range(start = '2016-1-1', end = '2016-1-3', tz='UTC')
for day in days:
    logging.info('loading ' + day.strftime('%Y-%m-%d'))
    # Open IMERG files
    rain = xr.open_rasterio(PATH + f'IMERG/DLL06B/3B-DAY-L.GIS.IMERG.{day.strftime("%Y%m%d")}.V06B.liquid.tif').squeeze().drop('band')
    rain.name = 'Rain'
    antecedent = xr.open_rasterio(PATH + 'IMERG/antecedent/' + day.strftime('%Y%m%d') + '.tif').squeeze().drop('band')
    antecedent.name = 'Antecedent'
    # Open SMAP file
    date_L4 = day - pd.DateOffset(3)
    file_L4 = f'https://n5eil02u.ecs.nsidc.org:443/opendap/SMAP/SPL4SMGP.'\
        f'004/{date_L4.strftime("%Y.%m.%d")}/SMAP_L4_SM_gph_{date_L4.strftime("%Y%m%d")}T103000_Vv4030_001.h5'

    #L4 = xr.open_dataset(file_L4).squeeze().drop('FakeDim0')
    ##JL add st
    h = NSIDCdata()
    ds = h.get_dataset(file_L4)
    L4 = ds.squeeze().drop('FakeDim0')
    ## JL add ed

    # Convert to WGS84
    L4["x"] = L4.cell_lon[1,]
    L4["y"] = L4.cell_lat[:,1]
    # Crop to 60 N-S
    rain = rain.sel(y=slice(60, -60))
    antecedent = antecedent.sel(y=slice(60, -60))
    L4 = L4.sel(y=slice(60, -60))
    logging.info('opened ' + day.strftime('%Y-%m-%d'))
    # Mask no-data pixels
    rain = rain.where(rain < 29999)
    antecedent = antecedent.where(antecedent >= 0)
    logging.info('removed no-data')
    # Rescale rainfall by 99th percentile, converting from tenths of mm to mm
    rain = (rain / 10)/ p99.values
    logging.info('rescaled rainfall')
    # Nearest neighbor downscaling
    rain1km = rain.interp_like(slope, method='nearest')
    antecedent1km = antecedent.interp_like(slope, method='nearest')
    moisture = L4['Geophysical_Data_sm_profile_wetness'].interp_like(slope, method='nearest')
    snow = L4['Geophysical_Data_snow_mass'].interp_like(slope, method='nearest')
    logging.info('interpolated')
    mask = np.all(np.stack([
        rain1km.notnull(),
        antecedent1km.notnull(),
        moisture.notnull(),
        slope.notnull()
    ]), 0)
    logging.info('built mask')
    inputs = xgb.DMatrix(np.stack([
        rain1km.values[mask],
        antecedent1km.values[mask],
        moisture.values[mask],
        snow.values[mask],
        d2faults.values[mask],
        lithology.values[mask],
        slope.values[mask]
    ], 1))
    logging.info('converted variables to DMatrix')
    # Issue prediction with xgboost
    p = slope.values * np.nan
    p[mask] = model.predict(inputs, ntree_limit=300)
    logging.info('made predictions')
    ck = p.reshape((1,) + slope.shape)
    # Save output
    nowcast = xr.DataArray(
        p.reshape((1,) + slope.shape),
        coords=[[day.to_datetime64()], slope['y'], slope['x']],
        dims=['time', 'lat', 'lon'],
        name='p_landslide')
    print(nowcast)
    nowcast.to_netcdf(OUTPUTPATH + 'predictions/20200706/' + day.strftime('%Y%m%d') + '.nc4', encoding = {'p_landslide': {'_FillValue': -9999.0}})
    logging.info('saved output to disk')

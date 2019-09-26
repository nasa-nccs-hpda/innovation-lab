# innovation-lab
Innovation Lab


### Install Notes

##### Create Conda env:
```
    > conda create -n mmx python=3.7
    > source activate mmx
``` 

##### Install gdal:
```
    (mmx)> conda install gdal
``` 

##### Fix gdal LD_LIBRARY_PATH:
Mac:
```
    > export DYLD_FALLBACK_LIBRARY_PATH=$DYLD_FALLBACK_LIBRARY_PATH:$CONDA_HOME/envs/gdal/lib
``` 
Unix:
```
    > export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_HOME/envs/gdal/lib
``` 

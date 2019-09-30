# MMX Module Driver



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

##### Install pc2-module:
```
    (mmx)> git clone https://github.com/nasa-nccs-cds/pc2-module.git
    (mmx)> cd pc2-module
    (mmx)> python setup.py install
    (mmx)> conda install xarray
``` 

##### Install mmx:
```
    (mmx)> git clone https://github.com/nasa-nccs-hpda/innovation-lab.git
    (mmx)> cd innovation-lab
    (mmx)> git checkout -b mmx_alone
    (mmx)> python setup.py install
``` 

##### Run mmx:
```
    (mmx)> python mmx/model/tests/mmx_driver.py
``` 
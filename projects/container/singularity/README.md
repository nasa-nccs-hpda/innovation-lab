# Innovation Lab - Container project - Singularity artifacts
Overview:
This task formalizes an approach to container creation using Singularity on ADAPT.  The goal is to create reusable containers that guarantee identical environments for R&D, development, testing, and deployment within the Innovation Lab (IL).  Specifically, this approach involves designing a set of containers that extend one another to support targeted applications.  Conceptually, this hierarchy looks like this:
1.	cisto-data-science – contains the Python data science ecosystem:
	a.	NumPy
	b.	SciPy
	c.	matplotlib
	d.	IPython
	e.	pandas
	f.	Scikit-learn
2.	Ilab-core (extends -> cisto-data-science) – contains GIS & ilab dependencies:
	a.	GDAL
	b.	Celery
3.	Ilab-apps (extends -> ilab-infrastructure) – contains shared IL code and IL apps, including MMX:
	a.	Model
	b.	View
	c.	Controller
	d.	Projects
4.	cisto-jupyter-lab (extends any of the above) – contains notebook conveniences:
	a.	Jupyter lab
	b.	Firefox

Build steps:




DEMO SCRIPT (02/23/20) - BEGIN
# Build ilab MMX base image from Singularity definition file:  Note:  1) requires sudo, 2) absolute path, 3) no sandbox/writable, 4) contains. MMX dependencies: python 3.7, gdal, etc.
gtamkin@dsg101:/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity$ time sudo -E SINGULARITY_NOHTTPS=1 singularity build ilab-mmx-base.simg mmx/ilab-mmx-base.def 
INFO:    Creating SIF file...
INFO:    Build complete: ilab-mmx-base.simg

real	24m35.328s
user	11m17.079s
sys	1m44.119s

cd /att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity
gtamkin@dsg101:/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity$ ls -alt
total 3085464
-rwxr-xr-x  1 gtamkin k3000 661934080 Feb 23 19:30 ilab-mmx-base.simg
# Shell into non-sandbox [writable] and examine dependencies
tamkin@dsg101:/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity$ singularity shell -B /att ilab-mmx-base.simg
Singularity> pip freeze
amqp==2.5.2
bathyml==0.0.1
billiard==3.6.2.0
celery==4.3.0
certifi==2019.11.28
chardet==3.0.4
cycler==0.10.0
dask==2.11.0
GDAL==2.1.3
idna==2.8
importlib-metadata==1.5.0
joblib==0.14.1
kiwisolver==1.1.0
kombu==4.6.7
matplotlib==3.1.3
numpy==1.18.1
pandas==0.25.3
pyparsing==2.4.6
python-dateutil==2.8.1
pytz==2019.3
requests==2.22.0
scikit-learn==0.22.1
scipy==1.4.1
six==1.14.0
urllib3==1.25.8
vine==1.3.0
wget==3.2
xarray==0.15.0
zipp==2.2.0
# Examine MMX runtime script.  Note: 1) runs full MMX with static pre-processed data, 2) use Celery to run chained tasks, 3) hard-coded json parameters for now.
Singularity>  more /usr/local/mmx/innovation-lab/view/tests/MmxRequestCeleryView-adapt-gpfsfs.py 
import requests
from celery import Celery
from celery import chain
from celery.utils.log import get_task_logger
import json
import subprocess
import os

#from IPython.display import IFrame

logger = get_task_logger(__name__)

from view.MmxRequestTranslationView import order, status, download

app = Celery('MmxRequestCeleryView', broker='redis://localhost:6379/0')

@app.task
def _order(context):
    resp = order(context)
    return resp

@app.task
def _status(context):
    resp = status(context)
    print('\nStatus -> Service: ', context['service'], ' Request: ', context['request'] , ' Status: ', context['status'])
    return resp

@app.task
def _download(context):
    resp = download(context)
    return resp

def _nextStep(context, service, request):
    context['service'] = service
    context['request'] = request
    context['status'] = 'PENDING'
    print('\nExercise -> Service: ', service, ' Request: ', request, ' \nContext: ', context)
    #logger.info('Execute: %s %s %s', service, request, context)
    os.system("rm -rf /att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/testWorldClim/TMworldClim_fac/trials/*")
    return context

def asynch_func(context):
         _order.delay(context)

def chain_func(context):
    resp = context
    try:
        resp = chain(
                _nextStep(context,'IL','subsetData'),
                _order(context),

                _nextStep(context, 'MMX','prepareImages'),
                _order(context),

                _nextStep(context, 'MMX','runTrials'),
                _order(context),

                _nextStep(context,'MMX','getTopPredictors'),
                _order(context),

                _nextStep(context,'MMX','runFinalModel'),
                _order(context),
                )
        print(resp)

    except Exception as e:
        print (e)
        print("\nMmx chain finished.  Final Context:", resp)

    return resp

if __name__ == "__main__":

        json_string = "{\"observation\":\"/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/CassinSparrowData/ebd_Cassins_2006.csv\", " \
                        "\"species\":\"Cassins Sparrow\", \"startDate\":\"2006-01-01\", \"endDate\":\"2007-01-01\", \"collection\":\"merra2_t1nxslv\", " \
                        "\"vars\":\"U10M V10M\", \"operation\":\"ave\", \"EdasWorldClim\":\"True\", " \
                        "\"outDir\":\"/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/testWorldClim/TMworldClim_fac\", \"numTrials\":\"2\"
, \"numPredictors\":\"3\", " \
                        "\"workflow\":\"Rm\"}"
        context = json.loads(json_string)
        print("\nMmx chain starting.  Initial Context:", context)
        chain_func(context)

# Execute MMX runtime script within container.  
Singularity> python3.7  /usr/local/mmx/innovation-lab/view/tests/MmxRequestCeleryView-adapt-gpfsfs.py

Mmx chain starting.  Initial Context: {'observation': '/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/CassinSparrowData/ebd_Cassins_2006.csv', 'species': 'Cassins Sparrow', 'startDate': '2006-01-01', 'endDate': '2007-01-01', 'collection': 'merra2_t1nxslv', 'vars': 'U10M V10M', 'operation': 'ave', 'EdasWorldClim': 'True', 'outDir': '/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/testWorldClim/TMworldClim_fac', 'numTrials': '2', 'numPredictors': '3', 'workflow': 'Rm'}

Exercise -> Service:  IL  Request:  subsetData  
Context:  {'observation': '/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/CassinSparrowData/ebd_Cassins_2006.csv', 'species': 'Cassins Sparrow', 'startDate': '2006-01-01', 'endDate': '2007-01-01', 'collection': 'merra2_t1nxslv', 'vars': 'U10M V10M', 'operation': 'ave', 'EdasWorldClim': 'True', 'outDir': '/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/testWorldClim/TMworldClim_fac', 'numTrials': '2', 'numPredictors': '3', 'workflow': 'Rm', 'service': 'IL', 'request': 'subsetData', 'status': 'PENDING'}
/usr/local/lib/python3.7/site-packages/pandas/compat/__init__.py:85: UserWarning: Could not import the lzma module. Your installed Python is incomplete. Attempting to use lzma compression will result in a RuntimeError.
  warnings.warn(msg)
/usr/local/lib/python3.7/site-packages/pandas/compat/__init__.py:85: UserWarning: Could not import the lzma module. Your installed Python is incomplete. Attempting to use lzma compression will result in a RuntimeError.
  warnings.warn(msg)

Exercise -> Service:  MMX  Request:  prepareImages  
Context:  {'observation': '/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/CassinSparrowData/ebd_Cassins_2006.csv', 'species': 'Cassins Sparrow', 'startDate': '2006-01-01', 'endDate': '2007-01-01', 'collection': 'merra2_t1nxslv', 'vars': 'U10M V10M', 'operation': 'ave', 'EdasWorldClim': 'True', 'outDir': '/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/testWorldClim/TMworldClim_fac', 'numTrials': '2', 'numPredictors': '3', 'workflow': 'Rm', 'service': 'MMX', 'request': 'prepareImages', 'status': 'PENDING', 'source': 'EdasDev', 'images': ''}

Exercise -> Service:  MMX  Request:  runTrials  
Context:  {'observation': '/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/CassinSparrowData/ebd_Cassins_2006.csv', 'species': 'Cassins Sparrow', 'startDate': '2006-01-01', 'endDate': '2007-01-01', 'collection': 'merra2_t1nxslv', 'vars': 'U10M V10M', 'operation': 'ave', 'EdasWorldClim': 'True', 'outDir': '/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/testWorldClim/TMworldClim_fac', 'numTrials': '2', 'numPredictors': '3', 'workflow': 'Rm', 'service': 'MMX', 'request': 'runTrials', 'status': 'PENDING', 'source': 'EdasDev', 'images': '', 'imageDir': '/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/testWorldClim/TMworldClim_fac/merra', 'listOfIndexesInEachTrial': [[2, 4, 9], [7, 2, 8]]}
Processing /att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/testWorldClim/TMworldClim_fac/trials/trial-1/asc/bio-10_cip_merra2_mth_worldClim_2006.nc
Processing /att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/testWorldClim/TMworldClim_fac/trials/trial-2/asc/bio-9_cip_merra2_mth_worldClim_2006.nc
Warning 1: No UNIDATA NC_GLOBAL:Conventions attribute
Warning 1: No UNIDATA NC_GLOBAL:Conventions attribute
2 images remaining to process.
Processing /att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/testWorldClim/TMworldClim_fac/trials/trial-2/asc/bio-3_cip_merra2_mth_worldClim_2006.nc
2 images remaining to process.
Processing /att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/testWorldClim/TMworldClim_fac/trials/trial-1/asc/bio-5_cip_merra2_mth_worldClim_2006.nc
Warning 1: No UNIDATA NC_GLOBAL:Conventions attribute
Warning 1: No UNIDATA NC_GLOBAL:Conventions attribute
1 images remaining to process.
Processing /att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/testWorldClim/TMworldClim_fac/trials/trial-2/asc/bio-8_cip_merra2_mth_worldClim_2006.nc
1 images remaining to process.
Processing /att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/testWorldClim/TMworldClim_fac/trials/trial-1/asc/bio-3_cip_merra2_mth_worldClim_2006.nc
Warning 1: No UNIDATA NC_GLOBAL:Conventions attribute
Warning 1: No UNIDATA NC_GLOBAL:Conventions attribute
0 images remaining to process.
Running MaxEnt.
0 images remaining to process.
Running MaxEnt.

Exercise -> Service:  MMX  Request:  getTopPredictors  
Context:  {'observation': '/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/CassinSparrowData/ebd_Cassins_2006.csv', 'species': 'Cassins Sparrow', 'startDate': '2006-01-01', 'endDate': '2007-01-01', 'collection': 'merra2_t1nxslv', 'vars': 'U10M V10M', 'operation': 'ave', 'EdasWorldClim': 'True', 'outDir': '/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/testWorldClim/TMworldClim_fac', 'numTrials': '2', 'numPredictors': '3', 'workflow': 'Rm', 'service': 'MMX', 'request': 'getTopPredictors', 'status': 'PENDING', 'source': 'EdasDev', 'images': '', 'imageDir': '/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/testWorldClim/TMworldClim_fac/merra', 'listOfIndexesInEachTrial': [[2, 4, 9], [7, 2, 8]]}

Exercise -> Service:  MMX  Request:  runFinalModel  
Context:  {'observation': '/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/CassinSparrowData/ebd_Cassins_2006.csv', 'species': 'Cassins Sparrow', 'startDate': '2006-01-01', 'endDate': '2007-01-01', 'collection': 'merra2_t1nxslv', 'vars': 'U10M V10M', 'operation': 'ave', 'EdasWorldClim': 'True', 'outDir': '/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/testWorldClim/TMworldClim_fac', 'numTrials': '2', 'numPredictors': '3', 'workflow': 'Rm', 'service': 'MMX', 'request': 'runFinalModel', 'status': 'PENDING', 'source': 'EdasDev', 'images': '', 'imageDir': '/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/testWorldClim/TMworldClim_fac/merra', 'listOfIndexesInEachTrial': [[2, 4, 9], [7, 2, 8]]}
Processing /att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/testWorldClim/TMworldClim_fac/trials/trial-1/asc/bio-10_cip_merra2_mth_worldClim_2006.nc
Processing /att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/testWorldClim/TMworldClim_fac/trials/trial-2/asc/bio-9_cip_merra2_mth_worldClim_2006.nc
Warning 1: No UNIDATA NC_GLOBAL:Conventions attribute
Warning 1: No UNIDATA NC_GLOBAL:Conventions attribute
2 images remaining to process.
Processing /att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/testWorldClim/TMworldClim_fac/trials/trial-1/asc/bio-5_cip_merra2_mth_worldClim_2006.nc
2 images remaining to process.
Processing /att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/testWorldClim/TMworldClim_fac/trials/trial-2/asc/bio-3_cip_merra2_mth_worldClim_2006.nc
Warning 1: No UNIDATA NC_GLOBAL:Conventions attribute
Warning 1: No UNIDATA NC_GLOBAL:Conventions attribute
1 images remaining to process.
Processing /att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/testWorldClim/TMworldClim_fac/trials/trial-1/asc/bio-3_cip_merra2_mth_worldClim_2006.nc
1 images remaining to process.
Processing /att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/testWorldClim/TMworldClim_fac/trials/trial-2/asc/bio-8_cip_merra2_mth_worldClim_2006.nc
Warning 1: No UNIDATA NC_GLOBAL:Conventions attribute
Warning 1: No UNIDATA NC_GLOBAL:Conventions attribute
0 images remaining to process.
Running MaxEnt.
0 images remaining to process.
Running MaxEnt.
Processing /att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/testWorldClim/TMworldClim_fac/trials/trial-final/asc/bio-10_cip_merra2_mth_worldClim_2006.nc
Warning 1: No UNIDATA NC_GLOBAL:Conventions attribute
2 images remaining to process.
Processing /att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/testWorldClim/TMworldClim_fac/trials/trial-final/asc/bio-5_cip_merra2_mth_worldClim_2006.nc
Warning 1: No UNIDATA NC_GLOBAL:Conventions attribute
1 images remaining to process.
Processing /att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/testWorldClim/TMworldClim_fac/trials/trial-final/asc/bio-3_cip_merra2_mth_worldClim_2006.nc
Warning 1: No UNIDATA NC_GLOBAL:Conventions attribute
0 images remaining to process.
Running MaxEnt.
unsupported operand type(s) for |: 'dict' and 'dict'

Mmx chain finished.  Final Context: {'observation': '/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/CassinSparrowData/ebd_Cassins_2006.csv', 'species': 'Cassins Sparrow', 'startDate': '2006-01-01', 'endDate': '2007-01-01', 'collection': 'merra2_t1nxslv', 'vars': 'U10M V10M', 'operation': 'ave', 'EdasWorldClim': 'True', 'outDir': '/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/testWorldClim/TMworldClim_fac', 'numTrials': '2', 'numPredictors': '3', 'workflow': 'Rm', 'service': 'MMX', 'request': 'runFinalModel', 'status': 'PENDING', 'source': 'EdasDev', 'images': '', 'imageDir': '/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/testWorldClim/TMworldClim_fac/merra', 'listOfIndexesInEachTrial': [[2, 4, 9], [7, 2, 8]]}
# Examine MMX external output from within container.    
Singularity> ls -alt /att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/testWorldClim/TMworldClim_fac/trials/trial-final/
total 200
-rw-r--r-- 1 gtamkin k3000 21150 Feb 23 13:16 Cassins_Sparrow.png
drwxr-xr-x 4 gtamkin k3000  4096 Feb 23 13:16 .
-rw-r--r-- 1 gtamkin k3000 15099 Feb 23 13:16 maxent.log
-rw-r--r-- 1 gtamkin k3000 11065 Feb 23 13:16 Cassins_Sparrow.html
-rw-r--r-- 1 gtamkin k3000  3223 Feb 23 13:16 maxentResults.csv
drwxr-xr-x 2 gtamkin k3000  4096 Feb 23 13:16 plots
-rw-r--r-- 1 gtamkin k3000   229 Feb 23 13:16 Cassins_Sparrow_sampleAverages.csv
-rw-r--r-- 1 gtamkin k3000  1672 Feb 23 13:16 Cassins_Sparrow_thresholded.asc
-rw-r--r-- 1 gtamkin k3000  8565 Feb 23 13:16 Cassins_Sparrow.asc
-rw-r--r-- 1 gtamkin k3000 63721 Feb 23 13:16 Cassins_Sparrow_samplePredictions.csv
-rw-r--r-- 1 gtamkin k3000 17720 Feb 23 13:16 Cassins_Sparrow_omission.csv
-rw-r--r-- 1 gtamkin k3000  5653 Feb 23 13:16 Cassins_Sparrow.lambdas
drwxr-xr-x 3 gtamkin k3000  4096 Feb 23 13:16 asc
-rw-r--r-- 1 gtamkin k3000 29382 Feb 23 13:16 ebd_Cassins_2006.csv
drwxr-xr-x 5 gtamkin k3000  4096 Feb 23 13:16 ..
Singularity> date
Sun Feb 23 13:17:43 EST 2020
# Exit container and verity external output.    
Singularity> exit
exit
gtamkin@dsg101:/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity$ ls -alt /att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx/SystemTesting/testWorldClim/TMworldClim_fac/trials/trial-final/
total 200
-rw-r--r-- 1 gtamkin k3000 21150 Feb 23 13:16 Cassins_Sparrow.png
drwxr-xr-x 4 gtamkin k3000  4096 Feb 23 13:16 .
-rw-r--r-- 1 gtamkin k3000 15099 Feb 23 13:16 maxent.log
-rw-r--r-- 1 gtamkin k3000 11065 Feb 23 13:16 Cassins_Sparrow.html
-rw-r--r-- 1 gtamkin k3000  3223 Feb 23 13:16 maxentResults.csv
drwxr-xr-x 2 gtamkin k3000  4096 Feb 23 13:16 plots
-rw-r--r-- 1 gtamkin k3000   229 Feb 23 13:16 Cassins_Sparrow_sampleAverages.csv
-rw-r--r-- 1 gtamkin k3000  1672 Feb 23 13:16 Cassins_Sparrow_thresholded.asc
-rw-r--r-- 1 gtamkin k3000  8565 Feb 23 13:16 Cassins_Sparrow.asc
-rw-r--r-- 1 gtamkin k3000 63721 Feb 23 13:16 Cassins_Sparrow_samplePredictions.csv
-rw-r--r-- 1 gtamkin k3000 17720 Feb 23 13:16 Cassins_Sparrow_omission.csv
-rw-r--r-- 1 gtamkin k3000  5653 Feb 23 13:16 Cassins_Sparrow.lambdas
drwxr-xr-x 3 gtamkin k3000  4096 Feb 23 13:16 asc
-rw-r--r-- 1 gtamkin k3000 29382 Feb 23 13:16 ebd_Cassins_2006.csv
drwxr-xr-x 5 gtamkin k3000  4096 Feb 23 13:16 ..
# Run MMX inside of container from external command line.    
gtamkin@dsg101:/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity$ singularity run adapt-nosymlink-nosandbox.simg python3.7 /usr/local/mmx/innovation-lab/view/tests/MmxRequestCeleryView-adapt-gpfsfs.py

# Launch IDE (PyCharm) inside of container from external command line.    
gtamkin@dsg101:/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity$ singularity run -B /att adapt-nosymlink-nosandbox.simg sh /att/gpfsfs/briskfs01/ppl/gtamkin/bin/pycharm/bin/pycharm.sh&
[1] 18094
gtamkin@dsg101:/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity$ OpenJDK 64-Bit Server VM warning: Option UseConcMarkSweepGC was deprecated in version 9.0 and will likely be removed in a future release.


# Extend base with Jupyter Lab (and Firefox)
gtamkin@dsg101:/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity$ more mmx/ilab-mmx-base-jupyter.def 
## Generate container image using existing ilab MMX base image
Bootstrap: localimage
FROM: /att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/ilab-mmx-base.simg

%labels
    Author gtamkin
    Version v0.0.1

%environment
    JUP_PORT=8888
    JUP_IPNAME=localhost
    export JUP_PORT JUP_IPNAME

%startscript
    PORT=""
    if [ -n "$JUP_PORT" ]; then PORT="--port=${JUP_PORT}" fi
    IPNAME=""
    if [ -n "$JUP_IPNAME" ]; then
    IPNAME="--ip=${JUP_IPNAME}" fi
    exec jupyter lab --allow-root ${PORT} ${IPNAME}
    #exec jupyter notebook --allow-root ${PORT} ${IPNAME}

%post
    # install Firefox
    apt-get install -y firefox-esr

    # install JupyterLab
    python3.7 -m pip install --upgrade jupyterlab==1.2.6

# Build and run Jupyter Lab (and Firefox) container from command line
gtamkin@dsg101:/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity$ time sudo -E SINGULARITY_NOHTTPS=1 singularity build ilab-mmx-base-jupyter.simg mmx/ilab-mmx-base-jupyter.def 
gtamkin@dsg101:/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity$ singularity run ilab-mmx-base-jupyter.simg  jupyter lab &


DEMO SCRIPT (02/23/20) - END


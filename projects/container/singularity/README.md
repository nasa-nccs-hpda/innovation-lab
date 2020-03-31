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

For an overview of the general ILAB container architecture, see:
https://internal.nccs.nasa.gov/confluence/download/attachments/34472835/container-overview-03312020.pptx?api=v2

For specific details of the MMX application design, see:
https://internal.nccs.nasa.gov/confluence/download/attachments/34472835/Software-Task-Template-container-03312020.docx?api=v2

# Run steps (as ilab user on dsg103)

gtamkin@dsg103:~$ singularity run -B /att /att/nobackup/iluser/containers/ilab-mmx-1.0.0.simg 
```
python3.7 /att/nobackup/iluser/projects/ilab/src/innovation-lab/view/MmxRequestCommandLineView.py 
-f "/att/nobackup/iluser/projects/ilab/input/ebd_Cassins_2006.csv" 
-i "/att/nobackup/iluser/projects/ilab/input" 
-o "/tmp" 
-s "Cassins Sparrow" 
-sd "2006-01-01" 
-ed "2007-01-01" 
-c "merra2_t1nxslv" 
-v "U10M V10M" 
-op "ave" 
-ewc "True" 
-t "2" 
-p "3" 
-w "Rm" 
-m "/att/nobackup/iluser/ext/libraries/maxent.jar"
```

# Build steps (requires 'sudo' as iluser on dsg101)

## Checkout branch from git
[iluser@dsg101 src]$$ cd /att/gpfsfs/briskfs01/ppl/iluser/projects/ilab/src

[iluser@dsg101 src]$$ git clone https://github.com/nasa-nccs-hpda/innovation-lab.git

[iluser@dsg101 src]$$ cd innovation-lab/

[iluser@dsg101 src]$ git checkout -b MmxRequestCeleryView origin/MmxRequestCeleryView

[iluser@dsg101 innovation-lab]$ ls -alt view/

total 36
drwxr-xr-x 3 iluser ilab 4096 Mar 28 07:29 .
-rwxr-xr-x 1 iluser ilab 2233 Mar 28 07:29 MaxEntRequestCommandLineView.py
-rwxr-xr-x 1 iluser ilab 5504 Mar 28 07:29 MmxRequestCommandLineView.py
-rwxr-xr-x 1 iluser ilab 2619 Mar 28 07:29 MmxRequestJSONView.py
-rwxr-xr-x 1 iluser ilab 5325 Mar 28 07:29 MmxRequestTranslationView.py
drwxr-xr-x 3 iluser ilab 4096 Mar 28 07:29 tests
drwxr-xr-x 7 iluser ilab 4096 Mar 28 07:29 ..
-rw-r--r-- 1 iluser ilab    0 Mar 28 07:28 __init__.py

## Configure dependencies

[iluser@dsg101 ext]$ cd /att/gpfsfs/briskfs01/ppl/iluser/ext

[iluser@dsg101 ext]$ ls -alRt | more
```

.:
total 0
drwxr-xr-x 6 iluser ilab 4096 Mar 28 09:16 ..
drwxr-xr-x 4 iluser ilab 4096 Mar 28 09:15 .
drwxr-xr-x 2 iluser ilab 4096 Mar 28 09:15 libraries
drwxr-xr-x 4 iluser ilab 4096 Mar 28 09:08 bin

./libraries:
total 624
drwxr-xr-x 4 iluser ilab   4096 Mar 28 09:15 ..
drwxr-xr-x 2 iluser ilab   4096 Mar 28 09:15 .
-rwxr-xr-x 1 iluser ilab 637214 Mar 28 08:44 maxent.jar

./bin:
total 0
drwxr-xr-x  4 iluser ilab 4096 Mar 28 09:15 ..
drwxr-xr-x  4 iluser ilab 4096 Mar 28 09:08 .
drwxr-xr-x  6 iluser ilab 4096 Mar 28 07:48 jre1.8.0_221
drwxr-xr-x 10 iluser ilab 4096 Mar 28 07:48 pycharm
```

gtamkin@dsg101:/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity/mmx$ sh /att/gpfsfs/briskfs01/ppl/iluser/ext/bin/pycharm/bin/pycharm.sh&

[iluser@dsg101 containers]$ cd /att/gpfsfs/briskfs01/ppl/iluser/containers

[iluser@dsg101 containers]$ ln -sf /att/gpfsfs/briskfs01/ppl/iluser/projects/ilab/src/innovation-lab/projects/container/singularity/*.def .

[iluser@dsg101 containers]$ ln -sf /att/gpfsfs/briskfs01/ppl/iluser/projects/ilab/src/innovation-lab/projects/container/singularity/*.sh .

[iluser@dsg101 containers]$ ls -alt
```

total 0
lrwxrwxrwx 1 iluser ilab  117 Mar 28 09:27 build-ilab-iluser.sh -> /att/gpfsfs/briskfs01/ppl/iluser/projects/ilab/src/innovation-lab/projects/container/singularity/build-ilab-iluser.sh
drwxr-xr-x 2 iluser ilab 4096 Mar 28 09:27 .
lrwxrwxrwx 1 iluser ilab  116 Mar 28 09:18 ilab-core-1.0.0.def -> /att/gpfsfs/briskfs01/ppl/iluser/projects/ilab/src/innovation-lab/projects/container/singularity/ilab-core-1.0.0.def
lrwxrwxrwx 1 iluser ilab  116 Mar 28 09:18 ilab-apps-1.0.0.def -> /att/gpfsfs/briskfs01/ppl/iluser/projects/ilab/src/innovation-lab/projects/container/singularity/ilab-apps-1.0.0.def
lrwxrwxrwx 1 iluser ilab  124 Mar 28 09:18 cisto-jupyter-lab-1.0.0.def -> /att/gpfsfs/briskfs01/ppl/iluser/projects/ilab/src/innovation-lab/projects/container/singularity/cisto-jupyter-lab-1.0.0.def
lrwxrwxrwx 1 iluser ilab  125 Mar 28 09:18 cisto-data-science-1.0.0.def -> /att/gpfsfs/briskfs01/ppl/iluser/projects/ilab/src/innovation-lab/projects/container/singularity/cisto-data-science-1.0.0.def
drwxr-xr-x 6 iluser ilab 4096 Mar 28 09:16 ..
```

[iluser@dsg101 singularity]$ more build-ilab-iluser.sh 
```
echo "Build ilab container stack"
echo /bin/time /usr/bin/sudo -E SINGULARITY_NOHTTPS=1 /usr/bin/singularity build cisto-data-science-1.0.0.simg cisto-data-science-1.0.0.def
/bin/time /usr/bin/sudo -E SINGULARITY_NOHTTPS=1 /usr/bin/singularity build cisto-data-science-1.0.0.simg cisto-data-science-1.0.0.def
echo /bin/time /usr/bin/sudo -E SINGULARITY_NOHTTPS=1  /usr/bin/singularity build ilab-core-1.0.0.simg  ilab-core-1.0.0.def
/bin/time /usr/bin/sudo -E SINGULARITY_NOHTTPS=1 /usr/bin/singularity build ilab-core-1.0.0.simg  ilab-core-1.0.0.def
echo /bin/time /usr/bin/sudo -E SINGULARITY_NOHTTPS=1 /usr/bin/singularity build ilab-mmx-1.0.0.simg  ilab-mmx-1.0.0.def
/bin/time /usr/bin/sudo -E SINGULARITY_NOHTTPS=1 /usr/bin/singularity build ilab-mmx-1.0.0.simg  ilab-mmx-1.0.0.def
echo /bin/time /usr/bin/sudo -E SINGULARITY_NOHTTPS=1 /usr/bin/singularity build ilab-apps-1.0.0.simg  ilab-apps-1.0.0.def
/bin/time /usr/bin/sudo -E SINGULARITY_NOHTTPS=1 /usr/bin/singularity build ilab-apps-1.0.0.simg  ilab-apps-1.0.0.def
echo /bin/time /usr/bin/sudo -E SINGULARITY_NOHTTPS=1 /usr/bin/singularity build cisto-jupyter-lab-1.0.0.simg  cisto-jupyter-lab-1.0.0.def
/bin/time /usr/bin/sudo -E SINGULARITY_NOHTTPS=1 /usr/bin/singularity build cisto-jupyter-lab-1.0.0.simg  cisto-jupyter-lab-1.0.0.def
```
[iluser@dsg101 containers]$ source ~/.bashrc

[iluser@dsg101 containers]$ env | grep SING
```
SINGULARITY_TMPDIR=/att/gpfsfs/briskfs01/ppl/iluser/singularity-cache
SINGULARITY_CACHEDIR=/att/gpfsfs/briskfs01/ppl/iluser/singularity-cache
```

[iluser@dsg101 containers]$ pwd
/att/gpfsfs/briskfs01/ppl/iluser/containers

[iluser@dsg101 containers]$ time sh build-ilab-iluser.sh 2>&1 | tee -a build-ilab-iluser-03282020.out
```

Build ilab container stack
/bin/time /usr/bin/sudo -E SINGULARITY_NOHTTPS=1 /usr/bin/singularity build cisto-data-science-1.0.0.simg cisto-data-science-1.0.0.def
INFO:    Starting build...
Getting image source signatures
Copying blob sha256:3192219afd04f93d90f0af7f89cb527d1af2a16975ea391ea8517c602ad6ddb6
……… . . . 
```

[iluser@dsg101 containers]$ ls -alt
total 4751432
-rw-r--r-- 1 iluser ilab     943499 Mar 28 11:46 build-ilab-iluser-03282020.out
-rwxr-xr-x 1 iluser ilab 1562017792 Mar 28 11:39 cisto-jupyter-lab-1.0.0.simg
drwxr-xr-x 2 iluser ilab       4096 Mar 28 11:39 .
-rwxr-xr-x 1 iluser ilab 1433083904 Mar 28 11:07 ilab-apps-1.0.0.simg
-rwxr-xr-x 1 iluser ilab 1003683840 Mar 28 10:38 ilab-core-1.0.0.simg
-rwxr-xr-x 1 iluser ilab  865726464 Mar 28 10:11 cisto-data-science-1.0.0.simg
lrwxrwxrwx 1 iluser ilab        117 Mar 28 09:27 build-ilab-iluser.sh -> /att/gpfsfs/briskfs01/ppl/iluser/projects/ilab/src/innovation-lab/projects/container/singularity/build-ilab-iluser.sh
lrwxrwxrwx 1 iluser ilab        116 Mar 28 09:18 ilab-core-1.0.0.def -> /att/gpfsfs/briskfs01/ppl/iluser/projects/ilab/src/innovation-lab/projects/container/singularity/ilab-core-1.0.0.def
lrwxrwxrwx 1 iluser ilab        116 Mar 28 09:18 ilab-apps-1.0.0.def -> /att/gpfsfs/briskfs01/ppl/iluser/projects/ilab/src/innovation-lab/projects/container/singularity/ilab-apps-1.0.0.def
lrwxrwxrwx 1 iluser ilab        124 Mar 28 09:18 cisto-jupyter-lab-1.0.0.def -> /att/gpfsfs/briskfs01/ppl/iluser/projects/ilab/src/innovation-lab/projects/container/singularity/cisto-jupyter-lab-1.0.0.def
lrwxrwxrwx 1 iluser ilab        125 Mar 28 09:18 cisto-data-science-1.0.0.def -> /att/gpfsfs/briskfs01/ppl/iluser/projects/ilab/src/innovation-lab/projects/container/singularity/cisto-data-science-1.0.0.def
drwxr-xr-x 6 iluser ilab       4096 Mar 28 09:16 ..

### Optionally run PyCharm IDE via container
gtamkin@dsg101:/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity$ cd /att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity

gtamkin@dsg101:/att/gpfsfs/briskfs01/ppl/gtamkin/mmx-singularity$ singularity run -B /att /att/gpfsfs/briskfs01/ppl/iluser/containers/ilab-apps-1.0.0.simg sh /att/gpfsfs/briskfs01/ppl/gtamkin/bin/pycharm/bin/pycharm.sh&

## Shell into the container and examine dependencies

[iluser@dsg101 src]$ singularity shell -B /att /att/nobackup/iluser/containers/ilab-mmx-1.0.0.simg 
```
Singularity> pip freeze
amqp==2.5.2
attrs==19.3.0
backcall==0.1.0
billiard==3.6.3.0
bleach==3.1.4
boto3==1.12.3
botocore==1.15.31
celery==4.3.0
certifi==2019.11.28
cffi==1.14.0
chardet==3.0.4
click==7.1.1
cloudpickle==1.3.0
cryptography==2.8
cycler==0.10.0
dask==2.3.0
decorator==4.4.1
defusedxml==0.6.0
dill==0.3.1.1
distributed==2.5.2
docutils==0.15.2
entrypoints==0.3
GDAL==2.1.3
h5py==2.9.0
HeapDict==1.0.1
idna==2.8
imageio==2.8.0
importlib-metadata==1.6.0
ipykernel==5.1.4
ipython==7.12.0
ipython-genutils==0.2.0
ipywidgets==7.5.1
jedi==0.16.0
Jinja2==2.11.1
jmespath==0.9.5
joblib==0.14.1
jsonschema==3.2.0
jupyter-client==6.1.2
jupyter-core==4.6.3
kiwisolver==1.1.0
kombu==4.6.8
llvmlite==0.31.0
MarkupSafe==1.1.1
matplotlib==3.1.3
mistune==0.8.4
msgpack==1.0.0
nbconvert==5.6.1
nbformat==5.0.4
networkx==2.4
notebook==6.0.3
numba==0.45.1
numexpr==2.6.9
numpy==1.18.1
packaging==20.3
pandas==0.25.3
pandocfilters==1.4.2
parso==0.6.2
pexpect==4.8.0
pickleshare==0.7.5
Pillow==7.0.0
prometheus-client==0.7.1
prompt-toolkit==3.0.5
protobuf==3.11.3
protobuf3-to-dict==0.1.5
psutil==5.7.0
ptyprocess==0.6.0
pycparser==2.20
Pygments==2.6.1
pyparsing==2.4.6
pyrsistent==0.16.0
python-dateutil==2.8.1
pytz==2019.3
PyWavelets==1.1.1
PyYAML==5.3.1
pyzmq==19.0.0
requests==2.22.0
s3transfer==0.3.3
sagemaker==1.50.13
scikit-image==0.15.0
scikit-learn==0.21.3
scipy==1.3.3
seaborn==0.9.0
Send2Trash==1.5.0
six==1.14.0
smdebug-rulesconfig==0.1.2
sortedcontainers==2.1.0
tblib==1.6.0
terminado==0.8.3
testpath==0.4.4
toolz==0.10.0
tornado==6.0.4
traitlets==4.3.3
urllib3==1.24.3
vine==1.3.0
wcwidth==0.1.9
webencodings==0.5.1
widgetsnbextension==3.5.1
zict==2.0.0
zipp==3.1.0
Singularity> 
```
## Examine MMX runtime script.  Note: 1) runs full MMX with static pre-processed data, 2) use Celery to run chained tasks, 3) hard-coded json parameters for now.
```
Singularity> more /usr/local/mmx/projects/ilab/src/innovation-lab/view/MmxRequestCommandLineView.py 
from celery import Celery
from celery import chain
from celery.utils.log import get_task_logger
import json
import os
import argparse

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
    deletStr = "rm -rf " + context['outDir'] + "/trials/*"
    os.system(deletStr)
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

# -----------------------------------------------------------------------------
# main
#
# Example CLI/API invocation:
# cd innovation-lab
# export PYTHONPATH=`pwd`
# view/MmxRequestCommandLineView.py
#-f "/att/gpfsfs/briskfs01/ppl/iluser/mmx/input/ebd_Cassins_2006.csv"
#-i "/att/gpfsfs/briskfs01/ppl/iluser/mmx/input"
#-o "/att/gpfsfs/briskfs01/ppl/iluser/mmx/output"
#-s "Cassins Sparrow"
#-sd "2006-01-01"
#-ed "2007-01-01"
#-c "merra2_t1nxslv"
#-v "U10M V10M"
#-op "ave"
#-ewc "True"
#-t "2"
#-p "3"
#-w "Rm"
#-m "/att/gpfsfs/briskfs01/ppl/iluser/ext/libraries/maxent.jar"
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Process command-line args.
    desc = 'This application runs Maximum Entropy.'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-f',
                        required=True,
                        help='Path to observation file')

    parser.add_argument('-i',
                        required=True,
                        help='Path to directory of input image files')

    parser.add_argument('-o',
                        required=True,
                        help='Path to output directory')

    parser.add_argument('-s',
                        default='Cassins Sparrow',
                        help='Name of species in observation file')

    parser.add_argument('-sd',
                        default='2006-01-01',
                        help='Start date')

    parser.add_argument('-ed',
                        default='2007-01-01',
                        help='End date')

    parser.add_argument('-c',
                        default='merra2_t1nxslv',
                        help='Collection')

    parser.add_argument('-v',
                        default='U10M V10M',
                        help='Variables')

    parser.add_argument('-op',
                        default='ave',
                        help='Operation')

    parser.add_argument('-ewc',
                        default='True',
                        help='EdasWorldClim on')

    parser.add_argument('-t',
                        default='2',
                        help='Number of trials')

    parser.add_argument('-p',
                        default='3',
                        help='Number of predictors')

    parser.add_argument('-w',
                        default='Rm',
                        help='Workflow')

    parser.add_argument('-m',
                        default='/att/gpfsfs/briskfs01/ppl/iluser/ext/libraries/maxent.jar',
                        help='Path to Maximum Entropy jar')

    args = parser.parse_args()
    print(args.s)

    # format key value pairs for json
    observation = "\"observation\"" + ":\"" + args.f + "\""
    inDir = "\"inDir\"" + ":\"" + args.i + "\""
    outDir = "\"outDir\"" + ":\"" + args.o + "\""
    species = "\"species\"" + ":\"" + args.s + "\""
    startDate = "\"startDate\"" + ":\"" + args.sd + "\""
    endDate = "\"endDate\"" + ":\"" + args.ed + "\""
    collection = "\"collection\"" + ":\"" + args.c + "\""
    vars = "\"vars\"" + ":\"" + args.v + "\""
    operation = "\"operation\"" + ":\"" + args.op + "\""
    edasWorldClim = "\"EdasWorldClim\"" + ":\"" + args.ewc + "\""
    numTrials = "\"numTrials\"" + ":\"" + args.t + "\""
    numPredictors = "\"numPredictors\"" + ":\"" + args.p + "\""
    workflow = "\"workflow\"" + ":\"" + args.w + "\""
    maxEntPath = "\"maxEntPath\"" + ":\"" + args.m + "\""

    # create key/value pair string
    json_string = "{" + observation + "," + \
        inDir +  "," + \
        outDir +  "," + \
        species +  "," + \
        startDate + "," + \
        endDate + "," + \
        collection + "," + \
        vars + "," + \
        operation + "," + \
        edasWorldClim + "," + \
        numTrials + "," + \
        numPredictors + "," + \
        workflow + "," + \
        maxEntPath + "}"

    # convert string to JSON format (simulates AWS Lambda invocation)
    context = json.loads(json_string)
    print("\nMmx chain starting.  Initial Context:", context)
    chain_func(context)

```








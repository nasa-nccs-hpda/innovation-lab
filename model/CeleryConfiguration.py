from celery import Celery
from socket import socket
import os


# -----------------------------------------------------------------------------
# CeleryConfiguration
#
# Contains Celery/Redis server configuration
# -----------------------------------------------------------------------------

# Configuration keys:
IL_BACKEND = "_IL_backend"
IL_BROKER = "_IL_broker"
IL_CONCURRENCY = "_IL_concurrency"
IL_CONFIG = "_IL_celeryConfig"
IL_HOST = "_IL_host"
IL_LOGLEVEL = "_IL_loglevel"
IL_PORT = "_IL_port"

# -----------------------------------------------------------------------------
# REQUIRED:  Modify the next statement to include your distributed tasks.
# Note that PYTHONPATH must resolve this.
#
# _IL_include ='model.Tasks'
# OPTIONAL:  Modify the following defaults as desired
# -----------------------------------------------------------------------------

# Initialize defaults and add to context
_IL_port = '6388'

with socket() as s:
    s.bind(('', 0))
    # To automatically find a free port, uncomment the next line:
    # _IL_port = str(s.getsockname()[1]) + '/0'

_IL_broker = 'redis://'
_IL_host = 'localhost'
_IL_broker = _IL_broker + _IL_host + ':' + _IL_port + '/0'
_IL_backend =_IL_broker
_IL_pythonpath = './innovation-lab'

# Concatenate existing PYTHONPATH to allow runtime extenstion
if os.environ["PYTHONPATH"] != None:
    _IL_pythonpath + ':$' + os.environ["PYTHONPATH"]

# Create context map of key value pairs called 'app'
inclModules = \
    ['model.MaxEntRequestCelery',
     'model.MmxRequestCelery',
     'projects.aviris_regression_algorithms.model.ApplyAlgorithmCelery']

app = Celery('innovation-lab',
             backend='redis://localhost:6379/0',
             broker='redis://localhost:6379/0',
             include=inclModules)

app.conf.accept_content = ['application/json',
                           'json',
                           'pickle',
                           'application/x-python-serialize']

app.conf.setdefault(IL_BACKEND, _IL_backend)
app.conf.setdefault(IL_BROKER, _IL_broker)
# Uncomment and set next line to specify number of threads (defaults to max)
# app.conf.setdefault(IL_CONCURRERNCY, '8')
app.conf.setdefault(IL_CONFIG, 'model.CeleryConfiguration')
app.conf.setdefault(IL_HOST, _IL_host)
app.conf.setdefault(IL_LOGLEVEL, 'info')
app.conf.setdefault(IL_PORT, _IL_port)


from celery import Celery
from socket import socket
import os

#-----------------------------------------
# REQUIRED:  Modify the next statement to include your distributed tasks.  Note that PYTHONPATH must resolve this.
_IL_include ='model.Tasks'

#-----------------------------------------
#OPTIONAL:  Modify the following defaults as desired

# Initialize defaults and add to context
_IL_port = '6388'

with socket() as s:
    s.bind(('', 0))
    # To automatically find a free port, uncomment the next line:
    #_IL_port = str(s.getsockname()[1]) + '/0'
#dsg101 - eth0, eth1
_IL_host = '10.100.35.214'
#_IL_host = '10.100.161.24'
#_IL_host = 'localhost'
#dsg103 - eth0, eth1
#_IL_host = '10.100.35.216'
#_IL_host = '10.100.161.26'
_IL_broker = 'redis://'
#_IL_host = 'localhost'
_IL_broker = _IL_broker + _IL_host + ':' + _IL_port + '/0'
_IL_backend =_IL_broker
_IL_pythonpath = './innovation-lab'

if os.environ["PYTHONPATH"] != None:
    _IL_pythonpath + ':$' + os.environ["PYTHONPATH"]

app = Celery(_IL_pythonpath,
             broker=_IL_broker,
             backend=_IL_backend,
             include=[_IL_include])

app.conf.accept_content = ['application/json',
                           'json',
                           'pickle',
                           'application/x-python-serialize']

app.conf.setdefault('_IL_broker', _IL_broker)
app.conf.setdefault('_IL_backend', _IL_backend)
app.conf.setdefault('_IL_host', _IL_host)
app.conf.setdefault('_IL_port', _IL_port)
app.conf.setdefault('_IL_loglevel', 'info')
app.conf.setdefault('_IL_celeryConfig', 'model.CeleryConfiguration')
# Uncomment and set the next line to specify number of threads (defaults to max when not set)
#app.conf.setdefault('_IL_concurrency', '10')

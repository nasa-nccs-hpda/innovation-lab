#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from redis import exceptions
import subprocess
import sys

import os
from model.CeleryConfiguration import app
# -----------------------------------------------------------------------------
# class MultiThreader
# -----------------------------------------------------------------------------
class ILProcessController():
    _backendProcessId = 0
    _celeryConfig = None

    # -------------------------------------------------------------------------
    # runTrials - run trials concurrently (convenience method with knowledge of trial parms)
    # -------------------------------------------------------------------------
    def __enter__(self):

        print('In ILProcessController.__enter__()')

        try:

            # Start the Celery Server
            _backendPort = app.conf.get("_IL_port")
            self._backendProcessId = (subprocess.Popen(["/usr/local/bin/redis-server",
                                                        "--protected-mode",
                                                        "no",
                                                        "--port",
                                                        str(_backendPort)],
                                                        stdout=subprocess.PIPE)).pid

            print ("backendProcessId = ", self._backendProcessId, _backendPort)

            # Start the Celery Workers - defaults to max available [add --concurrency=X to throttle threads]
            self._celeryConfig = app.conf.get("_IL_celeryConfig")
            _concurrency = app.conf.get("_IL_concurrency")
            if _concurrency != None:
                _concurrencyStr = " --concurrency=" + _concurrency
            else:
                _concurrencyStr = ""

            _logLevel = app.conf.get("_IL_loglevel")
            _worker = "/usr/local/bin/celery -A " + \
                                     self._celeryConfig + " worker " + \
                                     _concurrencyStr + \
                                     " --loglevel=" + _logLevel + \
                                     " &"

            retcode = subprocess.run(_worker,
                                     shell=True,
                                     check=True)
            print (retcode)

        except OSError as e:
            print("Execution failed:", e, file=sys.stderr)


    # -------------------------------------------------------------------------
    # runTrials - run trials concurrently (convenience method with knowledge of trial parms)
    # -------------------------------------------------------------------------
    def __exit__(self, type, value, traceback):

        try:
            print('In ILProcessController.__exit__()', self._backendProcessId)

            # Shutdown the Celery workers
            shutdownWorkers = "/usr/bin/pkill -9 -f  " + self._celeryConfig
            os.system(shutdownWorkers)

            # Shutdown the Celery Server - TODO - Shutdown Redis cleanly - works now with uncaught exception
#            shutdownServer = str("/bin/kill -9 " + str(self._backendProcessId))
#            os.system(shutdownServer)

            return True

        except exceptions.ConnectionError as inst:
            print("Connection Error ignore")
        except OSError as e:
            print("Execution failed:", e, file=sys.stderr)
        except Exception as inst:
            print(type(inst))  # the exception instance
            print(inst.args)  # arguments stored in .args
            print(inst)  # __str__ allows args to be printed directly,


#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from celery import Celery
import subprocess
import sys
from socket import socket
import os

# -----------------------------------------------------------------------------
# class MultiThreader
# -----------------------------------------------------------------------------
#class ILProcessController(object):
class ILProcessController():
    backendProcessId = 0

    # -------------------------------------------------------------------------
    # runTrials - run trials concurrently (convenience method with knowledge of trial parms)
    # -------------------------------------------------------------------------
    def __enter__(self):

    # Start the Celery Server
    # Start the Celery Workers
        print('In ILProcessController.__enter__()')

        try:
            with socket() as s:
                s.bind(('', 0))
                backendPort = s.getsockname()[1]

            #redis-server --protected-mode no --port 6380
            backendPort = 6380
            self.backendProcessId = (subprocess.Popen(["/usr/local/bin/redis-server", "--protected-mode", "no", "--port", str(backendPort)], stdout=subprocess.PIPE)).pid
            print ("backendProcessId = ", self.backendProcessId, backendPort)

#            workerProcessId = (
#                subprocess.Popen(["/usr/local/bin/celery", "-A", "model.tests.test_Tasks", "--config=model.tests.celeryconfig", "--loglevel=info", "--concurrency=3"],
#                     stdout=subprocess.PIPE)).pid
#            print("workerProcessId = ", workerProcessId)

#            retcode = subprocess.run("/usr/local/bin/redis-server --protected-mode no --port 6380 &", shell=True, check=True)
#            if retcode.returncode < 0:
#                print("Child was terminated by signal", -retcode, file=sys.stderr)
#            else:
#                print("Child returned", retcode, file=sys.stderr)
            retcode = subprocess.run("/usr/local/bin/celery -A model.Tasks worker --config=model.tests.celeryconfig --loglevel=info --concurrency=3 &", shell=True,
                                         check=True)
            print (retcode)

        except OSError as e:
            print("Execution failed:", e, file=sys.stderr)


    # -------------------------------------------------------------------------
    # runTrials - run trials concurrently (convenience method with knowledge of trial parms)
    # -------------------------------------------------------------------------
    def __exit__(self, type, value, traceback):

        try:
            print('In ILProcessController.__exit__()', self.backendProcessId)

            # Shutdown the Celery workers
            shutdownWorkers = "/usr/bin/pkill -9 -f \'model.Tasks worker\' "
            os.system(shutdownWorkers)

            # Shutdown the Celery Server
            shutdownServer = str("/bin/kill -9 " + str(self.backendProcessId))
            os.system(shutdownServer)

        except OSError as e:
            print("Execution failed:", e, file=sys.stderr)


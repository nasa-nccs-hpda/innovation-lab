#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import argparse
import sys
import time

from model.MmxRequest import MmxRequest


# -----------------------------------------------------------------------------
# main
#
# cd innovation-lab
# export PYTHONPATH=`pwd`
# mkdir ~/SystemTesting/testMmx
# mkdir ~/SystemTesting/testMaxEnt/merra
# view/MmxRequestCommandLineView.py
# -f ~/SystemTesting/MaxEntData/GSENM_cheat_pres_abs_2001.csv
# -s "Cheat Grass" --start_date 2013-02-03 --end_date 2013-03-12
# -o ~/SystemTesting/testMaxEnt/
# -----------------------------------------------------------------------------
def main():

    context = {
        'observation' : '/att/nobackup/jli30/SystemTesting/CassinSparrowData/ebd_Cassins_2016.csv',
        'species'     : 'Cassins Sparrow',
        'outDir'      : '/att/nobackup/jli30/SystemTesting/testWorldClim/debug',
        'workflow'    : 'Parallel',
        'numPredictors' : 10,
        'numTrials'     : 10,
        'startDate'     : '2016-01-01',
        'endDate'       : '2017-01-01',
        'EdasWorldClim' : True,

    }
    print("test"+sys.argv[1])
    context['count'] = int(sys.argv[1])

    # Dynamically select workflow request (defaults to MmxRequest)
    clazzName = "Mmx{0}Request".format(context['workflow'])
    # import the class from module
    mod = __import__("model.{0}".format(clazzName), globals(), locals(), [clazzName])
    requestInstance = getattr(mod, clazzName)
    mmxr = requestInstance(context)
    t0=time.time()
    mmxr.run()
    print("Run Time in "+str(time.time()-t0)+" Seconds")

# ------------------------------------------------------------------------------
# Invoke the main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(main())


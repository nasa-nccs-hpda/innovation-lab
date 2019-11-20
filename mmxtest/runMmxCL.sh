#!/bin/bash
source ~/.bashrc
conda activate edas-stratus

export PYTHONPATH=/att/nobackup/jli30/innovation-lab/edask/stratus_endpoint:/att/nobackup/jli30/innovation-lab/edask/stratus/stratus/:/att/nobackup/jli30/innovation-lab/edask/stratus:/att/nobackup/jli30/innovation-lab/mmx/innovation-lab:{$PYTHONPATH}

echo "Ready for Python Run"

CODE=/att/nobackup/jli30/innovation-lab/mmx/innovation-lab/view
python $CODE/MmxMpTry.py $1 

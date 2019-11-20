#!/bin/bash
trials=90

################################################################################
s=$(date +%s)
parallel --sshloginfile nodelist --workdir $PWD sh runMmxCL.sh {}> std.log ::: $(seq 0 10 $trials) 

e=$(date +%s)

echo "It takes $(($e-$s)) seconds to complete"

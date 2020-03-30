echo "Build ilab container stack"
echo /bin/time /usr/bin/sudo -E SINGULARITY_NOHTTPS=1 /usr/bin/singularity build cisto-data-science-1.0.0.simg cisto-data-science-1.0.0.def
/bin/time /usr/bin/sudo -E SINGULARITY_NOHTTPS=1 /usr/bin/singularity build cisto-data-science-1.0.0.simg cisto-data-science-1.0.0.def
echo /bin/time /usr/bin/sudo -E SINGULARITY_NOHTTPS=1  /usr/bin/singularity build ilab-core-1.0.0.simg  ilab-core-1.0.0.def
/bin/time /usr/bin/sudo -E SINGULARITY_NOHTTPS=1 /usr/bin/singularity build ilab-core-1.0.0.simg  ilab-core-1.0.0.def
echo /bin/time /usr/bin/sudo -E SINGULARITY_NOHTTPS=1 /usr/bin/singularity build ilab-mmx-1.0.0.simg  ilab-apps-1.0.0.def
/bin/time /usr/bin/sudo -E SINGULARITY_NOHTTPS=1 /usr/bin/singularity build ilab-mmx-1.0.0.simg  ilab-apps-1.0.0.def
echo /bin/time /usr/bin/sudo -E SINGULARITY_NOHTTPS=1 /usr/bin/singularity build ilab-apps-1.0.0.simg  ilab-apps-1.0.0.def
/bin/time /usr/bin/sudo -E SINGULARITY_NOHTTPS=1 /usr/bin/singularity build ilab-apps-1.0.0.simg  ilab-apps-1.0.0.def
echo /bin/time /usr/bin/sudo -E SINGULARITY_NOHTTPS=1 /usr/bin/singularity build cisto-jupyter-lab-1.0.0.simg  cisto-jupyter-lab-1.0.0.def
/bin/time /usr/bin/sudo -E SINGULARITY_NOHTTPS=1 /usr/bin/singularity build cisto-jupyter-lab-1.0.0.simg  cisto-jupyter-lab-1.0.0.def

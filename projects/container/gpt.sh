#! /bin/sh

export SEADAS_HOME=/usr/local/seadas-7.5.3

if [ -z "$SEADAS_HOME" ]; then
    echo
    echo Error: SEADAS_HOME not found in your environment.
    echo Please set the SEADAS_HOME variable in your environment to match the
    echo location of the SeaDAS 7.x installation
    echo
    exit 2
fi

. "$SEADAS_HOME/bin/detect_java.sh"

"$app_java_home/bin/java" \
    -Xmx10G \
    -Dceres.context=seadas \
    "-Dseadas.mainClass=org.esa.beam.framework.gpf.main.GPT" \
    "-Dseadas.home=$SEADAS_HOME" \
    "-Dncsa.hdf.hdflib.HDFLibrary.hdflib=$SEADAS_HOME/modules/lib-hdf-2.7/lib/libjhdf.so" \
    "-Dncsa.hdf.hdf5lib.H5.hdf5lib=$SEADAS_HOME/modules/lib-hdf-2.7/lib/libjhdf5.so" \
    -jar "$SEADAS_HOME/bin/ceres-launcher.jar" "$@"

exit $?

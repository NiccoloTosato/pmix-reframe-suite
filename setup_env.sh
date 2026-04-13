#!/bin/bash

MYROOTDIR=$(pwd)



# Some ReFrame envvars that are helpful for us:
export RFM_KEEP_STAGE_FILES=1
export RFM_CONFIG_FILES=${MYROOTDIR}/sysconfig.yaml
export RFM_PREFIX=${MYROOTDIR}/outputdir
export RFM_REPORT_FILE=/dev/null
source .venv/bin/activate

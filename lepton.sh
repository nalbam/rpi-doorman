#!/bin/bash

LEPTON_AUTO=${LEPTON_AUTO:-N}
LEPTON_BASE=${LEPTON_BASE:-633.5}
LEPTON_MIN=${LEPTON_MIN:-12}
LEPTON_MAX=${LEPTON_MAX:-37}

pushd ~/LeptonModule/software/raspberrypi_video

if [ ! -f raspberrypi_video ]; then
  qmake && make
fi

PARAMS="-mirror -base ${LEPTON_BASE} -min ${LEPTON_MIN} -max ${LEPTON_MAX}"

if [ "${LEPTON_AUTO}" == "Y" ]; then
  PARAMS="${PARAMS} -auto"
fi

./raspberrypi_video ${PARAMS}

popd

#!/bin/bash

pushd ~/LeptonModule/software/raspberrypi_video

if [ ! -f raspberrypi_video ]; then
  qmake && make
fi

./raspberrypi_video -mirror -min 20 -max 37

popd

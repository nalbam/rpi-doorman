#!/bin/bash

pushd ~/rpi-doorman

  git pull

popd

pushd ~/LeptonModule

  git pull

  pushd ./software/raspberrypi_video
    qmake && make
  popd

popd

#!/bin/bash

./LeptonModule/software/raspberrypi_video/raspberrypi_video -mirror -min 29000 -max 31200

./rpi-doorman/camera.py

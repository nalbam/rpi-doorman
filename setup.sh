#!/bin/bash

sudo apt update
sudo apt upgrade -y

sudo apt install -y xscreensaver
sudo apt install -y build-essential cmake pkg-config qt5-default
sudo apt install -y libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev

sudo apt install -y libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt install -y libxvidcore-dev libx264-dev
sudo apt install -y libgtk2.0-dev libgtk-3-dev
sudo apt install -y libatlas-base-dev gfortran

sudo apt install -y python2.7-dev python3-dev

sudo apt install -y python3-scipy python3-pygame

sudo apt autoremove -y

pip3 install boto3
pip3 install cmake
pip3 install colour
pip3 install cython
pip3 install opencv-python==3.4.6.27
pip3 install scipy

pip3 install adafruit-blinka
pip3 install adafruit-circuitpython-amg88xx

# pip3 install face_recognition
# pip3 install imutils
# pip3 install opencv-python-headless
# pip3 install opencv-contrib-python

# pip3 uninstall Scipy
# pip3 install --user -U Cython --force-reinstall
# pip3 install --user -U Scipy

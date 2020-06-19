#!/bin/bash

sudo apt update
sudo apt upgrade -y

sudo apt install -y build-essential cmake pkg-config qt5-default gfortran \
                    libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev \
                    libavcodec-dev libavformat-dev libswscale-dev libv4l-dev \
                    libxvidcore-dev libx264-dev libatlas-base-dev libhdf5-dev

# sudo apt install -y libgtk2.0-dev libgtk-3-dev libjasper1

# sudo apt install -y python2.7-dev

sudo apt install -y python3-dev python3-scipy python3-pygame python3-pyqt5

sudo apt install -y qt4-dev-tools

sudo apt autoremove -y

pip3 install boto3
pip3 install cmake
pip3 install colour
pip3 install cython
pip3 install scipy
pip3 install imutils

# pip3 install adafruit-blinka
# pip3 install adafruit-circuitpython-amg88xx

# pip3 install face_recognition

pip3 install opencv-python==3.4.6.27

# pip3 install opencv-python-headless
# pip3 install opencv-contrib-python

# pip3 uninstall Scipy
# pip3 install --user -U Cython --force-reinstall
# pip3 install --user -U Scipy

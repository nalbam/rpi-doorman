# rpi-doorman

## raspberry pi config

```bash
sudo raspi-config
```

```
Interfacing Options -> Camera -> Enabled
Interfacing Options -> I2C -> Enabled
```

## Install Python Software

```bash
# sudo apt install -y python3-scipy python3-pygame

pip3 install awscli
pip3 install boto3
pip3 install colour
pip3 install opencv-python
pip3 install pygame
pip3 install scipy

pip3 install adafruit-blinka
pip3 install adafruit-circuitpython-amg88xx
```

### for Windows in vs-code terminal

```bash
py3 -m pip install boto3
```

## Test

```
sudo i2cdetect -y 1
```

## Run

```bash
python3 ./rpi-doorman/camera.py --bucket-name <DOORMAN-BUCKET-NAME>

python3 ./rpi-doorman/amg88xx.py --min 18 --max 26
```

* <https://learn.adafruit.com/adafruit-amg8833-8x8-thermal-camera-sensor/python-circuitpython>
* <https://github.com/adafruit/Adafruit_CircuitPython_AMG88xx>

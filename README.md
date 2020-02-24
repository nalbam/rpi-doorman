# rpi-thermal

## raspberry pi config

```bash
sudo raspi-config

Interfacing Options -> Camera
Interfacing Options -> I2C
```

## Install Python Software

```bash
sudo apt install -y python3-scipy python3-pygame

pip3 install colour
pip3 install adafruit-blinka
pip3 install adafruit-circuitpython-amg88xx
```

## Test

```
sudo i2cdetect -y 1
```

* <https://learn.adafruit.com/adafruit-amg8833-8x8-thermal-camera-sensor/python-circuitpython>
* <https://github.com/adafruit/Adafruit_CircuitPython_AMG88xx>

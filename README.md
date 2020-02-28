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
sudo apt install -y xscreensaver

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
& C:/Users/username/AppData/Local/Programs/Python/Python37/python.exe -m pip install boto3
```

## Test

```
sudo i2cdetect -y 1
```

## Run

```bash
python3 ./rpi-doorman/run.py --min-temp 18 --max-temp 26 --bucket-name <DOORMAN-BUCKET-NAME>
```

* <https://learn.adafruit.com/adafruit-amg8833-8x8-thermal-camera-sensor/python-circuitpython>
* <https://github.com/adafruit/Adafruit_CircuitPython_AMG88xx>

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
./setup.sh
```

## Test

```
sudo i2cdetect -y 1
```

## Run

```bash
export BUCKET_NAME="deeplens-doorman-demo"

python3 ./rpi-doorman/camera.py --bucket-name ${BUCKET_NAME}

python3 ./rpi-doorman/amg88xx.py --min 18 --max 26
```

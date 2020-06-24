# rpi-doorman

## first boot

* south korea
* user password
* wifi
* update software

## rpi-config

```bash
sudo raspi-config
```

* Menu > Preferences > Rapberry Pi Configuration
  * Interfaces
    * Camera: Enable
    * SSH: Enable
    * SPI: Enable
    * I2C: Enable
  * Performance
    * GPU Memory: 128

## git clone

```bash
git clone https://github.com/nalbam/rpi
git clone https://github.com/mzcdev/rpi-doorman
git clone https://github.com/mzcdev/LeptonModule
```

## install

```bash
./rpi/run.sh auto
./rpi/run.sh screensaver
./rpi-doorman/setup.sh
```

## aws configure

```bash
aws configure
```

## doorman env

```bash
vi ~/.bashrc

# mzc-demo
export AWSREGION="ap-northeast-2"
export SLACK_API_TOKEN="xoxb-xxxxxxxxxx-xxxxxxxxxx-xxxxxxxxxx"
export SLACK_CHANNEL_ID="XXXXXXXXXX"
export DEVICE_ID="mzc-01"
export BUCKET_NAME="deeplens-doorman-mzc"
export STORAGE_NAME="deeplens-doorman-mzc"
export TABLE_USERS="doorman-users-demo"
export TABLE_HISTORY="doorman-history-demo"
export TRAIN_URL="https://xxxxxx.execute-api.ap-northeast-1.amazonaws.com/demo/train"
export USERS_URL="https://xxxxxx.execute-api.ap-northeast-2.amazonaws.com/demo/users"

export LEPTON_AUTO="N"
export LEPTON_BASE="634"
export LEPTON_MIN="12"
export LEPTON_MAX="37"
```

## build

```bash
./rpi-doorman/build.py
```

## startup

```bash
./rpi-doorman/camera.py
./rpi-doorman/lepton.sh
```

#!/usr/bin/env python3

import argparse
import boto3
import cv2
import datetime
import json
import math
import numpy as np
import os
import socket

import busio
import board

import adafruit_amg88xx

from colour import Color
from scipy.interpolate import griddata

from colormap import colormap


# low range of the sensor (this will be blue on the screen)
MINTEMP = 22.0

# high range of the sensor (this will be red on the screen)
MAXTEMP = 30.0

BUCKET_NAME = os.environ.get("BUCKET_NAME", "deeplens-doorman-demo")

# Setup the S3 client
s3 = boto3.client("s3")


def parse_args():
    p = argparse.ArgumentParser(description="webcam demo")
    p.add_argument("-a", "--alpha", type=float, default=1.0, help="alpha")
    p.add_argument("-b", "--bucket-name", default=BUCKET_NAME, help="bucket name")
    p.add_argument("-c", "--camera-id", type=int, default=0, help="camera id")
    p.add_argument("-f", "--full-screen", action="store_true", help="full screen")
    p.add_argument("-m", "--mirror", action="store_true", help="mirror")
    p.add_argument("--width", type=int, default=0, help="width")
    p.add_argument("--height", type=int, default=0, help="height")
    p.add_argument("--min-temp", type=float, default=MINTEMP, help="min-temp")
    p.add_argument("--max-temp", type=float, default=MAXTEMP, help="max-temp")
    return p.parse_args()


def internet(host="8.8.8.8", port=53, timeout=1):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print(ex)
        return False


class Sensor:
    def __init__(self, args, width, height):
        self.min_temp = args.min_temp
        self.max_temp = args.max_temp

        self.size = [int(width / 3), int(width / 3)]
        self.pixels = [self.size[0] / 32, self.size[1] / 32]
        # self.start_pos = [0, int((height - self.size[1]) / 2)]
        self.start_pos = [0, 0]

        # pylint: disable=invalid-slice-index
        self.points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0, 64)]
        self.grid_x, self.grid_y = np.mgrid[0:7:32j, 0:7:32j]
        # pylint: enable=invalid-slice-index

        self.i2c_bus = busio.I2C(board.SCL, board.SDA)

        # initialize the sensor
        self.sensor = adafruit_amg88xx.AMG88XX(self.i2c_bus)

        self.temps = []

    def get_position(self, i, j):
        pt1 = (
            int((self.pixels[0] * i) + self.start_pos[0]),
            int((self.pixels[1] * j) + self.start_pos[1]),
        )
        pt2 = (
            int((self.pixels[0] * (i + 1)) + self.start_pos[0]),
            int((self.pixels[1] * (j + 1)) + self.start_pos[1]),
        )
        return pt1, pt2

    def get_color(self, v):
        i = min(255, max(0, int(v)))
        return (
            colormap[i * 3],
            colormap[i * 3 + 1],
            colormap[i * 3 + 2],
        )

    def map_value(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def detect(self):
        detected = False

        # read the pixels
        pixels = []
        for row in self.sensor.pixels:
            pixels = pixels + row

        # pixels = [
        #     self.map_value(p, self.min_temp, self.max_temp, 0, 255)
        #     for p in pixels
        # ]

        self.temps = []
        for p in pixels:
            if p > self.max_temp:
                detected = True

            temp = self.map_value(p, self.min_temp, self.max_temp, 0, 255)

            self.temps.append(temp)

        return detected

    def draw(self, frame, alpha):
        overlay = frame.copy()

        # perform interpolation
        bicubic = griddata(
            self.points, self.temps, (self.grid_x, self.grid_y), method="cubic"
        )

        # draw pixel
        for i, row in enumerate(bicubic):
            for j, pixel in enumerate(row):
                pt1, pt2 = self.get_position(i, j)
                color = self.get_color(pixel)

                cv2.rectangle(
                    overlay, pt1, pt2, color, cv2.FILLED,
                )

        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        cv2.imshow("Video", overlay)


def main():
    args = parse_args()

    # Get a reference to webcam #0 (the default one)
    cap = cv2.VideoCapture(args.camera_id)

    if args.width > 0 and args.height > 0:
        frame_w = args.width
        frame_h = args.height
    else:
        frame_w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        frame_h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    print(frame_w, frame_h)
    print(args.min_temp, args.max_temp)
    print('Press "Esc", "q" or "Q" to exit.')

    incoming = "incoming"
    file_ext = "jpg"

    # initialize the sensor
    sensor = Sensor(args, frame_w, frame_h)

    while True:
        # Grab a single frame of video
        ret, frame = cap.read()

        # Invert left and right
        frame = cv2.flip(frame, 1)

        filename = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S-%f")

        # temp detect
        detected = sensor.detect()

        if detected:
            if os.path.isdir(incoming) == False:
                os.mkdir(incoming)

            key = "{}/{}.{}".format(incoming, filename, file_ext)

            print(detected, key)

            cv2.imwrite(key, frame)

            if internet():
                try:
                    # create a s3 file key
                    _, jpg_data = cv2.imencode(".jpg", frame)
                    res = s3.put_object(
                        Bucket=args.bucket_name,
                        Key=key,
                        Body=jpg_data.tostring(),
                        ACL="public-read",
                    )
                    print(res)
                except Exception as ex:
                    print("Error", ex)

        # draw graph
        sensor.draw(frame, args.alpha)

        # if detected:
        #     key = "{}/{}-gph.{}".format(incoming, filename, file_ext)

        #     # Crop square
        #     crop = frame[y : y + w, x : x + w]

        if args.mirror:
            # Invert left and right
            frame = cv2.flip(frame, 1)

        # Display the resulting image
        cv2.imshow("Video", frame)

        cv2.namedWindow("Video", cv2.WINDOW_NORMAL)

        if args.full_screen:
            cv2.setWindowProperty(
                "Video", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN
            )

        ch = cv2.waitKey(1)
        if ch == 27 or ch == ord("q") or ch == ord("Q"):
            break

    # Release handle to the webcam
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

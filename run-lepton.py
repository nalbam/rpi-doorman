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
import traceback

from colour import Color
from scipy.interpolate import griddata

from pylepton.Lepton3 import Lepton3

from colormap import colormap


# low range of the sensor
MINTEMP = 29000

# high range of the sensor
MAXTEMP = 31000

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
    p.add_argument("--min", type=float, default=MINTEMP, help="min temp")
    p.add_argument("--max", type=float, default=MAXTEMP, help="max temp")
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
    def __init__(self, args):
        self.device = "/dev/spidev0.0"

        self.min_temp = args.min
        self.max_temp = args.max

        self.width = 160
        self.height = 120

        self.pixels = []
        self.length = self.width * self.height

        self.l = Lepton3(self.device)

    def get_position(self, i, j):
        pt1 = (
            int(self.width * i),
            int(self.height * j),
        )
        pt2 = (
            int(self.width * (i + 1)),
            int(self.height * (j + 1)),
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

        try:
            # with Lepton3(self.device) as l:
            _, nr = self.l.capture(self.pixels)

            # for ix, row in enumerate(self.pixels):  # 120
            #     for jx, pixel in enumerate(row):  # 160
            #         self.pixels[ix][jx] = min(max(pixel, MINTEMP), MAXTEMP)

            self.pixels[0][0] = MAXTEMP
            # self.pixels[0][1] = MINTEMP

            cv2.normalize(self.pixels, self.pixels, 0, 65535, cv2.NORM_MINMAX)
            np.right_shift(self.pixels, 8, self.pixels)

        except Exception:
            traceback.print_exc()

        return detected

    def draw(self, frame, alpha):
        overlay = frame.copy()

        # draw pixel
        for i, row in enumerate(self.pixels):
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
    print(args.min, args.max)
    print('Press "Esc", "q" or "Q" to exit.')

    incoming = "incoming"
    file_ext = "jpg"

    detected = False

    # initialize the sensor
    sensor = Sensor(args)

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

#!/usr/bin/env python3

"""
  This example is for Raspberry Pi (Linux) only!
  It will not work on microcontrollers running CircuitPython!
"""

import argparse
import boto3
import datetime
import json
import math
import numpy as np
import os
import pygame
import time
import traceback

import busio
import board

import adafruit_amg88xx

from scipy.interpolate import griddata

from colour import Color

from colormap import colormap

from pathlib import Path

HOME = str(Path.home())

# low range of the sensor (this will be blue on the screen)
MINTEMP = 18.0

# high range of the sensor (this will be red on the screen)
MAXTEMP = 26.0

FRAME_RATE = 15

BUCKET_NAME = os.environ.get("BUCKET_NAME", "deeplens-doorman-demo")

JSON_PATH = os.environ.get("JSON_PATH", "{}/.doorman.json".format(HOME))


# Setup the S3 client
s3 = boto3.client("s3")


def parse_args():
    p = argparse.ArgumentParser(description="doorman")
    p.add_argument("-b", "--bucket-name", default=BUCKET_NAME, help="bucket name")
    # p.add_argument("--width", type=int, default=8, help="width")
    # p.add_argument("--height", type=int, default=8, help="height")
    # p.add_argument("--pixel", type=int, default=50, help="pixel")
    p.add_argument("--min", type=float, default=MINTEMP, help="min-temp")
    p.add_argument("--max", type=float, default=MAXTEMP, help="max-temp")
    p.add_argument("--json-path", default=JSON_PATH, help="json path")
    return p.parse_args()


def load_json(json_path=JSON_PATH):
    try:
        if os.path.isfile(json_path):
            f = open(json_path)
            data = json.load(f)
            f.close()
            return data
    except Exception:
        traceback.print_exc()

    data = {"filename": "", "temperature": 0, "uploaded": False}
    save_json(json_path, data)
    return data


def save_json(json_path=JSON_PATH, data=None):
    if data == None:
        data = {"filename": "", "temperature": 0, "uploaded": False}
    with open(json_path, "w") as f:
        json.dump(data, f)
    f.close()
    print(json.dumps(data))


# some utility functions
def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))


def map_value(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def get_color(v):
    i = min(255, max(0, int(v)))
    return (
        colormap[i * 3],
        colormap[i * 3 + 1],
        colormap[i * 3 + 2],
    )


def main():
    args = parse_args()

    # os.putenv("SDL_FBDEV", "/dev/fb1")

    width = 8
    height = 8

    pixel_width = 10
    pixel_height = 10

    screen_width = int(width * pixel_width * 4)
    screen_height = int(height * pixel_height * 4)

    print(screen_width, screen_height)
    print(args.min, args.max)
    print('Press "Esc", "q" or "Q" to exit.')

    # pylint: disable=invalid-slice-index
    points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0, 64)]
    grid_x, grid_y = np.mgrid[0:7:32j, 0:7:32j]
    # pylint: enable=invalid-slice-index

    # i2c_bus
    i2c_bus = busio.I2C(board.SCL, board.SDA)

    # initialize the sensor
    sensor = adafruit_amg88xx.AMG88XX(i2c_bus)

    # let the sensor initialize
    time.sleep(0.1)

    # pygame
    pygame.init()

    clock = pygame.time.Clock()

    screen = pygame.display.set_mode((screen_width, screen_height))

    screen.fill((0, 0, 0))
    pygame.display.update()

    run = True
    while run:
        capture = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE] or keys[pygame.K_q]:
            run = False
        elif keys[pygame.K_c]:
            capture = True

        if run == False:
            break

        # read the pixels
        pixels = []
        # for temp in range(0, 64):
        #     pixels.append(MINTEMP + (temp / (MAXTEMP - MINTEMP)))
        for row in sensor.pixels:
            pixels = pixels + row

        min_temp = min(pixels)
        max_temp = max(pixels)

        pixels = [map_value(p, MINTEMP, MAXTEMP, 0, 255) for p in pixels]

        # perform interpolation
        bicubic = griddata(points, pixels, (grid_x, grid_y), method="cubic")

        # draw everything
        for ix, row in enumerate(bicubic):
            for jx, pixel in enumerate(row):
                color = get_color(pixel)
                pygame.draw.rect(
                    screen,
                    color,
                    (
                        # left, top, width, height
                        pixel_width * ix,
                        pixel_height * jx,
                        pixel_width,
                        pixel_height,
                    ),
                )

        print("{:2.1f} {:2.1f}".format(min_temp, max_temp))

        if max_temp > args.max or capture:
            filename = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S-%f")
            data = {"filename": filename, "temperature": max_temp, "uploaded": False}
            save_json(args.json_path, data)

        pygame.display.update()
        clock.tick(FRAME_RATE)

    pygame.quit()


if __name__ == "__main__":
    main()

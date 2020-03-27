#!/usr/bin/env python3

"""
  This example is for Raspberry Pi (Linux) only!
  It will not work on microcontrollers running CircuitPython!
"""

import argparse
import cv2
import datetime
import json
import math
import numpy as np
import os
import pygame
import time
import traceback

from pylepton.Lepton3 import Lepton3

from colormap import colormap

from pathlib import Path

HOME = str(Path.home())

# low range of the sensor
MINTEMP = 29000

# high range of the sensor
MAXTEMP = 31000

FRAME_RATE = 15

JSON_PATH = os.environ.get("JSON_PATH", "{}/.doorman.json".format(HOME))


def parse_args():
    p = argparse.ArgumentParser(description="doorman")
    p.add_argument("--width", type=int, default=160, help="width")
    p.add_argument("--height", type=int, default=120, help="height")
    p.add_argument("--pixel", type=int, default=3, help="pixel")
    p.add_argument("--min", type=float, default=MINTEMP, help="min-temp")
    p.add_argument("--max", type=float, default=MAXTEMP, help="max-temp")
    p.add_argument("--debug", action="store_true", help="debug")
    p.add_argument("--json-path", default=JSON_PATH, help="json path")
    return p.parse_args()


def load_json(json_path=JSON_PATH):
    if os.path.isfile(json_path):
        f = open(json_path)
        data = json.load(f)
        f.close()
    else:
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


def get_color(v):
    i = min(255, max(0, int(v)))
    return (
        colormap[i * 3],
        colormap[i * 3 + 1],
        colormap[i * 3 + 2],
    )


def main():
    args = parse_args()

    device = "/dev/spidev0.0"

    width = args.width
    height = args.height

    pixel_width = args.pixel
    pixel_height = args.pixel

    screen_width = width * pixel_width
    screen_height = height * pixel_height

    pixels = np.zeros((height, width, 1), dtype=np.uint16)

    print(screen_width, screen_height)
    print(args.min, args.max)
    print('Press "Esc", "q" or "Q" to exit.')

    # pygame
    pygame.init()

    clock = pygame.time.Clock()

    screen = pygame.display.set_mode((screen_width, screen_height))

    screen.fill((0, 0, 0))
    pygame.display.update()

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE] or keys[pygame.K_q]:
            run = False

        if run == False:
            break

        nr = 0
        max_temp = float("-inf")
        min_temp = float("inf")

        try:
            with Lepton3(device) as l:
                _, nr = l.capture(pixels, args.debug)

                for ix, row in enumerate(pixels):
                    max_temp = max(max_temp, max(row))
                    min_temp = min(min_temp, min(row))

                # pixels[0][0] = args.max
                # pixels[0][1] = args.min

                cv2.normalize(pixels, pixels, 0, 65535, cv2.NORM_MINMAX)
                np.right_shift(pixels, 8, pixels)

        except Exception:
            traceback.print_exc()

        # draw everything
        for ix, row in enumerate(pixels):  # 120
            for jx, pixel in enumerate(row):  # 160
                color = get_color(pixel)
                pygame.draw.rect(
                    screen,
                    color,
                    (
                        # left, top, width, height
                        pixel_width * jx,
                        pixel_height * ix,
                        pixel_width,
                        pixel_height,
                    ),
                )

        print(nr, args.min, min_temp, max_temp, args.max)

        if max_temp > args.max:
            filename = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S-%f")
            data = {"filename": filename, "temperature": max_temp, "uploaded": False}
            save_json(args.json_path, data)

        pygame.display.update()
        clock.tick(FRAME_RATE)

    pygame.quit()


if __name__ == "__main__":
    main()

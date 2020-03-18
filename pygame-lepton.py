#!/usr/bin/env python3

"""
  This example is for Raspberry Pi (Linux) only!
  It will not work on microcontrollers running CircuitPython!
"""

import cv2
import math
import numpy as np
import os
import pygame
import time
import traceback

from pylepton.Lepton3 import Lepton3

from colormap import colormap


# low range of the sensor
MINTEMP = 29000

# high range of the sensor
MAXTEMP = 31000

FRAME_RATE = 15


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


def run():
    device = "/dev/spidev0.0"

    # a = np.zeros((240, 320, 3), dtype=np.uint8)
    lepton_buf = np.zeros((120, 160, 1), dtype=np.uint16)

    pixels = [160, 120]
    length = pixels[0] * pixels[1]

    # pylint: disable=invalid-slice-index
    points = [(math.floor(ix / pixels[1]), (ix % pixels[1])) for ix in range(0, length)]
    grid_x, grid_y = np.mgrid[0:159:160j, 0:119:120j]
    # pylint: enable=invalid-slice-index

    width = pixels[0] * 4
    height = pixels[1] * 4

    displayPixelWidth = 4
    displayPixelHeight = 4

    # pygame
    pygame.init()

    # clock = pygame.time.Clock()

    screen = pygame.display.set_mode((width, height))

    screen.fill((0, 0, 0))
    pygame.display.update()

    # let the sensor initialize
    time.sleep(0.1)

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

        # read the pixels
        pixels = []

        try:
            with Lepton3(device) as l:
                _, nr = l.capture(lepton_buf)

                # for ix, row in enumerate(lepton_buf):  # 120
                #     for jx, pixel in enumerate(row):  # 160
                #         lepton_buf[ix][jx] = min(max(pixel, MINTEMP), MAXTEMP)

                lepton_buf[0][0] = MAXTEMP
                # lepton_buf[0][1] = MINTEMP

                cv2.normalize(lepton_buf, lepton_buf, 0, 65535, cv2.NORM_MINMAX)

                np.right_shift(lepton_buf, 8, lepton_buf)

        except Exception:
            traceback.print_exc()

        # draw everything
        for ix, row in enumerate(lepton_buf):  # 120
            for jx, pixel in enumerate(row):  # 160
                color = get_color(pixel)
                pygame.draw.rect(
                    screen,
                    color,
                    (
                        # left, top, width, height
                        displayPixelWidth * jx,
                        displayPixelHeight * ix,
                        displayPixelWidth,
                        displayPixelHeight,
                    ),
                )

        pygame.display.update()
        # clock.tick(FRAME_RATE)

    pygame.quit()


run()

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


def get_color(v):
    i = min(255, max(0, int(v)))
    return (
        colormap[i * 3],
        colormap[i * 3 + 1],
        colormap[i * 3 + 2],
    )


def run():
    device = "/dev/spidev0.0"

    width = 160
    height = 120

    pixels = np.zeros((height, width, 1), dtype=np.uint16)
    # length = width * height

    pixel_width = 2
    pixel_height = 2

    screen_width = width * pixel_width
    screen_height = height * pixel_height

    # pygame
    pygame.init()

    # clock = pygame.time.Clock()

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

        max_temp = 0

        try:
            with Lepton3(device) as l:
                _, nr = l.capture(pixels)

                for ix, row in enumerate(pixels):
                    max_temp = max(max_temp, max(row))

                pixels[0][0] = MAXTEMP
                # pixels[0][1] = MINTEMP

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

        pygame.display.update()
        # clock.tick(FRAME_RATE)

    pygame.quit()


run()

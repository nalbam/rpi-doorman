#!/usr/bin/env python3

"""
  This example is for Raspberry Pi (Linux) only!
  It will not work on microcontrollers running CircuitPython!
"""

import os
import math
import time

# import busio
# import board

import numpy as np
import pygame

from scipy.interpolate import griddata

from colour import Color

# import adafruit_amg88xx

# low range of the sensor (this will be blue on the screen)
MINTEMP = 22.0
MINCOLOR = "indigo"

# high range of the sensor (this will be red on the screen)
MAXTEMP = 30.0
MAXCOLOR = "red"

# how many color values we can have
COLORDEPTH = 1024


# some utility functions
def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))


def map_value(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def run():
    os.putenv("SDL_FBDEV", "/dev/fb1")

    pygame.init()

    # i2c_bus = busio.I2C(board.SCL, board.SDA)

    # # initialize the sensor
    # sensor = adafruit_amg88xx.AMG88XX(i2c_bus)

    # pylint: disable=invalid-slice-index
    points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0, 64)]
    grid_x, grid_y = np.mgrid[0:7:32j, 0:7:32j]
    # pylint: enable=invalid-slice-index

    # sensor is an 8x8 grid so lets do a square
    width = 640
    height = 640

    # the list of colors we can choose from
    colors = list(Color(MINCOLOR).range_to(Color(MAXCOLOR), COLORDEPTH))

    # create the array of colors
    colors = [(int(c.red * 255), int(c.green * 255), int(c.blue * 255)) for c in colors]

    displayPixelWidth = width / 30
    displayPixelHeight = height / 30

    screen = pygame.display.set_mode((width, height))

    # screen.fill((255, 0, 0))
    # pygame.display.update()

    # pygame.mouse.set_visible(False)

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
        # for row in sensor.pixels:
        #     pixels = pixels + row
        for temp in range(0, 64):
            pixels.append(MINTEMP + (temp / (MAXTEMP - MINTEMP)))

        pixels = [map_value(p, MINTEMP, MAXTEMP, 0, COLORDEPTH - 1) for p in pixels]

        # perform interpolation
        bicubic = griddata(points, pixels, (grid_x, grid_y), method="cubic")

        # draw everything
        for ix, row in enumerate(bicubic):
            for jx, pixel in enumerate(row):
                pygame.draw.rect(
                    screen,
                    colors[constrain(int(pixel), 0, COLORDEPTH - 1)],
                    (
                        # left, top, width, height
                        displayPixelWidth * jx,
                        displayPixelHeight * ix,
                        displayPixelWidth,
                        displayPixelHeight,
                    ),
                )

        pygame.display.update()

    pygame.quit()


run()

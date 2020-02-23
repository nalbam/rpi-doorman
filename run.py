import argparse
import cv2
import math
import numpy as np

import busio
import board

import adafruit_amg88xx

from colour import Color
from scipy.interpolate import griddata


# low range of the sensor (this will be blue on the screen)
MINTEMP = 22.0

# high range of the sensor (this will be red on the screen)
MAXTEMP = 30.0

# how many color values we can have
COLORDEPTH = 1024


def parse_args():
    p = argparse.ArgumentParser(description="webcam demo")
    p.add_argument("--camera-id", type=int, default=0, help="camera id")
    p.add_argument("--full-screen", action="store_true", help="full screen")
    p.add_argument("--mirror", action="store_true", help="mirror")
    p.add_argument("--width", type=int, default=0, help="width")
    p.add_argument("--height", type=int, default=0, help="height")
    p.add_argument("--min-temp", type=float, default=MINTEMP, help="height")
    p.add_argument("--max-temp", type=float, default=MAXTEMP, help="height")
    p.add_argument("--alpha", type=float, default=0.9, help="alpha")
    return p.parse_args()


# def draw_video(frame):
#     # move video
#     w = int(SCREEN_W / 4)
#     M = [[1, 0, w], [0, 1, 0]]

#     h, w = frame.shape[:2]
#     M = np.float32(M)
#     frame = cv2.warpAffine(frame, M, (w, h))


class Sensor:
    def __init__(self, args, width, height):
        self.min_temp = args.min_temp
        self.max_temp = args.max_temp

        self.size = [int(width / 3), int(width / 3)]
        self.pixels = [self.size[0] / 32, self.size[1] / 32]
        # self.start_pos = [0, int((height - self.size[1]) / 2)]
        self.start_pos = [0, 0]

        self.colors = self.get_colors()

        # pylint: disable=invalid-slice-index
        self.points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0, 64)]
        self.grid_x, self.grid_y = np.mgrid[0:7:32j, 0:7:32j]
        # pylint: enable=invalid-slice-index

        self.i2c_bus = busio.I2C(board.SCL, board.SDA)

        # initialize the sensor
        self.sensor = adafruit_amg88xx.AMG88XX(self.i2c_bus)

    def get_colors(self):
        # the list of colors we can choose from
        blue = Color("indigo")
        red = Color("red")
        colors = list(blue.range_to(red, COLORDEPTH))

        # create the array of colors
        return [
            (int(c.red * 255), int(c.green * 255), int(c.blue * 255)) for c in colors
        ]

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
        i = COLORDEPTH - min(COLORDEPTH, max(1, int(v)))
        return self.colors[i]

    def map_value(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def draw(self, frame, alpha):
        overlay = frame.copy()

        # read the pixels
        pixels = []
        for row in sensor.pixels:
            # pixels = pixels + row
            pixels.append(row)
        # for temp in range(0, 64):
        #     pixels.append(self.min_temp + (temp / 8))

        pixels = [
            self.map_value(p, self.min_temp, self.max_temp, 0, COLORDEPTH - 1)
            for p in pixels
        ]

        # perform interpolation
        bicubic = griddata(
            self.points, pixels, (self.grid_x, self.grid_y), method="cubic"
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
    print('Press "Esc", "q" or "Q" to exit.')

    # initialize the sensor
    sensor = Sensor(args, frame_w, frame_h)

    while True:
        # Grab a single frame of video
        ret, frame = cap.read()

        if args.mirror:
            # Invert left and right
            frame = cv2.flip(frame, 1)

        # draw tempo
        sensor.draw(frame, args.alpha)

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

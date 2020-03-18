#!/usr/bin/env python3

import argparse
import boto3
import cv2
import datetime
import os
import socket


BUCKET_NAME = os.environ.get("BUCKET_NAME", "deeplens-doorman-demo")


# Setup the S3 client
s3 = boto3.client("s3")


def parse_args():
    p = argparse.ArgumentParser(description="webcam demo")
    p.add_argument("-b", "--bucket-name", default=BUCKET_NAME, help="bucket name")
    p.add_argument("-c", "--camera-id", type=int, default=0, help="camera id")
    p.add_argument("-f", "--full-screen", action="store_true", help="full screen")
    p.add_argument("-m", "--mirror", action="store_true", help="mirror")
    p.add_argument("--width", type=int, default=0, help="width")
    p.add_argument("--height", type=int, default=0, help="height")
    return p.parse_args()


def internet(host="8.8.8.8", port=53, timeout=1):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print(ex)
        return False


def upload(args, frame, filename=""):
    incoming = "incoming"
    file_ext = "jpg"

    if os.path.isdir(incoming) == False:
        os.mkdir(incoming)

    if filename == "":
        filename = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S-%f")
    key = "{}/{}.{}".format(incoming, filename, file_ext)

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

    return filename


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

    detected = False
    filename = ""

    while True:
        # Grab a single frame of video
        ret, frame = cap.read()

        # Invert left and right
        frame = cv2.flip(frame, 1)

        # temp detect
        detected = False

        if detected:
            filename = upload(args, frame)

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

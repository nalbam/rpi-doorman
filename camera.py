#!/usr/bin/env python3

import argparse
import boto3
import cv2
import datetime
import json
import os
import socket


BUCKET_NAME = os.environ.get("BUCKET_NAME", "deeplens-doorman-demo")

JSON_PATH = os.environ.get("JSON_PATH", "data.json")


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
    p.add_argument("--json-path", default=JSON_PATH, help="json path")
    return p.parse_args()


def load_json(json_path=JSON_PATH):
    if os.path.isfile(json_path):
        f = open(json_path)
        data = json.load(f)
        f.close()
    else:
        data = {"filename": "", "uploaded": False}
        save_json(json_path, data)
    return data


def save_json(json_path=JSON_PATH, data=None):
    if data == None:
        data = {"filename": "", "uploaded": False}
    with open(json_path, "w") as f:
        json.dump(data, f)
    f.close()


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

    if internet():
        try:
            # save to local
            cv2.imwrite(key, frame)

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

    while True:
        # Grab a single frame of video
        ret, frame = cap.read()

        # Invert left and right
        frame = cv2.flip(frame, 1)

        # upload
        data = load_json(args.json_path)
        if data["uploaded"] == False:
            save_json(args.json_path)
            upload(args, frame, data.filename)

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

import cv2

# import glob
# import re

cam = 0
# for file in glob.glob("/dev/video*"):
#     m = re.search("/dev/video(.+?)", file)
#     if m:
#         cam = m.group(1)
#         break

# Get a reference to webcam #0 (the default one)
cap = cv2.VideoCapture(cam)

frame_w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
frame_h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

rate = 8 / frame_h
bigg = 400 / 8

while True:
    # Grab a single frame of video
    ret, frame = cap.read()

    # Resize to 8x8
    frame = cv2.resize(frame, (0, 0), fx=rate, fy=rate)

    # w1 = int((int(frame_w * rate) - 8) / 2)
    # w2 = 8 + w1
    # frame = frame[0:8, w1:w2]

    frame = cv2.resize(frame, (0, 0), fx=bigg, fy=bigg, interpolation=cv2.INTER_AREA)

    # Display the resulting image
    cv2.imshow("Video", frame)

    cv2.namedWindow("Video", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Video", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release handle to the webcam
cap.release()
cv2.destroyAllWindows()

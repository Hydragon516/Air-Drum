from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
import serial

ser = serial.Serial(
    port='COM10',
    baudrate=115200,
)

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
                help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
                help="max buffer size")
args = vars(ap.parse_args())

prevTime = 0
T1 = 0
T2 = 0
T3 = 0

T4 = 0
T5 = 0
T6 = 0

greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)

blueLower = (0, 100, 100)
blueUpper = (10, 255, 255)

pts = deque(maxlen=args["buffer"])

if not args.get("video", False):
    vs = VideoStream(src=0).start()

else:
    vs = cv2.VideoCapture(1)

time.sleep(2.0)

while True:
    frame = vs.read()

    curTime = time.time()
    sec = curTime - prevTime
    prevTime = curTime

    fps = 1 / (sec)
    FPS = "FPS: %0.1f" % fps

    frame = frame[1] if args.get("video", False) else frame

    if frame is None:
        break

    frame = imutils.resize(frame, width=600)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    mask1 = cv2.inRange(hsv, greenLower, greenUpper)
    mask1 = cv2.erode(mask1, None, iterations=2)
    mask1 = cv2.dilate(mask1, None, iterations=2)

    mask2 = cv2.inRange(hsv, blueLower, blueUpper)
    mask2 = cv2.erode(mask2, None, iterations=2)
    mask2 = cv2.dilate(mask2, None, iterations=2)

    cnts1 = cv2.findContours(mask1.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts1 = cnts1[0] if imutils.is_cv2() else cnts1[1]
    center1 = None

    cnts2 = cv2.findContours(mask2.copy(), cv2.RETR_EXTERNAL,
                             cv2.CHAIN_APPROX_SIMPLE)
    cnts2 = cnts2[0] if imutils.is_cv2() else cnts2[1]
    center2 = None

    cv2.rectangle(frame, (350, 200), (480, 300), (0, 255, 0), 2)
    cv2.putText(frame, "High Hat", (350, 190),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    cv2.rectangle(frame, (100, 300), (230, 400), (0, 255, 0), 2)
    cv2.putText(frame, "Snare", (100, 290),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    cv2.rectangle(frame, (500, 50), (580, 150), (0, 255, 0), 2)
    cv2.putText(frame, "Crash", (500, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    if len(cnts1) > 0:

        c1 = max(cnts1, key=cv2.contourArea)
        ((x1, y1), radius1) = cv2.minEnclosingCircle(c1)
        M1 = cv2.moments(c1)
        center1 = (int(M1["m10"] / M1["m00"]), int(M1["m01"] / M1["m00"]))


        if radius1 > 10:

            cv2.circle(frame, (int(x1), int(y1)), int(radius1),
                       (0, 255, 255), 2)
            cv2.circle(frame, center1, 5, (0, 0, 255), -1)

            cv2.putText(frame, "x1: " + str(int(x1)) + " y1: " + str(int(y1)), (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            if (350 < x1 < 480) and (200 < y1 < 300):
                cv2.rectangle(frame, (350, 200), (480, 300), (0, 0, 255), 2)
                if T1 == 1:
                    ser.write(b'1')
                    T1 = 0
            else:
                T1 = 1

            if (100 < x1 < 230) and (300 < y1 < 400):
                cv2.rectangle(frame, (100, 300), (230, 400), (0, 0, 255), 2)
                if T2 == 1:
                    ser.write(b'2')
                    T2 = 0
            else:
                T2 = 1

            if (500 < x1 < 580) and (50 < y1 < 150):
                cv2.rectangle(frame, (500, 50), (580, 150), (0, 0, 255), 2)
                if T3 == 1:
                    ser.write(b'3')
                    T3 = 0
            else:
                T3 = 1

    if len(cnts2) > 0:

        c2 = max(cnts2, key=cv2.contourArea)
        ((x2, y2), radius2) = cv2.minEnclosingCircle(c2)
        M2 = cv2.moments(c2)
        center2 = (int(M2["m10"] / M2["m00"]), int(M2["m01"] / M2["m00"]))

        if radius2 > 10:

            cv2.circle(frame, (int(x2), int(y2)), int(radius2),
                       (0, 255, 255), 2)
            cv2.circle(frame, center2, 5, (0, 0, 255), -1)

            cv2.putText(frame, "x2: " + str(int(x2)) + " y2: " + str(int(y2)), (10, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        if (350 < x2 < 480) and (200 < y2 < 300):
            cv2.rectangle(frame, (350, 200), (480, 300), (0, 0, 255), 2)
            if T4 == 1:
                ser.write(b'1')
                T4 = 0
        else:
            T4 = 1

        if (100 < x2 < 230) and (300 < y2 < 400):
            cv2.rectangle(frame, (100, 300), (230, 400), (0, 0, 255), 2)
            if T5 == 1:
                ser.write(b'2')
                T5 = 0
        else:
            T5 = 1

        if (500 < x2 < 580) and (50 < y2 < 150):
            cv2.rectangle(frame, (500, 50), (580, 150), (0, 0, 255), 2)
            if T6 == 1:
                ser.write(b'3')
                T6 = 0
        else:
            T6 = 1

    pts.appendleft(center1)

    pts.appendleft(center2)

    cv2.putText(frame, "Air Drum Beta", (50, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.putText(frame, str(FPS), (400, 370), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    for i in range(1, len(pts)):

        if pts[i - 1] is None or pts[i] is None:
            continue

    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

if not args.get("video", False):
    vs.stop()

else:
    vs.release()

cv2.destroyAllWindows()
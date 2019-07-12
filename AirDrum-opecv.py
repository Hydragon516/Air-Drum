# import the necessary packages
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

# construct the argument parse and parse the arguments
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

# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)

blueLower = (0, 100, 100)
blueUpper = (10, 255, 255)

pts = deque(maxlen=args["buffer"])

# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
    vs = VideoStream(src=0).start()

# otherwise, grab a reference to the video file
else:
    vs = cv2.VideoCapture(1)

# allow the camera or video file to warm up
time.sleep(2.0)

# keep looping
while True:
    # grab the current frame
    frame = vs.read()

    curTime = time.time()
    sec = curTime - prevTime
    prevTime = curTime

    fps = 1 / (sec)
    FPS = "FPS: %0.1f" % fps

    # handle the frame from VideoCapture or VideoStream
    frame = frame[1] if args.get("video", False) else frame

    # if we are viewing a video and we did not grab a frame,
    # then we have reached the end of the video
    if frame is None:
        break

    # resize the frame, blur it, and convert it to the HSV
    # color space
    frame = imutils.resize(frame, width=600)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask1 = cv2.inRange(hsv, greenLower, greenUpper)
    mask1 = cv2.erode(mask1, None, iterations=2)
    mask1 = cv2.dilate(mask1, None, iterations=2)

    mask2 = cv2.inRange(hsv, blueLower, blueUpper)
    mask2 = cv2.erode(mask2, None, iterations=2)
    mask2 = cv2.dilate(mask2, None, iterations=2)

    # find contours in the mask and initialize the current
    # (x, y) center of the ball
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

    # only proceed if at least one contour was found
    if len(cnts1) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c1 = max(cnts1, key=cv2.contourArea)
        ((x1, y1), radius1) = cv2.minEnclosingCircle(c1)
        M1 = cv2.moments(c1)
        center1 = (int(M1["m10"] / M1["m00"]), int(M1["m01"] / M1["m00"]))

        # only proceed if the radius meets a minimum size
        if radius1 > 10:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
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
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c2 = max(cnts2, key=cv2.contourArea)
        ((x2, y2), radius2) = cv2.minEnclosingCircle(c2)
        M2 = cv2.moments(c2)
        center2 = (int(M2["m10"] / M2["m00"]), int(M2["m01"] / M2["m00"]))

        # only proceed if the radius meets a minimum size
        if radius2 > 10:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
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

    # update the points queue
    pts.appendleft(center1)

    pts.appendleft(center2)

    cv2.putText(frame, "Air Drum Beta", (50, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.putText(frame, str(FPS), (400, 370), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)


    # loop over the set of tracked points
    for i in range(1, len(pts)):
        # if either of the tracked points are None, ignore
        # them
        if pts[i - 1] is None or pts[i] is None:
            continue

        # otherwise, compute the thickness of the line and
        # draw the connecting lines
        #thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
        #cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

    # show the frame to our screen
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

# if we are not using a video file, stop the camera video stream
if not args.get("video", False):
    vs.stop()

# otherwise, release the camera
else:
    vs.release()

# close all windows
cv2.destroyAllWindows()
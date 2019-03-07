import cv2
import sys
import numpy as np
from functools import reduce

from skimage import io, color
import matplotlib.pyplot as plt  # import matplotlib library
import matplotlib.animation as animation
from drawnow import *

# Create a VideoCapture object and get video from webcam
# 0 for internal, 1 for external
cap = cv2.VideoCapture(0)


# Create the haar cascade - used for lighting and stuff
cascPath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascPath)

list = []
time = []
currIndex = 0
lower = 0
upper = 100

# Check if camera opened successfully
if (cap.isOpened() == False):
    print("Error opening video stream or file")
    sys.exit(0)


def makeFig():  # Create a function that makes our desired plot
    global currIndex
    global upper
    global lower

    # sweaty gsr
    plot1 = plt.subplot(1,1,1) #allows graphing multiple simulaneously. the numbers represent 3 rows, 1 colmun, 1st position, respectively.
    plot1.grid()
    plot1.set_ylim(lower, upper)  # Set y min and max values
    plot1.set_title('My Live Streaming Sensor Data')  # Plot the title
    plot1.set_ylabel('LAB')  # Set ylabels

    # threshold1 = 200 #how to find?
    # plot1.axhline(y=threshold1, color='r', linestyle='dotted') #create a line to represent the threshold
    # percentDiff1 = ((gsrValues[currIndex - 1] - threshold1) / threshold1)
    # plot1.legend([round(percentDiff1, 2)], loc='upper right')   # prints out the difference between plotted point
    #                                                             # and the the threshold.
    plot1.set_xlim(0, 500) #currIndex
    plot1.plot(time, list, 'r--', label='Number')

# Read until video is completed
def run():
    global currIndex
    global lower
    global upper
    while (cap.isOpened()):
        # Capture frame-by-frame
        ret, frame = cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                flags = cv2.CASCADE_SCALE_IMAGE
            )

            L = 0
            for (x, y, w, h) in faces:
                rows = 0
                cols = 0

                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                # gets forehead from image and turns into lab

                # MIDDLE FACE REGION
                if ret:
                    forehead = frame[y+90:y+200, x:x+w]
                    rgb_forehead = cv2.cvtColor(forehead, cv2.COLOR_BGR2RGB)
                    lab_forehead = color.rgb2lab(rgb_forehead)

                    rows = len(lab_forehead)
                    cols = len(lab_forehead[0])
                    for i in range(rows):
                        for j in range(cols):
                            #for w in range(len(lab_forehead[0][0])):
                            #    print(lab_forehead[i][j][w])
                            L += lab_forehead[i][j][0]
                            #A += lab_forehead[i][j][1]
                            #B += lab_forehead[i][j][2]
                    numpix = rows*cols
                    L = L/(numpix)

#            print(L)
            # amplifier
            # if (L > 45):
            #     L *= 1.2

            # REDUNDANT BUT ONLY WORKS THIS WAY
            if (L < 30 and currIndex > 0):
                L = list[currIndex-1]
            if (L == 0 and currIndex > 0):
                L = list[currIndex-1]
#            print(L)
            if (currIndex == 20):
                avg = reduce(lambda x, y: x + y, list) / (currIndex+1)
                lower = avg - 10
                upper = avg + 10

            list.append(L)
            time.append(currIndex)

            drawnow(makeFig,  stop_on_close=True)  # Call drawnow to update our live graph
            plt.pause(.000001)  # Pause Briefly. Important to keep drawnow from crashing

            currIndex += 1

            cv2.imshow('Video', frame)



            # Press Q on keyboard to  exit
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        # Break the loop
        else:
            break
run()
# When everything done, release the video capture object
cap.release()

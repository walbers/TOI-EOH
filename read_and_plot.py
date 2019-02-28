import serial
import numpy as np
import time
import matplotlib.pyplot as plt  # import matplotlib library
import matplotlib.animation as animation
from drawnow import *
import string
import re
import struct
import functools
import sys


'''
MUST RERUN PROGRAM AND RESET ARDUINO FOR EACH NEW PERSON.
'''
'''
current code is written for 3 sensors on two arduinos, change shit if you want 4
'''

# global lists for storing sensor data
bpm = [] #used to store values until averaged
bpmValues = [] #stores average bpm valuesstretchy = []
stretchy = [] #used to store values until averaged
stretchyValues = [] #stores average stretchy values
gsr = [] #used to store values until averaged
gsrValues = [] #stores average gsr valuescount = 0

time = [] #currently stores index. this allows the x-axis to build constantly
currIndex = 0 # a way to keep track of which value to put into time; is incremented after being appended
sufficientEntries = 5 #a variable to allow enough time for graph and data to start loading in
maxTime = 30 #currently unused

RECORD_DATA = 150 # after 150 data points plot
NUM_SENSORS = 3
count = 0

arduinoData = None
arduinoData2 = None

def setup():
    try:
        arduinoData = serial.Serial('COM4', 9600)  # Creating our serial object named arduinoData
        arduinoData2 = serial.Serial('COM3', 9600)  # Creating our serial object named arduinoData
    except serial.SerialException:
        print('Plug in the arduino to the right COM please.')
        sys.exit(0)



def makeFig():  # Create a function that makes our desired plot
    plot1 = plt.subplot(3,1,1) #allows graphing multiple simulaneously. the numbers represent 3 rows, 1 colmun, 1st position, respectively.
    plot1.grid()
    plot1.set_ylim(0, 600)  # Set y min and max values
    plot1.set_title('My Live Streaming Sensor Data')  # Plot the title
    #plt.grid(True)  # Turn the grid on
    plot1.set_ylabel('Metric')  # Set ylabels
    if currIndex > sufficientEntries:
        plot1.set_xlim(0, currIndex - sufficientEntries)
        plot1.plot(time, gsrValues, 'ro-', label='Number')  # plot the temperature

    plot2 = plt.subplot(3,1,2) #will display a second graph directly beneath the first
    plot2.grid()
    plot2.set_ylim(0,600)#to create specific features for this graph, do plt.'functoin'(/*blah*/)
    # #plt.title('Testing other graph')
    # #plt.grid(True)
    plot2.set_ylabel('nonsense')
    if currIndex > sufficientEntries:
        plot2.set_xlim(0, currIndex - sufficientEntries)
        plot2.plot(time, stretchyValues, 'b--', label='Number') #plot other

    plot3 = plt.subplot(3, 1, 3) #will display a third graph directly beneath the third
    plot3.grid() #activate grid lines
    plot3.set_ylim(0, 600) #to create specific features for this graph, do plt.'functoin'(/*blah*/)
    # #plt.title('Testing other graph')
    # #plt.grid(True)
    plot3.set_ylabel('Other Nonsense')
    if currIndex > sufficientEntries:
        plot3.set_xlim(0, currIndex - sufficientEntries)
        plot3.plot(time, bpmValues, 'b--', label='Number')  # plot other; the 'b--' is a style thing. didn't play with it enough to know all the combinations

def pre_plot():
    # global shit?
    bpm_chunk = functools.reduce(lambda x, y: x + y, bpm) / (RECORD_DATA / NUM_SENSORS-1) # 75?
    stretchy_chunk = functools.reduce(lambda x, y: x + y, stretchy) / (RECORD_DATA / NUM_SENSORS-1)
    gsr_chunk = functools.reduce(lambda x, y: x + y, gsr) / (RECORD_DATA / NUM_SENSORS-1)

    # works?
    bpmValues.append(bpm_chunk)
    stretchyValues.append(stretchy_chunk)
    gsrValues.append(gsr_chunk)

    time.append(currIndex - sufficientEntries)
    currIndex += 1

    bpm.clear()
    stretchy.clear()
    gsr.clear()


def get_int_from_arduino(mod):
    # turn bytes from arduino into int
    if (mod == 0):
        arduinoReturn = arduinoData.readline() # get bytes from arduino
    elif (mod == 1):
        arduinoReturn = arduinoData2.readline() # get bytes from arduino

    arduinoString = str(arduinoReturn) # convert bytes to string
    arduinoString = ''.join(ch for ch in arduinoString if ch.isalnum()) # get rid off all non alphanumeric bytes
    x = int(re.search(r'\d+', arduinoString).group()) # get integer from string
    return x



def loop():
    while True:
        global count # complained without this

        # Wait here until there is data
        while (arduinoData.inWaiting() == 0 or arduinoData2.inWaiting() == 0):
            pass

        mod = count % NUM_SENSORS

        # arduino with two sensors - sends bpm first then stretchy
        if (mod == 0):
            bpm.append(get_int_from_arduino(mod))
            stretchy.append(get_int_from_arduino(mod))

            # if (isbpm):
            #     bpm.append(x)
            #     #print(x)
            #     isbpm = 0
            # else:
            #      stretchy.append(x)
            #      isbpm = 1
        # arduino with gsr
        elif (mod == 1):
            gsr.append(get_int_from_arduino(mod))

        if (count%RECORD_DATA == 0 and count > RECORD_DATA*3): # the first 3 sets are garbage
            #print('averaging')
            #print(bpm)
            #print(stretchy)
            #print(gsr)
            #print(len(bpm))
            #print(len(gsr))
            pre_plot()

            if (count > 600):
                drawnow(makeFig)  # Call drawnow to update our live graph
                plt.pause(.000001)  # Pause Briefly. Important to keep drawnow from crashing
        count += 1

plt.figure(figsize=[12, 7.5]) #initial width and height of the display. pressing x will close the window, and the default size will show up
setup()
loop()

import serial
import numpy as np

import matplotlib.pyplot as plt  # import matplotlib library
import matplotlib.animation as animation
from drawnow import *
import string
import re
import struct
import functools

'''
MUST RERUN PROGRAM AND RESET ARDUINO FOR EACH NEW PERSON.
'''

'''
testing
'''

bpm = [] #used to store values until averaged
bpmValues = [] #stores average bpm values

stretchy = [] #used to store values until averaged
stretchyValues = [] #stores average stretchy values

gsr = [] #used to store values until averaged
gsrValues = [] #stores average gsr values

pressure = []
pressureValues = []

time = [] #currently stores index. this allows the x-axis to build constantly
currIndex = 0 # a way to keep track of which value to put into time; is incremented after being appended
sufficientEntries = 5 #a variable to allow enough time for graph and data to start loading in
maxTime = 30 #currently unused

arduinoData = None
arduinoData2 = None
# arduinoData3 = None

NUM_SENSORS = 4
NUM_BOARDS = 3
count = 0
isbpm = 0

def setup():
    try:
        global arduinoData
        global arduinoData2
        global arduinoData3
        # 4 is double sesnor bottom right port
        arduinoData = serial.Serial('COM4', 9600)  # Creating our serial object named arduinoData
        # 3 is gsr and left port
        arduinoData2 = serial.Serial('COM3', 9600)  # Creating our serial object named arduinoData
        # 5 is pressure and top righ port
        arduinoData3 = serial.Serial('COM5', 9600)  # Creating our serial object named arduinoData
    except serial.SerialException:
        print('Plug in the arduino to the right COM please.')
        sys.exit(0)


def makeFig():  # Create a function that makes our desired plot
    global currIndex

    # sweaty gsr
    plot1 = plt.subplot(4,1,1) #allows graphing multiple simulaneously. the numbers represent 3 rows, 1 colmun, 1st position, respectively.
    plot1.grid()
    plot1.set_ylim(0, 600)  # Set y min and max values
    plot1.set_title('My Live Streaming Sensor Data')  # Plot the title
    plot1.set_ylabel('sweaty/gsr')  # Set ylabels
    if currIndex > sufficientEntries:
        plot1.set_xlim(0, currIndex - sufficientEntries)
        plot1.plot(time, gsrValues, 'ro-', label='Number')  # plot the temperature

    # stretchy
    plot2 = plt.subplot(4,1,2) #will display a second graph directly beneath the first
    plot2.grid()
    plot2.set_ylim(0,600)#to create specific features for this graph, do plt.'functoin'(/*blah*/)
    plot2.set_ylabel('stretchy')
    if currIndex > sufficientEntries:
        plot2.set_xlim(0, currIndex - sufficientEntries)
        plot2.plot(time, stretchyValues, 'b--', label='Number') #plot other

    # bpm
    plot3 = plt.subplot(4, 1, 3) #will display a third graph directly beneath the third
    plot3.grid() #activate grid lines
    plot3.set_ylim(0, 150) #to create specific features for this graph, do plt.'functoin'(/*blah*/)
    plot3.set_ylabel('bpm')
    if currIndex > sufficientEntries:
        plot3.set_xlim(0, currIndex - sufficientEntries)
        plot3.plot(time, bpmValues, 'b--', label='Number')  # plot other; the 'b--' is a style thing. didn't play with it enough to know all the combinations

    # pressure
    plot4 = plt.subplot(4, 1, 4) #will display a third graph directly beneath the third
    plot4.grid() #activate grid lines
    plot4.set_ylim(0, 100) #to create specific features for this graph, do plt.'functoin'(/*blah*/)
    plot4.set_ylabel('pressure')
    if currIndex > sufficientEntries:
        plot4.set_xlim(0, currIndex - sufficientEntries)
        plot4.plot(time, bpmValues, 'b--', label='Number')  # plot other; the 'b--' is a style thing. didn't play with it enough to know all the combinations

def get_int_from_arduino(mod):
    # turn bytes from arduino into int
    if (mod == 0):
        arduinoReturn = arduinoData.readline() # get bytes from arduino
    elif (mod == 1):
        arduinoReturn = arduinoData2.readline() # get bytes from arduino
    else (mod == 2):
        arduinoReturn = arduinoData3.readline() # get bytes from arduino


    arduinoString = str(arduinoReturn) # convert bytes to string
    arduinoString = ''.join(ch for ch in arduinoString if ch.isalnum()) # get rid off all non alphanumeric bytes
    hmm = re.search(r'\d+', arduinoString)
    x = 0
    if not hmm is None:
        x = int(hmm.group()) # get integer from string

    return x

def loop():
    global count
    global isbpm
    global currIndex
    while True:  # While loop that loops forever
        while (arduinoData.inWaiting() == 0 or arduinoData2.inWaiting() == 0 or arduinoData3.inWaiting() == 0):  # Wait here until there is data
            pass  # do nothing


        mod = count % NUM_BOARDS

        if (mod == 0):
            tiger = get_int_from_arduino(mod)
            # filter out real big numbers
            if tiger > 500 and currIndex > sufficientEntries:
                tiger = stretchyValues[currIndex]
            stretchy.append(tiger)

            bpm.append(get_int_from_arduino(mod))
        elif (mod == 1):
            gsr.append(get_int_from_arduino(mod))
        elif (mod == 2):
            pressure.append(get_int_from_arduino(mod))


        if (count%60 == 0 and count > 400):
            w = functools.reduce(lambda x, y: x + y, bpm) / 20
            m = functools.reduce(lambda x, y: x + y, stretchy) / 20
            z = functools.reduce(lambda x, y: x + y, gsr) / 20
            q = functools.reduce(lambda x, y: x + y, pressure) / 20
            bpmValues.append(w)
            stretchyValues.append(m) # NOTE SURE IF ALL THE DATA CAN BE COLLECTED SIMULTAENOUSLY. IF IT CAN, YOU CAN PUT M AS THE ARGUMENT
            gsrValues.append(z)
            pressureValues.append(q)

            time.append(currIndex - sufficientEntries)  #The first 'sufficientEntries' entries recorded will not be displayed
                                                        #The first 2 entries, from my testing haven't been useful.
            currIndex = currIndex + 1
            bpm.clear()
            stretchy.clear()
            gsr.clear()
            pressure.clear()

            if (count > 600):
                drawnow(makeFig)  # Call drawnow to update our live graph
                plt.pause(.000001)  # Pause Briefly. Important to keep drawnow from crashing
        count += 1

plt.figure(figsize=[12, 6.5]) #initial width and height of the display. pressing x will close the window, and the default size will show up
setup()
loop()

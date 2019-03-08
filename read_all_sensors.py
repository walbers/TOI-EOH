import serial
import numpy as np

import matplotlib.pyplot as plt  # import matplotlib library
import matplotlib.animation as animation
from drawnow import *
import string
import re
import struct
import functools


from pynput import keyboard
from pynput.keyboard import Key, Controller
import time



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
lowergsr = 0
uppergsr = 600

pressure = []
pressureValues = []

time = [] #currently stores index. this allows the x-axis to build constantly
currIndex = 0 # a way to keep track of which value to put into time; is incremented after being appended
sufficientEntries = 4 #a variable to allow enough time for graph and data to start loading in
maxTime = 30 #currently unused

arduinoData = None
arduinoData2 = None
arduinoData3 = None

NUM_SENSORS = 3
NUM_BOARDS = 3
count = 0
#isbpm = 0

threshold1 = 1
threshold2 = 100
threshold3 = 1

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

''' MOHI '''
typer = Controller()
def on_press(key):
    global threshold1
    global threshold2
    global threshold3
    try:
        #print("this is:" + key)
        print('alphanumeric key {0} pressed'.format(
            key.char
        ))
        if key.char == 'i':
            mp.savefig('graph_output.png')
        if key.char == 't':
            if currIndex > 6:
                threshold1 = 0
                threshold2 = 0
                threshold3 = 0
                for i in range(2,7):
                    threshold1 += gsrValues[currIndex-i]
                    threshold2 += stretchyValues[currIndex-i]
                    threshold3 += bpmValues[currIndex-i]
                    print(bpmValues[currIndex-i])
                    # TODO SENSOR 4
                print('a', threshold3)
                threshold1 /= 5
                threshold2 /= 5
                threshold3 /= 5
            
                print('t', threshold3)
            #threshold1 = (gsrValues[currIndex-2] + gsrValues[currIndex-3] + gsrValues[currIndex-4] + gsrValues[currIndex-5] + gsrValues[currIndex-6]) / 5

    except AttributeError:
        print('special key {0} pressed'.format(key))

def on_release(key):
    if key == keyboard.Key.esc:
        return False


def makeFig():  # Create a function that makes our desired plot
    global currIndex

    # sweaty gsr
    plot1 = plt.subplot(3,1,1) #allows graphing multiple simulaneously. the numbers represent 3 rows, 1 colmun, 1st position, respectively.
    plot1.grid()
    plot1.set_ylim(0, 600)  # Set y min and max values
    plot1.set_title('My Live Streaming Sensor Data')  # Plot the title
    plot1.set_ylabel('sweaty/gsr')  # Set ylabels


    if currIndex > sufficientEntries:
        plot1.axhline(y=threshold1, color='r', linestyle='dotted') #create a line to represent the threshold
        percentDiff1 = ((gsrValues[currIndex - 1] - threshold1) / threshold1)
        plot1.legend([round(percentDiff1, 4)], loc='upper right')   # prints out the difference between plotted point

        plot1.set_xlim(0, currIndex - sufficientEntries)
        plot1.plot(time, gsrValues, 'r--', label='Number')
                                                            # and the the threshold.

    # stretchy
    plot2 = plt.subplot(3, 1, 2)    #will display a second graph directly beneath the first
    plot2.grid() #activate grid lines
    #plot2.set_ylim(threshold2-100, threshold2+100)
    plot2.set_ylim(threshold2-75, threshold2+75)
    plot2.set_ylabel('stretchy')

                                                        # and the the threshold.

    if currIndex > sufficientEntries:
        plot2.axhline(y=threshold2, color='r', linestyle='dotted')  # create a line to represent the threshold
        percentDiff2 = ((stretchyValues[currIndex - 1] - threshold2) / threshold2)
        plot2.legend([round(percentDiff2, 4)], loc='upper right')   # prints out the difference between plotted point

        plot2.set_xlim(0, currIndex - sufficientEntries)
        plot2.plot(time, stretchyValues, 'bo-', label='Number') #plot other

    # bpm
    plot3 = plt.subplot(3, 1, 3) #will display a third graph directly beneath the third
    plot3.grid() #activate grid lines
    plot3.set_ylim(0, 150)
    plot3.set_ylabel('bpm')
                            # and the the threshold.
    if currIndex > sufficientEntries:
        plot3.axhline(y=threshold3, color='r', linestyle='dotted')  # create a line to represent the threshold
        percentDiff3 = ((bpmValues[currIndex - 1] - threshold3) / threshold3)
        plot3.legend([round(percentDiff3, 4)], loc='upper right')   # prints out the difference between plotted point

        plot3.set_xlim(0, currIndex - sufficientEntries)
        plot3.plot(time, bpmValues, 'g--', label='Number')  # plot other; the 'b--' is a style thing.

    # pressure
    # plot4 = plt.subplot(4, 1, 4) #will display a third graph directly beneath the third
    # plot4.grid() #activate grid lines
    # plot4.set_ylim(0, 100)
    # plot4.set_ylabel('pressure')
    #
    # threshold4 = 200  # how to find?
    # plot4.axhline(y=threshold4, color='r', linestyle='dotted')  # create a line to represent the threshold
    # percentDiff4 = ((stretchyValues[currIndex - 1] - threshold4) / threshold4)
    # plot4.legend([round(percentDiff4, 2)], loc='upper right')   # prints out the difference between plotted point
    #                                                             # and the the threshold.
    # if currIndex > sufficientEntries:
    #     plot4.set_xlim(0, currIndex - sufficientEntries)
    #     plot4.plot(time, bpmValues, 'g--', label='Number')  # plot other; the 'b--' is a style thing.

        

def get_int_from_arduino(mod):
    # turn bytes from arduino into int
    if (mod == 0):
        arduinoReturn = arduinoData3.readline() # get bytes from arduino
    elif (mod == 1):
        arduinoReturn = arduinoData2.readline() # get bytes from arduino
    elif (mod == 2):
        arduinoReturn = arduinoData.readline() # get bytes from arduino


    arduinoString = str(arduinoReturn) # convert bytes to string
    arduinoString = ''.join(ch for ch in arduinoString if ch.isalnum()) # get rid off all non alphanumeric bytes
    hmm = re.search(r'\d+', arduinoString)
    x = 0
    if not hmm is None:
        x = int(hmm.group()) # get integer from string
    
    #if (mod == 2):
      #  print(x)
    return x


def loop():
    global count
    global isbpm
    global currIndex
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        while True:  # While loop that loops forever
            while (arduinoData.inWaiting() == 0 or arduinoData2.inWaiting() == 0): # or arduinoData3.inWaiting() == 0):  # Wait here until there is data
                pass  # do nothing


            mod = count % NUM_BOARDS

            if (mod == 0):
                tiger = get_int_from_arduino(mod)
                # filter out real big numbers
                if tiger > 500 and currIndex > sufficientEntries:
                    tiger = stretchyValues[currIndex-1]
                stretchy.append(tiger)

                #print(bpm)
            elif (mod == 1):
                gsr.append(get_int_from_arduino(mod))
            elif (mod == 2):
                bpm.append(get_int_from_arduino(mod))
                

            if (count%30 == 0 and count > 400):
                w = functools.reduce(lambda x, y: x + y, bpm) / 10
                m = functools.reduce(lambda x, y: x + y, stretchy) / 10
                z = functools.reduce(lambda x, y: x + y, gsr) / 10
                # q = functools.reduce(lambda x, y: x + y, pressure) / 20
                bpmValues.append(w)
                stretchyValues.append(m) # NOT SURE IF ALL THE DATA CAN BE COLLECTED SIMULTAENOUSLY. IF IT CAN, YOU CAN PUT M AS THE ARGUMENT
                gsrValues.append(z)
                # pressureValues.append(q)

                #print(bpm)
                #print(len(bpm))
                #print(bpmValues)
                #print(stretchyValues)
                #print(gsrValues)
                if  (currIndex == 20):
                    lowergsr = functools.reduce(lambda x, y: x+y, bpmValues) / len(bpmValues) + 30
                    uppergsr = functools.reduce(lambda x, y: x+y, bpmValues) / len(bpmValues) - 30


                time.append(currIndex - sufficientEntries)  #The first 'sufficientEntries' entries recorded will not be displayed
                                                            #The first 2 entries, from my testing haven't been useful.
                currIndex = currIndex + 1
                del bpm[:]
                del stretchy[:]
                del gsr[:]
                #bpm.clear()
                #stretchy.clear()
                #gsr.clear()
                # pressure.clear()

                if (count > 600):
                    drawnow(makeFig)  # Call drawnow to update our live graph
                    plt.pause(.000001)  # Pause Briefly. Important to keep drawnow from crashing
            count += 1

plt.figure(figsize=[12, 6.5]) #initial width and height of the display. pressing x will close the window, and the default size will show up
setup()
loop()

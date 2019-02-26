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


'''
MUST RERUN PROGRAM AND RESET ARDUINO FOR EACH NEW PERSON.
'''

bpm = []
stretchy = []
gsr = []

#arduinoData = serial.Serial('COM4', 9600)  # Creating our serial object named arduinoData
arduinoData2 = serial.Serial('COM3', 9600)  # Creating our serial object named arduinoData

#plt.ion()  # Tell matplotlib you want interactive mode to plot live data
NUM_SENSORS = 3
count = 0
isbpm = 0


def makeFig():  # Create a function that makes our desired plot
    plt.ylim(0, 600)  # Set y min and max values
    plt.title('My Live Streaming Sensor Data')  # Plot the title
    plt.grid(True)  # Turn the grid on
    plt.ylabel('Temp F')  # Set ylabels
    plt.plot(z, 'ro-', label='Degrees F')  # plot the temperature
    #plt.legend(loc='upper left')  # plot the legend

    # plt2 = plt.twinx()  # Create a second y axis
    # plt.ylim(0, 500)  # Set limits of second y axis- adjust to readings you are getting
    # plt2.plot(stretchy, 'b^-', label='strechness (Pa)')  # plot pressure data
    # plt2.set_ylabel('stretchness (Pa)')  # label second y axis
    # plt2.ticklabel_format(useOffset=False)  # Force matplotlib to NOT autoscale y axis
    # plt2.legend(loc='upper right')  # plot the legend

# def live_update_demo(blit = True):
#     x = np.linspace(0,50., num=100)
#     X,Y = np.meshgrid(x,x)
#     fig = plt.figure()
#     ax1 = fig.add_subplot(2, 1, 1)
#     ax2 = fig.add_subplot(2, 1, 2)
#
#     fig.canvas.draw()   # note that the first draw comes before setting data
#
#     h1 = ax1.imshow(X, vmin=-1, vmax=1, interpolation="None", cmap="RdBu")
#
#     h2, = ax2.plot(x, lw=3)
#     text = ax2.text(0.8,1.5, "")
#     ax2.set_ylim([-1,1])
#
#
#     if blit:
#         # cache the background
#         axbackground = fig.canvas.copy_from_bbox(ax1.bbox)
#         ax2background = fig.canvas.copy_from_bbox(ax2.bbox)
#
#     t_start = time.time()
#     k=0.
#     for i in np.arange(1000):
#         h1.set_data(np.sin(X/3.+k)*np.cos(Y/3.+k))
#         h2.set_ydata(np.sin(x/3.+k))
#         tx = 'Mean Frame Rate:\n {fps:.3f}FPS'.format(fps= ((i+1) / (time.time() - t_start)) )
#         text.set_text(tx)
#         #print tx
#         k+=0.11
#         if blit:
#             # restore background
#             fig.canvas.restore_region(axbackground)
#             fig.canvas.restore_region(ax2background)
#
#             # redraw just the points
#             ax1.draw_artist(h1)
#             ax2.draw_artist(h2)
#
#             # fill in the axes rectangle
#             fig.canvas.blit(ax1.bbox)
#             fig.canvas.blit(ax2.bbox)
#             # in this post http://bastibe.de/2013-05-30-speeding-up-matplotlib.html
#             # it is mentionned that blit causes strong memory leakage.
#             # however, I did not observe that.
#
#         else:
#             # redraw everything
#             fig.canvas.draw()
#             fig.canvas.flush_events()
#
#
#         plt.pause(0.000000000001)
#         #plt.pause calls canvas.draw(), as can be read here:
#         #http://bastibe.de/2013-05-30-speeding-up-matplotlib.html
#         #however with Qt4 (and TkAgg??) this is needed. It seems,using a different backend,
#         #one can avoid plt.pause() and gain even more speed.


# fig = plt.figure()
# ax1 = fig.add_subplot(1,1,1)
#
# def animate(i):
#     ax1.clear()
#     ax1.plot(count, z)



while True:  # While loop that loops forever
    while (arduinoData2.inWaiting() == 0):  # Wait here until there is data
        pass  # do nothing

    mod = count % NUM_SENSORS

    # if (mod == 0 or mod == 1):
    #
    #     arduinoReturn = arduinoData.readline() # get bytes from arduino
    #
    #     # turn bytes from arduino into int
    #     arduinoString = str(arduinoReturn) # convert bytes to string
    #     arduinoString = ''.join(ch for ch in arduinoString if ch.isalnum()) # get rid off all non alphanumeric bytes
    #     x = int(re.search(r'\d+', arduinoString).group()) # get integer from string
    #
    #     if (isbpm):
    #         bpm.append(x)
    #         isbpm = 0
    #     else:
    #          stretchy.append(x)
    #          isbpm = 1
    #elif (mod == 2):
    if (mod == 2):
        arduinoReturn = arduinoData2.readline() # get bytes from arduino

        # turn bytes from arduino into int
        arduinoString = str(arduinoReturn) # convert bytes to string
        arduinoString = ''.join(ch for ch in arduinoString if ch.isalnum()) # get rid off all non alphanumeric bytes
        x = int(re.search(r'\d+', arduinoString).group()) # get integer from string

        gsr.append(x)

    if (count%90 == 0 and count > 400):
        print('averaging')
        print(gsr)
        # w = functools.reduce(lambda x, y: x + y, bpm) / 30
        # m = functools.reduce(lambda x, y: x + y, stretchy) / 30
        z = functools.reduce(lambda x, y: x + y, gsr) / 30
        print(z)
        # bpm.clear()
        # stretchy.clear()
        gsr.clear()

        if (count > 600):
            drawnow(makeFig)  # Call drawnow to update our live graph
            plt.pause(.000001)  # Pause Briefly. Important to keep drawnow from crashing
    count += 1

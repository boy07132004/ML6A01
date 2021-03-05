import time
import numpy as np
import pandas as pd
from collections import deque
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import matplotlib.animation as ani
import paho.mqtt.publish as publish
from scipy.fftpack import fft,fftshift

THRESHOLD = -1
POWERON = False


def on_connect(client, userdata, flags, rc):
    client.subscribe('ctValue')
    client.subscribe('vibration')
    

def on_message(client, userdata, msg):
    global POWERON
    if msg.topic == 'ctValue':
        ctValue = int(msg.payload.decode('utf-8'))
        POWERON = True if ctValue>THRESHOLD else False
        ctDeque.append(ctValue)

    elif msg.topic == 'vibration':
        try:
            if POWERON:
                msgDecode = msg.payload.decode('utf-8').split()
                ls = []
                for i in msgDecode:
                    ls.append(i.split(','))
                vibrationDeque.extend(ls)
                plotDeque.append([float(i) for i in ls[0]])
                return

        except:
            pass

        plotDeque.append([0,0,0])


class mqttPlot():
    def __init__(self):
        self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot(2,1,1)
        xs  = list(range(200)) 
        self.lineX, = self.ax1.plot(xs,[0]*200,'r')
        self.lineY, = self.ax1.plot(xs,[0]*200,'g')
        self.lineZ, = self.ax1.plot(xs,[0]*200,'b')
        self.ax1.legend([self.lineX,self.lineY,self.lineZ],['X','Y','Z'])
        self.ax1.set_ylim([-1.5,1.5])
        self.ax2 = self.fig.add_subplot(2,1,2)
        self.ax2.set_ylim([0,5000])
        self.lineCT, = self.ax2.plot(xs,[0]*200,'r')
        self.ani = ani.FuncAnimation(self.fig,self.mqttAnimate,interval=100)
    
    def mqttAnimate(self,i):
        self.lineX.set_ydata([vib[0] for vib in list(plotDeque)])
        self.lineY.set_ydata([vib[1] for vib in list(plotDeque)])
        self.lineZ.set_ydata([vib[2] for vib in list(plotDeque)])
        self.lineCT.set_ydata(ctDeque)


class fftPlot():
    def __init__(self):
        self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot(1,3,1)
        self.ax2 = self.fig.add_subplot(1,3,2)
        self.ax3 = self.fig.add_subplot(1,3,3)
        self.fftPlotX, = self.ax1.plot([0]*500)
        self.fftPlotY, = self.ax2.plot([0]*500)
        self.fftPlotZ, = self.ax3.plot([0]*500)
        self.ani = ani.FuncAnimation(self.fig,self.fftAnimate,interval=900)

    def fftAnimate(self,i):
        fftPlot = [self.fftPlotX, self.fftPlotY, self.fftPlotZ]
        for i in range(3):
            if POWERON:
                vib = [vib[i] for vib in list(vibrationDeque)]
                try:fftData = fft(vib)
                except:pass
                myfft   = abs(fftData)*2 / 1000   # length of vib1000Data 
                myfft2  = myfft[:500]             # 500 -> length of vib1000Data * 0.5
                yData = fftshift(np.abs(myfft2))
                yData[250] = 0 
                fftPlot[i].set_ydata(yData)
            else:
                fftPlot[i].set_ydata([0]*500)


if __name__ == "__main__":
    ctDeque        = deque([0]*200, maxlen=200)
    plotDeque      = deque([[0,0,0]]*200, maxlen=200)
    vibrationDeque = deque([[0,0,0]]*1000, maxlen=1000)
    
    fftPlot = fftPlot()
    mqttPlot = mqttPlot()

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    #client.username_pw_set('user', 'password')
    client.connect("localhost", 1883, 60)
    client.loop_start()
    plt.show()
    client.loop_stop()
    client.disconnect()

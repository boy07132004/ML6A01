import time
import numpy as np
import pandas as pd
from collections import deque
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import matplotlib.animation as ani
import paho.mqtt.publish as publish
from scipy.fftpack import fft,fftshift

THRESHOLD = 20
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
        return

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
        
    #ctDeque.append(0)
    plotDeque.append([0,0,-1])


class mqttPlot():
    def __init__(self):
        self.fig = plt.figure()
        self.xs  = list(range(200)) 
        self.xPlot()
        self.yPlot()
        self.zPlot()
        self.ax2 = self.fig.add_subplot(3,2,4)
        self.ax2.set_title("CT value")
        self.ax2.set_ylim([0,500])
        self.lineCT, = self.ax2.plot(self.xs,[0]*200,'b')
        self.ax2.plot(self.xs,[30]*200,'r') # Threshold
        self.ani = ani.FuncAnimation(self.fig,self.mqttAnimate,interval=100)
    
    def xPlot(self):
        self.axisX = self.fig.add_subplot(3,2,1)
        self.axisX.set_title("Vibration 3-Axis")
        self.axisX.set_ylim([-0.3,0.3])
        self.lineX, = self.axisX.plot(self.xs,[0]*200,'r')
        self.axisX.legend(handles=[self.lineX],labels='X')
    
    def yPlot(self):
        self.axisY = self.fig.add_subplot(3,2,3)
        self.axisY.set_ylim([-0.3,0.3])
        self.lineY, = self.axisY.plot(self.xs,[0]*200,'g')
        self.axisY.legend(handles=[self.lineY],labels='Y')
    
    def zPlot(self):
        self.axisZ = self.fig.add_subplot(3,2,5)
        self.axisZ.set_ylim([-1.3,-0.7])
        self.lineZ, = self.axisZ.plot(self.xs,[0]*200,'b')
        self.axisZ.legend(handles=[self.lineZ],labels='Z')
    
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
        self.ax1.set_title("FFT Axis X")
        self.ax2.set_title("FFT Axis Y")
        self.ax3.set_title("FFT Axis Z")
        self.fftPlotX, = self.ax1.plot([0]*500)
        self.fftPlotY, = self.ax2.plot([0]*500)
        self.fftPlotZ, = self.ax3.plot([0]*500)
        self.ax1.set_ylim([0,0.05])
        self.ax2.set_ylim([0,0.05])
        self.ax3.set_ylim([0,0.05])
        self.ani = ani.FuncAnimation(self.fig,self.fftAnimate,interval=900)

    def fftAnimate(self,i):
        fftPlot = [self.fftPlotX, self.fftPlotY, self.fftPlotZ]
        try:
            for i in range(3):
                if POWERON:
                    vib = [vib[i] for vib in list(vibrationDeque)]
                    fftData = fft(vib)
                    myfft   = abs(fftData)*2 / 1000   # length of vib1000Data 
                    myfft2  = myfft[:500]             # 500 -> length of vib1000Data * 0.5
                    yData = fftshift(np.abs(myfft2))
                    yData[250] = 0 
                    fftPlot[i].set_ydata(yData)
                else:
                    fftPlot[i].set_ydata([0]*500)
        except:pass


if __name__ == "__main__":
    ctDeque        = deque([0]*200, maxlen=200)
    plotDeque      = deque([[0,0,-1]]*200, maxlen=200)
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

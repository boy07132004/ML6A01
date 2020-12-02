import ads1x15
import time
import threading
import pandas as pd
from collections import deque
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import matplotlib.animation as ani
import paho.mqtt.publish as publish

def detectCT(flag):
    global ctValue
    timeStamp = time.perf_counter()
    ads = ads1x15.ads1015()
    while not flag():
        while time.perf_counter()-timeStamp < 0.01 :pass
        ctValue = ads.read()
        publish.single("CT",ctValue,hostname="192.168.0.100",port=1883)
        
def on_connect(client, userdata, flags, rc):
    client.subscribe('rand')
    
def on_message(client, userdata, msg):
    global ctValue
    global x
    global y
    global z
    try:
        if ctValue>200:
        #if True:
            msgDecode = msg.payload.decode('utf-8').split()[0].split('\\n')
            ls = []
            for i in msgDecode:
                ls.append(i.split(','))
            df = pd.DataFrame(ls)
            _x,_y,_z = df.mean()[1:]
            #print(_x,_y,_z)
        else:
            _x,_y,_z = 0,0,0
        for i in ('x','y','z'):
            eval(i).popleft()
            eval(i).append(float(eval('_'+i)))
    except:_x,_y,_z = 0,0,0
def animate(i):
    for line,ls in ((line_x,x),(line_y,y),(line_z,z)):
        line.set_ydata(ls)
    return 0

if __name__ == "__main__":
    x = deque([0]*200)
    y = deque([0]*200)
    z = deque([0]*200)
    fig = plt.figure()
    ax1 = fig.add_subplot(1,1,1)
    xs  = list(range(200)) 
    ax1.set_ylim([-1.5,1.5])
    line_x, = ax1.plot(xs,x,'r')
    line_y, = ax1.plot(xs,y,'g')
    line_z, = ax1.plot(xs,z,'b')
    ax1.legend([line_x,line_y,line_z],['X','Y','Z'])
    ani = ani.FuncAnimation(fig,animate,interval=50)
    
    stopFlag = False
    t = threading.Thread(target=detectCT,args=(lambda:stopFlag,))
    t.start()
    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    #client.username_pw_set('user', 'password')
    client.connect("192.168.0.100", 1883, 60)
    client.loop_start()
    plt.show()
    client.loop_stop()
    client.disconnect()
    
    stopFlag = True
    t.join()
    
    

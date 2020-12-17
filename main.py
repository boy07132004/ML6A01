import time
import signal
import pandas as pd
import multiprocessing as mp
from collections import deque
import paho.mqtt.client as mqtt

ctValue = 0
THRESHOLD = 2
STOPFLAG = False

def signal_handler(signal,frame):
    print("End the program")
    client.loop_stop()
    client.disconnect()
    
    global fftProcess
    fftProcess.terminate()
    fftProcess.join()
    import sys
    sys.exit(0)
    

def on_connect(client, userdata, flags, rc):
    client.subscribe("ctValue")
    client.subscribe("rand")
    
def on_message(client, userdata, msg):
    global ctValue
    global vibrationDataQueue
    if msg.topic == 'rand':
        # Save vibration data to queue
        dataList = msg.payload.decode('utf-8').split("\n")
        for data in dataList:
            vibrationDataQueue.append(data.split(','))
    elif msg.topic == 'ctValue':
        ctValue = int(msg.payload)

def fft_process(featureExtractionQueue):
    import fft
    from sqlalchemy import create_engine
    engine = create_engine('mysql+pymysql://user:password@localhost:3306/Fan')
    while True:
        try:
            queue = featureExtractionQueue.get(timeout=2)
            df = pd.DataFrame(queue,columns=['T','X','Y','Z'])
            rawdataX = df['X'].values.astype('float32')
            rawdataY = df['Y'].values.astype('float32')
            rawdataZ = df['Z'].values.astype('float32')
            feature = fft.get_all_feature(rawdataX,rawdataY,rawdataZ,1000)
            #feature.to_sql('FanTable',engine,index=False,if_exists='append')
            print(feature)

        except (KeyboardInterrupt,SystemExit):
            break
        except:
            # Block queue
            featureExtractionQueue.get()
            # Wait buffer to be fill with new data
            time.sleep(1)


if __name__ == "__main__":
    
    signal.signal(signal.SIGINT,signal_handler)

    # Make a deque for vibration data
    vibrationDataQueue = deque(maxlen=1000)
    featureExtractionQueue = mp.Queue(maxsize=1)
    
    # Client setup
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(host="localhost")
    client.loop_start()
    
    # Process start
    fftProcess = mp.Process(target=fft_process,args=(featureExtractionQueue,))
    fftProcess.start()
    lastTime = time.perf_counter()
    enterBuffer = 0
    while True:
        try:
            # Start feature extraction when the CT Value continuously exceed the threhold 10 times.
            while enterBuffer>=10 and len(vibrationDataQueue)==1000:
                # Wait for 1 second
                while time.perf_counter()-lastTime<1:pass
                featureExtractionQueue.put(list(vibrationDataQueue))
                # Publish fft vibration data
                lastTime = time.perf_counter()
                if ctValue<=THRESHOLD:
                    break
            if ctValue>THRESHOLD: enterBuffer+=1
            else:
                # Clear buffer
                enterBuffer = 0
        except:
            break

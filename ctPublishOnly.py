import ads1x15
import time
import paho.mqtt.publish as publish

def main():
    ads = ads1x15.ads1015()
    timeStamp = time.perf_counter()
    while True:
        while time.perf_counter()-timeStamp < 0.01 :pass
        ctValue = ads.read()
        publish.single("CT",ctValue,hostname="192.168.0.100",port=1883)

if __name__ == "__main__":
    main()
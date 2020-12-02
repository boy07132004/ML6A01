# pip install Adafruit_ADS1x15
from Adafruit_ADS1x15 import ADS1015

class ads1015():
    def __init__(self,pin=0,rate = 1600):
        self.ads = ADS1015()
        self.ads.start_adc(pin,gain=1,data_rate=rate)
    def read(self):
        return self.ads.get_last_result()
    
if __name__ == '__main__':
    import time
    ads = ads1015()
    now = time.perf_counter()
    while 1:
        while time.perf_counter()-now<1/100:pass
        print(ads.read(),1/(time.perf_counter()-now))
        now = time.perf_counter()
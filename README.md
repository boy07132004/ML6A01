# Status plot
Plot vibration data and fft plot when the CT value over the threshold.
## Devices
```
* CT data publisher
    - D1 mini + ADS1015
        - D1 <-> SCL
        - D2 <-> SDA

* Vibration data publisher
    - [DUAL ESP32](https://github.com/boy07132004/MQTT_HighFreqAccelData)
```

## Start
```bash
 python3 LiveGraph.py
 ```

## Image
<img src="https://github.com/boy07132004/ML6A01/blob/master/image.png">

## issue
 I don't know why the half of fftData (yData[250] in this case) is always larger than others, so I set it to zero temporarily.
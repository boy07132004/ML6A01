import time
import pywt
import numpy as np
import pandas as pd
from scipy.fftpack import fft
from scipy.stats import skew,kurtosis



def feature_extraction_st(healthy_Vibrationdataset):
    #####wavelet extraction####
    Hamp_healthy_Vibration = [
        np.sqrt(np.mean(healthy_Vibrationdataset**2)),
        np.mean(healthy_Vibrationdataset),
        kurtosis(healthy_Vibrationdataset,axis=0,fisher= False),
        np.ptp(healthy_Vibrationdataset),
        skew(healthy_Vibrationdataset),
        np.std(healthy_Vibrationdataset)]
        
    return Hamp_healthy_Vibration # list shape(6,)

def fourier_transform(data):
    dataLength = len(data)
    myfft = abs(fft(data))*2/dataLength
    myfft2 = myfft[0:dataLength//2]
    #return myfft2
    return np.array([myfft2]).transpose()

def feature_extraction_fft(healthy_Vibrationdataset,dataLength):
    ###########parameter ###################
    dataLength2 = int(dataLength/2)
    Fs = dataLength
    n= dataLength
    dF = Fs/n
    T= 1/Fs
    t = np.linspace(0,dataLength-1,dataLength)*T
    freq = np.linspace(0,dataLength2-1,dataLength2)*dF
    baseFreq1 = 35   #2000/60 = 33
    dFreq1 = 15; dFreq2 = 20; dFreq3 = 25 #; dFreq4 = 15  #### can change
    len1 = 7
    ###Fourier transform and plot spectrum figure
    Hfeat_Vibration = fourier_transform(healthy_Vibrationdataset)
    ###feature extraction for healthy vibration data 
    Hamp_healthy_Vibration = [
        max(Hfeat_Vibration[int((baseFreq1*1-dFreq1)/dF):int((baseFreq1*1+dFreq1)/dF)]),
        max(Hfeat_Vibration[int((baseFreq1*2-dFreq1)/dF):int((baseFreq1*2+dFreq1)/dF)]),
        max(Hfeat_Vibration[int((baseFreq1*3-dFreq1)/dF):int((baseFreq1*3+dFreq1)/dF)]),
        max(Hfeat_Vibration[int((baseFreq1*6-dFreq2)/dF):int((baseFreq1*6+dFreq2)/dF)]),
        max(Hfeat_Vibration[int((baseFreq1*8-dFreq1)/dF):int((baseFreq1*8+dFreq1)/dF)]),
        max(Hfeat_Vibration[int((baseFreq1*8+dFreq1)/dF):int((baseFreq1*8+dFreq3)/dF)]),
        max(Hfeat_Vibration[int((baseFreq1*9)/dF):int((baseFreq1*10+dFreq3)/dF)])
    ]
    
    return Hamp_healthy_Vibration


def feature_extraction_wv(SingleDataWavelet,n=3):
    wp = pywt.WaveletPacket(SingleDataWavelet, wavelet='db1',mode='symmetric',maxlevel=n)

    re = []
    for j in [node.path for node in wp.get_level(n, 'freq')]:
        re.append(wp[j].data)
    SingleDir_SamplesFeature = []
    
    for k in range(len(re)):
        SingleDir_SamplesFeature.append(np.linalg.norm(np.array(re)[k],ord=None)**2)

    return SingleDir_SamplesFeature

def get_all_feature(vibration_x,vibration_y,vibration_z,dataLength): 
    ###step1_st
    Hamp_xVibration_st = feature_extraction_st(vibration_x)
    Hamp_yVibration_st = feature_extraction_st(vibration_y)
    Hamp_zVibration_st = feature_extraction_st(vibration_z)
    
    ###step2_fft
    Hamp_xVibration_fft = feature_extraction_fft(vibration_x,dataLength)
    Hamp_yVibration_fft = feature_extraction_fft(vibration_y,dataLength)
    Hamp_zVibration_fft = feature_extraction_fft(vibration_z,dataLength)
    
    ###step3_wavelet
    Hamp_xVibration_wv = feature_extraction_wv(vibration_x)
    Hamp_yVibration_wv = feature_extraction_wv(vibration_y)
    Hamp_zVibration_wv = feature_extraction_wv(vibration_z)
    
    ### Concateante feature lists
    Hamp_healthy_xVibration = Hamp_xVibration_st + Hamp_xVibration_fft + Hamp_xVibration_wv
    Hamp_healthy_yVibration = Hamp_yVibration_st + Hamp_yVibration_fft + Hamp_yVibration_wv
    Hamp_healthy_zVibration = Hamp_zVibration_st + Hamp_zVibration_fft + Hamp_zVibration_wv
    
    feature_name = ['1-x-rms','2-x-mean','3-x-kurtosis','4-x-peak2peak','5-x-skewness','6-x-std',
                    '7-x-FFT1X','8-x-FFT2X','9-x-FFT3X','10-x-FFT4X','11-x-FFT5X','12-x-FFT6X','13-x-FFT7X',
                    '14-x-WT1','15-x-WT2','16-x-WT3','17-x-WT4','18-x-WT5','19-x-WT6','20-x-WT7','21-x-WT8',

                    '22-y-rms','23-y-mean','24-y-kurtosis','25-y-peak2peak','26-y-skewness','27-y-std',
                    '28-y-FFT1X','29-y-FFT2X','30-y-FFT3X','31-y-FFT4X','32-y-FFT5X','33-y-FFT6X','34-y-FFT7X',
                    '35-y-WT1','36-y-WT2','37-y-WT3','38-y-WT4','39-y-WT5','40-y-WT6','41-y-WT7','42-y-WT8',
                    
                    '43-z-rms','44-z-mean','45-z-kurtosis','46-z-peak2peak','47-z-skewness','48-z-std',
                    '49-z-FFT1X','50-z-FFT2X','51-z-FFT3X','52-z-FFT4X','53-z-FFT5X','54-z-FFT6X','55-z-FFT7X',
                    '56-z-WT1','57-z-WT2','58-z-WT3','59-z-WT4','60-z-WT5','61-z-WT6','62-z-WT7','63-z-WT8']                 

    newfeature  = pd.DataFrame([Hamp_healthy_xVibration + Hamp_healthy_yVibration + Hamp_healthy_zVibration], columns=feature_name).astype('float32')
    newfeature.insert(0,'SystemTime',time.strftime("%Y-%m-%d %H:%M:%S"))
    return newfeature

if __name__ == '__main__':
    import csv
    _x = pd.read_csv("sample.csv",header=None).values
    _x = _x[:,0]
    print(_x.shape) # np.ndarray -> [0,1,2,3,4,....]
    import time
    start = time.perf_counter()
    print(get_all_feature(_x,_x,_x,1000))
    print(f"Feature extractions cost {time.perf_counter()-start}s")
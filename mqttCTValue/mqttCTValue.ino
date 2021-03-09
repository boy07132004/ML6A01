#include <Wire.h>
#include <ESP8266WiFi.h>
#include <AsyncMqttClient.h>
#include <Adafruit_ADS1015.h>

#define MQTT_PORT 1883
#define MQTT_HOST IPAddress(192,168,0,250)
#define SSID "SSID"
#define PASSWORD "PASSWORD"

AsyncMqttClient mqttClient;
Adafruit_ADS1015 ads;     /* Use this for the 12-bit version */

void setup(void) 
{
  Serial.begin(9600);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(SSID,PASSWORD);
  while (!WiFi.isConnected()) delay(100);
  Serial.println("WIFIBegin");
  mqttClient.setServer(MQTT_HOST,MQTT_PORT);
  mqttClient.connect();
  Serial.println("ADC Range: +/- 6.144V (1 bit = 3mV/ADS1015, 0.1875mV/ADS1115)");
  
  // The ADC input range (or gain) can be changed via the following
  // functions, but be careful never to exceed VDD +0.3V max, or to
  // exceed the upper and lower limits if you adjust the input range!
  // Setting these values incorrectly may destroy your ADC!
  //                                                                ADS1015  ADS1115
  //                                                                -------  -------
  // ads.setGain(GAIN_TWOTHIRDS);  // 2/3x gain +/- 6.144V  1 bit = 3mV      0.1875mV (default)
  // ads.setGain(GAIN_ONE);        // 1x gain   +/- 4.096V  1 bit = 2mV      0.125mV
  // ads.setGain(GAIN_TWO);        // 2x gain   +/- 2.048V  1 bit = 1mV      0.0625mV
  // ads.setGain(GAIN_FOUR);       // 4x gain   +/- 1.024V  1 bit = 0.5mV    0.03125mV
  ads.setGain(GAIN_EIGHT);      // 8x gain   +/- 0.512V  1 bit = 0.25mV   0.015625mV
  // ads.setGain(GAIN_SIXTEEN);    // 16x gain  +/- 0.256V  1 bit = 0.125mV  0.0078125mV
  
  ads.begin();
}

void loop(void) 
{
  int16_t adc0;
  adc0 = ads.readADC_SingleEnded(0);
  char out[5];
  snprintf(out,5,"%d",adc0);
  mqttClient.publish("ctValue",0,true,out);
  delay(20);
}

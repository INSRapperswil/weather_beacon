import urequests
import time
from machine import Pin,  RTC
from settings import Settings
from ntplib import NTPClient

API_KEY = "123"
NUMBER_OF_3HRS_WINDOWS = 2


class Main(object):
    def __init__(self):
        self.settings = Settings('settings.json')
                
    def configure(self):
        print('Config menu')
        print('Type c to configure device, otherwise just wait')
        read_data = input()

        if 'c' in read_data:
            wifi_password = input('WiFi Password: ')
            ssid = input('Enter SSID: ')
            self.settings.set('ssid',  ssid)
            self.settings.set('password',  wifi_password)
        else:
            print('No configuration changes')
        print('Booting')


    def do_connect():
        import network
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        if not wlan.isconnected():
            ssid = self.settings.get('ssid')
            password = self.settings.get('password')
            wlan.connect(ssid, password)
            print('Connecting to network %s...' % ssid)
            while not wlan.isconnected():
                pass
            print('Connected to %s' % ssid)
        print('network config:', wlan.ifconfig())
        
    def setup_time():
        ntp_client = NTPClient()
        resp = ntp_client.request('0.ch.pool.ntp.org',  version=3,  port=123)
        rtc = RTC()
        rtc.init(time.localtime(time.time() + resp.offset))   


if __name__ == '__main__':
    main = Main()
    #main.do_connect()
    #main.setup_time()
    main.configure()
    
    
    """"
        
    do_connect()
    dictionary = {num: False for num in range(NUMBER_OF_3HRS_WINDOWS)}

    url = "http://api.openweathermap.org/data/2.5/forecast?q=Hinwil,ch&mode=json&cnt=%i&appid=%s" % (
        NUMBER_OF_3HRS_WINDOWS, API_KEY)
    print(url)
    while True:
        try:
            response = urequests.get(url)
        except Exception:
            continue

        json = response.json()

        forecasts = json['list']
        rain = False
        for i, forecast in enumerate(forecasts[0:NUMBER_OF_3HRS_WINDOWS]):
            print(forecast["rain"])
            if forecast["rain"]:
                rain = True
                dictionary[i] = True

        if rain:
            print("It is going to rain!")
        else:
            print("It wont rain")

        for k in dictionary.items():
            pin = Pin(k + 3, Pin.OUT)
            pin.high if k else pin.low()
        print(dictionary)
        time.sleep(10)"""

import urequests
import time
import pycom
from machine import Pin, RTC
from settings import Settings
from untplib import NTPClient
import network

API_KEY = 'd0f45e3399601a8ffe9724652905c8f7'
NUMBER_OF_3HRS_WINDOWS = 4


class Main(object):
    CONFIGURE_WLAN = '2'
    CONFIGURE_LOCATION = '1'
    REPL_MODE = '3'
    BEACON_MODE = '4'
    SHOW_SETTINGS = '5'
    SHOW_MENU = 'x'

    CHOICES = [CONFIGURE_WLAN, CONFIGURE_LOCATION, REPL_MODE, BEACON_MODE, SHOW_SETTINGS]

    def __init__(self):
        self.settings = Settings('/flash/settings.json')
        self.exit = False
        self.wlan = None

    def configure(self):

        choice = Main.SHOW_MENU
        while choice not in Main.CHOICES:
            try:
                print('\n\nConfiguration menu')
                print('-' * 30)
                choice = input(
                    'Type:\n  1) to configure location settings\n  2) to configure WiFi Settings\n  3) to get REPL for your own experiments\n  4) start the weather beacon application\n'
                    '  5) to show all settings\n\nChoice: ')[
                    0].lower()
                if choice == Main.CONFIGURE_WLAN:
                    print('Scanning for available networks...')
                    if not self.wlan:
                        self.wlan = network.WLAN(mode=network.WLAN.STA)
                    wlans = self.wlan.scan()
                    print("Available WiFi networks:")
                    for i, wlan in enumerate(wlans):
                        sec_string = 'Open'
                        if wlan.sec == network.WLAN.WEP:
                            sec_string = 'WEP'
                        elif wlan.sec == network.WLAN.WPA:
                            sec_string = 'WPA'
                        elif wlan.sec == network.WLAN.WPA2:
                            sec_string = 'WPA2'

                        print('%i: %s security: %s' % (i, wlan.ssid, sec_string))

                    # Chose ssid to connect to
                    ssid_chosen = False
                    while not ssid_chosen:
                        ssid = input('Enter SSID number: ')
                        try:
                            wlan = wlans[int(ssid)]
                            wifi_password = None
                            if (wlan.sec != 0):
                                wifi_password = input('Enter WiFi Password: ')
                            print('Settings saved')
                            choice = Main.SHOW_MENU
                            ssid_chosen = True
                            self.settings.set('ssid', wlan.ssid)
                            self.settings.set('wifi_sec', wlan.sec)
                            self.settings.set('password', wifi_password)
                            print('Settings saved')
                        except ValueError:
                            continue
                elif choice == Main.CONFIGURE_LOCATION:
                    location = input('Name of the location (e.g Zurich): ')
                    self.settings.set('location', location)
                    choice = Main.SHOW_MENU
                    print('Location saved')

                elif choice == Main.REPL_MODE:
                    print('Starting REPL mode')
                    self.exit = True
                elif choice == Main.BEACON_MODE:
                    print('Starting beacon application')
                elif choice == Main.SHOW_SETTINGS:
                    print('\n\nSettings')
                    print('-' * 30)
                    ssid = self.settings.get('ssid')
                    password = self.settings.get('password')
                    location = self.settings.get('location')
                    print('WiFi SSID: %s \nWiFi Password: %s\nLocation: %s' % (ssid, password, location))
                    choice = Main.SHOW_MENU

            except KeyboardInterrupt:
                choice = Main.SHOW_MENU

    def blink(self, color, times):
        pycom.rgbled(color)
        time.sleep_ms(500)
        pycom.rgbled(0x000000)
        time.sleep_ms(500)

    def do_connect(self):
        if not self.wlan:
            self.wlan = network.WLAN(mode=network.WLAN.STA)
        if not self.wlan.isconnected():
            ssid = self.settings.get('ssid')
            password = self.settings.get('password')
            sec = self.settings.get('wifi_sec')

            if sec:
                self.wlan.connect(ssid, auth=(sec, password))
            else:
                self.wlan.connect(ssid, auth=None)
            print('Connecting to network %s...' % ssid)

            for i in range(10):
                if not self.wlan.isconnected():
                    self.blink(0x0000FF, 2)
            while not self.wlan.isconnected():
                self.blink(0xFF0000)
            self.blink(0x00FF00, 1)
            print('Connected to %s' % ssid)

        self.blink(0x00FF00, 3)
        print('network config:', self.wlan.ifconfig())

    def setup_time(self):
        ntp_client = NTPClient()
        resp = ntp_client.request('0.ch.pool.ntp.org', version=3, port=123)
        rtc = RTC()
        rtc.init(time.localtime(time.time() + resp.offset))

    def get_weather(self):
        print('Querying weather data')
        url = "http://api.openweathermap.org/data/2.5/forecast?q=Hinwil,ch&mode=json&cnt=%i&appid=%s" % (
            NUMBER_OF_3HRS_WINDOWS, API_KEY)


        codes = []
        try:
            response = urequests.get(url)
            json = response.json()
            forecasts = json['list']
            for item in forecasts:
                codes += int(item['weather'][0]['id'])
        except Exception as e:
            print('Something went wrong while processing weather data')
            self.blink(0xFF0000, 3)
            print(e)
            return weather.NODATA

        rain = False
        sun = False
        snow = False
        clouds = False

        for code in codes:
            if 300 <= code <=600:
                rain = True
            if 600 <= code <= 600:
                snow = True
            if code == 800 or code == 801:
                sun = True
            if code <= 800 <= 900:
                clouds = True

        if snow:
            return weather.SNOW
        if rain:
            return weather.RAIN
        if sun:
            return weather.SUNSHINE


class weather(object):
    SUNSHINE = 0xFFFF00
    RAIN = 0x0000FF
    SNOW = 0xFFFFFF
    NODATA = 0xFF0000


if __name__ == '__main__':
    print('start')
    main = Main()

    # detect pressed button
    button = Pin("G17", Pin.IN, pull=Pin.PULL_UP)
    val = 10
    for i in range(10):
        val -= button.value()
        time.sleep_ms(20)

    if val > 6:
        main.configure()

    if not main.exit:
        try:
            pycom.heartbeat(False)
            main.do_connect()
            while True:
                weather_color = main.get_weather()
                pycom.rgbled(weather_color)

                time.sleep(10)
        except KeyboardInterrupt:
            print('Main interrupted')

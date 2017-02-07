import urequests
import time
from machine import Timer
import sys
import pycom
from machine import Pin, RTC
from settings import Settings
import network

API_KEY = 'd0f45e3399601a8ffe9724652905c8f7'
NUMBER_OF_3HRS_WINDOWS = 4
QUERY_INTERVAL = 600


class Main(object):
    # Menu choices
    CONFIGURE_WLAN = '2'
    CONFIGURE_LOCATION = '1'
    REPL_MODE = '3'
    BEACON_MODE = '4'
    SHOW_SETTINGS = '5'
    SHOW_MENU = 'x'

    CHOICES = [CONFIGURE_WLAN, CONFIGURE_LOCATION, REPL_MODE, BEACON_MODE, SHOW_SETTINGS]

    # State colors
    WLAN_CONNECTING = 0x0000FF
    WLAN_CONNECTED = 0x00FF00
    ERROR = 0xFF0000

    def __init__(self):
        self.settings = Settings('/flash/settings.json')
        self.exit = False
        self.wlan = None
        self.alarm = None

    def configure(self):
        choice = Main.SHOW_MENU
        while choice not in Main.CHOICES:
            try:
                print('\n\nConfiguration menu')
                print('-' * 30)
                choice_raw = input(
                    ('Type:\n  1) Configure location settings [{0}]\n  '
                     '2) Configure WiFi Settings [{1}]\n  '
                     '3) Get REPL for your own experiments\n  '
                     '4) Start the weather beacon application\n  '
                     '5) Show all settings\n\nChoice: ').format(self.settings.get('location'),
                                                                self.settings.get('ssid')))
                if not len(choice_raw):
                    choice = Main.SHOW_MENU
                else:
                    choice = choice_raw[0].lower()
                if choice == Main.CONFIGURE_WLAN:
                    print('Scanning for available networks...')
                    if not self.wlan:
                        self.wlan = network.WLAN(mode=network.WLAN.STA)
                    wlans = self.wlan.scan()
                    print("Available WiFi networks:")
                    for i, wlan in enumerate(wlans):
                        sec_string = 'Open/unknown'
                        if wlan.sec == network.WLAN.WEP:
                            sec_string = 'WEP'
                        elif wlan.sec == network.WLAN.WPA:
                            sec_string = 'WPA'
                        elif wlan.sec == network.WLAN.WPA2:
                            sec_string = 'WPA2'

                        print('%i: %s\tsecurity: %s' % (i, wlan.ssid, sec_string))

                    # Chose ssid to connect to
                    ssid_chosen = False
                    while not ssid_chosen:
                        ssid = input('Enter SSID number: ')
                        try:
                            ssid_num = int(ssid)
                            if ssid_num > len(wlans) - 1 or ssid_num < 0:
                                raise ValueError()
                            wlan = wlans[ssid_num]
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

    def blink(self, color):
        pycom.rgbled(color)
        time.sleep_ms(500)
        pycom.rgbled(0x000000)
        time.sleep_ms(500)

    def do_connect(self):
        ssid = self.settings.get('ssid')
        password = self.settings.get('password')
        sec = self.settings.get('wifi_sec')

        if not self.wlan:
            self.wlan = network.WLAN(mode=network.WLAN.STA)
        if not self.wlan.isconnected():
            if sec:
                self.wlan.connect(ssid, auth=(sec, password))
            else:
                self.wlan.connect(ssid, auth=None)
            print('Connecting to network %s...' % ssid)
            # Wait max 20 seconds for connection
            for i in range(20):
                if not self.wlan.isconnected():
                    self.blink(Main.WLAN_CONNECTING)
            if not self.wlan.isconnected():
                print('Could not connect to network %s\nPlease configure WiFi settings' % ssid)
                for i in range(3):
                    self.blink(Main.ERROR)
                pycom.rgbled(Main.ERROR)
                return False
                # raise ConnectionError()
        self.blink(Main.WLAN_CONNECTED)
        print('Connected to %s' % ssid)
        print('network config:', self.wlan.ifconfig())
        return True

    def start(self):
        if self.alarm:
            self.alarm.callback(self.get_weather)
        else:
            self.alarm = Timer.Alarm(self.do, QUERY_INTERVAL, periodic=True)
        print('Weather Beacon app started')

    def stop(self):
        self.alarm.callback(None)

    def do(self, alarm):
        color = self.get_weather()
        pycom.rgbled(color)

    def get_weather(self):
        location = self.settings.get('location')
        print('Querying weather data for %s' % location)
        pycom.rgbled(0x000000)
        time.sleep_ms(500)
        pycom.rgbled(0x990050)
        url = "http://api.openweathermap.org/data/2.5/forecast?q=%s,ch&mode=json&cnt=%i&appid=%s" % (
            location,
            NUMBER_OF_3HRS_WINDOWS, API_KEY)

        codes = []
        try:
            response = urequests.get(url)
            json = response.json()
            forecasts = json['list']
            for item in forecasts:
                codes.append(int(item['weather'][0]['id']))
        except Exception as e:
            print('Something went wrong while processing weather data')
            self.blink(0xFF0000)
            print(e)
            return Weather.NODATA

        print(codes)

        rain = False
        sun = False
        snow = False
        clouds = False

        for code in codes:
            if 300 <= code <= 600:
                rain = True
            if 600 <= code <= 600:
                snow = True
            if code == 800 or code == 801:
                sun = True
            if code <= 800 <= 900:
                clouds = True

        pycom.rgbled(0x000000)
        time.sleep_ms(500)

        if snow:
            print("Forecast is snow!")
            return Weather.SNOW
        if rain:
            print("Forecast is rain!")
            return Weather.RAIN
        if sun:
            print("Forecast is sun!")
            return Weather.SUNSHINE
        else:
            return Weather.NODATA


class Weather(object):
    SUNSHINE = 0xFFFF00
    RAIN = 0x0000FF
    SNOW = 0xFFFFFF
    NODATA = 0xFF0000


class ConnectionError(Exception):
    pass


if __name__ == '__main__':
    main = Main()

    # detect pressed button and interrupt normal startup
    button = Pin("G17", Pin.IN, pull=Pin.PULL_UP)

    # debounce button input, pressed == LOW
    val = 10
    for i in range(10):
        val -= button.value()
        time.sleep_ms(20)

    if val > 6:
        main.configure()

    if not main.exit:
        pycom.heartbeat(False)
        while not main.do_connect():
            main.configure()
        main.start()

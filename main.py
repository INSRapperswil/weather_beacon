import urequests
import time
from machine import Pin

API_KEY = "123"
NUMBER_OF_3HRS_WINDOWS = 2


def do_connect():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('wireless', 'massiveloosing')
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())


if __name__ == "__main__":
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
        time.sleep(10)

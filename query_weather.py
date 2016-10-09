import requests

from settings import API_KEY

NUMBER_OF_3HRS_WINDOWS = 2

if __name__ == "__main__":
    response = requests.get("http://api.openweathermap.org/data/2.5/forecast?q=Hinwil,ch&mode=json&appid=%s" % API_KEY)
    json = response.json()
    dict = {num: False for num in range(NUMBER_OF_3HRS_WINDOWS)}
    forecasts = json['list']
    rain = False
    for i, forecast in enumerate(forecasts[0:NUMBER_OF_3HRS_WINDOWS]):
        print(forecast["rain"])
        if forecast["rain"]:
            rain = True
            dict[i] = True

    print("It is going to rain!") if rain else print("It wont rain")
    print(dict)

#####     MetOcean (MetService)

from datetime import datetime, timezone, timedelta
from requests import post
import pytz
import pendulum


def tz_diff(home, away, on=None):
    """
    
    """
    
    if on is None:
        on = pendulum.today()
    diff = (on.set(tz=home) - on.set(tz=away)).total_hours()

    if abs(diff) > 12.0:
        if diff < 0.0:
            diff += 24.0
        else:
            diff -= 24.0

    return diff

def get_weather(user_api, lat, lon, time_from):
    """Gets and returns JSON with given info from Metocean API 
    
    """
    
    return post('https://forecast-v2.metoceanapi.com/point/time',
      headers={'x-api-key': user_api},
      json={
        "points": [{
          "lon": lon,
          "lat": lat
        }],
        "variables": [
          "air.temperature.at-2m",
          "precipitation.rate",
          "cloud.cover",
        ],
        "time": {
          "from": time_from,
          "interval": "1h",
          "repeat": 18
        }
      }
    )


user_api = input("API Key: ")

nztimezone = "Pacific/Auckland"
uktimezone = "Europe/London"

lat = -43.56466732569939
lon = 172.66372008707805

time_now = (datetime.now(pytz.utc)).strftime("%Y-%m-%dT14:00:00Z")

utctime = datetime.now(pytz.utc)
nztime = datetime.now(pytz.timezone(nztimezone))

difference = tz_diff(uktimezone, nztimezone)


resp = get_weather(user_api, lat, lon, time_now)


# print just values of wave height:
temps = resp.json()['variables']['air.temperature.at-2m']['data']
rain = resp.json()['variables']['precipitation.rate']['data']       # mm per hour
cloud = resp.json()['variables']['cloud.cover']['data']
times = resp.json()['dimensions']['time']['data']

time = 2

for i in range(0, len(temps)):
    print(f"Time: {time+i}, Temp: {temps[i]-273.15:.2f}*C, Rain: {rain[i]:.1f}mm/h, Cloud cover: {cloud[i]:.0f}%")


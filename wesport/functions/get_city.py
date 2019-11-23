import requests
import json


def get_city():

    access_key = '68ecc8eed3700d80beef22d1d4a527e8'
    send_url = 'http://api.ipstack.com/check?access_key='
    r = requests.get(send_url + access_key)
    j = json.loads(r.text)
    lat = j['latitude']
    lon = j['longitude']
    return lat, lon, j


a, b, j = get_city()

print a, b, j
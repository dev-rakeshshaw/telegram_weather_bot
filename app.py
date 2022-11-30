import requests
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from datetime import *
import pytz
import json 
import requests
import re

TOKEN = "telegram_bot_token"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
key="vcw_key"



#Find the wind direction
def getWindDir(deg):
    if deg == 90:
        dir = "E"
    elif deg == 180:
        dir = "S"
    elif deg == 270:
        dir = "W"
    elif deg == 360:
        dir = "N"
    elif ((deg > 90) & (deg < 180)):
        dir = "SE"
    elif ((deg > 180) & (deg < 270)):
        dir = "SW"
    elif ((deg > 270) & (deg < 360)):
        dir = "NW"
    elif ((deg < 360) & (deg < 90)):
        dir = "N"
    return dir
    



#creating getWeather function:
def getWeather(city):

    #Finding the Latitude and Longitude for the City
    geolocator = Nominatim(user_agent="geoapiExercises")
    location=geolocator.geocode(city ,timeout=None)

    if location == None:
        msg = "error"
    else:
        obj = TimezoneFinder()
        timezone_=obj.timezone_at(lng=location.longitude,lat=location.latitude)
        long_lat = f"({round(location.latitude,4)}° N,{round(location.longitude,4)}° E)"

        #Finding the Current date and time for the City using Lat. snd Long.
        home = pytz.timezone(timezone_)
        local_time=datetime.now(home)
        current_time=local_time.strftime("%I:%M %p %Z")
        current_date=local_time.strftime("%d/%m/%Y")

        
        #open_weather_api
    
        api = (f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location.latitude},{location.longitude}/next7days?unitGroup=metric&elements=datetime%2Ctempmax%2Ctempmin%2Ctemp%2Cfeelslike%2Chumidity%2Cwindspeed%2Cwinddir%2Cpressure%2Ccloudcover%2Csunrise%2Csunset%2Cmoonphase%2Cconditions%2Cdescription%2Cicon&include=days%2Ccurrent&key={key}&contentType=json")
    
        #Fetching the whole from the open_weather_api
        json_data=requests.get(api).json()

        #Fetching the current data from the open_weather_api and setting them on their respective labels
        temp = json_data["currentConditions"]["temp"]
        humidity = json_data["currentConditions"]["humidity"]
        pressure = json_data["currentConditions"]["pressure"]
        windspeed = json_data["currentConditions"]["windspeed"]
        winddir = getWindDir(json_data["currentConditions"]["winddir"])
        conditions = json_data["currentConditions"]["conditions"]
        sunrise = json_data["currentConditions"]['sunrise']
        sunset = json_data["currentConditions"]['sunrise']
        first_day_image = json_data["currentConditions"]['icon']

        msg = f" The weather report for {city.title()}: \n\n Timezone: {timezone_} \n Latitude/Longitude: {long_lat} \n Date: {current_date} \n Time: {current_time} \n Temperature: {temp} °C \n Humidity: {humidity}% \n Pressure: {pressure} mb \n Wind: {winddir} {windspeed} km/h \n Conditions: {conditions} \n Sunrise: {sunrise} AM \n Sunset: {sunset} PM"

    return(msg)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> TELEGRAM BOT <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js

def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)

def send_message(text, chat_id):
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)

def echo_all(updates):
    for update in updates["result"]:
        try:
            text = update["message"]["text"]
            chat_id = update["message"]["chat"]["id"]
            if text=="/start":
                msg = "Hi! I am a 🌤⛈ Weather Forecast Bot 🌪🌩. \n Created by ❤Rakesh Shaw❤. \n\n Please enter a location:"
            elif re.findall("^/", text):
                msg="Only /start command is supported till now. Other commands will be added soon.❤"
            else:
                report=getWeather(text) #text==city
                if report == "error":
                    msg = f"Oops {text} not found on map. \nPlease enter a correct location. \nThank You."
                else:
                    msg = report
            send_message(msg, chat_id)
        except Exception as e:
            print(e)


def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            echo_all(updates)
        # time.sleep(0.2)

if __name__ == '__main__':
    main()




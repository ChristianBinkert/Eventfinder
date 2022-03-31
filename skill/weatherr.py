# Copyright 2021, Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Representations and conversions of the data returned by the weather API."""
from datetime import timedelta
import time
from pathlib import Path
from typing import List

from .config import MILES_PER_HOUR
from .util import convert_to_local_datetime

# Forecast timeframes
CURRENT = "current"
DAILY = "daily"
HOURLY = "hourly"

# Days of week
SATURDAY = 5
SUNDAY = 6

# Condition Icons (see https://openweathermap.org/weather-conditions)
#   Map each of the possible weather condition icon codes from OpenWeatherMap to an
#   image/animation file used by the GUI.  The icon codes contain a number and a letter.
#   A "n" after the number indicates night and a "d" indicates day.
#
#   The icon/image map is used by the Mark II, which does not use animations for
#   performance reasons.  The icon/animation map is used by the scalable QML.  The
#   icon/code map is for the Mark I, which accepts a code to determine what
#   is displayed.

def get_timezone_for_request(report):
    for event in report[:1]:
        timezone = event.get('dates').get('timezone')
    return timezone

def get_eventname_for_request(report):
    for event in report[:1]:
        eventname = event.get('name')
    return eventname

def get_localdate_for_request(report):
    for event in report[:1]:
        localdate = event.get('dates').get('start').get('localDate')
    return localdate

class WeatherCondition:
    """Data representation of a weather conditions JSON object from the API"""

    def __init__(self, conditions: dict):
        self.id = conditions["id"]
        self.category = conditions["main"]
        self.description = conditions["description"]
        self.icon = conditions["icon"]


class CurrentWeather:
    """Abstract data representation of commonalities in forecast types."""
    #--------------------------------------------------------------------------------------------- here
    def __init__(self, eventname: str, localdate:str, timezone: str):
        self.date_time = convert_to_local_datetime(int(time.time()), timezone)
        self.event_name = eventname
        self.localDate = localdate
        """self.feels_like = weather["feelsLike"]
        self.pressure = weather["pressure"]
        self.humidity = weather["humidity"]
        self.dew_point = weather["dewPoint"]
        self.clouds = weather["clouds"]
        self.wind_speed = int(weather["windSpeed"])
        self.wind_direction = self._determine_wind_direction(weather["windDeg"])
        self.condition = WeatherCondition(weather["weather"][0])"""


class DailyFeelsLike:
    """Data representation of a "feels like" JSON object from the API"""

    def __init__(self, temperatures: dict):
        self.day = round(temperatures["day"])
        self.night = round(temperatures["night"])
        self.evening = round(temperatures["eve"])
        self.morning = round(temperatures["morn"])


class DailyTemperature(DailyFeelsLike):
    """Data representation of a temperatures JSON object from the API"""

    def __init__(self, temperatures: dict):
        super().__init__(temperatures)
        self.low = round(temperatures["min"])
        self.high = round(temperatures["max"])


class DailyWeather:
    """Data representation of a daily forecast JSON object from the API"""
    #--------------------------------------------------------------------------------------------- here
    def __init__(self, report: dict, timezone: str):
        self.date_time = convert_to_local_datetime(int(time.time()), timezone)
        self.event_name = report['name']
        self.localDate = report['dates']['start']['localDate']

        """self.sunrise = convert_to_local_datetime(weather["sunrise"], timezone)
        self.sunset = convert_to_local_datetime(weather["sunset"], timezone)
        self.temperature = will thDailyTemperature(weather["temp"])
        self.feels_like = DailyFeelsLike(weather["feelsLike"])
        self.chance_of_precipitation = int(weather["pop"] * 100)"""


class WeatherAlert:
    """Data representation of a weather conditions JSON object from the API"""

    def __init__(self, alert: dict, timezone: str):
        self.sender = alert.get("sender_name")
        self.event = alert["event"]
        self.start = convert_to_local_datetime(alert["start"], timezone)
        self.end = convert_to_local_datetime(alert["end"], timezone)
        self.description = alert["description"]


class WeatherReportt:
    """Full representation of the data returned by the Open Weather Maps One Call API"""

    def __init__(self, report):
        #--------------------------------------------------------------------------------------------- here
        timezone = get_timezone_for_request(report)
        eventname = get_eventname_for_request(report)
        localdate = get_localdate_for_request(report)
        self.current = CurrentWeather(eventname, localdate, timezone)
        #--------------------------------------------------------------------------------------------- here
        #self.daily = [DailyWeather(event, timezone) for event in report["_embedded"]['events']]
        #today = self.daily[0]


    def get_weather_for_intent(self, intent_data):
        """Use the intent to determine which forecast satisfies the request.

        Args:
            intent_data: Parsed intent data
        """

        if intent_data.timeframe == "daily":
            weather = self.get_forecast_for_date(intent_data)
        else:
            weather = self.current

        return weather

    def get_forecast_for_date(self, intent_data):
        """Use the intent to determine which daily forecast(s) satisfies the request.

        Args:
            intent_data: Parsed intent data
        """
        if intent_data.intent_datetime.date() == intent_data.location_datetime.date():
            forecast = self.daily[0]
        else:
            delta = intent_data.intent_datetime - intent_data.location_datetime
            day_delta = int(delta / timedelta(days=1))
            day_index = day_delta + 1
            forecast = self.daily[day_index]

        return forecast

    def get_forecast_for_multiple_days(self, days: int) -> List[DailyWeather]:
        """Use the intent to determine which daily forecast(s) satisfies the request.

        Args:
            days: number of forecast days to return

        Returns:
            list of daily forecasts for the specified number of days

        Raises:
            IndexError when number of days is more than what is returned by the API
        """
        if days > 7:
            raise IndexError("Only seven days of forecasted weather available.")

        forecast = self.daily[1 : days + 1]

        return forecast


    def get_weekend_forecast(self):
        """Use the intent to determine which daily forecast(s) satisfies the request.

        Returns:
            The Saturday and Sunday forecast from the list of daily forecasts
        """
        forecast = list()
        for forecast_day in self.daily:
            report_date = forecast_day.date_time.date()
            if report_date.weekday() in (SATURDAY, SUNDAY):
                forecast.append(forecast_day)

        return forecast

    def get_next_precipitation(self, intent_data):
        """Determine when the next chance of precipitation is in the forecast.

        Args:
            intent_data: Parsed intent data

        Returns:
            The weather report containing the next chance of rain and the timeframe of
            the selected report.
        """
        report = None
        current_precipitation = True
        timeframe = HOURLY
        for hourly in self.hourly:
            if hourly.date_time.date() > intent_data.location_datetime.date():
                break
            if hourly.chance_of_precipitation > THIRTY_PERCENT:
                if not current_precipitation:
                    report = hourly
                    break
            else:
                current_precipitation = False

        if report is None:
            timeframe = DAILY
            for daily in self.daily:
                if daily.date_time.date() == intent_data.location_datetime.date():
                    continue
                if daily.chance_of_precipitation > THIRTY_PERCENT:
                    report = daily
                    break

        return report, timeframe

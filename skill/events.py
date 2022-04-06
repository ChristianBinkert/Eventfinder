
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



class CurrentEvents:
    """Abstract data representation of commonalities in forecast types."""
    #--------------------------------------------------------------------------------------------- here
    def __init__(self, eventname: str, localdate:str, timezone: str):
        self.date_time = convert_to_local_datetime(int(time.time()), timezone)
        self.event_name = eventname
        self.localDate = localdate



class DailyWeather:
    """Data representation of a daily forecast JSON object from the API"""
    #--------------------------------------------------------------------------------------------- here
    def __init__(self, report: dict, timezone: str):
        self.date_time = convert_to_local_datetime(int(time.time()), timezone)
        self.event_name = report['name']
        self.localDate = report['dates']['start']['localDate']



class EventReport:
    """Full representation of the data returned by the Ticketmaster API"""

    def __init__(self, report):
        
        self.report = report
        timezone = report[0]["dates"].get("timezone")
        eventname = report[0].get("name")
        localdate = report[0]['dates'].get('start').get('localDate')
        self.current = CurrentEvents(eventname, localdate, timezone)
        #--------------------------------------------------------------------------------------------- here
        self.daily = [DailyWeather(event, timezone) for event in report[:10]]
        today = self.daily[0]


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

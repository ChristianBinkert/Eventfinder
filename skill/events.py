
"""Representations and conversions of the data returned by Ticketmasters API."""
from datetime import datetime
import time
from pathlib import Path
from typing import List

from .util import convert_to_local_datetime

# Forecast timeframes
CURRENT = "current"
DAILY = "daily"
HOURLY = "hourly"



class CurrentEvents:
    """Abstract data representation of commonalities in forecast types."""
    #--------------------------------------------------------------------------------------------- here
    def __init__(self, eventname: str, localdate:str, timezone: str):
        self.date_time = convert_to_local_datetime(int(time.time()), timezone)
        self.event_name = eventname
        self.localDate = localdate


class EventReport:
    """Full representation of the data returned by the Ticketmaster API"""

    def __init__(self, report):
        
        self.report = report
        timezone = report[0]["dates"].get("timezone")
        eventname = report[0].get("name")
        localdate = report[0]['dates'].get('start').get('localDate')
        localdate_datetime = datetime.strptime(localdate, '%Y-%m-%d').date()
        localdate = localdate_datetime.strftime("%B %d, %Y")  
        self.current = CurrentEvents(eventname, localdate, timezone)


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

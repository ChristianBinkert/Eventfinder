from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from .skill.config import EventConfig
from .skill.intent import EventIntent
from .skill.api import TicketmasterApi

from adapt.intent import IntentBuilder
from mycroft import MycroftSkill, intent_file_handler, intent_handler

#Forecast timeframes
CURRENT = "current"
DAILY = "daily"
HOURLY = "hourly"


class Eventfinder(MycroftSkill):
    def __init__(self):
        self.ticketmaster_api = TicketmasterApi()
        MycroftSkill.__init__(self)
        self.event_config = None

    def initialize(self):
        self.event_config = EventConfig(self.config_core, self.settings)
        self.log.info("the skill has loaded")
        self.log.info(self.event_config.city)

    @intent_file_handler('eventfinder.intent')
    def handle_eventfinder(self, message):
        self.speak_dialog('eventfinder')

    @intent_handler(IntentBuilder('FutureEventIntent').require('Event').require('future'))
    def handle_future_event_intent(self, message):
        self.speak_dialog("weekly")
        intent_data = self._get_intent_data(message)
        self._get_event(intent_data)


    def _get_intent_data(self, message) -> EventIntent:
        """Parse the intent data from the message into data used in the skill.
        Args:
            message: Message Bus event information from the intent parser
        Returns:
            parsed information about the intent
        """
        intent_data = None
        try:
            intent_data = EventIntent(message, self.lang)
        except ValueError:
            self.speak_dialog("cant.get.forecast")
        else:
            if self.voc_match(intent_data.utterance, "today"):
                intent_data.timeframe = HOURLY
            """elif self.voc_match(intent_data.utterance, "relative-day"):
                if not self.voc_match(intent_data.utterance, "today"):
                    intent_data.timeframe = DAILY"""
        self.log.info(intent_data)
        self.log.info("return of _get_intent_data")
        self.log.info(intent_data.timeframe)
        self.log.info(intent_data.location)
        return intent_data

    # removed -> WeatherReport which was not defined and broke the code
    def _get_event(self, intent_data: EventIntent):
        """Call the Open Weather Map One Call API to get weather information
        Args:
            intent_data: Parsed intent data
        Returns:
            An object representing the data returned by the API
        """
        weather = None
        if intent_data is not None:
            try:
                latitude, longitude = self._determine_event_location(intent_data)
                weather = self.ticketmaster_api.get_weather_for_coordinates(
                    self.config_core.get("system_unit"), latitude, longitude, self.lang
                )
            except HTTPError as api_error:
                self.log.exception("Weather API failure")
                self._handle_api_error(api_error)
            except LocationNotFoundError:
                self.log.exception("City not found.")
                self.speak_dialog(
                    "location-not-found", data=dict(location=intent_data.location)
                )
            except Exception:
                self.log.exception("Unexpected error retrieving weather")
                self.speak_dialog("cant-get-forecast")
                
        self.log.info(intent_data)
        self.log.info("Returned weather from API instances follows right below")
        self.log.info(weather)
        return weather


    def _determine_event_location(
        self, intent_data: EventIntent
    ) -> Tuple[float, float]:
        """Determine latitude and longitude using the location data in the intent.
        Args:
            intent_data: Parsed intent data
        Returns
            latitude and longitude of the location"""
        
        if intent_data.location is None:
            latitude = self.event_config.latitude
            longitude = self.event_config.longitude
        else:
            latitude = intent_data.geolocation["latitude"]
            longitude = intent_data.geolocation["longitude"]

        return latitude, longitude

    @intent_file_handler('sheet.intent')
    def handle_sheet(self, message):
        self.speak_dialog('sheet')

def create_skill():
    return Eventfinder() 


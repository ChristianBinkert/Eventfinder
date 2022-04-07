from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from requests import HTTPError

from .skill.config import EventConfig
from .skill.intent import EventIntent
from .skill.api import TicketmasterApi
from .skill.dialog import CurrentDialog
from .skill.events import EventReport
from .skill.util import LocationNotFoundError
from mycroft.util import extract_datetime


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

    @intent_handler(IntentBuilder('FutureEventIntent').require('next').require('Event').optionally('location'))
    def handle_future_event_intent(self, message):
        self._report_current_event(message)
        self.log.info("FutureEventIntentHandled")


    @intent_handler(IntentBuilder('RelativeDateEventIntent').optionally('query').require('Event').require('relative-date').optionally('location'))
    def handle_relative_date_intent(self, message):
        day_query = extract_datetime(message.data.get("utterance"))[0].strftime("%Y-%m-%dT%H:%M:%SZ")
        speakable_day_query = extract_datetime(message.data.get("utterance"))[0].strftime("%B %d, %Y")
        self.log.info(day_query)

        if day_query:
            self._search(day_query,speakable_day_query, message)
        else:
            self._search(date.today().strftime("%B %d, %Y"))

    def _report_current_event(self, message):
        """Handles all requests for current events.
        """
        intent_data = self._get_intent_data(message)
        event = self._get_event(intent_data)
        self.log.info("Weather variable is not none")
        if event is not None:
            dialog = CurrentDialog(intent_data, self.event_config, event.current)
            dialog.build_event_dialog()
            self._speak_event(dialog)

    def _search(self, day_query, speakable_day_query, message):
        """Handles all requests for a single day forecast.
        """

        intent_data = EventIntent(message, self.lang)
        eventname, speakable_localdate = self._get_event_date(intent_data, day_query)
     
        if speakable_day_query == speakable_localdate:
            self.log.info(eventname, speakable_localdate)
            self.speak("On " + speakable_day_query + ", " + eventname + " will take place.")
        else:
            self.speak("Unfortunately, there is no event on that day, but on " + speakable_localdate + ", " + eventname + " will be in town.")
            self.log.info(eventname, speakable_localdate)
            self.log.info("end of search")

    def _get_intent_data(self, message) -> EventIntent:
        """Parse the intent data from the message into data used in the skill.
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
            elif self.voc_match(intent_data.utterance, "relative-day"):
                if not self.voc_match(intent_data.utterance, "today"):
                    intent_data.timeframe = DAILY
        self.log.info(intent_data)
        self.log.info("return of _get_intent_data in init.py")
        self.log.info(intent_data.timeframe)
        self.log.info(intent_data.location)
        return intent_data

    # removed -> WeatherReport which was not defined and broke the code
    def _get_event(self, intent_data: EventIntent):
        """Call the Ticketmaster API to get event information
        Args:
            intent_data: Parsed intent data
        Returns:
            An object representing the data returned by the API
        """
        event = None
        if intent_data is not None:
            try:
                latitude, longitude = self._determine_event_location(intent_data)
                event = self.ticketmaster_api.get_event_for_coordinates(
                    self.config_core.get("system_unit"), latitude, longitude, self.lang
                )
                self.log.info("Event API called successfull")
            except HTTPError as api_error:
                self.log.exception("Event API failure")
                self._handle_api_error(api_error)
            except LocationNotFoundError:
                self.log.exception("City not found.")
                self.speak_dialog(
                    "location-not-found", data=dict(location=intent_data.location)
                )
            except Exception:
                self.log.exception("Unexpected error retrieving Events")
                self.speak_dialog("cant-get-forecast")

        return event

    def _get_event_date(self, intent_data: EventIntent, day_query):
        """Call the Ticketmaster API to get event information
        Args:
            intent_data: Parsed intent data
        Returns:
            An object representing the data returned by the API
        """
        event = None
        if intent_data is not None:
            try:
                latitude, longitude = self._determine_event_location(intent_data)
                eventname, localdate = self.ticketmaster_api.get_event_for_coordinates_date(
                    self.config_core.get("system_unit"), latitude, longitude, self.lang, day_query
                )
            except HTTPError as api_error:
                self.log.exception("Event API failure")
                self._handle_api_error(api_error)
            except LocationNotFoundError:
                self.log.exception("City not found.")
                self.speak_dialog(
                    "location-not-found", data=dict(location=intent_data.location)
                )
            except Exception:
                self.log.exception("Unexpected error retrieving Events")
                self.speak_dialog("cant-get-forecast")
                
        self.log.info(intent_data)
        self.log.info(eventname, localdate)

        return eventname, localdate


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

    def _speak_event(self, dialog):
        """Instruct device to speak the contents of the specified dialog.
        :param dialog: the dialog that will be spoken
        """
        self.log.info("Speaking dialog: " + dialog.name)
        self.speak_dialog(dialog.name, dialog.data, wait=True)

def create_skill():
    return Eventfinder() 


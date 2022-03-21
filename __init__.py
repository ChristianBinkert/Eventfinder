from datetime import datetime
from pathlib import Path

from .skill.config import EventConfig
from .skill.intent import EventIntent

from adapt.intent import IntentBuilder
from mycroft import MycroftSkill, intent_file_handler, intent_handler

#Forecast timeframes
CURRENT = "current"
DAILY = "daily"
HOURLY = "hourly"


class Eventfinder(MycroftSkill):
    def __init__(self):
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
        self._get_intent_data(message)

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
        return intent_data

    @intent_file_handler('sheet.intent')
    def handle_sheet(self, message):
        self.speak_dialog('sheet')

def create_skill():
    return Eventfinder() 


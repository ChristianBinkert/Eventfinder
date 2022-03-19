from datetime import datetime
from pathlib import Path

from .skill.config import EventConfig
from .skill.intent import EventIntent

from adapt.intent import IntentBuilder
from mycroft import MycroftSkill, intent_file_handler, intent_handler


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

    @intent_handler(IntentBuilder('ThankYouIntent').require('Event').require('Time'))
    def handle_thank_you_intent(self, message):
        self.speak_dialog("weekly")

    @intent_file_handler('sheet.intent')
    def handle_sheet(self, message):
        self.speak_dialog('sheet')

def create_skill():
    return Eventfinder() 


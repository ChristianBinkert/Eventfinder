
from typing import List, Tuple

from mycroft.util.format import join_list, nice_number, nice_time
from mycroft.util.time import now_local
from .config import EventConfig
from .intent import EventIntent
from .util import get_speakable_day_of_week, get_time_period
from .events import (
    CURRENT,
    CurrentEvents,
    DAILY,
    HOURLY,
)


class EventDialog:
    """Abstract base class for the event dialog builders."""

    def __init__(self, intent_data: EventIntent, config: EventConfig):
        self.intent_data = intent_data
        self.config = config
        self.name = None
        self.data = None

    def _add_location(self):
        """Add location information to the dialog."""
        if self.intent_data.location is None:
            self.name += "-local"
        else:
            self.name += "-location"
            if self.config.country == self.intent_data.geolocation["country"]:
                spoken_location = ", ".join(
                    [
                        self.intent_data.geolocation["city"],
                        self.intent_data.geolocation["region"],
                    ]
                )
            else:
                spoken_location = ", ".join(
                    [
                        self.intent_data.geolocation["city"],
                        self.intent_data.geolocation["country"],
                    ]
                )
            self.data.update(location=spoken_location)


class CurrentDialog(EventDialog):
    """Event dialog builder for current events."""

    def __init__(
        self, intent_data: EventIntent, config: EventConfig, events: CurrentEvents
    ):
        super().__init__(intent_data, config)
        self.events = events
        self.name = CURRENT

    def build_event_dialog(self):
        """Build the components necessary to speak current events."""
        self.name += "-event"
        self.data = dict(
            event_name=self.events.event_name,
            localDate=self.events.localDate,
        )
        self._add_location()

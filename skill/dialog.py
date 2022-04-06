
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
    DailyWeather,
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
            temperature_unit=self.config.temperature_unit,
        )
        self._add_location()


class DailyDialog(EventDialog):
    """Weather dialog builder for daily weather."""

    def __init__(
        self, intent_data: EventIntent, config: EventConfig, weather: DailyWeather
    ):
        super().__init__(intent_data, config)
        self.weather = weather
        self.name = DAILY

    def build_weather_dialog(self):
        """Build the components necessary to speak the forecast for a day."""
        self.name += "-weather"
        self.data = dict(
            condition=self.weather.condition.description,
            day=get_speakable_day_of_week(self.weather.date_time),
            high_temperature=self.weather.temperature.high,
            low_temperature=self.weather.temperature.low,
        )
        self._add_location()



def get_dialog_for_timeframe(timeframe: str, dialog_ags: Tuple):
    """Use the intent data to determine which dialog builder to use.

    :param timeframe: current, hourly, daily
    :param dialog_ags: Arguments to pass to the dialog builder
    :return: The correct dialog builder for the timeframe
    """
    if timeframe == DAILY:
        dialog = DailyDialog(*dialog_ags)
    elif timeframe == HOURLY:
        dialog = HourlyDialog(*dialog_ags)
    else:
        dialog = CurrentDialog(*dialog_ags)

    return dialog

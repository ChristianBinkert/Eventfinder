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
"""Abstraction of dialog building for the weather skill.

There are A LOT of dialog files in this skill.  All the permutations of timeframe,
weather condition and location add up fast.  To help with discoverability, a naming
convention was applied to the dialog files:
    <timeframe>-<weather info>-<qualifier>-<locale>.dialog

    Example:
         daily-temperature-high-local.dialog

    * Timeframe: the date or time applicable to the forecast.  This skill supports
        current, hourly and daily weather.
    * Weather info: a description of what type of weather the dialog refers to.
        Examples include "temperature", "weather" and "sunrise".
    * Qualifier: further qualifies what type of weather is being reported.  For
        example, temperature can be qualified by "high" or "low".
    * Locale: indicates if the dialog is for local weather or weather in a remote
        location.

The skill class will use the "name" and "data" attributes to pass to the TTS process.
"""
from typing import List, Tuple

from mycroft.util.format import join_list, nice_number, nice_time
from mycroft.util.time import now_local
from .config import EventConfig
from .intent import EventIntent
from .util import get_speakable_day_of_week, get_time_period
from .events import (
    CURRENT,
    CurrentWeather,
    DAILY,
    DailyWeather,
    HOURLY,
)

# TODO: MISSING DIALOGS
#   - current.clear.alternative.local
#   - current.clouds.alternative.local
#   - daily.snow.alternative.local
#   - all hourly.<condition>.alternative.local/location
#   - all hourly.<condition>.not.expected.local/location
class WeatherDialog:
    """Abstract base class for the weather dialog builders."""

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


class CurrentDialog(WeatherDialog):
    """Weather dialog builder for current weather."""

    def __init__(
        self, intent_data: EventIntent, config: EventConfig, weather: CurrentWeather
    ):
        super().__init__(intent_data, config)
        self.weather = weather
        self.name = CURRENT

    def build_event_dialog(self):
        """Build the components necessary to speak current weather."""
        self.name += "-event"
        self.data = dict(
            event_name=self.weather.event_name,
            localDate=self.weather.localDate,
            temperature_unit=self.config.temperature_unit,
        )
        self._add_location()


class DailyDialog(WeatherDialog):
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

    def build_temperature_dialog(self, temperature_type: str):
        """Build the components necessary to speak the daily temperature.

        :param temperature_type: indicates if temperature is day, high or low
        """
        self.name += "-temperature"
        if temperature_type == "high":
            self.name += "-high"
            self.data = dict(temperature=self.weather.temperature.high)
        elif temperature_type == "low":
            self.name += "-low"
            self.data = dict(temperature=self.weather.temperature.low)
        else:
            self.data = dict(temperature=self.weather.temperature.day)
        self.data.update(
            day=get_speakable_day_of_week(self.weather.date_time),
            temperature_unit=self.intent_data.unit or self.config.temperature_unit,
        )
        self._add_location()



class WeeklyDialog(WeatherDialog):
    """Weather dialog builder for weekly weather."""

    def __init__(
        self,
        intent_data: EventIntent,
        config: EventConfig,
        forecast: List[DailyWeather],
    ):
        super().__init__(intent_data, config)
        self.forecast = forecast
        self.name = "weekly"

    def build_temperature_dialog(self):
        """Build the components necessary to temperature ranges for a week."""
        low_temperatures = [daily.temperature.low for daily in self.forecast]
        high_temperatures = [daily.temperature.high for daily in self.forecast]
        self.name += "-temperature"
        self.data = dict(
            low_min=min(low_temperatures),
            low_max=max(low_temperatures),
            high_min=min(high_temperatures),
            high_max=max(high_temperatures),
        )


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

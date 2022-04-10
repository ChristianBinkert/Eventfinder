"""Parse the intent into data used by the event skill."""

from datetime import timedelta

from mycroft.util.time import now_local
from .util import (
    get_utterance_datetime,
    get_geolocation,
    get_tz_info,
    LocationNotFoundError,
)

CURRENT = "current"

class EventIntent:
    _geolocation = None
    _intent_datetime = None
    _location_datetime = None

    def __init__(self, message, language):
        """Constructor

        :param message: Intent data from the message bus
        :param language: The configured language of the device
        """
        self.utterance = message.data["utterance"]
        self.location = message.data.get("location")
        self.language = language
        self.unit = message.data.get("unit")
        self.timeframe = CURRENT

    @property
    def geolocation(self):
        """Lookup the intent location using the Selene API.

        The Selene geolocation API assumes the location of a city is being
        requested.  If the user asks "What is the weather in Russia"
        an error will be raised.
        """
        if self._geolocation is None:
            if self.location is None:
                self._geolocation = dict()
            else:
                self._geolocation = get_geolocation(self.location)
                if self._geolocation["city"].lower() not in self.location.lower():
                    raise LocationNotFoundError(self.location + " is not a city")

        return self._geolocation

    @property
    def intent_datetime(self):
        """Use the configured timezone and the utterance to know the intended time.

        If a relative date or relative time is supplied in the utterance, use a
        datetime object representing the request.  Otherwise, use the timezone
        configured by the device.
        """
        if self._intent_datetime is None:
            utterance_datetime = get_utterance_datetime(
                self.utterance,
                timezone=self.geolocation.get("timezone"),
                language=self.language,
            )
            if utterance_datetime is not None:
                delta = utterance_datetime - self.location_datetime
                if int(delta / timedelta(days=1)) > 365:
                    raise ValueError("Event forecasts only supported up to 365 days")
                if utterance_datetime.date() < self.location_datetime.date():
                    raise ValueError("Historical events are not supported")
                self._intent_datetime = utterance_datetime
            else:
                self._intent_datetime = self.location_datetime

        return self._intent_datetime

    @property
    def location_datetime(self):
        """Determine the current date and time for the request.

        If a location is specified in the request, use the timezone for that
        location, otherwise, use the timezone configured on the device.
        """
        if self._location_datetime is None:
            if self.location is None:
                self._location_datetime = now_local()
            else:
                tz_info = get_tz_info(self.geolocation["timezone"])
                self._location_datetime = now_local(tz_info)

        return self._location_datetime

"""Call the Discovery API from Ticketmaster

The Discovery API provides upcoming events sorted by date with a default rang of 100 km. 
The endpoint is passed a latitude and longitude from either the users configured location or requested location."""

from datetime import datetime
import requests
from .events import EventReport

api_key = "1917ATlicnE4Sc702QXsk6oFS7WlvnG3"

class TicketmasterApi:

    def __init__(self):
        self.language = "en"

    def get_event_for_coordinates(
        self, measurement_system: str, latitude: float, longitude: float, lang: str
    ) -> EventReport:

        """Use Ticketsmasters API to retrieve the upcoming events, sorting by distance.
        
        Arguments:
            latitude: the geologic latitude of the event location
            longitude: the geologic longitude of the event location
        """

        latlong = str(latitude) + "," + str(longitude)
        url = f'https://app.ticketmaster.com/discovery/v2/events.json?latlong={latlong}&apikey={api_key}'
        response = requests.get(url).json()
        #Will transform response into list
        response = sorted(response.get('_embedded').get('events'), key=lambda x: x.get('distance'))
        
        local_events = EventReport(response)

        return local_events

    def get_event_for_coordinates_date(
        self, measurement_system: str, latitude: float, longitude: float, lang: str, day_query
    ) -> EventReport:

        """Use Ticketsmasters API to retrieve events happening on a specific date.
        
        Arguments:
            latitude: the geologic latitude of the event location
            longitude: the geologic longitude of the event location 
            day_query: string with the requested date
        """

        radius = 20
        latlong = str(latitude) + "," + str(longitude)
        startdatetime = str(day_query)
        url = f'https://app.ticketmaster.com/discovery/v2/events.json?latlong={latlong}&apikey={api_key}&startDateTime={startdatetime}&radius={radius}'
        response = requests.get(url).json()
        #Will transform response into list
        eventname = response['_embedded'].get('events')[0].get('name')
        localdate = response['_embedded'].get('events')[0].get('dates').get('start').get('localDate')

        localdate_datetime = datetime.strptime(localdate, '%Y-%m-%d').date()
        speakable_localdate = localdate_datetime.strftime("%B %d, %Y")        

        return eventname, speakable_localdate
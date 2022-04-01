import requests
from .events import EventReport

api_key = "1917ATlicnE4Sc702QXsk6oFS7WlvnG3"

class TicketmasterApi:

    def __init__(self):
        self.language = "en"

    def get_event_for_coordinates(
        self, measurement_system: str, latitude: float, longitude: float, lang: str
    ) -> EventReport:

        latlong = str(latitude) + "," + str(longitude)
        url = f'https://app.ticketmaster.com/discovery/v2/events.json?latlong={latlong}&apikey={api_key}'
        response = requests.get(url).json()
        #Will transform response into list
        response = sorted(response.get('_embedded').get('events'), key=lambda x: x.get('distance'))
        
        local_events = EventReport(response)

        return local_events
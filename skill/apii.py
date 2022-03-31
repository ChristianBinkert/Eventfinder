import requests
from .weatherr import WeatherReportt

api_key = "1917ATlicnE4Sc702QXsk6oFS7WlvnG3"

class TicketmasterApi:

    def __init__(self):
        self.language = "en"

    """def get_weather_for_coordinates(
        self, measurement_system: str, latitude: float, longitude: float
    ) -> WeatherReport:
        """"""Issue an API call and map the return value into a weather report

        Args:
            measurement_system: Metric or Imperial measurement units
            latitude: the geologic latitude of the weather location
            longitude: the geologic longitude of the weather location
        """"""
        query_parameters = dict(
            exclude="minutely",
            lang=self.language,
            lat=latitude,
            lon=longitude,
            units=measurement_system
        )
        api_request = dict(path="/onecall", query=query_parameters)
        response = self.request(api_request)
        local_weather = WeatherReport(response)"""

    def get_weather_for_coordinates(
        self, measurement_system: str, latitude: float, longitude: float, lang: str
    ) -> WeatherReportt:

        latlong = str(latitude) + "," + str(longitude)
        url = f'https://app.ticketmaster.com/discovery/v2/events.json?latlong={latlong}&apikey={api_key}'
        response = requests.get(url).json()
        #Will transform response into list
        response = sorted(response.get('_embedded').get('events'), key=lambda x: x.get('distance'))
        
        local_weather = WeatherReportt(response)

        return local_weather
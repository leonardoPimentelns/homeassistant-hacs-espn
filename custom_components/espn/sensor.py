"""Platform for sensor integration."""
from __future__ import annotations

from datetime import timedelta,datetime
import logging
import voluptuous
import json
from requests.structures import CaseInsensitiveDict
import requests
import pytz
from homeassistant import const
from homeassistant.helpers import entity
from homeassistant import util
from homeassistant.helpers import config_validation
from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
_LOGGER = logging.getLogger(__name__)


NAME = 'name'
UPDATE_FREQUENCY = timedelta(seconds=1)
LEAGUE ='league'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(LEAGUE): cv.string,
        vol.Required(NAME): cv.string,
        
    }
)
def setup_platform(
    hass,
    config,
    add_entities,
    discovery_info
):
    """Set up the Espn sensors."""
   
    get_espn = espn()
    add_entities([EspnSensor(get_espn,config)],True)


class EspnSensor(entity.Entity):
    """Representation of a Espn sensor."""

    def __init__(self,get_espn,config):
        """Initialize a new Espn sensor."""
        self.config = config
        self._attr_name = self.config[NAME]
        self.event = None
        self.espn = get_espn
        self.logo = None
        self.matches= []
        self.times = []
        self.live = None
        


    @property
    def icon(self):
        """Return icon."""
        return "mdi:soccer"


    @util.Throttle(UPDATE_FREQUENCY)
    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        
        self.matches = self.espn.get_matches(self.config[LEAGUE])
        
            


    @property
    def extra_state_attributes(self):
        """Return device specific state attributes."""
        self._attributes = {
            "logo": self.logo ,
            "Live_events": self.live,
            "events": self.matches,

        }
        return  self._attributes


def get_matches(championship):
    data_atual = datetime.now()
    inicio = data_atual - timedelta(days=2)
    fim = data_atual + timedelta(days=2) 

    inicio =inicio.strftime("%Y%m%d")
    fim =  fim.strftime("%Y%m%d")

    # Fazer solicitação à URL da API ESPN
    response = requests.get("https://site.api.espn.com/apis/site/v2/sports/soccer/"+championship+"/scoreboard?dates="+inicio +"-"+fim )

    # Verificar se a solicitação foi bem-sucedida
    if response.status_code == 200:
        # Carregar JSON em um objeto Python
        data = json.loads(response.content)
        goal_data = []

        # Extrair informações de jogos
        for event in data["events"]:
            date = event["date"]
            utc_time = datetime.fromisoformat(date.replace('Z', '+00:00')).replace(tzinfo=timezone.utc)
            local_timezone = pytz.timezone('America/Sao_Paulo')  # substitua pelo seu fuso horário
            local_time = utc_time.astimezone(local_timezone)
            date = local_time.strftime('%A %d at %H:%M')

            team_home = event["competitions"][0]["competitors"][0]["team"]["name"]
            venue = event["competitions"][0]["venue"]["fullName"]

            team_home_score = event["competitions"][0]["competitors"][0]["score"]
            team_home_logo = event["competitions"][0]["competitors"][0]['team']["logo"]
            team_home_color = event["competitions"][0]["competitors"][0]['team']["color"]

            team_visiting = event["competitions"][0]["competitors"][1]["team"]["name"]
            team_visiting_logo = event["competitions"][0]["competitors"][1]['team']["logo"]
            team_visiting_color = event["competitions"][0]["competitors"][1]['team']["color"]
            team_visiting_score = event["competitions"][0]["competitors"][1]["score"]

            displayClock = event['competitions'][0]['status']['displayClock']
            completed = event['competitions'][0]['status']['type']['completed']
            description = event['competitions'][0]['status']['type']['description']
            goal_data ={
                "date": date,
                "displayClock":displayClock,
                "completed": completed,
                "description":description,
                "venue":venue,
                "team_home": team_home,
                "team_home_logo":team_home_logo,
                "team_home_color":team_home_color,
                "team_home_score": team_home_score,
                "team_visiting": team_visiting,
                "team_visiting_logo":team_visiting_logo,
                "team_visiting_color":team_visiting_color,
                "team_visiting_score": team_visiting_score
            }
            return goal_data

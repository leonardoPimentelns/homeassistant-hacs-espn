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

class espn():
    def __init__(self):
        self.result = None
        self.videos = None
        self.matches= []
        self.videos_event = None
        self._matches_live_event = []
        self.times = []
        self._highlights = []
        


    

    
    def get_matches(self,config):
        start = datetime.today() - timedelta(days=1)
        start = start.strftime('%Y%m%d') 
        end =  datetime.today()  + timedelta(days=1)
        end = end.strftime('%Y%m%d')
        request = requests.get("https://site.api.espn.com/apis/site/v2/sports/soccer/"+config+"/scoreboard?dates="+start+"-"+end+"")
        result = json.loads(request.content)
        year = result['leagues'][0]['season']['year']
        name = result['leagues'][0]['name']
        logo = result['leagues'][0]['logos'][0]['href']
       

        return result
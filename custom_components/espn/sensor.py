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

_LOGGER = logging.getLogger(__name__)


DEFAULT_NAME = 'Espn_premier_league'
UPDATE_FREQUENCY = timedelta(seconds=1)
league ='eng.1'

def setup_platform(
    hass,
    config,
    add_entities,
    discovery_info
):
    """Set up the Espn sensors."""
   
 
    add_entities([EspnSensor()],True)


class EspnSensor(entity.Entity):
    """Representation of a Espn sensor."""

    def __init__(self):
        """Initialize a new Espn sensor."""
        self._attr_name = "Espn_premier_league"
        self.event = None
        self.logo = None
        self.matches= []
        self.times = []
        self.live = None


    @property
    def icon(self):
        """Return icon."""
        return "mdi:bank"


    @util.Throttle(UPDATE_FREQUENCY)
    def update(self):
        start = datetime.today() - timedelta(days=2)
        start = start.strftime('%Y%m%d') 
        end =  datetime.today()  + timedelta(days=5)
        end = end.strftime('%Y%m%d')
        request = requests.get("https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard?dates="+start+"-"+end+"")
        result = json.loads(request.content)
        year = result['leagues'][0]['season']['year']
        name = result['leagues'][0]['name']
        logo = result['leagues'][0]['logos'][0]['href']
       
    
        for leagues in result['events'][0:10]:
            date_z =leagues['date'].replace('Z', '+00:00') 
            date = datetime.fromisoformat(date_z)
            new_date = date.astimezone(pytz.timezone('America/Sao_Paulo')).strftime('%a-%m-%d %H:%M')
            
            leagues['date'] = new_date
            leagues['name'] = leagues['name'].replace("at","vs.")
            leagues.pop('links')
            self.matches.append(leagues)
       
           

            for competitions  in leagues['competitions']:
                competitions.pop('situation')
                if 'odds' not in competitions:
                    print('odds not found')
                else:
                    competitions.pop('odds')

                for details in competitions['details']:
                    if 'athletesInvolved' not in details:
                        continue
                    else:
                        for athletesInvolved in details['athletesInvolved']:
                            athletesInvolved.pop('links')
                            
                for competitors in competitions['competitors']:
                    time1 = competitions['competitors'][0]['team']['displayName'] 
                    time2 = competitions['competitors'][1]['team']['displayName']
                    times = f"{time1} vs. {time2}"
                    self.times.append(times)
                    competitors['team'].pop('links')
                    if 'leaders' not in competitors:
                        continue
                    else:
                        competitors.pop('leaders')
                        
       
        


    @property
    def extra_state_attributes(self):
        """Return device specific state attributes."""
        self._attributes = {
            "logo": self.logo ,
            "Live_events": self.live,
            "events": self.matches,

        }
        return  self._attributes


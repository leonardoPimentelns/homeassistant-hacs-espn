"""Platform for sensor integration."""
from __future__ import annotations

from datetime import timedelta,datetime
import logging
import voluptuous
import json
import requests
import pytz
from homeassistant import const
from homeassistant.helpers import entity
from homeassistant import util
from homeassistant.helpers import config_validation

_LOGGER = logging.getLogger(__name__)


DEFAULT_NAME = 'Espn'
UPDATE_FREQUENCY = timedelta(seconds=1)

# PLATFORM_SCHEMA = config_validation.PLATFORM_SCHEMA.extend(
#     {
#         voluptuous.Required(CONF_CLIENT_ID): config_validation.string,
#         voluptuous.Required(CONF_CLIENT_SECRET): config_validation.string,
#         voluptuous.Required(CONF_CLIENT_CERT): config_validation.string,
#         voluptuous.Optional(
#             const.CONF_NAME,
#             default=DEFAULT_NAME
#     ):      config_validation.string,


#     }
# )


def setup_platform(
    hass,
    config,
    add_entities,
    discovery_info
):
    """Set up the pyNubank sensors."""

    add_entities([EspnSensor()],True)


class EspnSensor(entity.Entity):
    """Representation of a pyNubank sensor."""

    def __init__(self):
        """Initialize a new pyNubank sensor."""
        self._attr_name = "Espn"
        self.event = None
        self.logo = None


    @property
    def extra_state_attributes(self):
        """Return device specific state attributes."""
        return self._attributes

    @util.Throttle(UPDATE_FREQUENCY)
    def update(self):
        """Fetches new state data for the sensor."""
        raise NotImplementedError

    @property
    def icon(self):
        """Return icon."""
        return "mdi:bank"


    @property
    def _name_suffix(self):
        """Returns the name suffix of the sensor."""
        return 'FATURA'

    @util.Throttle(UPDATE_FREQUENCY)
    def update(self):
        date1 = (datetime.now()- timedelta(days=2)).strftime('%Y%m%d') 
        date2 = (datetime.now()+ timedelta(days=5)).strftime('%Y%m%d')
        request = requests.get("https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard?dates="+date1+"-"+date2+"")
        self.result = json.loads(request.content)
        self.leagues = self.result
        self.event= []
        self.logo = self.leagues['leagues'][0]['logos'][0]['href']
        for leagues in self.leagues['events'][0:10]:
            date_z =leagues['date'].replace('Z', '+00:00')
            date = datetime.fromisoformat(date_z)
            new_date = date.astimezone(pytz.timezone('America/Sao_Paulo')).strftime('%a-%m-%d %H:%M')

            leagues['date'] = new_date
            leagues.pop('links')
            self.event.append(leagues)

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
            "events": self.event,

        }
        return  self._attributes

import json
import requests
from urlparse import urljoin

class EventRegistry(object):
    """
    Wrapper around EventRegistry API
    """

    @staticmethod
    def get_base_url():
        return "http://eventregistry.org/json/"

    def __init__(self, key):
        self.key = key

    def get_concept_uri(self, thing):
        results = self._get("suggestConcepts", params=dict(prefix=thing))
        return results[0]['uri'] if len(results) > 0 else None

    def get_events(self, thing):
        params = {
            "resultType": "events",
            "action": "getEvents",
        }
        concept_uri = self.get_concept_uri(thing)
        if concept_uri:
            params['conceptUri'] = concept_uri
        else:
            params['keywords'] = thing
        results = self._get("event", params=params)
        return results['events']['results'] if results and 'events' in results else []

    def _get(self, path, params={}, headers={}):
        url = urljoin(self.get_base_url(), path)
        params=params.copy()
        params['apiKey'] = self.key
        params['lang'] = 'eng'

        resp = requests.get(url, params, headers=headers)
        if resp.status_code != 200:
            return None
        else:
            return resp.json()

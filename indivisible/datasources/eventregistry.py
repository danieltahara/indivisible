import httplib
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

    def get_events(self, keyword):
        params = {
            "keywords": keyword,
            "lang": "eng",
            "resultType": "events",
            "action": "getEvents",
        }
        results = self._get("event", params=params)
        return results['events']['results'] if results else []

    def _get(self, path, params={}, headers={}):
        url = urljoin(self.get_base_url(), path)
        params=params.copy()
        params['apiKey'] = self.key

        resp = requests.get(url, params, headers=headers)
        if resp.status_code != 200:
            return None
        else:
            return resp.json()

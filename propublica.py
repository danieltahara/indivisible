import requests
import httplib
import json
import os
from urlparse import urljoin

class ProPublica(object):
    version = 1

    @classmethod
    def load_api_key(cls):
        with open('.api', 'r') as f:
            cls.key = f.read().rstrip()

    @staticmethod
    def get_base_url(version):
        return "https://api.propublica.org/congress/v{}/".format(version)

    def __init__(self):
        pass

    def get_members(self, congress, chamber):
        # Fetch members for congress, chamber as per:
        # https://propublica.github.io/congress-api-docs/#lists-of-members
        resp = self._get(os.path.join(str(congress), chamber, 'members.json'))
        if resp.status_code != 200:
            print resp.reason
        else:
            res = resp.json()
            return res['results'][0]['members']

    def _get(self, path, headers={}):
        url = urljoin(self.get_base_url(self.version), path)
        headers = headers.copy()
        headers.update(self._get_base_headers())
        return requests.get(url, headers=headers)

    def _get_base_headers(self):
        return {
            'X-API-Key': self.key,
        }

import requests
import httplib
import json
from urlparse import urljoin

class ProPublica(object):
    version = "v1"

    @classmethod
    def load_api_key(cls):
        with open('.api', 'r') as f:
            cls.key = f.read().rstrip()

    @staticmethod
    def get_base_url(version):
        return "https://api.propublica.org/congress/{}/".format(version)

    def __init__(self):
        pass

    def get_member_by_id(self, id):
        """
        Get member by id.

        @param id: member-id
        @return: member
        """
        # TODO: parametrize url
        results = self._get("members/{}.json".format(id))
        return results[0] if results else None

    def get_members(self, congress, chamber):
        """
        Fetch members for congress, chamber from:
        https://propublica.github.io/congress-api-docs/#lists-of-members

        @param congress: number (current is 115)
        @param chamber: HOUSE or SENATE
        @return: list of members
        """
        results = self._get("{congress}/{chamber}/members.json".format(
            congress=congress, chamber=chamber))
        return results[0]['members'] if results else []

    def get_members_by_location(self, chamber, state, district=None):
        """
        Get members by chamber, state, and district.

        @param chamber: SENATE or HOUSE
        @param state: two-letter state abbreviation
        @param district: (optional) house district
        @return: members
        """

        params = {
            chamber: chamber,
            state: state,
            district: district,
        }
        # https://pypi.python.org/pypi/us
        # TODO: parametrize url
        if chamber == 'senate':
            resp = self._get("{chamber}/{state}/current.json".format(**params))
        else:
            resp = self._get("{chamber}/{state}/{district}/current.json".format(**params))

        return results or []

    def _get(self, path, headers={}):
        url = urljoin(self.get_base_url(self.version), path)
        headers = headers.copy()
        headers.update(self._get_base_headers())
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            return None
        else:
            results = resp.json()
            if results['status'] == 'ERROR':
                return None
            else:
                return results['results']

    def _get_base_headers(self):
        return {
            'X-API-Key': self.key,
        }

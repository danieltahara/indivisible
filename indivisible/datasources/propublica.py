from six.moves.html_parser import HTMLParser
import requests
from urlparse import urljoin
import us


class ProPublica(object):
    version = "v1"

    @staticmethod
    def get_base_url(version):
        return "https://api.propublica.org/congress/{}/".format(version)

    @classmethod
    def initialize(cls, key):
        cls.key = key

    def get_member_by_id(self, id):
        """
        Get member by id.

        @param id: member-id
        @return: member
        """
        results = self._get("members/{id}.json".format(id=id))
        return results[0] if results else None

    def get_members(self, congress, chamber):
        """
        Fetch members for congress, chamber from:
        https://propublica.github.io/congress-api-docs/#lists-of-members

        @param congress: number (current is 115)
        @param chamber: HOUSE or SENATE
        @return: list of members
        """
        params = {
            "congress": congress,
            "chamber": chamber,
        }
        results = self._get("{congress}/{chamber}/members.json".format(**params))
        return results[0]['members'] if results else []

    def get_members_by_location(self, chamber, state, district=None):
        """
        Get current members by chamber, state, and district.

        @param chamber: SENATE or HOUSE
        @param state: two-letter state abbreviation
        @param district: (optional) house district
        @return: members
        """
        state = us.states.lookup(unicode(state))
        if state is None:
            return []
        params = {
            "chamber": chamber,
            "state": state.abbr,
            "district": district,
        }
        if chamber == 'senate':
            results = self._get("members/{chamber}/{state}/current.json".format(**params))
        else:
            results = self._get("members/{chamber}/{state}/{district}/current.json".format(
                **params))

        return results or []

    def get_member_votes(self, id):
        """
        Get votes for given memer

        @param id: member-id
        @return: votes
        """
        results = self._get("members/{id}/votes.json".format(id=id))
        return results[0]['votes'] if results else []

    def get_committee(self, congress, chamber, code):
        results = self._get("{congress}/{chamber}/committees/{code}.json".format(
            congress=congress, chamber=chamber.lower(), code=code))
        if results:
            c = results[0]
            del c['former_members']
            c['committee'] = HTMLParser().unescape(c['committee'])
            return c
        else:
            return None

    def get_committees(self, congress, chamber):
        """
        Get committees for given congress and chamber
        """
        results = self._get("{congress}/{chamber}/committees.json".format(
            congress=congress, chamber=chamber.lower()))
        ret = results[0]['committees'] if results else []

        h = HTMLParser()
        for c in ret:
            c['name'] = h.unescape(c['name'])
        return ret

    def _get(self, path, params={}, headers={}):
        url = urljoin(self.get_base_url(self.version), path)
        headers = headers.copy()
        headers.update(self._get_base_headers())
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            return None
        else:
            results = resp.json()
            if results['status'] == 'ERROR' or results['status'] == '404':
                return None
            else:
                return results['results']

    def _get_base_headers(self):
        return {
            'X-API-Key': self.key,
        }

import us
import re

from base import JSONSource


class GoogleCivicInformation(JSONSource):

    @classmethod
    def initialize(cls, key):
        cls.key = key

    def __init__(self):
        super(GoogleCivicInformation, self).__init__(
            "https://www.googleapis.com/civicinfo/v2/")

    def lookup_congressional_district(self, address):
        params = {
            "address": address,
            "includeOffices": False,
            "key": self.key,
        }
        results = self._get("representatives", params=params)
        if results:
            district_regex = r"ocd-division/country:us/state:([a-zA-Z]{2})/cd:(\d{2})"
            for k in results["divisions"].iterkeys():
                print k
                matches = re.findall(district_regex, k)
                if len(matches) < 1:
                    continue
                state = matches[0][0]
                state = us.states.lookup(state).name
                district = int(matches[0][1])
                return (state, district)
            return (None, None)

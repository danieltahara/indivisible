from collections import defaultdict
import json
import requests
from urlparse import urljoin

class GPO(object):
    """
    Pulls data from the GPO
    """

    @staticmethod
    def get_base_url():
        return "http://memberguide.gpo.gov/Congressional.svc/GetMember/"

    def __init__(self, path):
        """
        Initialize a GPO object

        @param path: path to file containing dump of
        http://memberguide.gpo.gov/Congressional.svc/GetMembers/114
        """
        with open(path) as f:
            members = json.loads(f.read())
            by_name = defaultdict(lambda: defaultdict(list))
            for member in members:
                last = member['LastName'].upper()
                first = member['FirstName'].upper()
                by_name[last][first].append(member)
            self.members = by_name

    def get_member_id(self, last_name, first_name):
        members = self.members[last_name.upper()][first_name.upper()]
        return members[0]['MemberId'] if len(members) == 1 else None

    def get_member_info(self, last_name, first_name):
        member_id = self.get_member_id(last_name, first_name)
        if member_id:
            result = self._get(str(member_id))
            if result is not None and result.get('MemberId', 0) != 0:
                return result
        return {}

    def get_offices(self, last_name, first_name):
        info = self.get_member_info(last_name, first_name)
        return info['OfficeList'] if info else []

    def _get(self, path, params={}, headers={}):
        url = urljoin(self.get_base_url(), path)
        resp = requests.get(url, params, headers=headers)
        if resp.status_code != 200:
            return None
        else:
            return resp.json()

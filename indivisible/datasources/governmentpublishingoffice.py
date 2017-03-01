from collections import defaultdict

from base import JSONSource

class GovernmentPublishingOffice(JSONSource):
    """
    Pulls data from the GPO
    """

    def __init__(self, congress):
        """
        Initialize a GPO object

        @param path: path to file containing dump of
        """
        super(GovernmentPublishingOffice, self).__init__(
            "http://memberguide.gpo.gov/Congressional.svc/GetMember/")

        members = self._get("http://memberguide.gpo.gov/Congressional.svc/"\
                            "GetMembers/{}".format(congress))
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

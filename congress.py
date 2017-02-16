from collections import defaultdict
import propublica

class Congress(object):
    SENATE = 'senate'
    HOUSE = 'house'

    def __init__(self, congress):
        self.pp = propublica.ProPublica()
        self.congress = congress

    def get_members(self, chamber):
        return self.pp.get_members(self.congress, chamber)

    def get_members_by_name(self, chamber):
        """
        Get members of Congress.

        @param chamber: HOUSE or SENATE
        @return: map of last -> first -> list of Congressppl
        """
        members = self.get_members(chamber)
        by_name = defaultdict(lambda: defaultdict(list))
        for member in members:
            last = member.get('last_name').upper()
            first = member.get('first_name').upper()
            by_name[last][first].append(member)
        return by_name

    def get_senators(self, state):
        pass

    def get_congressperson(self, state, district):
        pass

    def search_members(self, name):
        """
        Search members of Congress.

        @param name: either a full name or last name.
        @return: list of Congresspersons with given name.
        """

        first, last = None, name
        if " " in name:
            first, last = name.split(" ")

        first = first.upper() if first else None
        last = last.upper()

        members = []
        for chamber in [self.HOUSE, self.SENATE]:
            by_name = self.get_members_by_name(chamber)
            by_first = by_name[last]
            if first is None:
                for vals in by_first.itervalues():
                    members.extend(vals)
            else:
                members.extend(by_first[first])

        return members

from collections import defaultdict
import datetime
import json


class Congress(object):
    SENATE = 'senate'
    HOUSE = 'house'

    def __init__(self, pp, er, gpo, pf, dhg, sg, congress):
        self.pp = pp
        self.er = er
        self.gpo = gpo
        self.pf = pf
        self.dhg = dhg
        self.sg = sg
        self.congress = congress
        self.events = {}

    def get_all_members(self):
        senators = self.get_members(self.SENATE)
        for s in senators:
            s['chamber'] = self.SENATE.capitalize()
        reps = self.get_members(self.HOUSE)
        for r in reps:
            r['chamber'] = self.HOUSE.capitalize()
        return senators + reps

    def get_members(self, chamber):
        return self.pp.get_members(self.congress, chamber)

    # TODO: do this by default...
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
        """
        Get Senators for state

        @param state: can be abbreviation or full name
        """
        members = self.pp.get_members_by_location(self.SENATE, state)
        return [self._make_cp_from_self(member['id']) for member in members]

    def get_representative(self, state, district):
        """
        Get House Rep for state and district

        @param state: can be abbreviation or full name
        @param district: congressional district
        """
        members = self.pp.get_members_by_location(self.HOUSE, state, district)
        return [self._make_cp_from_self(member['id']) for member in members]

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

        return [self._make_cp_from_self(member['id']) for member in members]

    def get_events_by_committee(self, chamber, days):
        """
        Get events for the next days.

        @param days: number of days
        @return: map of committee id (e.g. HSHA) to list of events with form: {
            'name': name of event,
            'url': event url,
            'date': date event occurs,
            'time': time event will occur,
            'committee': commitee name,
            'committee_codee': commitee code,
            'subcommittee': (optional) subcommittee,
            'subcommittee_code': (optional) subcommittee code,
        }
        """
        committees = self.get_committees_by_name(chamber)
        all_events = []
        if chamber.upper() == self.HOUSE.upper():
            today = datetime.date.today()
            for i in range(days):
                date = today + datetime.timedelta(days=i)
                all_events.extend(self.dhg.get_events(date))
        else:
            all_events.extend(self.sg.get_events(None))

        events_by_commmittee_id = defaultdict(list)
        for e in all_events:
            committee = committees.get(e['committee'].upper(), None)
            if committee:
                e['committee_code'] = committee['id']
                e['chamber'] = chamber
                events_by_commmittee_id[committee['id']].append(e)
            else:
                events_by_commmittee_id['UNKNOWN'].append(e)
        return dict(events_by_commmittee_id)

    def get_committees(self, chamber):
        return self.pp.get_committees(self.congress, chamber)

    def get_events(self, chamber):
        # TODO: periodic refresh
        if not self.events.get(chamber, None):
            self.events[chamber] = self.get_events_by_committee(chamber, 15)
        return self.events[chamber]

    def get_events_for_committee(self, chamber, code):
        events = self.get_events(chamber)
        return events.get(code.upper(), [])

    def get_committees_by_name(self, chamber):
        committees = {}
        for c in self.get_committees(chamber):
            committees[c['name'].upper()] = c
        return committees

    def _make_cp_from_self(self, id):
        from congressperson import Congressperson

        return Congressperson(id)


def json_pretty(j):
    print json.dumps(j, sort_keys=True, indent=4, separators=(',', ': '))

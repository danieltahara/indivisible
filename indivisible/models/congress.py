from collections import defaultdict
import datetime
import json
from sqlalchemy import or_
import us

from committee import Committee
from congressperson import Congressperson
from database import db


class Congress(db.Model):
    __tablename__ = 'congress'
    congress = db.Column(db.Integer, primary_key=True)
    last_updated = db.Column(db.DateTime, nullable=False,
                          server_default=db.func.now(),
                          server_onupdate=db.func.now())

    SENATE = 'senate'
    HOUSE = 'house'

    @classmethod
    def initialize_datasources(cls, pp, er, gpo, pf, dhg, sg):
        """
        Initialize class with the following datasources:
            * ProPublica
            * EventRegistry
            * Government Publishing Office
            * Politifact
            * docs.house.gov
            * senate.gov
        """
        cls.pp = pp
        cls.er = er
        cls.gpo = gpo
        cls.pf = pf
        cls.dhg = dhg
        cls.sg = sg

    @classmethod
    def get_or_create(cls, congress):
        cg = cls.query.filter_by(congress=congress).first()
        if not cg:
            cg = cls(congress=congress)
            db.session.add(cg)
            db.session.commit()
        elif cg.last_updated + datetime.timedelta(days=1) < datetime.datetime.today():
            print "Updating {}th congress".format(congress)
            cg.last_updated = datetime.datetime.now()
            db.session.commit()
        try:
            cg.members
        except AttributeError:
            cg.refresh()
        return cg

    def refresh(self):
        self.members = {}
        self.committees = {}
        self.events = {}
        for chamber in [self.SENATE, self.HOUSE]:
            self.get_members(chamber)
            self.get_committees(chamber)
            #self.get_events(chamber)

    def get_all_members(self):
        return self.get_members(self.HOUSE) + self.get_members(self.SENATE)

    def get_members(self, chamber):
        if chamber not in self.members:
            members = []
            pp_members = self.pp.get_members(self.congress, chamber)
            for pp in pp_members:
                cp = Congressperson.get_or_create(pp['id'])
                members.append(cp)
            self.members[chamber] = members
        return self.members[chamber]

    def get_senators(self, state):
        """
        Get Senators for state

        @param state: can be abbreviation or full name
        """
        return self.search_members(chamber=self.SENATE, state=state)

    def get_representative(self, state, district):
        """
        Get House Rep for state and district

        @param state: can be abbreviation or full name
        @param district: congressional district
        """
        return self.search_members(chamber=self.HOUSE, state=state, district=district)

    def search_members(self, name=None, chamber=None, state=None, district=None):
        """
        Search members of Congress.

        @param name: part of a first name or last name.
        @return: list of Congresspersons with given name.
        """
        members = Congressperson.query.filter_by(congress=self.congress)
        if chamber is not None:
            members = members.filter_by(chamber=chamber.capitalize())
        if state is not None:
            state = us.states.lookup(unicode(state))
            if state is None:
                return []
            members = members.filter_by(state=state.abbr)
        if district is not None:
            members = members.filter_by(district=district)
        if name is not None:
            members = members.filter(or_(Congressperson.first_name.contains(name),
                                         Congressperson.last_name.contains(name)))
        return members.all()

    def get_committees(self, chamber):
        """
        Gets list of committees for a given chamber, organized by code
        """
        if chamber not in self.committees:
            self.committees[chamber] = {}
            committees = self.pp.get_committees(self.congress, chamber)
            for c in committees:
                committee = Committee.get_or_create(self.congress, chamber, c['id'])
                self.committees[chamber][c['id']] = committee
        return self.committees[chamber]

    def get_code_for_committee(self, chamber, name):
        committee = Committee.query.filter(
            db.func.lower(Committee.chamber) == chamber.lower()).filter(
            db.func.lower(Committee.name) == name.lower()).first()
        return committee.code if committee else None

    def get_events(self, chamber, code=None):
        if self.events.get(chamber, None) is None:
            self.events[chamber] = self._get_events_by_committee(chamber, 15)

        if code is not None:
            return self.events[chamber].get(code, [])
        else:
            events = []
            for v in self.events[chamber].iteritems():
                events.extend(v)
            return events

    def _get_events(self, chamber, days):
        all_events = []
        if chamber.upper() == self.HOUSE.upper():
            today = datetime.datetime.today()
            for i in range(days):
                date = today + datetime.timedelta(days=i)
                all_events.extend(self.dhg.get_events(date))
        else:
            all_events.extend(self.sg.get_events(None))
        return all_events

    def _get_events_by_committee(self, chamber, days):
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

        all_events = self._get_events(chamber, days)
        committees = self.get_committees(chamber)

        events_by_commmittee_id = defaultdict(list)
        for e in all_events:
            code = self.get_code_for_committee(chamber, e['committee'])
            committee = committees.get(code, None)
            if committee:
                e['committee_code'] = code
                e['chamber'] = chamber
                events_by_commmittee_id[code].append(e)
            else:
                events_by_commmittee_id['UNKNOWN'].append(e)
        return dict(events_by_commmittee_id)

def json_pretty(j):
    print json.dumps(j, sort_keys=True, indent=4, separators=(',', ': '))

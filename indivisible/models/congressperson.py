from six.moves.html_parser import HTMLParser
import datetime
import feedparser
import json

from committee import Committee
from database import db


class Congressperson(db.Model):
    __tablename__ = 'congressperson'
    id = db.Column(db.String(10), primary_key=True)
    last_name = db.Column(db.String(30), nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    congress = db.Column(db.Integer, nullable=False) # FOREIGN KEY
    chamber = db.Column(db.String(10), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    district = db.Column(db.String(4))
    image = db.Column(db.String(200))
    member_json = db.Column(db.String(8192), nullable=False)
    member_hash = db.Column(db.String(32), nullable=False) # TODO
    last_updated = db.Column(db.DateTime, nullable=False,
                             server_default=db.func.now(),
                             server_onupdate=db.func.now())

    @classmethod
    def initialize_datasources(cls, pp, er, gpo, pf, cg):
        """
        Initialize class with the following datasources:
            * ProPublica
            * EventRegistry
            * GPO
            * Politifact
        """
        cls.pp = pp
        cls.er = er
        cls.gpo = gpo
        cls.pf = pf
        cls.cg = cg  # TODO: get rid of this dep

    @classmethod
    def get_or_create(cls, id):
        cp = cls.query.filter_by(id=id).first()
        if not cp:
            member = cl.pp.get_member_by_id(id)
            if len(member['roles']) > 2:
                member['roles'] = member['roles'][:2]

            cp_dict = {
                'member_json': json.dumps(member),
                'member_hash': "ABC",  # TODO
                'last_name': HTMLParser().unescape(member['last_name']),
                'first_name': HTMLParser().unescape(member['first_name']),
                'congress': member['roles'][0]['congress'],
                'chamber': member['roles'][0]['chamber'],
                'state': member['roles'][0]['state'],
                'district': member['roles'][0]['district'],
            }

            cp = cls(**cp_dict)
            db.session.add(cp)
            db.session.commit()
        # else if last_update > 1 day ago...
        return cp

    @property
    def member(self):
        try:
            self.__member
        except AttributeError:
            self.__member = json.loads(self.member_json)
        return self.__member

    @member.setter
    def member(self, member):
        self.__member = member

    def get_id(self):
        return self.id

    def get_last_name(self):
        return self.last_name

    def get_first_name(self):
        return self.first_name

    def get_name(self):
        return " ".join([self.get_first_name(), self.get_last_name()])

    def get_image_url(self):
        if self.image is None:
            member_info = self.gpo.get_member_info(self.get_last_name(),
                                                   self.get_first_name())
            self.image = member_info.get("ImageUrl", None) if member_info else None
            if self.image is not None:
                db.session.commit()
        return self.image

    def get_party(self):
        return self.member['current_party']

    def get_twitter_handle(self):
        return self.member['twitter_account']

    def get_facebook_account(self):
        return self.member['facebook_account']

    def get_google_entity(self):
        return self.member['google_entity_id']

    def get_website(self):
        return self.member['url']

    def get_state(self):
        return self.state

    def get_chamber(self):
        return self.chamber

    def get_district(self):
        return self.district

    def get_committees(self):
        committees = self.member['roles'][0]['committees']
        if len(committees) == 0 and len(self.member['roles']) > 1:
            committees = self.member['roles'][1]['committees']
        committees = [Committee.get_or_create(self.congress, self.chamber, c['code'])
                for c in committees]
        return [c for c in committees if c is not None]

    def get_offices(self):
        return self.gpo.get_offices(self.get_last_name(),
                                    self.get_first_name())

    def get_votes(self, last_n=0):
        """
        Get votes by congressperson.

        @param last_n: if > 0, limit on number of votes to return.
        @return: Votes by congressperson.
        """
        votes = self.pp.get_member_votes(self.get_id())
        return votes[:last_n] if last_n > 0 else votes

    def get_bills(self, limit=0):
        """
        Get votes by congressperson.

        @param limit: if > 0, limit on number of votes to return.
        @return: Bills sponsored by congressperson.
        """
        bills = self.pp.get_member_bills(self.get_id())
        return bills[:limit] if limit > 0 else bills

    def get_news(self, limit=0):
        """
        Get new events related to congressperson using EventRegistry API

        @param limit: if > 0, limit on number of votes to return.
        @return: Votes by congressperson.
        """
        events = self.er.get_events(self.get_name(), limit=limit)
        return events if events else []

    def get_statements(self, last_n=0):
        """
        Get public statements from Congressperson

        @param last_n: if > 0, limit on number of votes to return.
        @return: rss statements by congressperson.
        """
        feed = feedparser.parse(self.member['rss_url'])
        ret = feed['items'][:last_n] if feed['items'] and last_n > 0 else []
        for r in ret:
            # e.g. https://amodei.house.gov/rss/news-releases.xml
            if r['published_parsed'] is not None:
                r['date'] = datetime.datetime(*r['published_parsed'][:6]).strftime(
                    '%m-%d-%Y')
        return ret

    def get_politifacts(self, limit=0):
        """
        Get politifact ratings for statements by cp

        @param limit: if > 0, limit on number of statements to return.
        @return: politifacts ratings
        """
        return self.pf.get_statements_by_person(
            self.get_first_name(), self.get_last_name(), limit=limit)

    def get_events(self):
        result = []
        for c in self.get_committees():
            events = self.cg.get_events(self.get_chamber(), c.code)
            for event in events:
                result.append((event['date'], event))
        return sorted(result, key=lambda ev: ev[0])

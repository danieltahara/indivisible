from six.moves.html_parser import HTMLParser
import datetime
import feedparser
import json
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import func

from database import Base
from database import db_session
from committee import Committee


class Congressperson(Base):
    __tablename__ = 'congressperson'
    id = Column(String(10), primary_key=True)
    last_name = Column(String(30), nullable=False)
    first_name = Column(String(30), nullable=False)
    congress = Column(Integer, nullable=False) # FOREIGN KEY
    chamber = Column(String(10), nullable=False)
    state = Column(String(2), nullable=False)
    district = Column(String(4))
    member_json = Column(String(8192), nullable=False)
    member_hash = Column(String(32), nullable=False) # TODO
    last_updated = Column(DateTime, nullable=False,
                          server_default=func.now(),
                          server_onupdate=func.now())

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
        cp = cls.query.filter(cls.id == id).first()
        if not cp:
            cp = cls(id)
            db_session.add(cp)
            db_session.commit()
        # else if last_update > 1 day ago...
        return cp

    def __init__(self, id):
        self.id = id
        self.__member = self.pp.get_member_by_id(id)
        if len(self.__member['roles']) > 2:
            self.__member['roles'] = self.__member['roles'][:2]
        self.member_json = json.dumps(self.__member)
        self.member_hash = "ABC"  # TODO
        self.last_name = HTMLParser().unescape(self.member['last_name'])
        self.first_name = HTMLParser().unescape(self.member['first_name'])
        self.congress = self.member['roles'][0]['congress']
        self.chamber = self.member['roles'][0]['chamber']
        self.state = self.member['roles'][0]['state']
        self.district = self.member['roles'][0]['district']

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
        member_info = self.gpo.get_member_info(self.get_last_name(),
                                               self.get_first_name())
        return member_info.get("ImageUrl", None) if member_info else None

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
            if r['published_parsed'] is not None:  # e.g. https://amodei.house.gov/rss/news-releases.xml
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

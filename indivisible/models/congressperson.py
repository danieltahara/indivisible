import feedparser
import json

class Congressperson(object):
    @classmethod
    def from_id(cls, pp, er, gpo, id):
        member = pp.get_member_by_id(id)
        if member is None:
            return None
        return cls(pp, er, gpo, member)

    def __init__(self, pp, er, gpo, member):
        self.pp = pp
        self.er = er
        self.gpo = gpo
        self.member = member

    def get_id(self):
        return self.member['member_id']

    def get_last_name(self):
        return self.member['last_name']

    def get_first_name(self):
        return self.member['first_name']

    def get_name(self):
        return " ".join([self.get_first_name(), self.get_last_name()])

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
        return self.member['roles'][0]['state']

    def get_chamber(self):
        return self.member['roles'][0]['chamber']

    def get_district(self):
        return self.member['roles'][0]['district']

    def get_committees(self):
        return self.member['roles'][0]['committees']

    def get_offices(self):
        return self.gpo.get_offices(self.get_last_name(), self.get_first_name())

    def get_votes(self, last_n=0):
        """
        Get votes by congressperson.

        @param last_n: if > 0, limit on number of votes to return. Else returns 100.
        @return: Votes by congressperson.
        """
        votes = self.pp.get_member_votes(self.get_id())
        return votes[:last_n] if last_n > 0 else votes

    def get_events(self, last_n=0):
        """
        Get new events related to congressperson using EventRegistry API

        @param last_n: if > 0, limit on number of votes to return. Else returns 100.
        @return: Votes by congressperson.
        """
        events = self.er.get_events(self.get_name())
        return events[:last_n] if last_n > 0 else events

    def get_statements(self, last_n=0):
        """
        Get public statements from Congressperson

        @param last_n: if > 0, limit on number of votes to return. Else returns 100.
        @return: rss statements by congressperson.
        """
        feed = feedparser.parse(self.member['rss_url'])
        return feed['items'][:last_n] if feed['items'] and last_n > 0 else []

    def get_calendar(self):
        pass

    def to_dict(self):
        member = {
            "name": self.get_name(),
            "party": self.get_party(),
            "website": self.member['url'],
            "facebook": self.member['facebook_account'],
            "twitter": self.get_twitter_handle(),
            "google_entity_id": self.member['google_entity_id'],
        }
        member.update(self.member['roles'][0])
        member['committees'] = [{'name': c['name'], 'code': c['code']} \
                                for c in member['committees']]
        return member

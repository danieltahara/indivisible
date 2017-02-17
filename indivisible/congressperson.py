from datasources import propublica
from datasources import twitter

class Congressperson(object):
    @classmethod
    def from_id(cls, id):
        member = propublica.ProPublica().get_member_by_id(id)
        if member is None:
            return None
        return cls(member)

    def __init__(self, member):
        self.pp = propublica.ProPublica()
        self.member = member

    def get_id(self):
        return self.member['member_id']

    def get_last_name(self):
        return self.member['last_name']

    def get_first_name(self):
        return self.member['first_name']

    def get_name(self):
        return " ".join([self.get_first_name(), self.get_last_name()])

    def get_twitter_handle(self):
        return self.member['twitter_account']

    def get_recent_votes(self, last_n=0):
        """
        Get votes by congressperson.

        @param last_n: if > 0, limit on number of votes to return. Else returns 100.
        @return: Votes by congressperson.
        """
        votes = self.pp.get_member_votes(self.get_id())
        return votes[:last_n] if last_n > 0 else votes

    def get_recent_tweets(self):
        handle = self.member['twitter_account']

    def get_calendar(self):
        pass

    def to_dict(self):
        return self.member

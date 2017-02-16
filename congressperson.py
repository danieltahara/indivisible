from datasources import propublica
from datasources import twitter

class Congressperson(object):
    def __init__(self, id):
        self.pp = propublica.ProPublica()
        self.id = id
        self.member = self.pp.get_member_by_id(id)

    def _get_twitter(self):
        handle = self.member['twitter_account']

    def get_name(self):
        return " ".join([self.member['first_name'],
                         self.member['last_name']])

    def get_recent_votes(self, last_n=0):
        """
        Get votes by congressperson.

        @param last_n: if > 0, limit on number of votes to return
        @return: Votes by congressperson.
        """
        votes = self.pp.get_member_votes(self.id)
        return votes[:last_n] if last_n > 0 else votes

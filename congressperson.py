from datasources import propublica

class Congressperson(object):
    def __init__(self, member):
        self.member = member

    def get_recent_votes(self, last_n):
        pass

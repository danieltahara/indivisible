import json
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import func
from sqlalchemy import Integer
from sqlalchemy import String

from database import db


class Committee(db.Model):
    __tablename__ = 'committee'
    # pkey = code, congress
    code = Column(String(10), primary_key=True)
    congress = Column(Integer, nullable=False)
    chamber = Column(String(10), nullable=False)
    name = Column(String(100), nullable=False)
    committee_json = Column(String(1024), nullable=False)
    committee_hash = Column(String(32), nullable=False)
    last_updated = Column(DateTime, nullable=False,
                          server_default=func.now(),
                          server_onupdate=func.now())

    @classmethod
    def initialize_datasources(cls, pp):
        """
        Initialize class with the following datasources:
            * ProPublica
        """
        cls.pp = pp

    @classmethod
    def get_or_create(cls, congress, chamber, code):
        c = cls.query.filter_by(congress=congress).filter_by(code=code).first()
        if c is None:
            pp_c = cls.pp.get_committee(congress, chamber, code)
            if pp_c is None:
                return None  # e.g. SCNC
            c_dict = {
                'code': code,
                'congress': congress,
                'chamber': chamber,
                'name': pp_c['committee'],
                'committee_json': json.dumps(pp_c),
                'committee_hash': "ABC",  # TODO
            }
            c = cls(**c_dict)
            db.session.add(c)
            db.session.commit()
        return c

    @property
    def committee(self):
        try:
            self.__committee
        except AttributeError:
            self.__committee = json.loads(self.committee_json)
        return self.__committee

    @committee.setter
    def committee(self, committee):
        self.__committee = committee

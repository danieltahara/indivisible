import datetime
import hashlib
import json

from database import db


class Committee(db.Model):
    __tablename__ = 'committee'
    # pkey = code, congress
    code = db.Column(db.String(10), primary_key=True)
    congress = db.Column(db.Integer, nullable=False)
    chamber = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    committee_json = db.Column(db.String(1024), nullable=False)
    committee_hash = db.Column(db.String(32), nullable=False)
    last_updated = db.Column(db.DateTime, nullable=False,
                          server_default=db.func.now(),
                          server_onupdate=db.func.now())

    @classmethod
    def initialize_datasources(cls, pp):
        """
        Initialize class with the following datasources:
            * ProPublica
        """
        cls.pp = pp

    @classmethod
    def get_c_dict(cls, congress, chamber, code):
        pp_c = cls.pp.get_committee(congress, chamber, code)
        if pp_c is None:
            return None  # e.g. SCNC
        c_dict = {
            'code': code,
            'congress': congress,
            'chamber': chamber,
            'name': pp_c['committee'],
            'committee_json': json.dumps(pp_c),
        }
        md5 = hashlib.md5()
        md5.update(c_dict['committee_json'])
        c_dict['committee_hash'] = md5.hexdigest()
        return c_dict

    @classmethod
    def get_or_create(cls, congress, chamber, code):
        results = cls.query.filter_by(congress=congress).filter_by(code=code)
        c = results.first()
        if c is None:
            c_dict = cls.get_c_dict(congress, chamber, code)
            if c_dict is None: # FIXME
                return None
            c = cls(**c_dict)
            db.session.add(c)
            db.session.commit()
        elif c.last_updated + datetime.timedelta(days=7) < datetime.datetime.today():
            c_dict = cls.get_c_dict(congress, chamber, code)
            if c_dict['committee_hash'] != c.committee_hash:
                print "Refreshing committee info for {}".format(c_dict['code'])
                results.update(c_dict)
                db.session.commit()
                return cls.get_or_create(congress, chamber, code)
            else:
                c.last_updated = datetime.datetime.now()
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
        self.committee_json = json.dumps(self.__committee)
        md5 = hashlib.md5()
        md5.update(self.committee_json)
        self.committee_hash = md5.hexdigest()

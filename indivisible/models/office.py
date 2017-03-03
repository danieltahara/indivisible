from six.moves.html_parser import HTMLParser
import datetime
import feedparser
import json

from database import db


class Office(db.Model):
    __tablename__ = 'office'
    id = db.Column(db.Integer, primary_key=True)
    cp_id = db.Column(db.String(10), db.ForeignKey('congressperson.id'), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    info_json =  db.Column(db.String(1000), nullable=True)
    __table_args__ = (db.UniqueConstraint("cp_id", "city"),)


    @classmethod
    def get_or_create(cls, cp_id, city):
        office = cls.query.filter_by(cp_id=cp_id).filter_by(city=city).first()
        if not office:
            office = cls(cp_id=cp_id, city=city)
            db.session.add(office)
            db.session.commmit()

    @property
    def info(self):
        try:
            self.__info
        except AttributeError:
            self.__info = json.loads(self.info_json)
        return self.__info

    @info.setter
    def info(self, info):
        self.__info = info

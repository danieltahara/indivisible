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
    phone = db.Column(db.String(10), nullable=True)
    info_json =  db.Column(db.String(2048), nullable=True)
    __table_args__ = (db.UniqueConstraint("cp_id", "city"),)


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
        self.info_json = json.dumps(self.__info)

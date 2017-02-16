from flask import Flask
import pprint

from datasources import propublica
from congressperson import Congressperson

app = Flask(__name__)

propublica.ProPublica.load_api_key()

@app.route('/')
def main():
    return "Hello world"

@app.route('/member/<name>')
def get_member(name):
    cp = Congressperson.by_name(115, name)
    return pprint.pformat(cp.member)

@app.route('/member/<name>/votes')
def get_votes(name):
    cp = Congressperson.by_name(115, name)
    return pprint.pformat(cp.get_recent_votes(5))

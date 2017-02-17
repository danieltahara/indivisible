from flask import (
    Flask,
    render_template,
    request,
    url_for,
)
from flask_bootstrap import Bootstrap
import json
import us

from datasources.eventregistry import EventRegistry
from datasources.propublica import ProPublica
from models.congress import Congress
from models.congressperson import Congressperson

app = Flask(__name__)
app.config.from_envvar('CONFIG')
Bootstrap(app)

pp = ProPublica(app.config['PROPUBLICA_API_KEY'])
er = EventRegistry(app.config['EVENT_REGISTRY_API_KEY'])

@app.route('/')
def main():
    all_states = us.states.STATES
    return render_template("main.html", all_states=us.states.STATES)

@app.route('/members/search')
def search_members():
    name = request.args.get('q')
    cg = Congress(pp, er, 115)
    members = cg.search_members(name)
    return render_template('members_search.html', members=members)

@app.route('/members/location_search')
def search_members_by_location():
    state = request.args.get('state')
    district = request.args.get('district')
    cg = Congress(pp, er, 115)
    members = cg.get_senators(state)
    members.extend(cg.get_representative(state, district))
    return render_template('members_search.html', members=members)

@app.route('/members/<id>')
def get_member(id):
    cp = Congressperson.from_id(pp, er, id)
    return render_template('member.html', member=cp)

@app.route('/members/<id>/votes')
def get_votes(id):
    cp = Congressperson(pp, er, id)
    last_n = int(request.args.get('last', 0))
    votes = cp.get_recent_votes(last_n)
    return render_template('json.html', data=votes)

@app.route('/committees/<chamber>/<id>')
def get_committee(chamber, id):
    return "FOO"

@app.context_processor
def add_utilities():
    def json_pretty(arg):
        return json.dumps(arg, indent=4, separators=(',', ': '))
    return dict(json_pretty=json_pretty, url_for=url_for)

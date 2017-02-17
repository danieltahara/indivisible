from flask import (
    Flask,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_bootstrap import Bootstrap
import json
from urlparse import urljoin
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

@app.route('/votes/<congress>/<chamber>/<session>/<roll_call>')
def get_votes(congress, chamber, session, roll_call):
    url = "https://projects.propublica.org/represent/votes/{congress}/{chamber}/{session}/{roll_call}".format(
        congress=congress, chamber=chamber, session=session, roll_call=roll_call)
    return redirect(url, 302)

@app.route('/committees/<chamber>/<code>')
def get_committee(chamber, code):
    return redirect(
        urljoin('https://www.govtrack.us/congress/committees/', code), 302)

@app.route('/events/<uri>')
def get_event(uri):
    url = "http://eventregistry.org/event/{uri}?displayLang=eng&tab=articles".format(uri=uri)
    return redirect(url, 302)

@app.context_processor
def add_utilities():
    def json_pretty(arg):
        return json.dumps(arg, indent=4, separators=(',', ': '))
    return dict(
        json_pretty=json_pretty,
        url_for=url_for,
    )

from flask import (
    Flask,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_bootstrap import Bootstrap
import json
import os
from urlparse import urljoin
import us

from datasources.eventregistry2 import EventRegistry2
from datasources.gpo import GPO
from datasources.politifact import Politifact
from datasources.propublica import ProPublica
from datasources.docshousegov import DocsHouseGov
from models.congress import Congress
from models.congressperson import Congressperson

app = Flask(__name__)
Bootstrap(app)

pp = ProPublica(os.environ['PROPUBLICA_API_KEY'])
er = EventRegistry2(os.environ['EVENT_REGISTRY_API_KEY'])
gpo = GPO(os.environ['GPO_DATA_PATH'])
dhg = DocsHouseGov()
pf = Politifact()
cg = Congress(pp, er, gpo, pf, dhg, 115)


@app.route('/')
def main():
    return render_template("main.html", cg=cg, all_states=us.states.STATES)


@app.route('/members/search')
def search_members():
    name = request.args.get('q')
    members = cg.search_members(name)
    return render_template('members_search.html', members=members)


@app.route('/members/location_search')
def search_members_by_location():
    state = request.args.get('state')
    district = request.args.get('district')
    members = cg.get_senators(state)
    members.extend(cg.get_representative(state, district))
    return render_template('members_search.html', members=members)


@app.route('/members/<id>')
def get_member(id):
    cp = Congressperson.from_id(pp, er, gpo, pf, cg, id)
    return render_template('member.html', member=cp)


@app.route('/votes/<congress>/<chamber>/<session>/<roll_call>')
def get_votes(congress, chamber, session, roll_call):
    url = "https://projects.propublica.org/represent/votes/{congress}/" \
        "{chamber}/{session}/{roll_call}".format(
            congress=congress, chamber=chamber, session=session,
            roll_call=roll_call)
    return redirect(url, 302)


@app.route('/committees/<chamber>/<code>')
def get_committee(chamber, code):
    return redirect(
        urljoin('https://www.govtrack.us/congress/committees/', code), 302)


@app.route('/news/<uri>')
def get_news(uri):
    url = "http://eventregistry.org/event/{uri}?displayLang=eng&tab=articles" \
        .format(uri=uri)
    return redirect(url, 302)


@app.route('/politifact/<first_name>/<last_name>')
def get_politifact(last_name, first_name):
    url = "http://www.politifact.com/personalities/{first_name}-{last_name}/" \
        "statements".format(last_name=last_name.lower(),
                            first_name=first_name.lower())
    return redirect(url, 302)


@app.context_processor
def add_utilities():
    def json_pretty(arg):
        return json.dumps(arg, indent=4, separators=(',', ': '))
    return dict(
        json_pretty=json_pretty,
        url_for=url_for,
    )

if __name__ == "__main__":
    host = '0.0.0.0'
    if os.environ.get('FLASK_DEBUG', '0') == '1':
        host = '127.0.0.1'
    app.run(host=host, port=os.environ.get('PORT', 5000))

from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_bootstrap import Bootstrap
import json
import os
from twilio.util import TwilioCapability
from twilio import twiml
from urlparse import urljoin
import us

from datasources.docshousegov import DocsHouseGov
from datasources.eventregistry2 import EventRegistry2
from datasources.gpo import GPO
from datasources.politifact import Politifact
from datasources.propublica import ProPublica
from datasources.senategov import SenateGov
from models.congress import Congress
from models.congressperson import Congressperson

app = Flask(__name__)
Bootstrap(app)

pp = ProPublica(os.environ['PROPUBLICA_API_KEY'])
er = EventRegistry2(os.environ['EVENT_REGISTRY_API_KEY'])
gpo = GPO(os.environ['GPO_DATA_PATH'])
dhg = DocsHouseGov()
sg = SenateGov()
pf = Politifact()
cg = Congress(pp, er, gpo, pf, dhg, sg, 115)

# Create a TwilioCapability object with our Twilio API credentials
capability = None
twilio_phone_number =os.environ.get('TWILIO_PHONE_NUMBER', None)
if os.environ.get('TWILIO_AUTH_TOKEN', None) is not None:
    # Allow our users to make outgoing calls with Twilio Client
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    capability = TwilioCapability(account_sid, auth_token)
    capability.allow_client_outgoing(os.environ['TWIML_APP_SID'])


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


@app.route('/members/token', methods=['GET'])
def get_token():
    if capability is not None:
        token = capability.generate()
        page = request.args.get('forPage')
        return jsonify({'token': token})
    else:
        response = jsonify({"error": "Missing capability"})
        response.status_code = 500
        return response


@app.route('/members/call', methods=['POST'])
def call():
    """Returns TwiML instructions to Twilio's POST requests"""
    response = twiml.Response()

    with response.dial(callerId=twilio_phone_number) as dial:
        dial.number("+16463976379")

    return response


@app.route('/members/call_new', methods=['POST'])
def call_new():
    """Returns TwiML instructions to Twilio's POST requests"""
    response = twiml.Response()

    with response.dial(callerId=twilio_phone_number) as dial:
        member_id = request.form.get('member_id', None)
        if not member_id:
            response = jsonify({"error": "Missing member id"})
            response.status_code = 500
            return response

        cp = Congressperson.from_id(pp, er, gpo, pf, cg, member_id)

        office_id = request.form.get('office_id', 0)
        offices = cp.get_offices()
        if office_id >= len(offices) or office_id < 0:
            office_id = 0
        phone = offices[office_id]['Phone']

        dial.number(phone)

    return str(response)


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

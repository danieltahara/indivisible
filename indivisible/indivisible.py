from flask import Flask
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
import os
import json
import re
import requests
from twilio.util import TwilioCapability
from twilio import twiml
from urlparse import urljoin
import us

from datasources.congressgov import CongressGov
from datasources.docshousegov import DocsHouseGov
from datasources.eventregistry2 import EventRegistry2
from datasources.googlecivicinformation import GoogleCivicInformation
from datasources.governmentpublishingoffice import GovernmentPublishingOffice
from datasources.politifact import Politifact
from datasources.propublica import ProPublica
from datasources.senategov import SenateGov
from models.committee import Committee
from models.congress import Congress
from models.congressperson import Congressperson
from models.office import Office

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
Bootstrap(app)

cg = None # Congress object
capability = None # Twilio capability
twilio_phone_number = None

@app.route('/')
def main():
    return render_template("main.html")


@app.route('/whatshot')
def get_whats_hot():
    cog = CongressGov()
    bills = cog.get_hot_bills()
    return render_template("whatshot.html", hot_bills=bills)


@app.route('/data')
def get_data():
    return render_template("data.html")


@app.route('/members')
def get_members():
    return render_template("members.html", cg=cg, all_states=us.states.STATES)


@app.route('/members/search')
def search_members():
    address = request.args.get('address', None)
    if address:
        state, district = cg.lookup_congressional_district(address)
        if state is not None:
            members = cg.search_members(chamber=cg.SENATE, state=state)
            members.extend(cg.search_members(chamber=cg.HOUSE, state=state, district=district))
        else:
            members = []
    else:
        name = request.args.get('name', None)
        chamber = request.args.get('chamber', None)
        state = request.args.get('state', None)
        district = request.args.get('district', None)
        members = cg.search_members(name=name, chamber=chamber, state=state, district=district)
    return render_template('members_search.html', members=members, args=request.args)

@app.route('/members/token', methods=['GET'])
def get_token():
    if capability is not None:
        token = capability.generate()
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
        phone_number = request.form.get('phoneNumber', None)
        office_id = request.form.get('officeId', None)
        if not phone_number or not office_id:
            response = jsonify({"error": "Missing params (phone #, office #)"})
            response.status_code = 500
            return response

        office = Office.query.filter_by(id=office_id).first()
        if not office or office.phone != phone_number:
            response = jsonify({"error": "Invalid office"})
            response.status_code = 500
            return response

        if str(phone_number) != office.phone:
            response = jsonify({"error": "Phone number failed validation"})
            response.status_code = 500
            return response

        phone = "+1{}".format(office.phone)
        dial.number(phone)

    return str(response)


@app.route('/members/<id>')
def get_member(id):
    cp = Congressperson.get_or_create(id)
    return render_template('member.html', member=cp)


@app.route('/members/<id>/politifact')
def get_politifact(last_name, first_name):
    cp = Congressperson.get_or_create(id)
    if cp is None:
        response = jsonify({"error": "Missing capability"})
        response.status_code = 500
        return response
    url = "http://www.politifact.com/personalities/{first_name}-{last_name}/" \
        "statements".format(last_name=cp.get_last_name().lower(),
                            first_name=cp.get_first_name().lower())
    return redirect(url, 302)


@app.route('/members/<id>/on_the_issues')
def get_on_the_issues(id):
    cp = Congressperson.get_or_create(id)
    if cp is None:
        response = jsonify({"error": "Missing capability"})
        response.status_code = 500
        return response
    url = "http://www.ontheissues.org/{state}/{first_name}_{last_name}.htm" \
        .format(state=cp.get_state(), last_name=cp.get_last_name(), first_name=cp.get_first_name())
    resp = requests.head(url)
    if resp.status_code != 200:
        url = "http://www.ontheissues.org/{chamber}/{first_name}_{last_name}.htm" \
            .format(chamber=cp.get_chamber(), last_name=cp.get_last_name(),
                    first_name=cp.get_first_name())
    return redirect(url, 302)


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


@app.route('/bills/<congress>/<number>')
def get_bill(congress, number):
    url = "https://www.govtrack.us/congress/bills/{congress}/{number}".format(
        congress=congress, number=re.sub(r"\W", "", number).lower())
    return redirect(url, 302)


@app.route('/news/<uri>')
def get_news(uri):
    url = "http://eventregistry.org/event/{uri}?displayLang=eng&tab=articles" \
        .format(uri=uri)
    return redirect(url, 302)


@app.context_processor
def add_utilities():
    def json_pretty(arg):
        return json.dumps(arg, indent=4, separators=(',', ': '))
    return dict(
        json_pretty=json_pretty,
        url_for=url_for,
    )

def initialize_app(app):
    from models.database import db
    db.init_app(app)
    app.app_context().push()

    ProPublica.initialize(os.environ['PROPUBLICA_API_KEY'])
    EventRegistry2.initialize(os.environ['EVENT_REGISTRY_API_KEY'])
    GoogleCivicInformation.initialize(os.environ['GOOGLE_CIVIC_INFORMATION_API_KEY'])

    pp = ProPublica()
    er = EventRegistry2()
    gpo = GovernmentPublishingOffice(114)
    cog = CongressGov()
    dhg = DocsHouseGov()
    sg = SenateGov()
    pf = Politifact()
    gci = GoogleCivicInformation()

    Committee.initialize_datasources(pp)
    Congress.initialize_datasources(pp, er, gpo, pf, dhg, sg, gci)
    Congressperson.initialize_datasources(pp, er, gpo, pf, None)
    global cg
    cg = Congress.get_or_create(115)
    Congressperson.initialize_datasources(pp, er, gpo, pf, cg)

    # Create a TwilioCapability object with our Twilio API credentials
    global twilio_phone_number
    twilio_phone_number = os.environ.get('TWILIO_PHONE_NUMBER', None)
    if os.environ.get('TWILIO_AUTH_TOKEN', None) is not None:
        # Allow our users to make outgoing calls with Twilio Client
        account_sid = os.environ['TWILIO_ACCOUNT_SID']
        auth_token = os.environ['TWILIO_AUTH_TOKEN']
        global capability
        capability = TwilioCapability(account_sid, auth_token)
        capability.allow_client_outgoing(os.environ['TWIML_APP_SID'])


if __name__ == "__main__":
    initialize_app(app)

    host = '0.0.0.0'
    if os.environ.get('FLASK_DEBUG', '0') == '1':
        host = '127.0.0.1'
    app.run(host=host, port=os.environ.get('PORT', 5000))

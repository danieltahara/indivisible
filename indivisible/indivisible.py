from flask import (
    Flask,
    render_template,
    request,
    url_for,
)
from flask_bootstrap import Bootstrap
import json

from datasources import propublica
from congress import Congress
from congressperson import Congressperson

app = Flask(__name__)
Bootstrap(app)

propublica.ProPublica.load_api_key()

@app.route('/')
def main():
    return "Hello world"

@app.route('/members/search')
def search_members():
    name = request.args.get('q')
    cg = Congress(115)
    members = cg.search_members(name)

    for member in members:
        member['_url'] = url_for('get_member', id=member['id'])

    return render_template('members_search.html', members=members)

@app.route('/members/<id>')
def get_member(id):
    cp = Congressperson(id)
    return render_template('member.html', data=cp.member)

@app.route('/members/<id>/votes')
def get_votes(id):
    cp = Congressperson(id)
    last_n = int(request.args.get('last', 0))
    votes = cp.get_recent_votes(last_n)
    return render_template('json.html', data=votes)

@app.context_processor
def json_processor():
    def json_pretty(arg):
        return json.dumps(arg, indent=4, separators=(',', ': '))
    return dict(json_pretty=json_pretty)

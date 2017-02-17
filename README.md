# indivisibleguide

A collection of tools to help realize the organizing principles from the Indivisible Guide:
https://www.indivisibleguide.com/, utilizing the ProPublica Data APIs:
https://www.propublica.org/datastore/apis

Candidate focus inspired by: https://www.propublica.org/article/election-databot-sources

## Setup:
* You have python installed on your computer (comes by default), as well as the following libraries:
~~~
sudo apt-get install python-pip
sudo apt-get install python-virtualenv
~~~

* You will need to create and activate a virtualenv for the project as follows:
~~~
virtualenv venv
. venv/bin/activate
~~~

* Then install the dependencies:
~~~
pip install -r requirements.txt
~~~

* Request an API key from ProPublica: https://www.propublica.org/datastore/api/propublica-congress-api
* Request an API key from Event Registry: https://www.eventregistry.org
* Save the API keys in a local file:
~~~
PROPUBLICA_API_KEY="PASTE_API_KEY_HERE"
EVENT_REGISTRY_API_KEY="PASTE_API_KEY_HERE"
~~~

## How to run:
~~~
pushd indivisible
env PYTHONPATH=. CONFIG=/path/to/config FLASK_DEBUG=1 FLASK_APP=indivisible.py flask run
popd
~~~

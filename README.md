# indivisibleguide

A collection of tools to help realize the organizing principles from the [Indivisible Guide](
https://www.indivisibleguide.com/). Data sources include:

1. [ProPublica Data APIs](https://www.propublica.org/datastore/apis)
2. [Event Registry](https://www.eventregistry.org)
3. [U.S. Government Publishing Office](http://memberguide.gpo.gov/)
4. [GovTrack.us](https://www.govtrack.us/)
5. [Politifact](http://www.politifact.com/)

## Setup:
* You have python installed on your computer (comes by default), as well as the following libraries:
On Linux:
~~~
sudo apt-get install python-pip
sudo apt-get install python-virtualenv
~~~
On Mac OSX:
~~~
sudo apt-get install python-pip
sudo pip install virtualenv
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

* Request an API key from [ProPublica](https://www.propublica.org/datastore/api/propublica-congress-api)
* Request an API key from [Event Registry](https://www.eventregistry.org)
* Save the API keys in a local file, along with path to GPO data:
~~~
PROPUBLICA_API_KEY="PASTE_API_KEY_HERE"
EVENT_REGISTRY_API_KEY="PASTE_API_KEY_HERE"
GPO_DATA_PATH="/path/to/data/assets/gpo-114.json"
~~~

## How to run:
~~~
pushd indivisible
env PYTHONPATH=. CONFIG=/path/to/config FLASK_DEBUG=1 FLASK_APP=indivisible.py flask run
popd
~~~

# indivisibleguide

A collection of tools to help realize the organizing principles from the Indivisible Guide:
https://www.indivisibleguide.com/, utilizing the ProPublica Data APIs:
https://www.propublica.org/datastore/apis

Candidate focus inspired by: https://www.propublica.org/article/election-databot-sources

## Prerequisites:
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

* Then install the following:
~~~
pip install requests
pip install us
pip install Flask
pip install flask-bootstrap
~~~

* Request an API key from ProPublica: https://www.propublica.org/datastore/api/propublica-congress-api
* Save the API key in a local file named ".api":
~~~
echo "PASTE_API_KEY_HERE" > .api
~~~

## How to use:
~~~
env FLASK_DEBUG=1 FLASK_APP=indivisible.py flask run
~~~

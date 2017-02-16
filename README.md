# indivisibleguide

A collection of tools to help realize the organizing principles from the Indivisible Guide:
https://www.indivisibleguide.com/, utilizing the ProPublica Data APIs:
https://www.propublica.org/datastore/apis

Candidate focus inspired by: https://www.propublica.org/article/election-databot-sources

## Pre-requisites:
* You have python installed on your computer (comes by default), as well as the following libraries:
~~~
sudo apt-get install python-pip
sudo pip install requests
sudo pip install us
~~~

* Request an API key from ProPublica: https://www.propublica.org/datastore/api/propublica-congress-api
* Save the API key in a local file named ".api":
~~~
cat "PASTE_API_KEY_HERE" > .api
~~~

## How to use:
~~~
python indivisible.py
~~~

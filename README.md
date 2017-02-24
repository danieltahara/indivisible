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
On Mac OSX (with [Homebrew](https://brew.sh/)):
~~~
brew install python-pip
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
* [Optional] Request credentials from [Twilio](https://www.twilio.com/) and a phone number and [application sid](https://www.twilio.com/console/voice/dev-tools/twiml-apps):
* Save the API keys in a local file, along with path to GPO data:
~~~
PROPUBLICA_API_KEY="PASTE_API_KEY_HERE"
EVENT_REGISTRY_API_KEY="PASTE_API_KEY_HERE"
...
GPO_DATA_PATH="/path/to/data/assets/gpo-114.json"
~~~

* Install DB of choice.
~~~
sudo apt-get install mysql-server
sudo mysql_secure_installation
mysqld --initialize
~~~

* Add database URI to configs:
~~~
DB_ADDR="mysql+pymysql://USER:PASSWORD@localhost/indivisible"
~~~

* Initialize DB:
~~~
env $(cat indivisible.cfg | xargs) python
from indivisible.models.database import init_db
init_db()
~~~

## How to run:
~~~
export FLASK_DEBUG=1
env $(cat indivisible.cfg | xargs) python indivisible/indivisible.py
~~~

## Hosting your own public server:
* Set up an Ubuntu VPS ala [Digital Ocean](https://www.digitalocean.com/)
* Run the following to set up Apache:
~~~
sudo apt-get update
sudo apt-get install apache2 libapache2-mod-wsgi python-dev
sudo a2enmod wsgi
~~~
* Clone your repo into /var/www:
~~~
cd /var/wwww
git clone git@github.com:danieltahara/indivisible.git
~~~
* Repeat setup steps above.
* Add an app.conf as per Digital Ocean
  [instructions](https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps):
~~~
sudo vim /etc/apache2/sites-available/indivisible.conf
~~~
~~~
WSGIPythonHome /var/www/indivisible/venv/bin
WSGIPythonPath /var/www/indivisible/venv/lib/python2.7/site-packages

<VirtualHost *:80>
    ServerName YOUR_IP_ADDR_OR_DOMAIN
    ServerAdmin YOUR_EMAIL_ADDR
    WSGIScriptAlias / /var/www/indivisible/indivisible.wsgi
    WSGIScriptReloading On
    <Directory /var/www/indivisible/indivisible/>
        Order allow,deny
        Allow from all
    </Directory>
    Alias /static /var/www/indivisible/indivisible/static
    <Directory /var/www/indivisible/indivisible/static/>
        Order allow,deny
        Allow from all
    </Directory>
    ErrorLog
    ${APACHE_LOG_DIR}/error.log
    LogLevel warn
    CustomLog
    ${APACHE_LOG_DIR}/access.log
    combined
</VirtualHost>
~~~
* Add a .wsgi file:
~~~
sudo vim /var/www/indivisible/indivisible.wsgi
~~~
~~~
import os
import sys
import logging

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/indivisible/")

# Add your keys here.
os.environ['PROPUBLICA_API_KEY'] = "XXXX"

from indivisible import app as application
~~~
* Enable Virtual Host:
~~~
sudo a2ensite indivisible
~~~
* Restart apache
~~~
sudo service apache2 restart
~~~
* Optionally install SSL certs using [Let's Encrypt](https://certbot.eff.org/#ubuntuxenial-apache):
~~~
sudo apt-get install python-letsencrypt-apache
letsencrypt apache
~~~

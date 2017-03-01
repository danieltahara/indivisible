from bs4 import BeautifulSoup
import requests
from urlparse import urljoin
import urllib
import urllib2
from xml.etree import ElementTree


class BeautifulSoupSource(object):

    def __init__(self, base_url):
        self.base_url = base_url

    def _get(self, path, params={}, headers={}):
        url = urljoin(self.base_url, path)
        if len(params) > 0:
            url = url % urllib.urlencode(params)
        print url
        request = urllib2.Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0')
        opener = urllib2.build_opener()
        soup = BeautifulSoup(opener.open(request), "html.parser")
        return soup

class XMLSource(object):

    def __init__(self, base_url):
        self.base_url = base_url

    def _get(self, path, params={}, headers={}):
        url = urljoin(self.base_url, path)
        if len(params) > 0:
            url = url % urllib.urlencode(params)
        print url
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            return None
        else:
            return ElementTree.fromstring(resp.text)


class JSONSource(object):

    def __init__(self, base_url):
        self.base_url = base_url

    def _get(self, path, params={}, headers={}):
        url = urljoin(self.base_url, path)
        if len(params) > 0:
            url = url % urllib.urlencode(params)
        print url
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            return None
        else:
            results = resp.json()
            return results

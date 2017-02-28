from bs4 import BeautifulSoup
from urlparse import urljoin
import urllib
import urllib2


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

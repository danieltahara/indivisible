from bs4 import BeautifulSoup
import re
from urlparse import urljoin
import urllib2


class CongressGov(object):
    @staticmethod
    def get_base_url():
        return "https://www.congress.gov/resources/display/content/"

    def get_hot_bills(self):
        """
        Get list of most viewed bills from last week

        @return: list of dicts of the form: {
            'congress': which # congress,
            'number': bill #,
            'title': short text,
        }

        """
        soup = self._get("Most-Viewed+Bills")
        table = soup.find("table", class_="confluenceTable")
        if table:
            to_ret = []
            rows = table.findAll("tr")
            for row in rows:
                bills = {}
                columns = row.findAll("td")
                if columns and len(columns) == 3:
                    bill = {}
                    bill['congress'] = re.search(r"\[(\d+)\w+\]", columns[1].contents[1]).groups()[0]
                    bill['congress'] = int(bill['congress'])
                    bill['number'] = columns[1].find("a").contents[0].strip()
                    bill['title'] = re.sub(r"\"", "", columns[2].contents[0])
                    to_ret.append(bill)
            return to_ret

    def _get(self, path, params={}, headers={}):
        url = urljoin(self.get_base_url(), path)
        if len(params) > 0:
            url = url % urllib2.urlencode(params)
        print url
        request = urllib2.Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0')
        opener = urllib2.build_opener()
        soup = BeautifulSoup(opener.open(request), "html.parser")
        return soup

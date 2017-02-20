from bs4 import BeautifulSoup
import re
from urlparse import urljoin
import urllib


class DocsHouseGov(object):
    @staticmethod
    def get_base_url():
        return "http://docs.house.gov/"

    def get_events(self, date):
        """
        Get list of Committee events from calendar.

        @param date: datetime.date
        @return: list of dicts of the form: {
            'name': name of event,
            'url': event url,
            'date': date event occurs,
            'time': time event will occur,
            'committee': commitee name,
            'subcommittee': (optional) subcommittee,
        }

        """
        params = {
            'DayID': date.strftime("%m%d%Y"),
        }
        path = "Committee/Calendar/ByDay.aspx?%s"
        soup = self._get(path, params)
        table = soup.find("table", {"id": "MainContent_GridViewMeetings"})
        if table:
            to_ret = []
            rows = table.findAll("tr")
            for row in rows:
                event = {}
                columns = row.findAll("td")
                if columns and len(columns) == 3:
                    event['date'] = date.strftime("%m-%d-%Y")
                    event['time'] = columns[1].find("span").contents[0].strip()
                    event['committee'] = columns[0].find("span").contents[0].strip()
                    a = columns[0].find("a")
                    event['name'] = a.contents[0].strip()
                    event['url'] = urljoin(
                        self.get_base_url(),
                        "Committee/Calendar/{}".format(a['href']))

                    committees = re.findall(r'[^()]+', event['committee'])
                    if len(committees) == 2:
                        event['subcommittee'] = committees[0].strip()
                        event['committee'] = committees[1].strip()
                    to_ret.append(event)
            return to_ret
        else:
            return None

    def _get(self, path, params={}, headers={}):
        url = urljoin(self.get_base_url(), path)
        soup = BeautifulSoup(urllib.urlopen(url % urllib.urlencode(params)),
                             "html.parser")
        return soup

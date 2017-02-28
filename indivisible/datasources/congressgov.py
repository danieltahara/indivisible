import re

from beautifulsoupsource import BeautifulSoupSource


class CongressGov(BeautifulSoupSource):

    def __init__(self):
        super(CongressGov, self).__init__(
            "https://www.congress.gov/resources/display/content/")

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
                    bill['congress'] = re.search(r"\[(\d+)\w+\]",
                                                 columns[1].contents[1]).groups()[0]
                    bill['congress'] = int(bill['congress'])
                    bill['number'] = columns[1].find("a").contents[0].strip()
                    bill['title'] = re.sub(r"\"", "", columns[2].contents[0])
                    to_ret.append(bill)
            return to_ret

from unidecode import unidecode

from base import JSONSource

class Politifact(JSONSource):

    def __init__(self):
        super(Politifact, self).__init__("http://www.politifact.com/api/")

    def get_statements_by_person(self, first_name, last_name, limit=0):
        """
        Get statements and ratings by name.

        @param first_name: of MoC
        @param last_name: of MoC
        @param limit: optional limit
        @return: statements
        """
        limit = limit if limit > 0 else 10
        results = self._get(
            "statements/truth-o-meter/people/{first_name}-{last_name}/"
            "json/?n={limit}".format(first_name=unidecode(first_name.lower()),
                                     last_name=unidecode(last_name.lower()),
                                     limit=limit))
        return results if results else []

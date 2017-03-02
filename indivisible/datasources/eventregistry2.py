from eventregistry import EventRegistry
from eventregistry import QueryEvents
from eventregistry import RequestEventsInfo


class EventRegistry2(EventRegistry):
    """
    Wrapper around EventRegistry API
    """

    @classmethod
    def initialize(cls, key):
        cls.key = key

    def __init__(self):
        super(EventRegistry2, self).__init__(
            host="http://eventregistry.org", apiKey=self.key)

    def get_events(self, thing, limit=0):
        query = QueryEvents(lang='eng')
        concept_uri = self.getConceptUri(thing)
        query.addKeyword(thing)
        if concept_uri:
            query.addConcept(concept_uri)

        count = limit if limit > 0 else 30
        requested_result = RequestEventsInfo(
            page=1, count=count, sortBy="date", sortByAsc=False)
        query.addRequestedResult(requested_result)

        result = self.execQuery(query)
        if 'error' in result:
            print result['error']
            return []
        else:
            if concept_uri:
                to_ret = []
                for res in result['events']['results']:
                    for c in res['concepts']:
                        if c['uri'] == concept_uri and c['score'] >= 50:
                            to_ret.append(res)
                return to_ret
            else:
                return result['events']['results']

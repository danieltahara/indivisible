import requests
from urlparse import urljoin
from eventregistry import (
    EventRegistry,
    QueryEvents,
    RequestEventsInfo,
)


class EventRegistry2(EventRegistry):
    """
    Wrapper around EventRegistry API
    """

    def __init__(self, key):
        self.key = key
        super(EventRegistry2, self).__init__(
            host="http://eventregistry.org", apiKey=key)

    def get_events(self, thing, limit=0):
        query = QueryEvents(lang='eng')
        concept_uri = self.getConceptUri(thing)
        if concept_uri:
            query.addConcept(concept_uri)
        else:
            query.addKeyword(thing)

        count = limit if limit > 0 else 30
        requested_result = RequestEventsInfo(
            page=1, count=count, sortBy="date", sortByAsc=False)
        query.addRequestedResult(requested_result)

        result = self.execQuery(query)
        if 'error' in result:
            print result['error']
            return []
        else:
            # TODO: paging
            return result['events']['results']

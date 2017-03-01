from datetime import datetime

from base import XMLSource


class SenateGov(XMLSource):

    def __init__(self):
        super(SenateGov, self).__init__(
            "https://www.senate.gov/general/committee_schedules/hearings.xml")

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
        baseTree = self._get('')
        if baseTree is None:
            return []
        trees = baseTree.findall("meeting")
        events = []
        for tree in trees:
            committee = tree.find('committee').text
            if committee and len(committee) > 0:
                event = {}
                event['committee'] = "Committee on {}".format(committee)
                date = datetime.strptime(tree.find('date').text, '%d-%b-%Y %I:%M %p')
                event['date'] = date.strftime('%m-%d-%Y')
                event['time'] = tree.find('time').text
                event['name'] = tree.find('matter').text
                events.append(event)
        return events

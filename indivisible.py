import congressperson
from datasources import propublica
import pprint

if __name__ == '__main__':
    propublica.ProPublica.load_api_key()

    cp = congressperson.Congressperson.by_name(115, "kamala harris")
    pprint.pprint(cp.get_recent_votes(5))

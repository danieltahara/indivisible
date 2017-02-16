import propublica
import congress

def test_get_members():
    cg = congress.Congress(115)
    cg.get_members(cg.SENATE)

def test_search_members():
    cg = congress.Congress(115)

    # Senate
    print cg.search_members("schumer")
    # Full name
    print cg.search_members("charles schumer")
    # Unknown
    print cg.search_members("foobarbaz")
    # House
    print cg.search_members("lowey")
    # Multiple results
    print cg.search_members("smith")


if __name__ == '__main__':
    propublica.ProPublica.load_api_key()

    test_get_members()
    test_search_members()

import unittest

import propublica
import congress

class TestCongress(unittest.TestCase):
    def setUp(self):
        self.cg = congress.Congress(115)

    def test_get_members(self):
        members = self.cg.get_members(self.cg.SENATE)
        self.assertEqual(len(members), 101) # Luther Strange replaced Sessions

    def test_search_members(self):
        # House
        self.assertEqual(len(self.cg.search_members("lowey")), 1)

        # Senate
        schumer = self.cg.search_members("schumer")[0]
        schumerFull = self.cg.search_members("charles schumer")[0]
        self.assertEqual(schumer, schumerFull)

        # Unknown
        self.assertEqual(len(self.cg.search_members("foobarbaz")), 0)

        # Multiple results
        self.assertEqual(len(self.cg.search_members("smith")), 5)

if __name__ == '__main__':
    propublica.ProPublica.load_api_key()
    unittest.main()

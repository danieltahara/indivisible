import unittest

import congressperson
from datasources import propublica

class TestCongress(unittest.TestCase):
    def setUp(self):
        self.cp = congressperson.Congressperson("H001075")

    def test_get_name(self):
        self.assertEqual(self.cp.get_name(), "Kamala Harris")

    def test_get_recent_votes(self):
        # Doesn't error
        self.cp.get_recent_votes()
        self.assertEqual(len(self.cp.get_recent_votes(10)), 10)

if __name__ == '__main__':
    propublica.ProPublica.load_api_key()
    unittest.main()

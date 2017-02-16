import unittest

import propublica

class TestPropublica(unittest.TestCase):
    def setUp(self):
        self.pp = propublica.ProPublica()

    def test_get_member_by_id(self):
        member = self.pp.get_member_by_id("A000360")
        self.assertEqual(member['first_name'], "Lamar")

        member = self.pp.get_member_by_id("FOOBARBAZ")
        self.assertIsNone(member)


if __name__ == '__main__':
    propublica.ProPublica.load_api_key()
    unittest.main()

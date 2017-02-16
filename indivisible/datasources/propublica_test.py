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

    def test_get_members_by_location(self):
        members = self.pp.get_members_by_location("house", "ny", 17)
        self.assertEqual(len(members), 1)
        member = members[0]
        self.assertEqual(member['name'], "Nita M. Lowey")

        # Converts state name
        members = self.pp.get_members_by_location("house", "new york", 17)
        self.assertEqual(len(members), 1)
        member = members[0]
        self.assertEqual(member['name'], "Nita M. Lowey")

        # Gets senators
        members = self.pp.get_members_by_location("senate", "ny")
        self.assertEqual(len(members), 2)
        member = members[0]
        self.assertEqual(member['name'], "Kirsten E. Gillibrand")

        # District doesn't matter for senate
        members = self.pp.get_members_by_location("senate", "ny", 201293812810)
        self.assertEqual(len(members), 2)


if __name__ == '__main__':
    propublica.ProPublica.load_api_key()
    unittest.main()

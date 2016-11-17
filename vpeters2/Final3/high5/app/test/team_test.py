import unittest
import os
import sys
sys.path.append('..')
from app.team import *
from app.user import *
from app import create_static_team

"""
Class to test tthe team and user classes and that the methods function properly to update both.
"""
class MyTeamTest(unittest.TestCase):
    #Function to setup for the rest of the tests. Creates the test team from the UIUC Girls Running Team
    def setUp(self):
        super(MyTeamTest, self).setUp()
        self.team = create_static_team.create_running_team()

    #Tests for adding a member to the team. Makes sure that a User is created correctly and added to members dict
    def test_add_member(self):
        self.assertEqual(len(self.team.get_members()), 8)
        self.team.add_member(User("NewGuy", "Joe Shmoh", "joe2@illinois.edu", "abc456"))
        self.assertEqual(len(self.team.get_members()), 9)
        new_guy = self.team.get_members()["NewGuy"]
        self.assertEqual(new_guy.get_name(), "Joe Shmoh")
        self.assertEqual(new_guy.get_email(), "joe2@illinois.edu")
        self.assertEqual(new_guy.get_password(), "abc456")
        self.assertEqual(len(new_guy.get_high5s()), 0)
        self.assertEqual(new_guy.get_high5_score(), 0)

    #Test that the team is created with the correct name and admin.
    def test_team_attrs(self):
        self.assertEqual(self.team.get_admin(), "VPeterson")
        self.assertEqual(self.team.get_name(), "UIUC Girls Running Club")

    #Tests for the team calculations of top scorers and high5 receivers. Make sure the order is returned correctly and
    #the right values are associated with the right user names.
    def test_team_metrics(self):
        top_scorers = self.team.get_top_scorers()
        top_high5ers = self.team.get_top_high5s()
        self.assertEqual(len(top_scorers), 3)
        self.assertEqual(len(top_high5ers), 3)
        self.assertEqual(top_scorers[0][1], 7)
        self.assertEqual(top_scorers[2][0], "Josie1")
        self.assertEqual(top_high5ers[0][0], "VPeterson")
        self.assertEqual(top_high5ers[0][1], 3)

    #Tests that updating the high5s for a team updates the top scorers and top high5 receivers.
    #Makes sure that making a new high scorer and reciever updates the top three lists correctly.
    def test_team_metrics_add_high5(self):
        self.team.add_high5(High5("Hunter1994", "RaychHeinz", "Sam made treats for the pasta party", 5))
        self.team.add_high5(High5("Hunter1994", "RaychHeinz", "Sam gave me a ride home", 1))
        self.team.add_high5(High5("Hunter1994", "RaychHeinz", "Sam is the best", 1))
        top_scorers = self.team.get_top_scorers()
        top_high5ers = self.team.get_top_high5s()
        self.assertEqual(len(top_scorers), 3)
        self.assertEqual(len(top_high5ers), 3)
        self.assertEqual(top_scorers[0][1], 12)
        self.assertEqual(top_scorers[0][0], "Hunter1994")
        self.assertEqual(top_high5ers[0][0], "Hunter1994")
        self.assertEqual(top_high5ers[0][1], 4)
        self.assertEqual(top_high5ers[1][0], "VPeterson")
        self.assertEqual(top_high5ers[1][1], 3)

if __name__ == '__main__':
    unittest.main()


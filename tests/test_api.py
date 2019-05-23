import unittest
from zeep import CachingClient
from azlegapiclient.AzLegApiClient import AzLegApiClient

class TestApiClient(unittest.TestCase):

    def test_api_client(self):
        api = AzLegApiClient(username="DHoover", password="B23da@d8s")
        self.assertIsInstance(api.client, CachingClient)


class TestSessionByID(unittest.TestCase):
    
    def setUp(self):
        
        self.api = AzLegApiClient(username="DHoover", password="B23da@d8s")


    def test_session_by_id(self):

        session = self.api.session_by_id(121)

        self.assertEqual(
            session,
            {
                "session_id": "121",
                "session_full_name": "Fifty-fourth Legislature - First Regular Session",
                "legislature": "54",
                "session": "1R",
                "legislation_Year": "2019",
                "session_start_date": None,
                "sine_die_sate": None,
            },
        )

if __name__ == "__main__":
    unittest.main()

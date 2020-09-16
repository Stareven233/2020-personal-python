import unittest
import os
from GHAnalysis import Data


class TestGHA(unittest.TestCase):

    def setUp(self):
        self.data = Data()
        self.assertIsInstance(self.data, Data)

    def tearDown(self):
        pass

    def test_init(self):
        self.data.init('./data')
        # 此时数据为 4份2020-01-01-15.json + 1份2015-01-01-15.json
        file_exist = all((os.path.exists(f'{i}.pkl') for i in range(3)))
        self.assertTrue(file_exist)

    def test_user_event(self):
        self.data.load()
        num = self.data.user_events.get('waleko', {}).get('PushEvent', 0)
        self.assertEqual(num, 8)

    def test_repo_event(self):
        self.data.load()
        num = self.data.repo_events.get('katzer/cordova-plugin-background-mode', {}).get('PushEvent', 0)
        self.assertEqual(num, 0)

    def test_user_repo_event(self):
        self.data.load()
        num = self.data.user_repo_events.get('cdupuis', {}).get('atomist/automation-client', {}).get('PushEvent', 0)
        self.assertEqual(num, 4)


if __name__ == '__main__':
    unittest.main()

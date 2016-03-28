import unittest
import os

# Add parent dir to path to import utils
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                '..')))
from test_cases import utils
import sdk


class CRMCampaign(unittest.TestCase):

    def setUp(self):
        account_id = 832496
        self.account = sdk.Account.retrieve(id=account_id)
        data = {
            'name': 'API Test Campaign Name'
        }
        self.obj = self.account.crm_campaigns.create(data=data)

    def tearDown(self):
        self.obj.delete()

    def test_list_object(self):
        objects = self.account.crm_campaigns.all()
        # assert properties
        if objects:
            obj = objects[0]
            self.assertEqual(obj.type, 'Campaign')
            self.assertTrue('raw' in obj)

    def test_read_object(self):
        obj = self.account.crm_campaigns.retrieve(self.obj.id)
        # assert Campaign properties
        self.assertEqual(obj.id, self.obj.id)
        self.assertEqual(obj.type, 'Campaign')
        self.assertTrue('raw' in obj)

        self.assertTrue('created' in obj)
        self.assertTrue('modified' in obj)
        self.assertTrue('description' in obj)

    def test_update_object(self):
        obj = self.obj
        obj.description = 'test campaign description'
        obj.save()
        self.assertEqual('test campaign description', obj.description)


def test_cases():
    return [CRMCampaign]

if __name__ == '__main__':
    suite = utils.create_suite(test_cases())
    unittest.TextTestRunner(verbosity=2).run(suite)

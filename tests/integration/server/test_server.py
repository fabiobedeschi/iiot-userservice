import unittest
from os import environ

from server.app import app
from ..fixtures import Fixtures


class TestServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        app.config['TESTING'] = True
        environ['DISABLE_UPDATES'] = 'true'
        cls.client = app.test_client()
        cls.fixtures = Fixtures()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fixtures.clean_database()
        cls.fixtures.close_connection()

    def setUp(self) -> None:
        self.fixtures.clean_database()

    def test_post_user_successfully(self):
        uuid = 'f9b358cc522a4cb7a60c27da6fbed8f1'

        response = self.client.post(f'/users/{uuid}', json={'delta': 42, 'area': 'ABC'})
        user = self.fixtures.find_user(uuid)

        self.assertEqual(201, response.status_code)
        self.assertIsNotNone(user)
        self.assertEqual(42, user['delta'])
        self.assertEqual('ABC', user['area'])

    def test_post_user_already_exists(self):
        uuid = 'f9b358cc522a4cb7a60c27da6fbed8f1'
        self.fixtures.insert_user(uuid, delta=0, area='XYZ')

        response = self.client.post(f'/users/{uuid}', json={'delta': 42, 'area': 'ABC'})
        user = self.fixtures.find_user(uuid)

        self.assertEqual(409, response.status_code)
        self.assertIsNone(response.json)
        self.assertIsNotNone(user)
        self.assertEqual(0, user['delta'])
        self.assertEqual('XYZ', user['area'])

    def test_patch_user_successfully(self):
        uuid = 'f9b358cc522a4cb7a60c27da6fbed8f1'
        self.fixtures.insert_user(uuid, delta=0, area='XYZ')

        response = self.client.patch(f'/users/{uuid}', json={'delta': 42, 'area': 'ABC'})
        user = self.fixtures.find_user(uuid)

        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(user)
        self.assertEqual(42, user['delta'])
        self.assertEqual('ABC', user['area'])

    def test_patch_user_fail_if_user_does_not_exists(self):
        uuid = 'f9b358cc522a4cb7a60c27da6fbed8f1'
        ne_uuid = 'nonexistent-user-uuid'
        self.fixtures.insert_user(uuid, delta=0, area='XYZ')

        response = self.client.patch(f'/users/{ne_uuid}', json={'delta': 42, 'area': 'ABC'})
        user = self.fixtures.find_user(uuid)
        ne_user = self.fixtures.find_user(ne_uuid)

        self.assertEqual(404, response.status_code)
        self.assertIsNone(ne_user)
        self.assertIsNotNone(user)
        self.assertEqual(0, user['delta'])
        self.assertEqual('XYZ', user['area'])

    def test_delete_user_successfully(self):
        uuid = 'f9b358cc522a4cb7a60c27da6fbed8f1'
        self.fixtures.insert_user(uuid, delta=0, area='XYZ')

        response = self.client.delete(f'/users/{uuid}')
        user = self.fixtures.find_user(uuid)

        self.assertEqual(200, response.status_code)
        self.assertIsNone(user)

    def test_delete_user_fail_if_user_does_not_exists(self):
        uuid = 'f9b358cc522a4cb7a60c27da6fbed8f1'
        ne_uuid = 'nonexistent-user-uuid'
        self.fixtures.insert_user(uuid, delta=0, area='XYZ')

        response = self.client.delete(f'/users/{ne_uuid}')
        user = self.fixtures.find_user(uuid)
        ne_user = self.fixtures.find_user(ne_uuid)

        self.assertEqual(404, response.status_code)
        self.assertIsNone(ne_user)
        self.assertIsNotNone(user)
        self.assertEqual(0, user['delta'])
        self.assertEqual('XYZ', user['area'])

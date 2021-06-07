import unittest
import unittest.mock

from server.src.database import Database
from server.src.server import UserServer


class TestServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.db = unittest.mock.create_autospec(Database)
        cls.server = UserServer(db=cls.db, send_updates=False)

    def test_find_all_users_successfully(self):
        self.db.find_all_users.return_value = expected_result = [
            {'uuid': '668e2987956a4943a9e6a2c77e56dc17'},
            {'uuid': '86c822ee6f9a4f69b2f57a9c8702e4a2'},
            {'uuid': '94565bc0210546f6990bce590d94be39'}
        ]
        result, code = self.server.find_all_users()

        self.db.find_all_users.assert_called_with()
        self.assertEqual(expected_result, result)
        self.assertEqual(200, code)

    def test_find_users_by_area_successfully(self):
        self.db.find_users_by_area.return_value = expected_result = [
            {'uuid': '86c822ee6f9a4f69b2f57a9c8702e4a2'},
            {'uuid': '94565bc0210546f6990bce590d94be39'}
        ]
        result, code = self.server.find_all_users(data={'area': 'area_name'})

        self.db.find_users_by_area.assert_called_with(area='area_name')
        self.assertEqual(expected_result, result)
        self.assertEqual(200, code)

    def test_find_user_successfully(self):
        self.db.find_user.return_value = expected_result = {
            'uuid': '668e2987956a4943a9e6a2c77e56dc17'
        }
        result, code = self.server.find_user(uuid='668e2987956a4943a9e6a2c77e56dc17')

        self.db.find_user.assert_called_with(uuid='668e2987956a4943a9e6a2c77e56dc17')
        self.assertEqual(expected_result, result)
        self.assertEqual(200, code)

    def test_find_user_not_exists(self):
        self.db.find_user.return_value = expected_result = None
        result, code = self.server.find_user(uuid='668e2987956a4943a9e6a2c77e56dc17')

        self.db.find_user.assert_called_with(uuid='668e2987956a4943a9e6a2c77e56dc17')
        self.assertEqual(expected_result, result)
        self.assertEqual(404, code)

    def test_update_user_successfully(self):
        self.db.update_user.return_value = expected_result = {
            'uuid': '668e2987956a4943a9e6a2c77e56dc17',
            'delta': 1200,
            'area': 'area_name'
        }
        result, code = self.server.update_user(
            uuid='668e2987956a4943a9e6a2c77e56dc17',
            data={'delta': 100, 'area': 'area_name'}
        )

        self.db.update_user.assert_called_with(
            uuid='668e2987956a4943a9e6a2c77e56dc17',
            delta=100,
            area='area_name'
        )
        self.assertEqual(expected_result, result)
        self.assertEqual(200, code)

    def test_update_user_not_exists(self):
        self.db.update_user.return_value = expected_result = None
        result, code = self.server.update_user(
            uuid='668e2987956a4943a9e6a2c77e56dc17',
            data={'delta': 100, 'area': 'area_name'}
        )

        self.db.update_user.assert_called_with(
            uuid='668e2987956a4943a9e6a2c77e56dc17',
            delta=100,
            area='area_name'
        )
        self.assertEqual(expected_result, result)
        self.assertEqual(404, code)

    def test_create_user_successfully(self):
        self.db.find_user.return_value = None
        self.db.insert_user.return_value = expected_result = {
            'uuid': '668e2987956a4943a9e6a2c77e56dc17',
            'delta': 100,
            'area': 'area_name'
        }
        result, code = self.server.create_user(
            uuid='668e2987956a4943a9e6a2c77e56dc17',
            data={'delta': 100, 'area': 'area_name'}
        )
        self.db.insert_user.assert_called_with(
            uuid='668e2987956a4943a9e6a2c77e56dc17',
            delta=100,
            area='area_name'
        )
        self.assertEqual(expected_result, result)
        self.assertEqual(201, code)

    def test_create_user_already_exists(self):
        self.db.find_user.return_value = {
            'uuid': '668e2987956a4943a9e6a2c77e56dc17',
            'delta': 100,
            'area': 'area_name'
        }
        self.db.insert_user.return_value = expected_result = None
        result, code = self.server.create_user(
            uuid='668e2987956a4943a9e6a2c77e56dc17',
            data={'delta': 100, 'area': 'area_name'}
        )
        self.assertEqual(expected_result, result)
        self.assertEqual(409, code)

    def test_remove_user_successfully(self):
        self.db.find_user.return_value = self.db.delete_user.return_value = expected_result = {
            'uuid': '668e2987956a4943a9e6a2c77e56dc17',
            'delta': 100,
            'area': 'area_name'
        }
        result, code = self.server.remove_user(uuid='668e2987956a4943a9e6a2c77e56dc17')
        self.assertEqual(expected_result, result)
        self.assertEqual(200, code)

    def test_remove_user_not_exists(self):
        self.db.find_user.return_value = self.db.delete_user.return_value = expected_result = None
        result, code = self.server.remove_user(uuid='668e2987956a4943a9e6a2c77e56dc17')
        self.assertEqual(expected_result, result)
        self.assertEqual(404, code)


if __name__ == '__main__':
    unittest.main()

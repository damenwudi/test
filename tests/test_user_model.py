import unittest
from app.models import User

class UserModelTestCase(unittest.TestCase):
    def test_password_setter(self):
        u = User(password = 'cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_check(self):
        u = User(password='cat')
        self.assertTrue(u.check_pass('cat'))
        #self.assertFalse(u.check_pass('cat'))

    def test_check_hash(self):
        u = User(password='cat')
        u1 = User(password='cat')
        self.assertTrue(u.password_hash != u1.password_hash)
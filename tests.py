import unittest
from app import create_app, db
from app.models import User, Request
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_credits_default(self):
        u = User(username='john', email='john@example.com')
        db.session.add(u)
        db.session.commit()
        self.assertEqual(u.credits, 0)

    def test_request_creation(self):
        u = User(username='john', email='john@example.com')
        db.session.add(u)
        db.session.commit()
        
        req = Request(author=u, product_type='PVC', quantity='100 Ton')
        db.session.add(req)
        db.session.commit()
        
        self.assertEqual(req.author.username, 'john')
        self.assertEqual(u.requests.count(), 1)

if __name__ == '__main__':
    unittest.main(verbosity=2)

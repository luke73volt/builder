import unittest
from app import create_app, db
from app.models import User, Role, Medication, Transaction
from config import TestConfig
from datetime import datetime, timedelta

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

    def test_roles(self):
        r_admin = Role(name='admin')
        r_pharma = Role(name='pharmacist')
        db.session.add(r_admin)
        db.session.add(r_pharma)
        db.session.commit()

        u1 = User(username='john', email='john@example.com')
        u1.roles.append(r_admin)
        u1.roles.append(r_pharma)
        db.session.add(u1)
        db.session.commit()

        self.assertEqual(len(u1.roles), 2)

class MedicationModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_medication_creation(self):
        m = Medication(name='Aspirin', description='Pain reliever', quantity=100, min_stock_level=20, aic_code='12345')
        db.session.add(m)
        db.session.commit()
        self.assertEqual(Medication.query.count(), 1)
        self.assertEqual(Medication.query.first().name, 'Aspirin')

class RoutesCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        # Create a user and role for testing protected routes
        r_admin = Role(name='admin')
        db.session.add(r_admin)
        db.session.commit()
        u = User(username='testuser', email='test@example.com')
        u.set_password('password')
        u.roles.append(r_admin)
        db.session.add(u)
        db.session.commit()


    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_index_redirects_for_anonymous(self):
        response = self.client.get('/index')
        self.assertEqual(response.status_code, 302) # Should redirect to login

    def test_login_and_logout(self):
        response = self.client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'password'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Hello, testuser!', response.data)

        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign In', response.data) # Should be back to login page


if __name__ == '__main__':
    unittest.main(verbosity=2)

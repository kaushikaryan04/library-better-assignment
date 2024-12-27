import unittest
from app import app, db, Member

class MemberTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        cls.client = app.test_client()

        with app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_member(self):
        """Test creating a new member."""
        response = self.client.post('/members', json={
            'name': 'John Doe',
            'email': 'john@example.com'
        })
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['name'], 'John Doe')
        self.assertEqual(data['email'], 'john@example.com')

    def test_get_members(self):
        """Test retrieving all members."""
        # Add a member first
        self.client.post('/members', json={
            'name': 'Jane Smith',
            'email': 'jane@example.com'
        })

        response = self.client.get('/members')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Jane Smith')

    def test_get_member_by_id(self):
        """Test retrieving a single member by ID."""
        # Add a member first
        create_response = self.client.post('/members', json={
            'name': 'Alice Brown',
            'email': 'alice@example.com'
        })
        member_id = create_response.get_json()['id']

        response = self.client.get(f'/members/{member_id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['name'], 'Alice Brown')

    def test_update_member(self):
        """Test updating an existing member."""
        # Add a member first
        create_response = self.client.post('/members', json={
            'name': 'Charlie Green',
            'email': 'charlie@example.com'
        })
        member_id = create_response.get_json()['id']

        # Update the member
        update_response = self.client.put(f'/members/{member_id}', json={
            'name': 'Charlie Updated',
            'email': 'charlie.updated@example.com'
        })
        self.assertEqual(update_response.status_code, 200)
        updated_data = update_response.get_json()
        self.assertEqual(updated_data['name'], 'Charlie Updated')
        self.assertEqual(updated_data['email'], 'charlie.updated@example.com')

    def test_delete_member(self):
        """Test deleting a member."""
        # Add a member first
        create_response = self.client.post('/members', json={
            'name': 'David Black',
            'email': 'david@example.com'
        })
        member_id = create_response.get_json()['id']

        # Delete the member
        delete_response = self.client.delete(f'/members/{member_id}')
        self.assertEqual(delete_response.status_code, 200)

        # Ensure member is deleted
        get_response = self.client.get(f'/members/{member_id}')
        self.assertEqual(get_response.status_code, 404)

    def test_create_member_with_duplicate_email(self):
        """Test creating a member with a duplicate email."""
        # Add a member first
        self.client.post('/members', json={
            'name': 'Eve White',
            'email': 'eve@example.com'
        })

        # Attempt to add another member with the same email
        response = self.client.post('/members', json={
            'name': 'Duplicate Eve',
            'email': 'eve@example.com'
        })
        self.assertEqual(response.status_code, 500)  # Should fail due to unique constraint

if __name__ == '__main__':
    unittest.main()

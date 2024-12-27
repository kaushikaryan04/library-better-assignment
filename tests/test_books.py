import unittest
from app import app, db, Book

class TestBooksAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_book(self):
        response = self.app.post('/books', json={"title": "Book 1", "author": "Author 1", "year": 2020})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()['title'], 'Book 1')

    def test_get_books(self):
        self.app.post('/books', json={"title": "Book 1", "author": "Author 1", "year": 2020})
        response = self.app.get('/books')
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.get_json()), 0)

if __name__ == '__main__':
    unittest.main()

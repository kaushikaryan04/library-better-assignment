from flask import Flask, request, jsonify
from models import db, Book, Member
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



migrate = Migrate(app, db)
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()
    title = data.get('title')
    author = data.get('author')
    year = data.get('year')

    if not title or not author or not year:
        return jsonify({"error": "Missing required fields"}), 400

    book = Book(title=title, author=author, year=year)
    db.session.add(book)
    db.session.commit()
    return jsonify(book.to_dict()), 201

@app.route('/books', methods=['GET'])
def get_books():
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    # Search by title or author
    search = request.args.get('search', '')
    books_query = Book.query.filter(
        (Book.title.ilike(f'%{search}%')) | (Book.author.ilike(f'%{search}%'))
    )
    books = books_query.paginate(page, per_page, error_out=False)
    return jsonify([book.to_dict() for book in books.items])

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book.to_dict())

@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.get_json()
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    book.title = data.get('title', book.title)
    book.author = data.get('author', book.author)
    book.year = data.get('year', book.year)
    db.session.commit()
    return jsonify(book.to_dict())

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted successfully"})

@app.route('/books/<int:book_id>/borrow', methods=['POST'])
def borrow_book(book_id):
    data = request.get_json()
    member_id = data.get('member_id')

    book = Book.query.get(book_id)
    member = Member.query.get(member_id)

    if not book:
        return jsonify({"error": "Book not found"}), 404
    if not member:
        return jsonify({"error": "Member not found"}), 404
    if book.member_id is not None:
        return jsonify({"error": "Book is already borrowed"}), 400

    book.member_id = member_id
    db.session.commit()
    return jsonify({"message": f"Book '{book.title}' borrowed by member '{member.name}'"}), 200

@app.route('/books/<int:book_id>/return', methods=['POST'])
def return_book(book_id):
    book = Book.query.get(book_id)

    if not book:
        return jsonify({"error": "Book not found"}), 404
    if book.member_id is None:
        return jsonify({"error": "Book is not borrowed"}), 400

    book.member_id = None
    db.session.commit()
    return jsonify({"message": f"Book '{book.title}' returned"}), 200

@app.route('/members', methods=['POST'])
def add_member():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')

    if not name or not email:
        return jsonify({"error": "Missing required fields"}), 400

    member = Member(name=name, email=email)
    db.session.add(member)
    db.session.commit()
    return jsonify(member.to_dict()), 201

@app.route('/members', methods=['GET'])
def get_members():
    members = Member.query.all()
    return jsonify([member.to_dict() for member in members])

@app.route('/members/<int:member_id>', methods=['GET'])
def get_member(member_id):
    member = Member.query.get(member_id)
    if not member:
        return jsonify({"error": "Member not found"}), 404
    return jsonify(member.to_dict())

@app.route('/members/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    data = request.get_json()
    member = Member.query.get(member_id)
    if not member:
        return jsonify({"error": "Member not found"}), 404

    member.name = data.get('name', member.name)
    member.email = data.get('email', member.email)
    db.session.commit()
    return jsonify(member.to_dict())

@app.route('/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    member = Member.query.get(member_id)
    if not member:
        return jsonify({"error": "Member not found"}), 404

    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": "Member deleted successfully"})

# Main
if __name__ == '__main__':
    db.create_all()  # Ensure database is created
    app.run(debug=True)

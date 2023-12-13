from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config['SECRET_KEY']='secret_key_33'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'  # Replace with your database URI
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma =Marshmallow(app)

# Define the Book model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(13), unique=True, nullable=False)

    def __repr__(self):
        return f"(Book: {self.title})"


class BookListSchema(ma.Schema):
    class Meta:
        fields= ('id','title', 'author', 'isbn')

booklist_schema=BookListSchema(many= False)
booklists_schema=BookListSchema(many= True)

# Endpoint 1: Add a New Book
@app.route('/POST/api/books', methods=['POST'])
def add_book():
    data = request.json
    new_book = Book(title=data['title'], author=data['author'], isbn=data['isbn'])
    try:
        db.session.add(new_book)
        db.session.commit()
        return booklist_schema.jsonify(new_book)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Duplicate book entry or invalid data'}), 400
    
# Endpoint 2: Retrieve All Books
@app.route('/GET/api/books', methods=['GET'])
def get_books():
    try:
        books = Book.query.all()
        result= booklists_schema.dump(books)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': 'Database connection error'}), 500

# Endpoint 3: Update Book Details
@app.route('/PUT/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.json
    try:
        book = Book.query.get(book_id)
        if book:
            book.title = data.get('title', book.title)
            book.author = data.get('author', book.author)
            book.isbn = data.get('isbn', book.isbn)
            db.session.commit()
            return booklist_schema.jsonify(book)
        else:
            return jsonify({'error': 'Book not found'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update book'}), 400


if __name__ == '__main__':
    app.run(debug=True)

from bson.objectid import ObjectId

# The file exposes helper functions around the `users` collection.
_db = None

def init_db(db):
    global _db
    _db = db

def get_user_collection():
    if _db is None:
        raise RuntimeError('Database not initialized. Call init_db(db) from main.')
    return _db.get_collection('users')

def to_public(user_doc):
    if not user_doc:
        return None
    return {
        'id': str(user_doc.get('_id')),
        'username': user_doc.get('username'),
        'email': user_doc.get('email')
    }

def from_dict(data):
    return {
        'username': data.get('username'),
        'email': data.get('email')
    }

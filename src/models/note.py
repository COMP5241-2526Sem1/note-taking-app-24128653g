from datetime import datetime
from bson.objectid import ObjectId

# Mongo-backed helpers for notes collection
_db = None

def init_db(db):
    global _db
    _db = db

def get_notes_collection():
    if _db is None:
        raise RuntimeError('Database not initialized. Call init_db(db) from main.')
    return _db.get_collection('notes')

def to_public(note_doc):
    if not note_doc:
        return None
    return {
        'id': str(note_doc.get('_id')),
        'title': note_doc.get('title'),
        'content': note_doc.get('content'),
        'tags': note_doc.get('tags', []),
        'created_at': note_doc.get('created_at').isoformat() if note_doc.get('created_at') else None,
        'updated_at': note_doc.get('updated_at').isoformat() if note_doc.get('updated_at') else None
    }

def make_note_doc(data):
    now = datetime.utcnow()
    return {
        'title': data.get('title'),
        'content': data.get('content'),
        'tags': data.get('tags') or [],
        'created_at': now,
        'updated_at': now
    }



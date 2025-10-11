from flask import Blueprint, jsonify, request
from bson.objectid import ObjectId
from datetime import datetime
from src.models import note as note_model
from src.llm import generate_note_metadata

note_bp = Blueprint('note', __name__)


@note_bp.route('/notes', methods=['GET'])
def get_notes():
    """Get all notes, ordered by most recently updated"""
    col = note_model.get_notes_collection()
    docs = col.find().sort('updated_at', -1)
    return jsonify([note_model.to_public(d) for d in docs])

@note_bp.route('/notes', methods=['POST'])
def create_note():
    """Create a new note"""
    try:
        data = request.json
        if not data or 'title' not in data or 'content' not in data:
            return jsonify({'error': 'Title and content are required'}), 400
        col = note_model.get_notes_collection()
        doc = note_model.make_note_doc(data)
        res = col.insert_one(doc)
        created = col.find_one({'_id': res.inserted_id})
        return jsonify(note_model.to_public(created)), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@note_bp.route('/notes/<note_id>', methods=['GET'])
def get_note(note_id):
    """Get a specific note by ID"""
    try:
        col = note_model.get_notes_collection()
        doc = col.find_one({'_id': ObjectId(note_id)})
        if not doc:
            return jsonify({'error': 'Not found'}), 404
        return jsonify(note_model.to_public(doc))
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@note_bp.route('/notes/<note_id>', methods=['PUT'])
def update_note(note_id):
    """Update a specific note"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        col = note_model.get_notes_collection()
        update = {}
        if 'title' in data:
            update['title'] = data['title']
        if 'content' in data:
            update['content'] = data['content']
        if 'tags' in data:
            update['tags'] = data['tags']
        if update:
            update['updated_at'] = datetime.utcnow()
            col.update_one({'_id': ObjectId(note_id)}, {'$set': update})
        doc = col.find_one({'_id': ObjectId(note_id)})
        if not doc:
            return jsonify({'error': 'Not found'}), 404
        return jsonify(note_model.to_public(doc))
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@note_bp.route('/notes/<note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Delete a specific note"""
    try:
        col = note_model.get_notes_collection()
        res = col.delete_one({'_id': ObjectId(note_id)})
        if res.deleted_count == 0:
            return jsonify({'error': 'Not found'}), 404
        return '', 204
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@note_bp.route('/notes/search', methods=['GET'])
def search_notes():
    """Search notes by title or content"""
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    col = note_model.get_notes_collection()
    docs = col.find({'$or': [
        {'title': {'$regex': query, '$options': 'i'}},
        {'content': {'$regex': query, '$options': 'i'}}
    ]}).sort('updated_at', -1)
    return jsonify([note_model.to_public(d) for d in docs])

@note_bp.route('/notes/generate', methods=['POST'])
def generate_note():
    """Generate a note with title and tags using LLM"""
    try:
        data = request.json
        if not data or 'content' not in data:
            return jsonify({'error': 'Content is required'}), 400
        
        # Generate title and tags using LLM
        metadata = generate_note_metadata(data['content'])
        
        col = note_model.get_notes_collection()
        doc = note_model.make_note_doc({
            'title': metadata['title'],
            'content': data['content'],
            'tags': metadata['tags']
        })
        res = col.insert_one(doc)
        created = col.find_one({'_id': res.inserted_id})
        return jsonify(note_model.to_public(created)), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


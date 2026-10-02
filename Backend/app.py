from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Task, init_db
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_db(app)

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    try:
        tasks = Task.query.order_by(Task.created_at.desc()).all()
        return jsonify([task.to_dict() for task in tasks])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        return jsonify(task.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/api/tasks', methods=['POST'])
def create_task():
    try:
        data = request.json
        
        if not data or not data.get('title') or not data.get('subject'):
            return jsonify({'error': 'Title and Subject are required'}), 400
        
        task = Task(
            title=data['title'],
            subject=data['subject'],
            category=data.get('category', 'assignment'),
            description=data.get('description', ''),
            status=data.get('status', 'pending')
        )
        
        if 'dueDate' in data and data['dueDate']:
            task.due_date = datetime.fromisoformat(data['dueDate'])
        
        db.session.add(task)
        db.session.commit()
        
        return jsonify(task.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        data = request.json
        
      
        task.title = data.get('title', task.title)
        task.subject = data.get('subject', task.subject)
        task.category = data.get('category', task.category)
        task.description = data.get('description', task.description)
        task.status = data.get('status', task.status)
        
        if 'dueDate' in data and data['dueDate']:
            task.due_date = datetime.fromisoformat(data['dueDate'])
            
        db.session.commit()
        
        return jsonify(task.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({'message': 'Task deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/filter/<category>', methods=['GET'])
def get_tasks_by_category(category):
    try:
        tasks = Task.query.filter_by(category=category).all()
        return jsonify([task.to_dict() for task in tasks])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/status/<status>', methods=['GET'])
def get_tasks_by_status(status):
    try:
        tasks = Task.query.filter_by(status=status).all()
        return jsonify([task.to_dict() for task in tasks])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Task, ProjectMember
from datetime import datetime

tasks_bp = Blueprint('tasks', __name__)

# Create Task (Admin only)
@tasks_bp.route('/projects/<int:project_id>/tasks', methods=['POST'])
@jwt_required()
def create_task(project_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()

    membership = ProjectMember.query.filter_by(
        project_id=project_id, user_id=user_id, role='Admin'
    ).first()
    if not membership:
        return jsonify({'message': 'Only Admin can create tasks'}), 403

    if not data.get('title'):
        return jsonify({'message': 'Title is required'}), 400

    task = Task(
        title=data['title'],
        description=data.get('description', ''),
        due_date=datetime.strptime(data['due_date'], '%Y-%m-%d') if data.get('due_date') else None,
        priority=data.get('priority', 'Medium'),
        status='To Do',
        assigned_to=data.get('assigned_to'),
        project_id=project_id
    )
    db.session.add(task)
    db.session.commit()

    return jsonify({'message': 'Task created successfully', 'task_id': task.id}), 201


# Get All Tasks
@tasks_bp.route('/projects/<int:project_id>/tasks', methods=['GET'])
@jwt_required()
def get_tasks(project_id):
    user_id = int(get_jwt_identity())

    membership = ProjectMember.query.filter_by(
        project_id=project_id, user_id=user_id
    ).first()
    if not membership:
        return jsonify({'message': 'Access denied'}), 403

    if membership.role == 'Admin':
        tasks = Task.query.filter_by(project_id=project_id).all()
    else:
        tasks = Task.query.filter_by(
            project_id=project_id, assigned_to=user_id
        ).all()

    result = []
    for t in tasks:
        result.append({
            'id': t.id,
            'title': t.title,
            'description': t.description,
            'due_date': t.due_date.strftime('%Y-%m-%d') if t.due_date else None,
            'priority': t.priority,
            'status': t.status,
            'assigned_to': t.assigned_to,
            'overdue': t.due_date < datetime.utcnow() and t.status != 'Done' if t.due_date else False
        })

    return jsonify(result), 200


# Update Task
@tasks_bp.route('/tasks/<int:task_id>', methods=['PATCH'])
@jwt_required()
def update_task(task_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()

    task = Task.query.get(task_id)
    if not task:
        return jsonify({'message': 'Task not found'}), 404

    membership = ProjectMember.query.filter_by(
        project_id=task.project_id, user_id=user_id
    ).first()
    if not membership:
        return jsonify({'message': 'Access denied'}), 403

    if membership.role == 'Member' and task.assigned_to != user_id:
        return jsonify({'message': 'You can only update your assigned tasks'}), 403

    if data.get('status'):
        if data['status'] not in ['To Do', 'In Progress', 'Done']:
            return jsonify({'message': 'Invalid status'}), 400
        task.status = data['status']

    if membership.role == 'Admin':
        if data.get('title'):
            task.title = data['title']
        if data.get('description'):
            task.description = data['description']
        if data.get('priority'):
            task.priority = data['priority']
        if data.get('assigned_to'):
            task.assigned_to = data['assigned_to']
        if data.get('due_date'):
            task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')

    db.session.commit()
    return jsonify({'message': 'Task updated successfully'}), 200


# Dashboard
@tasks_bp.route('/projects/<int:project_id>/dashboard', methods=['GET'])
@jwt_required()
def dashboard(project_id):
    user_id = int(get_jwt_identity())

    membership = ProjectMember.query.filter_by(
        project_id=project_id, user_id=user_id
    ).first()
    if not membership:
        return jsonify({'message': 'Access denied'}), 403

    tasks = Task.query.filter_by(project_id=project_id).all()

    total = len(tasks)
    todo = len([t for t in tasks if t.status == 'To Do'])
    in_progress = len([t for t in tasks if t.status == 'In Progress'])
    done = len([t for t in tasks if t.status == 'Done'])
    overdue = len([t for t in tasks if t.due_date and t.due_date < datetime.utcnow() and t.status != 'Done'])

    tasks_per_user = {}
    for t in tasks:
        if t.assigned_to:
            tasks_per_user[t.assigned_to] = tasks_per_user.get(t.assigned_to, 0) + 1

    return jsonify({
        'total_tasks': total,
        'by_status': {
            'To Do': todo,
            'In Progress': in_progress,
            'Done': done
        },
        'overdue_tasks': overdue,
        'tasks_per_user': tasks_per_user
    }), 200
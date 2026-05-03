from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Project, ProjectMember, User

projects_bp = Blueprint('projects', __name__)

# Create Project
@projects_bp.route('/projects', methods=['POST'])
@jwt_required()
def create_project():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data.get('name'):
        return jsonify({'message': 'Project name is required'}), 400

    project = Project(
        name=data['name'],
        description=data.get('description', ''),
        created_by=user_id
    )
    db.session.add(project)
    db.session.flush()

    member = ProjectMember(
        project_id=project.id,
        user_id=user_id,
        role='Admin'
    )
    db.session.add(member)
    db.session.commit()

    return jsonify({'message': 'Project created', 'project_id': project.id}), 201


# Get All Projects
@projects_bp.route('/projects', methods=['GET'])
@jwt_required()
def get_projects():
    user_id = int(get_jwt_identity())

    memberships = ProjectMember.query.filter_by(user_id=user_id).all()
    projects = []
    for m in memberships:
        project = Project.query.get(m.project_id)
        projects.append({
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'role': m.role
        })

    return jsonify(projects), 200


# Add Member (Admin only)
@projects_bp.route('/projects/<int:project_id>/members', methods=['POST'])
@jwt_required()
def add_member(project_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()

    membership = ProjectMember.query.filter_by(
        project_id=project_id, user_id=user_id, role='Admin'
    ).first()
    if not membership:
        return jsonify({'message': 'Only Admin can add members'}), 403

    new_user = User.query.filter_by(email=data.get('email')).first()
    if not new_user:
        return jsonify({'message': 'User not found'}), 404

    already = ProjectMember.query.filter_by(
        project_id=project_id, user_id=new_user.id
    ).first()
    if already:
        return jsonify({'message': 'User already a member'}), 400

    member = ProjectMember(
        project_id=project_id,
        user_id=new_user.id,
        role='Member'
    )
    db.session.add(member)
    db.session.commit()

    return jsonify({'message': 'Member added successfully'}), 201


# Remove Member (Admin only)
@projects_bp.route('/projects/<int:project_id>/members/<int:member_id>', methods=['DELETE'])
@jwt_required()
def remove_member(project_id, member_id):
    user_id = int(get_jwt_identity())

    membership = ProjectMember.query.filter_by(
        project_id=project_id, user_id=user_id, role='Admin'
    ).first()
    if not membership:
        return jsonify({'message': 'Only Admin can remove members'}), 403

    member = ProjectMember.query.filter_by(
        project_id=project_id, user_id=member_id
    ).first()
    if not member:
        return jsonify({'message': 'Member not found'}), 404

    db.session.delete(member)
    db.session.commit()

    return jsonify({'message': 'Member removed successfully'}), 200


# Get Project Members
@projects_bp.route('/projects/<int:project_id>/members', methods=['GET'])
@jwt_required()
def get_members(project_id):
    user_id = int(get_jwt_identity())

    membership = ProjectMember.query.filter_by(
        project_id=project_id, user_id=user_id
    ).first()
    if not membership:
        return jsonify({'message': 'Access denied'}), 403

    members = ProjectMember.query.filter_by(project_id=project_id).all()
    result = []
    for m in members:
        user = User.query.get(m.user_id)
        result.append({
            'user_id': user.id,
            'name': user.name,
            'email': user.email,
            'role': m.role
        })

    return jsonify(result), 200
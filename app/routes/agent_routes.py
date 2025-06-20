from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.agent_service import AgentService

agent_bp = Blueprint('agents', __name__)


@agent_bp.route('/', methods=['POST'])
@jwt_required()
def create_agent():
    user_id = get_jwt_identity()
    data = request.get_json()

    required_fields = ['name', 'system_prompt']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    agent = AgentService.create_agent(
        user_id=user_id,
        name=data['name'],
        system_prompt=data['system_prompt'],
        description=data.get('description', ''),
        model=data.get('model', 'gpt-3.5-turbo'),
        temperature=data.get('temperature', 0.7),
        max_tokens=data.get('max_tokens', 1000),
        is_public=data.get('is_public', False)
    )

    return jsonify(agent.to_dict()), 201


@agent_bp.route('/', methods=['GET'])
@jwt_required()
def list_agents():
    user_id = get_jwt_identity()
    public = request.args.get('public', '').lower() == 'true'

    agents = AgentService.list_agents(user_id, public)
    return jsonify([agent.to_dict() for agent in agents]), 200


@agent_bp.route('/<int:agent_id>', methods=['GET'])
@jwt_required()
def get_agent(agent_id):
    user_id = get_jwt_identity()
    agent = AgentService.get_agent(user_id, agent_id)

    if not agent:
        return jsonify({"error": "Agent not found or access denied"}), 404

    return jsonify(agent.to_dict()), 200


@agent_bp.route('/<int:agent_id>', methods=['PUT'])
@jwt_required()
def update_agent(agent_id):
    user_id = get_jwt_identity()
    data = request.get_json()

    agent = AgentService.update_agent(
        user_id=user_id,
        agent_id=agent_id,
        update_data=data
    )

    if not agent:
        return jsonify({"error": "Agent not found or access denied"}), 404

    return jsonify(agent.to_dict()), 200


@agent_bp.route('/<int:agent_id>', methods=['DELETE'])
@jwt_required()
def delete_agent(agent_id):
    user_id = get_jwt_identity()
    success = AgentService.delete_agent(user_id, agent_id)

    if not success:
        return jsonify({"error": "Agent not found or access denied"}), 404

    return jsonify({"message": "Agent deleted successfully"}), 200


@agent_bp.route('/<int:agent_id>/executions', methods=['GET'])
@jwt_required()
def list_agent_executions(agent_id):
    user_id = get_jwt_identity()
    executions = AgentService.list_agent_executions(user_id, agent_id)

    if executions is None:
        return jsonify({"error": "Agent not found or access denied"}), 404

    return jsonify([execution.to_dict() for execution in executions]), 200
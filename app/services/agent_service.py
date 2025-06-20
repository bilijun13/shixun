from app import db
from app.models import Agent, AgentExecution
from datetime import datetime


class AgentService:
    @staticmethod
    def create_agent(user_id, name, system_prompt, **kwargs):
        agent = Agent(
            user_id=user_id,
            name=name,
            system_prompt=system_prompt,
            **kwargs
        )
        db.session.add(agent)
        db.session.commit()
        return agent

    @staticmethod
    def list_agents(user_id, public=False):
        query = Agent.query
        if public:
            query = query.filter_by(is_public=True)
        else:
            query = query.filter_by(user_id=user_id)
        return query.order_by(Agent.created_at.desc()).all()

    @staticmethod
    def get_agent(user_id, agent_id):
        return Agent.query.filter_by(id=agent_id, user_id=user_id).first()

    @staticmethod
    def update_agent(user_id, agent_id, update_data):
        agent = Agent.query.filter_by(id=agent_id, user_id=user_id).first()
        if not agent:
            return None

        for key, value in update_data.items():
            if hasattr(agent, key):
                setattr(agent, key, value)

        db.session.commit()
        return agent

    @staticmethod
    def delete_agent(user_id, agent_id):
        agent = Agent.query.filter_by(id=agent_id, user_id=user_id).first()
        if not agent:
            return False

        db.session.delete(agent)
        db.session.commit()
        return True

    @staticmethod
    def create_execution(user_id, agent_id, input_text):
        agent = Agent.query.filter_by(id=agent_id, user_id=user_id).first()
        if not agent:
            return None

        execution = AgentExecution(
            agent_id=agent_id,
            user_id=user_id,
            input=input_text,
            status='pending'
        )
        db.session.add(execution)
        db.session.commit()
        return execution

    @staticmethod
    def update_execution_status(execution_id, status):
        execution = AgentExecution.query.get(execution_id)
        if execution:
            execution.status = status
            db.session.commit()

    @staticmethod
    def complete_execution(execution_id, output):
        execution = AgentExecution.query.get(execution_id)
        if execution:
            execution.output = output
            execution.status = 'completed'
            execution.end_time = datetime.utcnow()
            db.session.commit()
        return execution

    @staticmethod
    def list_agent_executions(user_id, agent_id):
        agent = Agent.query.filter_by(id=agent_id, user_id=user_id).first()
        if not agent:
            return None

        return AgentExecution.query.filter_by(
            agent_id=agent_id,
            user_id=user_id
        ).order_by(AgentExecution.start_time.desc()).all()

    @staticmethod
    def get_execution(user_id, execution_id):
        return AgentExecution.query.filter_by(
            id=execution_id,
            user_id=user_id
        ).first()
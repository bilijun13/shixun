from app.extensions import db
from app.models import Agent, AgentExecution
from datetime import datetime
from app.services.tongyi_service import Message
from app.services.tongyi_service import TongyiService


class AgentService:

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


    @staticmethod
    def create_agent(user_id, name, system_prompt, **kwargs):
        """创建agent并测试模型连接"""
        kwargs.setdefault('model', 'qwen-turbo')

        agent = Agent(
            user_id=user_id,
            name=name,
            system_prompt=system_prompt,
            **kwargs
        )
        db.session.add(agent)
        db.session.commit()

        # 测试模型连接
        try:
            test_response, _ = TongyiService.generate_response(
                agent=agent,
                user_input="测试连接"
            )
            print(f"模型连接测试成功: {test_response}")
        except Exception as e:
            print(f"模型连接测试失败: {str(e)}")

        return agent

    @staticmethod
    def execute_agent(user_id, agent_id, user_input, parent_execution_id=None):
        """
        执行Agent对话（支持多轮上下文）
        :param user_id: 用户ID
        :param agent_id: Agent ID
        :param user_input: 用户输入
        :param parent_execution_id: 父级执行ID（用于上下文关联）
        :return: (response_text, execution)
        """
        # 验证Agent归属
        agent = Agent.query.filter_by(id=agent_id, user_id=user_id).first()
        if not agent:
            raise ValueError("Agent not found or access denied")

        try:
            # 获取对话历史（如果是多轮对话）
            history_message = []
            # 验证父级执行记录归属（如果存在）
            if parent_execution_id:
                history = AgentExecution.query.filter_by(
                    id=parent_execution_id,
                    user_id=user_id,
                    status='completed'
                ).first()
                if history and history.output:
                    history_message.extend([
                        Message(role="user", content=history.input),
                        Message(role="assistant", content=history.output)
                    ])

            # 调用AI服务生成回复
            ai_response = TongyiService.generate_response(
                agent=agent,
                user_input=user_input,
                history_messages=history_message
            )

            # 如果是首次对话，则创建新执行记录
            if parent_execution_id:
                execution = AgentExecution.query.get(parent_execution_id)
            else:
                execution = AgentExecution(
                    agent_id=agent_id,
                    user_id=user_id,
                    input=user_input,
                    output=ai_response,
                    status='completed',
                    parent_execution_id=None
                )
                db.session.add(execution)
                db.session.commit()

            return ai_response, execution

        except Exception as e:
            if execution:
                execution.status = 'failed'
                execution.error_message = str(e)
                db.session.commit()
            raise
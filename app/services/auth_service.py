from flask_bcrypt import Bcrypt

from app import TongyiService
from app.models import User, AgentExecution, Agent, Api
from app.extensions import db
from datetime import datetime

bcrypt = Bcrypt()


class AuthService:
    """用户认证服务类，处理所有与认证相关的业务逻辑"""

    @staticmethod
    def register_user(username, email, password, tongyi_api_key=None, openai_api_key=None):
        """
        注册新用户并在api表中创建初始记录（API密钥可为空）
        :param username: 用户名
        :param email: 邮箱
        :param password: 密码
        :param tongyi_api_key: 通义API密钥（可选）
        :param openai_api_key: OpenAI API密钥（可选）
        :return: 字典 {success: bool, message: str, user: User|None}
        """
        # 检查用户名或邮箱是否已存在
        if User.query.filter_by(username=username).first():
            return {"success": False, "message": "用户名已被使用"}

        if User.query.filter_by(email=email).first():
            return {"success": False, "message": "邮箱已被注册"}

        try:
            # 创建用户记录
            new_user = User(
                username=username,
                email=email,
                created_at=datetime.utcnow(),
                is_active=True
            )
            new_user.set_password(password)

            # 开始数据库事务
            db.session.add(new_user)
            db.session.flush()  # 刷新以获取new_user.id

            # 创建API记录（API密钥默认置为空字符串）
            api_record = Api(
                user_id=new_user.id,
                tongyi_api_key=tongyi_api_key or "",
                openai_api_key=openai_api_key or ""
            )
            db.session.add(api_record)
            db.session.commit()

            return {
                "success": True,
                "message": "用户注册成功，API记录已创建",
                "user": new_user
            }
        except Exception as e:
            db.session.rollback()
            return {
                "success": False,
                "message": f"注册失败: {str(e)}"
            }

    @staticmethod
    def authenticate_user(username_or_email, password):
        """
        用户认证
        :param username_or_email: 用户名或邮箱
        :param password: 密码
        :return: 认证成功的用户对象或None
        """
        user = User.query.filter(
            (User.username == username_or_email) |
            (User.email == username_or_email)
        ).first()

        if user and user.check_password(password) and user.is_active:
            return user
        return None

    @staticmethod
    def get_user_by_id(user_id):
        """
        通过ID获取用户
        :param user_id: 用户ID
        :return: 用户对象或None
        """
        return User.query.get(user_id)

    @staticmethod
    def update_user_profile(user_id, update_data):
        """
        更新用户资料
        :param user_id: 用户ID
        :param update_data: 要更新的字段字典
        :return: 更新后的用户对象或None
        """
        user = User.query.get(user_id)
        if not user:
            return None

        try:
            for key, value in update_data.items():
                if hasattr(user, key) and key not in ['id', 'password_hash']:
                    setattr(user, key, value)

            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            return None

    @staticmethod
    def change_password(user_id, old_password, new_password):
        """
        修改密码
        :param user_id: 用户ID
        :param old_password: 旧密码
        :param new_password: 新密码
        :return: 是否成功
        """
        user = User.query.get(user_id)
        if not user or not user.check_password(old_password):
            return False

        try:
            user.set_password(new_password)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False

    @staticmethod
    def execute_agent(user_id, agent_id, user_input, execution_id=None):
        agent = Agent.query.filter_by(id=agent_id, user_id=user_id).first()
        if not agent:
            raise ValueError("Agent not found or access denied")

        # 获取历史对话（如果是后续提问）
        history_messages = []
        if execution_id:
            parent_execution = AgentExecution.query.get(execution_id)
            if parent_execution:
                history_messages.extend([
                    {"role": "user", "content": parent_execution.input},
                    {"role": "assistant", "content": parent_execution.output}
                ])

        # 创建新执行记录
        execution = AgentExecution(
            agent_id=agent_id,
            user_id=user_id,
            input=user_input,
            status='running',
            parent_execution_id=execution_id  # 关联父对话
        )
        db.session.add(execution)
        db.session.commit()

        try:
            # 调用AI服务（传入历史）
            ai_response, _ = TongyiService.generate_response(
                agent=agent,
                user_input=user_input,
                history_messages=history_messages  # 新增参数
            )

            # 更新执行结果
            execution.output = ai_response
            execution.status = 'completed'
            db.session.commit()

            return ai_response, execution

        except Exception as e:
            execution.status = 'failed'
            db.session.commit()
            raise

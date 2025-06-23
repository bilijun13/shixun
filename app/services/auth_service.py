from flask_bcrypt import Bcrypt
from app.models import User
from app.extensions import db
from datetime import datetime

bcrypt = Bcrypt()


class AuthService:
    """用户认证服务类，处理所有与认证相关的业务逻辑"""

    @staticmethod
    def register_user(username, email, password):
        """
        注册新用户
        :param username: 用户名
        :param email: 邮箱
        :param password: 密码
        :return: 字典 {success: bool, message: str, user: User|None}
        """
        # 检查用户名或邮箱是否已存在
        if User.query.filter_by(username=username).first():
            return {"success": False, "message": "用户名已被使用"}

        if User.query.filter_by(email=email).first():
            return {"success": False, "message": "邮箱已被注册"}

        try:
            new_user = User(
                username=username,
                email=email,
                created_at=datetime.utcnow(),
                is_active=True
            )
            new_user.set_password(password)

            db.session.add(new_user)
            db.session.commit()

            return {
                "success": True,
                "message": "用户注册成功",
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
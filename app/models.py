from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from flask_login import UserMixin
from app.extensions import db
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()


class User(db.Model,UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    api_key = db.relationship('Api', back_populates='user', uselist=False)
    agent = db.relationship('Agent', back_populates='owner')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

        # flask_login要求的方法

    def get_id(self):
        """返回用户唯一标识，必须为字符串类型"""
        return str(self.id)

class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    system_prompt = db.Column(db.Text, nullable=False)
    model = db.Column(db.String(64), default='gpt-3.5-turbo')
    temperature = db.Column(db.Float, default=0.7)
    max_tokens = db.Column(db.Integer, default=1000)
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    owner = db.relationship('User', back_populates='agent')
    execution = db.relationship('AgentExecution', backref='agent', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'system_prompt': self.system_prompt,
            'description': self.description,
            'model': self.model,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'is_public': self.is_public,
            # 其他需要返回的字段...
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class AgentExecution(db.Model):
    __tablename__ = 'agent_execution'  # 明确指定表名，避免潜在的表名不一致问题

    id = db.Column(db.Integer, primary_key=True)
    input = db.Column(db.Text, nullable=False)
    output = db.Column(db.Text)
    status = db.Column(db.String(32), default='pending')  # pending, running, completed, failed
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


    # 明确定义自引用外键
    parent_execution_id = db.Column(
        db.Integer,
        db.ForeignKey('agent_execution.id'),  # 注意这里使用表名.id
        nullable=True
    )

    # 关系定义
    user = db.relationship('User', backref='executions')

    # 明确定义父子关系
    children = db.relationship(
        'AgentExecution',
        backref=db.backref('parent', remote_side=[id]),  # 指定远程侧
        foreign_keys=[parent_execution_id],  # 明确指定外键
        lazy='dynamic'
    )

    def to_dict(self):
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "input": self.input,
            "output": self.output,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None
        }


@dataclass
class ApiKey:
    """API密钥数据类"""
    tongyi_api_key: str
    openai_api_key: str
    user_id: int
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Api(db.Model):
    """API密钥模型"""
    __tablename__ = 'api'

    id = db.Column(db.Integer, primary_key=True)
    tongyi_api_key = db.Column(db.String(255), nullable=False, comment='通义API密钥')
    openai_api_key = db.Column(db.String(255), nullable=False, comment='OpenAI API密钥')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True, comment='关联用户ID')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    # 定义关系
    user = db.relationship('User', back_populates='api_key')

    def to_dict(self) -> Dict[str, Any]:
        """将模型转换为字典形式"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'tongyi_api_key': self.tongyi_api_key,
            'openai_api_key': self.openai_api_key,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
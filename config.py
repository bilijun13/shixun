import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///dify.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-here')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

    # 其他配置
    MAX_AGENT_COUNT_PER_USER = 50
    AGENT_EXECUTION_TIMEOUT = 30  # 秒
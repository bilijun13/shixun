from app.models import Api, User
from app.extensions import db
from typing import Optional, Dict, Any
from datetime import datetime
from app.models import ApiKey


class ApiService:
    @staticmethod
    def get_api_key_by_user(user_id: int) -> Optional[ApiKey]:
        """根据用户ID获取API密钥"""
        api = Api.query.filter_by(user_id=user_id).first()
        if api:
            return ApiKey(
                id=api.id,
                tongyi_api_key=api.tongyi_api_key,
                openai_api_key=api.openai_api_key,
                user_id=api.user_id,
                created_at=api.created_at,
                updated_at=api.updated_at
            )
        return None

    @staticmethod
    def update_api_key(user_id: int, data: Dict[str, Any]) -> Optional[ApiKey]:
        """更新用户的API密钥"""
        api = Api.query.filter_by(user_id=user_id).first()
        if not api:
            raise ValueError("API key record not found for the user")

        update_fields = {}
        for key in ['tongyi_api_key', 'openai_api_key']:
            if key in data:
                update_fields[key] = data[key]

        if not update_fields:
            raise ValueError("No valid fields provided for update")

        for key, value in update_fields.items():
            setattr(api, key, value)

        api.updated_at = datetime.utcnow()
        db.session.commit()

        return ApiKey(
            id=api.id,
            tongyi_api_key=api.tongyi_api_key,
            openai_api_key=api.openai_api_key,
            user_id=api.user_id,
            updated_at=api.updated_at
        )
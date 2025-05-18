from typing import Union
from jose import jwt
from datetime import datetime
from fastapi import Request
from starlette.requests import HTTPConnection
from starlette_context.plugins import Plugin

from instance.config import config


class AuthenticationContext(Plugin):
    key = "user"

    async def process_request(self, request: Union[Request, HTTPConnection]):
        bearer_token = request.headers.get("Authorization")
        if not bearer_token or not bearer_token.startswith("Bearer "):
            return

        token = bearer_token.split(" ")[1]

        try:
            jwt_data = jwt.decode(
                token,
                key=config.JWT_CONFIG.JWT_SECRET_KEY,
                algorithms=[config.JWT_CONFIG.JWT_ALGORITHM],
            )
        except Exception:
            return

        if datetime.utcfromtimestamp(jwt_data["exp"]) < datetime.utcnow():
            return

        return jwt_data 

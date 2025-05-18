from fastapi import status
import logging

import crud
from models.user import User
from api.base_resource import PostResource
from core.security import verify_password, create_jwt_token
from ..schemas.login_user import UserLoginRequest, UserLoginResponse

# Logger setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(ch)


class LoginUser(PostResource):
    request_schema = UserLoginRequest
    response_schema = UserLoginResponse
    authentication_required = False

    api_name = "login_user"
    api_url = "login_user"

    async def check_user_exists(self):
        logger.info("Checking if user exists for email: %s", self.request_data.email)
        self.user: User = await crud.user.get_by_email(self.db, email=self.request_data.email)
        if not self.user:
            logger.warning("User not found: %s", self.request_data.email)
            self.early_response = True
            self.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            self.response_message = "User with specified credentials does not exist."
            self.response_data = {}

    async def verify_password(self):
        try:
            logger.info("Verifying password for user: %s", self.user.email)
            if not verify_password(self.request_data.password, self.user.hashed_password):
                raise ValueError("Password mismatch")
        except Exception as e:
            logger.exception("Password verification failed")
            self.early_response = True
            self.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            self.response_message = "User with specified credentials does not exist."
            self.response_data = {}

    async def generate_access_token(self):
        try:
            logger.info("Generating JWT for user: %s", self.user.email)
            payload = {
                "user_id": self.user.id,
                "email": self.user.email,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "is_admin": True  # Manually granting admin for development
            }
            self.access_token = create_jwt_token(payload=payload, typ="access")
        except Exception as e:
            logger.exception("JWT token generation failed")
            self.early_response = True
            self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_message = "Failed to generate authentication token."
            self.response_data = {}

    async def touch_last_login(self):
        try:
            logger.info("Touching last login for user: %s", self.user.email)
            await crud.user.touch_last_login(self.db, db_obj=self.user)
        except Exception as e:
            logger.warning("Unable to update last login: %s", e)

    async def generate_response(self):
        logger.info("Login successful for user: %s", self.user.email)
        self.status_code = status.HTTP_200_OK
        self.response_message = "User logged in successfully"
        self.response_data = {"access_token": self.access_token}

    async def process_flow(self):
        try:
            logger.info("\ud83d\udd10 Login process started")
            await self.check_user_exists()
            if self.early_response:
                return

            await self.verify_password()
            if self.early_response:
                return

            await self.generate_access_token()
            if self.early_response:
                return

            await self.touch_last_login()
            await self.generate_response()

        except Exception as e:
            logger.exception("\ud83d\udd25 Unexpected error in login_user")
            self.early_response = True
            self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_message = "Internal Server Error"
            self.response_data = {"error": str(e)}

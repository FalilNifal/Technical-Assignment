from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_access_token
from app.models.role import Role
from app.models.user import User
from app.schemas.auth_schema import RegisterRequest, LoginRequest, TokenResponse, AuthUserResponse


class AuthService:
    @staticmethod
    def register(db: Session, payload: RegisterRequest) -> TokenResponse:
        existing_user = db.query(User).filter(User.email == payload.email.lower()).first()

        if existing_user:
            raise ValueError("Email is already registered")

        default_role = db.query(Role).filter(Role.name == "TEAM_MEMBER").first()

        if not default_role:
            raise ValueError("Default role TEAM_MEMBER does not exist")

        user = User(
            full_name=payload.full_name.strip(),
            email=payload.email.lower(),
            password_hash=hash_password(payload.password),
            role_id=default_role.id,
            is_active=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        token = create_access_token(
            subject=str(user.id),
            role=default_role.name,
        )

        return TokenResponse(
            access_token=token,
            user=AuthUserResponse(
                id=user.id,
                full_name=user.full_name,
                email=user.email,
                role=default_role.name,
                is_active=user.is_active,
            ),
        )

    @staticmethod
    def login(db: Session, payload: LoginRequest) -> TokenResponse:
        user = db.query(User).filter(User.email == payload.email.lower()).first()

        if not user:
            raise ValueError("Invalid email or password")

        if not verify_password(payload.password, user.password_hash):
            raise ValueError("Invalid email or password")

        if not user.is_active:
            raise PermissionError("This account has been deactivated")

        token = create_access_token(
            subject=str(user.id),
            role=user.role.name,
        )

        return TokenResponse(
            access_token=token,
            user=AuthUserResponse(
                id=user.id,
                full_name=user.full_name,
                email=user.email,
                role=user.role.name,
                is_active=user.is_active,
            ),
        )

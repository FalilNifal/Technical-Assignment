from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.core.permissions import require_manager_or_admin, require_admin
from app.models.user import User


router = APIRouter(prefix="/protected", tags=["Protected Demo"])


@router.get("/member")
def member_route(
    current_user: User = Depends(get_current_user),
):
    return {
        "message": f"Hello {current_user.full_name}. You are authenticated.",
        "role": current_user.role.name,
    }


@router.get("/manager")
def manager_route(
    current_user: User = Depends(require_manager_or_admin),
):
    return {
        "message": "Manager/Admin protected route accessed successfully.",
        "user": current_user.email,
        "role": current_user.role.name,
    }


@router.get("/admin")
def admin_route(
    current_user: User = Depends(require_admin),
):
    return {
        "message": "Admin-only route accessed successfully.",
        "user": current_user.email,
        "role": current_user.role.name,
    }

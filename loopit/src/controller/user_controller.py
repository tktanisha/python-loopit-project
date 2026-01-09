
from fastapi import status
from helpers.error_handler import write_error_response
from helpers.success_handler import write_success_response
from service.user_service import UserService



def _is_admin(user_ctx) -> bool:
  
    role_val = None
    if isinstance(user_ctx, dict):
        role_val = user_ctx.get("role")
    else:
        role_val = getattr(user_ctx, "role", None)
    return str(role_val).lower() == "admin"

async def become_lender(user_service: UserService, user_ctx):

    if user_ctx is None:
        return write_error_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error="unauthorized",
            details="user context missing",
        )
    try:
        await user_service.become_lender(user_ctx)
        if isinstance(user_ctx, dict):
            user_ctx["role"] = "lender"
            
        else:
            setattr(user_ctx, "role", "lender")
            
    except Exception as e:
        return write_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            error="become lender failed",
            details=str(e),
        )
    return write_success_response(
        status_code=status.HTTP_200_OK,
        message="User promoted to lender successfully",
        data={"user": user_ctx},
    )

async def get_all_users(search: str, role: str, society_id: str, user_service: UserService, user_ctx):
 
    if user_ctx is None:
        return write_error_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error="unauthorized",
            details="user context missing",
        )
    if not _is_admin(user_ctx):
        return write_error_response(
            status_code=status.HTTP_403_FORBIDDEN,
            error="forbidden",
            details="only admins can view all users",
        )
    try:
        filters = {
            "search": search,
            "role": role,
            "society_id": society_id,
        }
        users = await user_service.get_all_users(filters)
        if isinstance(users, list):
            data = [
                u.model_dump() if hasattr(u, "model_dump") else u
                for u in users
            ]
        else:
            data = users
    except Exception as e:
        return write_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="failed to fetch users",
            details=str(e),
        )
    return write_success_response(
        status_code=status.HTTP_200_OK,
        message="Users fetched successfully",
        data=data,
    )

async def get_user_by_id(id: int, user_service: UserService, user_ctx):
    """
    GET /users/{id}
    Admin-only: fetch user by ID.
    """
    if user_ctx is None:
        return write_error_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error="unauthorized",
            details="user context missing",
        )
    if not _is_admin(user_ctx):
        return write_error_response(
            status_code=status.HTTP_403_FORBIDDEN,
            error="forbidden",
            details="only admins can view a user",
        )
    try:
        user = await user_service.get_user_by_id(id)
        if user is None:
            return write_error_response(
                status_code=status.HTTP_404_NOT_FOUND,
                error="user not found",
                details=f"user id={id}",
            )
        data = user.model_dump() if hasattr(user, "model_dump") else user
    except Exception as e:
        return write_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="internal server error",
            details=str(e),
        )
    return write_success_response(
        status_code=status.HTTP_200_OK,
        message="User fetched successfully",
        data=data,
    )

async def delete_user_by_id(id: int, user_service: UserService, user_ctx):
    """
    DELETE /users/{id}
    Admin-only: delete user by ID.
    """
    if user_ctx is None:
        return write_error_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error="unauthorized",
            details="user context missing",
        )
    if not _is_admin(user_ctx):
        return write_error_response(
            status_code=status.HTTP_403_FORBIDDEN,
            error="forbidden",
            details="only admins can delete users",
        )
    try:
        await user_service.delete_user_by_id(id)
    except Exception as e:
        return write_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="internal server error",
            details=str(e),
        )
    return write_success_response(
        status_code=status.HTTP_200_OK,
        message="User deleted successfully",
    )

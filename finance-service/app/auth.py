from fastapi import Header, HTTPException, status


def require_roles(*allowed_roles: str):
    """Dependency factory validating X-User-Role against allowed roles."""

    normalized_allowed = {role.upper() for role in allowed_roles}

    async def _verify_role(
        x_user_role: str | None = Header(default=None, alias="X-User-Role"),
    ) -> str:
        if x_user_role is None or not x_user_role.strip():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "UNAUTHORIZED",
                    "message": "Header X-User-Role wajib diisi",
                },
            )

        role = x_user_role.strip().upper()
        if role not in normalized_allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN",
                    "message": f"Role {role} tidak memiliki akses ke endpoint ini",
                },
            )

        return role

    return _verify_role

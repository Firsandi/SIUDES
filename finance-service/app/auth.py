from fastapi import Header, HTTPException, Query, status


def _validate_role(raw_role: str | None, normalized_allowed: set[str]) -> str:
    if raw_role is None or not raw_role.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "UNAUTHORIZED",
                "message": "Header X-User-Role wajib diisi",
            },
        )

    role = raw_role.strip().upper()
    if role not in normalized_allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN",
                "message": f"Role {role} tidak memiliki akses ke endpoint ini",
            },
        )

    return role


def require_roles(*allowed_roles: str):
    """Dependency factory validating X-User-Role against allowed roles."""

    normalized_allowed = {role.upper() for role in allowed_roles}

    async def _verify_role(
        x_user_role: str | None = Header(default=None, alias="X-User-Role"),
    ) -> str:
        return _validate_role(x_user_role, normalized_allowed)

    return _verify_role


def require_roles_header_or_query(*allowed_roles: str):
    """Validate role from X-User-Role header, falling back to ?role= query param for EventSource."""

    normalized_allowed = {role.upper() for role in allowed_roles}

    async def _verify_role(
        x_user_role: str | None = Header(default=None, alias="X-User-Role"),
        role_query: str | None = Query(default=None, alias="role"),
    ) -> str:
        raw_role = x_user_role if (x_user_role and x_user_role.strip()) else role_query
        return _validate_role(raw_role, normalized_allowed)

    return _verify_role

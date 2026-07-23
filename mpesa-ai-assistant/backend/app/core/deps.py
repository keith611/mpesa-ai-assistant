"""
FastAPI dependencies for authentication and role-based access control (RBAC).
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError

from app.core.security import decode_token

bearer_scheme = HTTPBearer()

ROLE_HIERARCHY = {"SUPER_ADMIN": 4, "ADMIN": 3, "SUPPORT": 2, "USER": 1}


def get_current_claims(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not an access token")
    return payload


def require_role(*allowed_roles: str):
    """Usage: Depends(require_role('ADMIN', 'SUPER_ADMIN'))"""
    def checker(claims: dict = Depends(get_current_claims)) -> dict:
        role = claims.get("role")
        if role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return claims
    return checker


def require_min_role(min_role: str):
    """Usage: Depends(require_min_role('ADMIN')) -> allows ADMIN and SUPER_ADMIN."""
    def checker(claims: dict = Depends(get_current_claims)) -> dict:
        role = claims.get("role")
        if ROLE_HIERARCHY.get(role, 0) < ROLE_HIERARCHY.get(min_role, 999):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return claims
    return checker

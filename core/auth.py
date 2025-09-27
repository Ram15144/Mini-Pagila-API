"""Authentication and authorization utilities."""

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from core.config import settings
from core.logging import auth_logger


# Initialize OAuth2PasswordBearer security scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def verify_token(token: str = Depends(oauth2_scheme)) -> str:
    """
    Verify authentication token.
    
    Args:
        token: Bearer token from the Authorization header
        
    Returns:
        str: The verified token value
        
    Raises:
        HTTPException: If the token is invalid
    """
    auth_logger.debug("Verifying token", token_length=len(token) if token else 0)
    
    if token != settings.auth_token:
        auth_logger.warning("Invalid authentication token attempted", token_length=len(token) if token else 0)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    auth_logger.info("Token verified successfully", user="dvd_admin")
    return token


async def get_current_user(token: str = Depends(verify_token)) -> str:
    """
    Get current authenticated user.
    
    For this demo, we're using a simple token system.
    In production, this would decode a JWT or validate against a user database.
    
    Args:
        token: Verified authentication token
        
    Returns:
        str: User identifier (for now, just return the token)
    """
    # In this simple implementation, we just return a fixed user
    # In production, you would:
    # 1. Decode JWT token
    # 2. Look up user in database
    # 3. Return user object
    return "dvd_admin"


# Dependency that requires authentication
RequireAuth = Depends(verify_token)

# Dependency that gets the current user
CurrentUser = Depends(get_current_user)

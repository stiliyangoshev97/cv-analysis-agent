"""Shared FastAPI dependencies.

This module provides common dependencies that can be used across
multiple feature modules. Feature-specific dependencies should
remain in their respective feature folders.

Dependencies:
    get_settings_dep: Inject application settings.

Example:
    Using dependencies in routes::
    
        from app.core.dependencies import get_settings_dep
        from app.config import Settings
        
        @router.get("/info")
        async def get_info(settings: Settings = Depends(get_settings_dep)):
            return {"app_name": settings.app_name}
"""

from ..config import get_settings, Settings


def get_settings_dep() -> Settings:
    """Dependency to inject application settings.
    
    Returns:
        The application Settings instance.
    
    Example:
        >>> @router.get("/config")
        ... async def get_config(settings = Depends(get_settings_dep)):
        ...     return {"debug": settings.debug}
    """
    return get_settings()

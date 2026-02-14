"""
Settings Dependencies

FastAPI dependencies for settings endpoints.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.features.settings.settings_service import SettingsService


async def get_settings_service(
    session: AsyncSession = get_db_session
) -> SettingsService:
    """Get SettingsService instance with database session.
    
    Args:
        session: Async database session from dependency injection.
        
    Returns:
        Configured SettingsService.
    """
    return SettingsService(session)

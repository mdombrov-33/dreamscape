from app.core.config import Settings, get_settings


def get_config() -> Settings:
    """
    Dependency that provides app settings.

    Usage:
        @router.get("/info")
        async def get_info(settings: Settings = Depends(get_config)):
            return {"app_name": settings.app_name}
    """
    return get_settings()

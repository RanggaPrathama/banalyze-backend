from app.core.config import settings
from app.core.logging import get_log_config

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.reload,
        log_config=get_log_config()
    )
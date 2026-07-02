from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration."""

    # API
    API_TITLE: str = "Transcription API"
    API_VERSION: str = "1.0.0"
    LOG_LEVEL: str = "INFO"

    # Whisper model
    MODEL_SIZE: str = "base"
    DEVICE: str = "cpu"
    COMPUTE_TYPE: str = "int8"

    # File upload
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100 MB
    ALLOWED_EXTENSIONS: set = {".wav", ".mp3", ".flac", ".ogg", ".webm", ".mp4", ".m4a"}
    ALLOWED_CONTENT_TYPES: set = {
        "audio/wav",
        "audio/x-wav",
        "audio/mpeg",
        "audio/mp3",
        "audio/flac",
        "audio/ogg",
        "audio/webm",
        "audio/mp4",
        "audio/x-m4a",
    }

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

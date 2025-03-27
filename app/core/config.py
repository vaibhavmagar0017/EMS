from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Event Management System"
    API_PREFIX: str = "/api"
    DEBUG: bool = True

    # Database Configuration
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # JWT Settings
    SECRET_KEY: str = "esIaBEOx8h81RAGy7O5_2QIRriITDEkyH1KW9RdSZFg="
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()

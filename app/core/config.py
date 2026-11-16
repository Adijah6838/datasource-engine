from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "DataSource Engine"
    database_url: str = "sqlite:///./datasource.db"
    default_page_size: int = 100

settings = Settings()
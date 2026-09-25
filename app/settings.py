from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database Settings
    DB_USER: str = "root"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5434
    DB_NAME: str = "quickcart"

    # Kafka Settings (ready for Version B)
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_ORDERS: str = "orders"

    # Tell Pydantic to read from the .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # ignores extra fields in .env without throwing errors
    )

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

# Instantiate once so it can be imported anywhere
settings = Settings()
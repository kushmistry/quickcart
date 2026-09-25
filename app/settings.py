from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # API Server Settings
    API_HOST: str = "localhost"
    API_PORT: int = 8000

    # Database Settings
    DB_USER: str = "root"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5434
    DB_NAME: str = "quickcart"

    # Kafka Settings (ready for Version B)
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_ORDERS: str = "orders"

    # Benchmark Defaults (overrideable in .env)
    BENCHMARK_TOTAL_ORDERS: int = 50
    BENCHMARK_CONCURRENCY: int = 10
    
    USE_KAFKA: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def API_BASE_URL(self) -> str:
        return f"http://{self.API_HOST}:{self.API_PORT}"

settings = Settings()
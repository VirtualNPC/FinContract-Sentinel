from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    app_name: str = Field(default="FinContract Sentinel", validation_alias="APP_NAME")
    env: str = Field(default="dev", validation_alias="ENV")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    port: int = Field(default=8000, validation_alias="PORT")

    postgres_dsn: str = Field(
        default="postgresql+psycopg://fincontract:fincontract@localhost:5432/fincontract",
        validation_alias="POSTGRES_DSN",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", validation_alias="REDIS_URL")
    vector_store: str = Field(default="chroma", validation_alias="VECTOR_STORE")
    ocr_provider: str = Field(default="aliyun", validation_alias="OCR_PROVIDER")
    knowledge_dir: str = Field(default="./data/knowledge", validation_alias="KNOWLEDGE_DIR")

    ocr_aliyun_key: str | None = Field(default=None, validation_alias="OCR_ALIYUN_KEY")
    ocr_aliyun_secret: str | None = Field(default=None, validation_alias="OCR_ALIYUN_SECRET")
    ocr_tencent_key: str | None = Field(default=None, validation_alias="OCR_TENCENT_KEY")
    ocr_tencent_secret: str | None = Field(default=None, validation_alias="OCR_TENCENT_SECRET")

    @property
    def is_dev(self) -> bool:
        return self.env.lower() == "dev"


settings = Settings()

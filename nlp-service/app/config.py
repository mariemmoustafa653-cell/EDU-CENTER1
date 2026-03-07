from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    summarization_provider: str = "huggingface"
    openai_api_key: str = ""
    huggingface_model: str = "Falconsai/text_summarization"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "info"
    max_input_length: int = 50000

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

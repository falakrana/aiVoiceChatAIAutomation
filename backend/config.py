import os
from dataclasses import dataclass, field
from typing import List

from dotenv import load_dotenv


load_dotenv()


def _csv(value: str) -> List[str]:
	if not value:
		return []
	return [item.strip() for item in value.split(",") if item.strip()]


@dataclass
class Settings:
	flask_env: str = os.getenv("FLASK_ENV", "development")
	flask_host: str = os.getenv("FLASK_HOST", "0.0.0.0")
	flask_port: int = int(os.getenv("FLASK_PORT", "5000"))
	cors_origins: List[str] = field(default_factory=lambda: _csv(os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")))

	mongodb_uri: str = os.getenv("MONGODB_URI", "")
	mongodb_db_name: str = os.getenv("MONGODB_DB_NAME", "task_reminders")
	mongodb_collection_name: str = os.getenv("MONGODB_COLLECTION_NAME", "tasks")

	twilio_account_sid: str = os.getenv("TWILIO_ACCOUNT_SID", "")
	twilio_auth_token: str = os.getenv("TWILIO_AUTH_TOKEN", "")
	twilio_caller_number: str = os.getenv("TWILIO_CALLER_NUMBER", "")
	twilio_voice_webhook_secret: str = os.getenv("TWILIO_VOICE_WEBHOOK_SECRET", "")

	timezone: str = os.getenv("TIMEZONE", "UTC")
	check_interval_seconds: int = int(os.getenv("CHECK_INTERVAL_SECONDS", "60"))

	app_base_url: str = os.getenv("APP_BASE_URL", "http://localhost:5000")


settings = Settings()

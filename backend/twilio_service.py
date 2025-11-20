from typing import Optional
from urllib.parse import urlencode

from bson import ObjectId
from twilio.rest import Client

from config import settings


class TwilioService:
	def __init__(self) -> None:
		if not settings.twilio_account_sid or not settings.twilio_auth_token:
			raise RuntimeError("Twilio credentials are not configured")
		self.client = Client(settings.twilio_account_sid, settings.twilio_auth_token)

	def make_call(self, to_phone: str, task_id: ObjectId, title: str, name: Optional[str]) -> str:
		query = urlencode({
			"task_id": str(task_id),
			"title": title,
			"name": name or "",
			"secret": settings.twilio_voice_webhook_secret,
		})
		url = f"{settings.app_base_url}/voice?{query}"
		call = self.client.calls.create(
			to=to_phone,
			from_=settings.twilio_caller_number,
			url=url,
		)
		return call.sid


def build_twiml(task_title: str, name: Optional[str]) -> str:
	# TwiML to speak out the reminder
	spoken_name = f"{name}. " if name else ""
	message = f"Hello {spoken_name}This is a reminder. It is time for: {task_title}."
	return f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<Response>
	<Say voice=\"Polly.Joanna\" language=\"en-US\">{message}</Say>
</Response>
"""

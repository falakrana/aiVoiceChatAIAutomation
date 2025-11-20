from datetime import datetime
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from bson import ObjectId

from config import settings
from db import find_due_tasks, mark_task_status
from twilio_service import TwilioService


_scheduler: Optional[BackgroundScheduler] = None
_twilio: Optional[TwilioService] = None


def _ensure_services() -> TwilioService:
	global _twilio
	if _twilio is None:
		_twilio = TwilioService()
	return _twilio


def check_and_call_jobs() -> None:
	service = _ensure_services()
	for task in find_due_tasks(datetime.now()):
		task_id = task.get("_id")
		try:
			call_sid = service.make_call(
				to_phone=task.get("phone", ""),
				task_id=ObjectId(task_id),
				title=task.get("title", ""),
				name=task.get("name", ""),
			)
			mark_task_status(task_id, "called", {"twilio_call_sid": call_sid})
		except Exception as ex:  # noqa: BLE001
			mark_task_status(task_id, "retry", {"error": str(ex)})


def start_scheduler() -> BackgroundScheduler:
	global _scheduler
	if _scheduler is not None:
		return _scheduler

	_scheduler = BackgroundScheduler(timezone=settings.timezone)
	_scheduler.add_job(
		check_and_call_jobs,
		trigger=IntervalTrigger(seconds=settings.check_interval_seconds),
		id="check_due_tasks",
		replace_existing=True,
	)
	_scheduler.start()
	return _scheduler

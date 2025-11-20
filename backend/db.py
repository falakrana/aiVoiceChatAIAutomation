from typing import Any, Dict, Optional
from datetime import datetime

from pymongo import MongoClient, ASCENDING
from pymongo.collection import Collection
from dateutil import parser as date_parser
import pytz

from config import settings


_client: Optional[MongoClient] = None
_collection: Optional[Collection] = None


def get_collection() -> Collection:
	global _client, _collection
	if _collection is not None:
		return _collection

	if not settings.mongodb_uri:
		raise RuntimeError("MONGODB_URI is not set.")

	_client = MongoClient(settings.mongodb_uri)
	db = _client[settings.mongodb_db_name]
	_collection = db[settings.mongodb_collection_name]

	# Indexes for efficient lookups
	_collection.create_index([("status", ASCENDING), ("time", ASCENDING)])
	_collection.create_index("phone")

	return _collection


ISO_FORMAT = "%Y-%m-%dT%H:%M:%S%z"

timezone = pytz.timezone(settings.timezone)


def to_aware_datetime(value: str | datetime) -> datetime:
	if isinstance(value, datetime):
		if value.tzinfo is None:
			return timezone.localize(value)
		return value.astimezone(timezone)
	# accept ISO strings or common formats
	dt = date_parser.parse(value)
	if dt.tzinfo is None:
		dt = timezone.localize(dt)
	return dt.astimezone(timezone)


def insert_task(title: str, time_value: str | datetime, phone: str, name: Optional[str]) -> str:
	col = get_collection()
	when = to_aware_datetime(time_value)
	doc: Dict[str, Any] = {
		"title": title,
		"time": when,
		"phone": phone,
		"name": name or "",
		"status": "scheduled",
	}
	res = col.insert_one(doc)
	return str(res.inserted_id)


def list_tasks(limit: int = 100) -> list[Dict[str, Any]]:
	col = get_collection()
	docs = col.find({}, sort=[("time", ASCENDING)], limit=limit)
	result = []
	for d in docs:
		result.append({
			"task_id": str(d.get("_id")),
			"title": d.get("title", ""),
			"time": d.get("time").astimezone(timezone).strftime(ISO_FORMAT) if d.get("time") else None,
			"phone": d.get("phone", ""),
			"name": d.get("name", ""),
			"status": d.get("status", ""),
		})
	return result


def find_due_tasks(now: Optional[datetime] = None) -> list[Dict[str, Any]]:
	col = get_collection()
	current = to_aware_datetime(now or datetime.now(timezone))
	# match tasks scheduled up to current minute and not yet completed/called
	window_start = current.replace(second=0, microsecond=0)
	window_end = window_start.replace(second=59, microsecond=999999)
	q = {
		"status": {"$in": ["scheduled", "retry"]},
		"time": {"$gte": window_start, "$lte": window_end},
	}
	return list(col.find(q))


def mark_task_status(task_id: Any, status: str, extra: Optional[Dict[str, Any]] = None) -> None:
	col = get_collection()
	update: Dict[str, Any] = {"$set": {"status": status}}
	if extra:
		update["$set"].update(extra)
	col.update_one({"_id": task_id}, update)

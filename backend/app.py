from typing import Any, Dict
from bson import ObjectId

from flask import Flask, jsonify, request, Response, abort
from flask_cors import CORS

from config import settings
from db import insert_task, list_tasks, get_collection
from scheduler import start_scheduler
from twilio_service import build_twiml


app = Flask(__name__)
CORS(app, origins=settings.cors_origins)


@app.route("/health", methods=["GET"])
def health() -> Any:
	return jsonify({"status": "ok"})


@app.route("/add-task", methods=["POST"])
def add_task() -> Any:
	payload: Dict[str, Any] = request.get_json(force=True) or {}
	title = (payload.get("title") or "").strip()
	time_value = (payload.get("time") or "").strip()
	phone = (payload.get("phone") or "").strip()
	name = (payload.get("name") or "").strip()

	if not title or not time_value or not phone:
		return jsonify({"error": "title, time and phone are required"}), 400

	task_id = insert_task(title=title, time_value=time_value, phone=phone, name=name)
	return jsonify({"task_id": task_id})


@app.route("/tasks", methods=["GET"])
def tasks() -> Any:
	return jsonify(list_tasks())


@app.route("/voice", methods=["POST", "GET"])  # Twilio will call this URL
def voice() -> Response:
	secret = request.args.get("secret") or request.form.get("secret")
	if secret != settings.twilio_voice_webhook_secret:
		abort(403)

	title = request.args.get("title") or request.form.get("title") or ""
	name = request.args.get("name") or request.form.get("name") or ""
	task_id = request.args.get("task_id") or request.form.get("task_id") or ""

	# mark as completed when webhook is hit
	if task_id:
		try:
			col = get_collection()
			col.update_one({"_id": ObjectId(task_id)}, {"$set": {"status": "completed"}})
		except Exception:
			pass

	twiml = build_twiml(task_title=title, name=name)
	return Response(twiml, mimetype="text/xml")


if __name__ == "__main__":
	start_scheduler()
	app.run(host=settings.flask_host, port=settings.flask_port, debug=(settings.flask_env == "development"))

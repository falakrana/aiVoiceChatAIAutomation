# AI-Powered Task Reminder with Automated Phone Calls

Full-stack demo: React + Tailwind front-end, Flask back-end, MongoDB Atlas, APScheduler, and Twilio Voice.

## Features
- Add tasks with title, time, and phone number
- View upcoming tasks
- Automatic phone call at scheduled time with spoken reminder via Twilio TTS

## Tech Stack
- Frontend: React + Vite + Tailwind CSS (TypeScript)
- Backend: Flask (Python)
- Database: MongoDB Atlas
- Scheduler: APScheduler (runs every minute)
- Calls: Twilio Voice API (TwiML webhook)

---

## Prerequisites
- Node.js 18+
- Python 3.11+
- A MongoDB Atlas cluster and connection string
- A Twilio account with a verified phone number and a Voice-capable phone number
- ngrok (or similar) to expose your local Flask webhook to Twilio

---

## Backend Setup

1) Create a virtual environment and install deps:

```bash
cd backend
python -m venv .venv
# Windows PowerShell
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
```

2) Configure environment variables:

Create a `.env` file in `backend/` using the following keys:

```
FLASK_ENV=development
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

MONGODB_URI=YOUR_ATLAS_URI
MONGODB_DB_NAME=task_reminders
MONGODB_COLLECTION_NAME=tasks

TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_CALLER_NUMBER=+1234567890
TWILIO_VOICE_WEBHOOK_SECRET=choose_a_random_secret

TIMEZONE=UTC
CHECK_INTERVAL_SECONDS=60

APP_BASE_URL=http://localhost:5000
```

3) Run the backend:

```bash
# From backend directory with venv active
python app.py
```

4) Expose the `/voice` webhook publicly for Twilio:

```bash
# In a separate terminal
ngrok http http://localhost:5000
```
Copy the public URL, e.g. `https://abcd-1234.ngrok-free.app`. Update `APP_BASE_URL` in your backend `.env`:

```
APP_BASE_URL=https://abcd-1234.ngrok-free.app
```
Restart the Flask app after changes.

5) Twilio setup:
- Buy/assign a Voice-capable number and set it as `TWILIO_CALLER_NUMBER`
- No need to set a webhook in the Twilio console; the app passes a per-call URL to Twilio including the secret
- Ensure the destination phone is verified if you are on a trial account

---

## Frontend Setup

```bash
cd frontend
npm install
```

Create `frontend/.env` with:

```
VITE_API_BASE=http://localhost:5000
```

Run the dev server:

```bash
npm run dev
```

Open the app at the shown localhost URL (typically `http://localhost:5173`).

---

## Usage
1) In the UI, add a task with title, time (local), phone number in E.164, and optional name
2) The task appears in the Upcoming list
3) At the scheduled minute, the back-end checks and places the call via Twilio
4) When Twilio requests `/voice`, the app responds with TwiML to speak the reminder

---

## Notes
- Time sent by the frontend is normalized by the backend to the configured `TIMEZONE`
- Scheduler polls every `CHECK_INTERVAL_SECONDS`; default 60s
- Statuses: `scheduled` → `called` → `completed` (after `/voice`), or `retry` if call failed
- For production, consider a queue, retries, and idempotency (e.g., only one call per task)

---

## Troubleshooting
- Calls not placed? Check that `MONGODB_URI`, Twilio credentials, and `TWILIO_CALLER_NUMBER` are valid
- Twilio 403 on `/voice`? Ensure `TWILIO_VOICE_WEBHOOK_SECRET` in the `.env` matches the URL param
- No voice or wrong text? Inspect server logs to see the generated TwiML
- Time mismatch? Verify `TIMEZONE` and the time sent from the browser

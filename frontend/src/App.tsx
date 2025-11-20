import { useEffect, useMemo, useState } from "react";

interface TaskItem {
	task_id: string;
	title: string;
	time: string;
	phone: string;
	name?: string;
	status: string;
}

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:5000";

function formatLocal(dtIso: string) {
	try {
		const d = new Date(dtIso);
		return new Intl.DateTimeFormat(undefined, {
			year: "numeric",
			month: "short",
			day: "2-digit",
			hour: "2-digit",
			minute: "2-digit",
		}).format(d);
	} catch {
		return dtIso;
	}
}

export default function App() {
	const [title, setTitle] = useState("");
	const [time, setTime] = useState("");
	const [phone, setPhone] = useState("");
	const [name, setName] = useState("");
	const [loading, setLoading] = useState(false);
	const [tasks, setTasks] = useState<TaskItem[]>([]);
	const [error, setError] = useState<string | null>(null);

	async function fetchTasks() {
		try {
			const res = await fetch(`${API_BASE}/tasks`);
			const data = await res.json();
			setTasks(data);
		} catch (e: any) {
			setError(e?.message || "Failed to load tasks");
		}
	}

	useEffect(() => {
		fetchTasks();
		const id = setInterval(fetchTasks, 5000);
		return () => clearInterval(id);
	}, []);

	async function onSubmit(e: React.FormEvent) {
		e.preventDefault();
		setError(null);
		setLoading(true);
		try {
			// Convert local datetime-local to ISO with timezone offset approximated as local
			// The backend will normalize to configured timezone
			const dt = new Date(time);
			const iso = new Date(dt.getTime() - dt.getTimezoneOffset() * 60000).toISOString().slice(0, 19) + "+00:00";

			const res = await fetch(`${API_BASE}/add-task`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ title, time: iso, phone, name }),
			});
			if (!res.ok) {
				const d = await res.json().catch(() => ({}));
				throw new Error(d.error || `Failed (${res.status})`);
			}
			setTitle("");
			setTime("");
			setPhone("");
			setName("");
			await fetchTasks();
		} catch (e: any) {
			setError(e?.message || "Failed to add task");
		} finally {
			setLoading(false);
		}
	}

	const upcoming = useMemo(() => tasks, [tasks]);

	return (
		<div className="min-h-screen bg-gray-50 text-gray-900">
			<div className="mx-auto max-w-3xl p-6">
				<h1 className="text-2xl font-bold mb-4">AI-Powered Task Reminder</h1>
				<form onSubmit={onSubmit} className="grid gap-3 bg-white p-4 rounded-md shadow">
					<div className="grid gap-1">
						<label className="text-sm">Task title</label>
						<input className="border rounded px-3 py-2" value={title} onChange={e => setTitle(e.target.value)} placeholder="Revision of software development" required />
					</div>
					<div className="grid gap-1">
						<label className="text-sm">Time</label>
						<input type="datetime-local" className="border rounded px-3 py-2" value={time} onChange={e => setTime(e.target.value)} required />
					</div>
					<div className="grid gap-1">
						<label className="text-sm">Phone number (E.164)</label>
						<input className="border rounded px-3 py-2" value={phone} onChange={e => setPhone(e.target.value)} placeholder="+1234567890" required />
					</div>
					<div className="grid gap-1">
						<label className="text-sm">Name (optional)</label>
						<input className="border rounded px-3 py-2" value={name} onChange={e => setName(e.target.value)} placeholder="John" />
					</div>
					<div className="flex gap-2 items-center">
						<button disabled={loading} className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded disabled:opacity-60">{loading ? "Adding..." : "Add task"}</button>
						{error && <span className="text-red-600 text-sm">{error}</span>}
					</div>
				</form>

				<h2 className="text-xl font-semibold mt-8 mb-3">Upcoming tasks</h2>
				<div className="bg-white rounded-md shadow divide-y">
					{upcoming.length === 0 && <div className="p-4 text-sm text-gray-500">No tasks yet.</div>}
					{upcoming.map(t => (
						<div key={t.task_id} className="p-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
							<div>
								<div className="font-medium">{t.title}</div>
								<div className="text-sm text-gray-600">{formatLocal(t.time)} • {t.phone}</div>
							</div>
							<span className="text-xs px-2 py-1 rounded bg-gray-100 text-gray-700 uppercase tracking-wide">{t.status}</span>
						</div>
					))}
				</div>
			</div>
		</div>
	);
}

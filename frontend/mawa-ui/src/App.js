import React, { useState, useEffect, useRef, useCallback } from "react";
import axios from "axios";

const API = "http://127.0.0.1:5000/api";

// ── Voice Setup ──────────────────────────────────────
const speakText = (text) => {
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 1.0;
  utterance.pitch = 1.6;
  utterance.volume = 1;

  const setVoice = () => {
    const voices = window.speechSynthesis.getVoices();
    const preferred = [
      v => v.name.includes("Heera"),
      v => v.name.includes("Swara"),
      v => v.name.includes("Zira"),
      v => v.lang === "hi-IN",
      v => v.name.toLowerCase().includes("female"),
      v => v.lang.startsWith("en") && v.name.toLowerCase().includes("female"),
    ];
    for (const fn of preferred) {
      const found = voices.find(fn);
      if (found) { utterance.voice = found; break; }
    }
    window.speechSynthesis.speak(utterance);
  };

  if (window.speechSynthesis.getVoices().length === 0) {
    window.speechSynthesis.onvoiceschanged = setVoice;
  } else {
    setVoice();
  }
};
  const TaskInput = ({ onAdd }) => {
  const [task, setTask] = useState("");
  const [time, setTime] = useState("");

  const handleAdd = () => {
    if (!task.trim()) return;
    onAdd(task, time);
    setTask("");
    setTime("");
  };

  return (
    <div style={{ display: "flex", gap: "8px" }}>
      <input
        style={{ flex: 2, padding: "9px 14px", borderRadius: "9px", border: "1px solid #1e1e3f", background: "#080814", color: "#e8e8ff", fontSize: "13px", outline: "none" }}
        placeholder="Task name..."
        value={task}
        onChange={e => setTask(e.target.value)}
        onKeyDown={e => e.key === "Enter" && handleAdd()}
        autoComplete="off"
        spellCheck="false"
      />
      <input
        style={{ flex: 1, padding: "9px 14px", borderRadius: "9px", border: "1px solid #1e1e3f", background: "#080814", color: "#e8e8ff", fontSize: "13px", outline: "none" }}
        placeholder="8:00 AM"
        value={time}
        onChange={e => setTime(e.target.value)}
        autoComplete="off"
      />
      <button
        style={{ padding: "7px 14px", borderRadius: "8px", background: "#7c5cfc", color: "white", border: "none", cursor: "pointer", fontSize: "12px", fontWeight: "600" }}
        onClick={handleAdd}
      >Add</button>
    </div>
  );
};
// ── Main App ─────────────────────────────────────────
export default function App() {
  const [dark, setDark] = useState(true);
  const [tab, setTab] = useState("home");
  const [messages, setMessages] = useState([
    { from: "mawa", text: "Namaste Krishna! Main Mawa hoon 🙏 Aaj main aapki kya madad kar sakti hoon?" }
  ]);
  const [chatInput, setChatInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);
  const [tasks, setTasks] = useState([]);
  const [reminders, setReminders] = useState([]);
  const [habits, setHabits] = useState([]);
  const [routine, setRoutine] = useState([]);
  const [weather, setWeather] = useState("");
  const [briefing, setBriefing] = useState("");
  const [news, setNews] = useState("");
  const [newTask, setNewTask] = useState("");
  const [newTaskTime, setNewTaskTime] = useState("");
  const bottomRef = useRef(null);
  const inputRef = useRef(null);
  const recogRef = useRef(null);

  // fetch data
  const fetchAll = useCallback(async () => {
    try {
      const [t, r, h, ro, w, br] = await Promise.all([
        axios.get(`${API}/tasks`),
        axios.get(`${API}/reminders`),
        axios.get(`${API}/habits`),
        axios.get(`${API}/routine`),
        axios.get(`${API}/weather`),
        axios.get(`${API}/briefing`),
      ]);
      setTasks(t.data);
      setReminders(r.data);
      setHabits(h.data);
      setRoutine(ro.data);
      setWeather(w.data.weather);
      setBriefing(br.data.briefing);
    } catch (e) { console.error(e); }
  }, []);

  useEffect(() => { fetchAll(); }, [fetchAll]);
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  // send message
  const sendMessage = useCallback(async (text) => {
    if (!text.trim()) return;
    setMessages(prev => [...prev, { from: "user", text }]);
    setChatInput("");
    setLoading(true);
    try {
  // Detect Hindi words
      const hindiWords = ["namaste", "namaskar", "kya", "hai", "mera", "tera",
        "aaj", "kal", "karo", "batao", "dikhao", "accha", "haan", "nahi",
        "mausam", "abhi", "bahut", "aur", "alvida", "madad", "chahiye",
        "hain", "gaya", "mein", "kaisa", "kaise", "subah", "shaam"];
      const words = text.toLowerCase().split(" ");
      const hindiCount = words.filter(w => hindiWords.includes(w)).length;
      const hindiChars = [...text].filter(c => c >= '\u0900' && c <= '\u097F').length;
      const detectedLang = (hindiCount >= 1 || hindiChars > 0) ? "hindi" : "english";

      const res = await axios.post(`${API}/chat`, { message: text, language: detectedLang });  
      let reply = "";
      const responseData = res.data.response;
      
      if (typeof responseData === "string") {
        reply = responseData;
      } else if (responseData?.type === "tasks") {
        const isHindi = responseData.language === "hindi";
        if (responseData.data.length === 0) {
          reply = isHindi ? "Krishna, koi pending task nahi hai!" : "You have no pending tasks Krishna!";
        } else {
          reply = isHindi ? "Krishna, aapke tasks:\n" : "Here are your tasks Krishna:\n";
          responseData.data.forEach(t => {
            reply += `• ${t.task}${t.time ? ` at ${t.time}` : ""}\n`;
          });
        }
      } else if (responseData?.type === "reminders") {
        if (responseData.data.length === 0) {
          reply = "You have no reminders Krishna!";
        } else {
          reply = "Here are your reminders Krishna:\n";
          responseData.data.forEach(r => {
            reply += `• ${r.title} at ${r.time}\n`;
          });
        }
      } else if (responseData?.type === "habits") {
        if (responseData.data.length === 0) {
          reply = "No habits tracked yet Krishna!";
        } else {
          reply = "Here are your habits Krishna:\n";
          responseData.data.forEach(h => {
            reply += `• ${h.done ? "✅" : "⬜"} ${h.name}\n`;
          });
        }
      } else if (responseData?.type === "routine") {
        if (responseData.data.length === 0) {
          reply = "No routine set yet Krishna!";
        } else {
          reply = "Here is your daily routine Krishna:\n";
          responseData.data.forEach(r => {
            reply += `• ${r.time} — ${r.activity}\n`;
          });
        }
      } else {
        reply = JSON.stringify(responseData);
      }
      setMessages(prev => [...prev, { from: "mawa", text: reply }]);
      speakText(reply);
      fetchAll();
    } catch {
      setMessages(prev => [...prev, { from: "mawa", text: "Sorry Krishna, something went wrong!" }]);
    }
    setLoading(false);
  }, [fetchAll]);

  // voice
  const toggleListen = () => {
    if (listening) { recogRef.current?.stop(); return; }
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) { alert("Use Chrome browser for voice!"); return; }
    const r = new SR();
    r.lang = "en-IN";
    r.onstart = () => setListening(true);
    r.onresult = e => { const t = e.results[0][0].transcript; setChatInput(t); sendMessage(t); };
    r.onend = () => setListening(false);
    recogRef.current = r;
    r.start();
  };

  const addTask = async () => {
    if (!newTask.trim()) return;
    await axios.post(`${API}/tasks`, { task: newTask, time: newTaskTime || null });
    setNewTask(""); setNewTaskTime(""); fetchAll();
  };

  const fmtTime = (t) => {
    try { return new Date(t).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", hour12: true }); }
    catch { return t; }
  };

  // ── Theme ─────────────────────────────────────────
  const c = {
    bg: dark ? "#080814" : "#f5f5ff",
    sidebar: dark ? "#0d0d1f" : "#ffffff",
    card: dark ? "#12122a" : "#ffffff",
    text: dark ? "#e8e8ff" : "#12122a",
    sub: dark ? "#8888aa" : "#6666aa",
    border: dark ? "#1e1e3f" : "#e0e0ff",
    accent: "#7c5cfc",
    pink: "#fc5c9c",
    green: "#22d98a",
    yellow: "#fcd34d",
  };

  const s = {
    app: { display: "flex", height: "100vh", background: c.bg, color: c.text, fontFamily: "'Segoe UI', Tahoma, sans-serif", overflow: "hidden" },
    sidebar: { width: "200px", minWidth: "200px", background: c.sidebar, borderRight: `1px solid ${c.border}`, display: "flex", flexDirection: "column" },
    logo: { padding: "24px 20px 20px", borderBottom: `1px solid ${c.border}` },
    logoText: { fontSize: "20px", fontWeight: "800", background: `linear-gradient(135deg, ${c.accent}, ${c.pink})`, WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" },
    nav: (active) => ({ display: "flex", alignItems: "center", gap: "10px", padding: "11px 18px", margin: "2px 8px", borderRadius: "10px", cursor: "pointer", fontSize: "14px", fontWeight: active ? "600" : "400", background: active ? `${c.accent}20` : "transparent", color: active ? c.accent : c.sub, transition: "all 0.15s" }),
    main: { flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" },
    topbar: { padding: "14px 24px", borderBottom: `1px solid ${c.border}`, display: "flex", justifyContent: "space-between", alignItems: "center", background: c.sidebar },
    scroll: { flex: 1, overflowY: "auto", padding: "20px 24px" },
    card: { background: c.card, border: `1px solid ${c.border}`, borderRadius: "14px", padding: "18px", marginBottom: "16px" },
    cardTitle: { fontSize: "15px", fontWeight: "600", color: c.accent, marginBottom: "14px", display: "flex", alignItems: "center", gap: "8px" },
    row: { display: "flex", alignItems: "center", gap: "10px", padding: "9px 0", borderBottom: `1px solid ${c.border}`, fontSize: "14px" },
    btn: (bg) => ({ padding: "7px 14px", borderRadius: "8px", background: bg, color: "white", border: "none", cursor: "pointer", fontSize: "12px", fontWeight: "600" }),
    input: { padding: "9px 14px", borderRadius: "9px", border: `1px solid ${c.border}`, background: c.bg, color: c.text, fontSize: "13px", outline: "none", width: "100%" },
    grid2: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" },
  };

  // ── Views ─────────────────────────────────────────
  const HomeView = () => (
    <div>
      <div style={{ background: "linear-gradient(135deg, #1a0a4a, #2a0a5a)", borderRadius: "14px", padding: "20px", marginBottom: "16px", color: "white" }}>
        <div style={{ fontSize: "12px", opacity: 0.7, marginBottom: "6px" }}>📍 Hyderabad, India</div>
        <div style={{ fontSize: "13px", lineHeight: "1.9" }}>{weather}</div>
      </div>
      <div style={s.card}>
        <div style={s.cardTitle}>📋 Today's Briefing</div>
        <div style={{ fontSize: "13px", lineHeight: "1.8", color: c.sub }}>{briefing}</div>
      </div>
      <div style={s.grid2}>
        <div style={s.card}>
          <div style={s.cardTitle}>⏰ Reminders</div>
          {reminders.slice(0, 3).map(r => (
            <div key={r.id} style={s.row}>
              <span>🔔</span>
              <div>
                <div style={{ fontSize: "13px" }}>{r.title}</div>
                <div style={{ fontSize: "11px", color: c.sub }}>{fmtTime(r.time)}</div>
              </div>
            </div>
          ))}
          {!reminders.length && <div style={{ fontSize: "13px", color: c.sub }}>No reminders</div>}
        </div>
        <div style={s.card}>
          <div style={s.cardTitle}>🌟 Habits</div>
          {habits.slice(0, 4).map(h => (
            <div key={h.id} style={s.row}>
              <span>{h.done ? "✅" : "⬜"}</span>
              <span style={{ fontSize: "13px" }}>{h.name}</span>
            </div>
          ))}
          {!habits.length && <div style={{ fontSize: "13px", color: c.sub }}>No habits</div>}
        </div>
      </div>
    </div>
  );

  const TasksView = () => (
    <div>
      <div style={s.card}>
        <div style={s.cardTitle}>➕ Add Task</div>
        <TaskInput onAdd={async (task, time) => {
          await axios.post(`${API}/tasks`, { task, time: time || null });
          fetchAll();
        }} />
      </div>
      <div style={s.card}>
        <div style={s.cardTitle}>📋 Tasks ({tasks.length})</div>
        {tasks.map(t => (
          <div key={t.id} style={s.row}>
            <span>⬜</span>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: "14px" }}>{t.task}</div>
              {t.time && <div style={{ fontSize: "11px", color: c.sub }}>⏰ {t.time}</div>}
            </div>
            <button style={s.btn(c.green)} onClick={() => { axios.post(`${API}/tasks/${t.id}/complete`).then(fetchAll); }}>✓</button>
            <button style={{ ...s.btn("#ef4444"), marginLeft: "6px" }} onClick={() => { axios.delete(`${API}/tasks/${t.id}`).then(fetchAll); }}>✕</button>
          </div>
        ))}
        {!tasks.length && <div style={{ fontSize: "13px", color: c.sub }}>No pending tasks! 🎉</div>}
      </div>
    </div>
  );

  const HabitsView = () => (
    <div style={s.card}>
      <div style={s.cardTitle}>🌟 Today's Habits</div>
      {habits.map(h => (
        <div key={h.id} style={s.row}>
          <span style={{ fontSize: "20px" }}>{h.done ? "✅" : "⬜"}</span>
          <span style={{ flex: 1, fontSize: "14px" }}>{h.name}</span>
          {!h.done
            ? <button style={s.btn(c.accent)} onClick={() => { axios.post(`${API}/habits/${h.id}/complete`).then(fetchAll); }}>Complete</button>
            : <span style={{ fontSize: "12px", color: c.green, fontWeight: "600" }}>Done! 🎉</span>}
        </div>
      ))}
      {!habits.length && <div style={{ fontSize: "13px", color: c.sub }}>No habits! Tell Mawa to add habits.</div>}
    </div>
  );

  const RoutineView = () => (
    <div style={s.card}>
      <div style={s.cardTitle}>🔄 Daily Routine</div>
      {routine.map(r => (
        <div key={r.id} style={s.row}>
          <span style={{ padding: "3px 10px", borderRadius: "99px", background: `${c.accent}20`, color: c.accent, fontSize: "12px", fontWeight: "600", whiteSpace: "nowrap" }}>{r.time}</span>
          <span style={{ fontSize: "14px" }}>{r.activity}</span>
        </div>
      ))}
      {!routine.length && <div style={{ fontSize: "13px", color: c.sub }}>No routine! Tell Mawa: "add routine exercise at 6:00 AM"</div>}
    </div>
  );

  const NewsView = () => (
    <div style={s.card}>
      <div style={s.cardTitle}>📰 Today's News</div>
      <div style={{ fontSize: "13px", lineHeight: "2", whiteSpace: "pre-line", color: c.sub }}>{news || "Click the button below to load today's news!"}</div>
      <button style={{ ...s.btn(c.accent), marginTop: "14px" }} onClick={async () => { const r = await axios.get(`${API}/news`); setNews(r.data.news); }}>🔄 Load News</button>
    </div>
  );

  const tabViews = { home: <HomeView />, tasks: <TasksView />, habits: <HabitsView />, routine: <RoutineView />, news: <NewsView /> };

  const navItems = [
    { id: "home", emoji: "🏠", label: "Home" },
    { id: "chat", emoji: "💬", label: "Chat" },
    { id: "tasks", emoji: "📋", label: "Tasks" },
    { id: "habits", emoji: "🌟", label: "Habits" },
    { id: "routine", emoji: "🔄", label: "Routine" },
    { id: "news", emoji: "📰", label: "News" },
  ];

  return (
    <div style={s.app}>
      {/* Sidebar */}
      <div style={s.sidebar}>
        <div style={s.logo}>
          <div style={s.logoText}>✨ Mawa</div>
          <div style={{ fontSize: "11px", color: c.sub, marginTop: "3px" }}>Your Personal Assistant</div>
        </div>
        <div style={{ flex: 1, padding: "10px 0" }}>
          {navItems.map(item => (
            <div key={item.id} style={s.nav(tab === item.id)} onClick={() => setTab(item.id)}>
              <span>{item.emoji}</span> {item.label}
            </div>
          ))}
        </div>
        <div style={{ padding: "16px 18px", borderTop: `1px solid ${c.border}`, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <span style={{ fontSize: "12px", color: c.sub }}>{dark ? "🌙 Dark" : "☀️ Light"}</span>
          <div onClick={() => setDark(!dark)} style={{ width: "38px", height: "20px", borderRadius: "10px", background: dark ? c.accent : "#ccc", cursor: "pointer", position: "relative", transition: "background 0.2s" }}>
            <div style={{ width: "14px", height: "14px", borderRadius: "50%", background: "white", position: "absolute", top: "3px", left: dark ? "21px" : "3px", transition: "left 0.2s" }} />
          </div>
        </div>
      </div>

      {/* Main */}
      <div style={s.main}>
        {/* Topbar */}
        <div style={s.topbar}>
          <div>
            <div style={{ fontWeight: "700", fontSize: "15px" }}>{navItems.find(n => n.id === tab)?.emoji} {tab.charAt(0).toUpperCase() + tab.slice(1)}</div>
            <div style={{ fontSize: "11px", color: c.sub }}>{new Date().toLocaleDateString("en-IN", { weekday: "long", year: "numeric", month: "long", day: "numeric" })}</div>
          </div>
          <button onClick={fetchAll} style={{ ...s.btn("transparent"), border: `1px solid ${c.border}`, color: c.sub }}>🔄 Refresh</button>
        </div>

        {/* Content */}
        {tab === "chat" ? (
          <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
            {/* Messages */}
            <div style={{ flex: 1, overflowY: "auto", padding: "20px 24px", display: "flex", flexDirection: "column", gap: "12px" }}>
              {messages.map((m, i) => (
                <div key={i} style={{ alignSelf: m.from === "user" ? "flex-end" : "flex-start", maxWidth: "68%" }}>
                  {m.from === "mawa" && <div style={{ fontSize: "11px", color: c.accent, fontWeight: "700", marginBottom: "4px" }}>✨ Mawa</div>}
                  <div style={{
                    padding: "11px 16px", borderRadius: m.from === "user" ? "18px 18px 4px 18px" : "18px 18px 18px 4px",
                    background: m.from === "user" ? `linear-gradient(135deg, ${c.accent}, ${c.pink})` : c.card,
                    border: m.from === "mawa" ? `1px solid ${c.border}` : "none",
                    fontSize: "14px", lineHeight: "1.6", color: m.from === "user" ? "white" : c.text
                  }}>{m.text}</div>
                </div>
              ))}
              {loading && (
                <div style={{ alignSelf: "flex-start", maxWidth: "68%" }}>
                  <div style={{ fontSize: "11px", color: c.accent, fontWeight: "700", marginBottom: "4px" }}>✨ Mawa</div>
                  <div style={{ padding: "11px 16px", borderRadius: "18px 18px 18px 4px", background: c.card, border: `1px solid ${c.border}`, fontSize: "14px", color: c.sub }}>Thinking... 💭</div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>
            {/* Input - FIXED outside component */}
            <div style={{ padding: "14px 24px", borderTop: `1px solid ${c.border}`, display: "flex", gap: "10px", alignItems: "center", background: c.sidebar }}>
              <input
                ref={inputRef}
                style={{ flex: 1, padding: "12px 18px", borderRadius: "25px", border: `1px solid ${c.border}`, background: c.bg, color: c.text, fontSize: "14px", outline: "none" }}
                value={chatInput}
                onChange={e => setChatInput(e.target.value)}
                onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(chatInput); } }}
                placeholder="Type your message..."
                autoComplete="off"
                spellCheck="false"
              />
              <button
                onClick={toggleListen}
                style={{ width: "44px", height: "44px", borderRadius: "50%", background: listening ? c.pink : c.accent, color: "white", border: "none", cursor: "pointer", fontSize: "16px", display: "flex", alignItems: "center", justifyContent: "center" }}
              >
                {listening ? "⏹" : "🎤"}
              </button>
              <button
                onClick={() => sendMessage(chatInput)}
                style={{ padding: "12px 22px", borderRadius: "25px", background: `linear-gradient(135deg, ${c.accent}, ${c.pink})`, color: "white", border: "none", cursor: "pointer", fontWeight: "700", fontSize: "14px" }}
              >
                Send
              </button>
            </div>
          </div>
        ) : (
          <div style={s.scroll}>{tabViews[tab]}</div>
        )}
      </div>
    </div>
  );
}
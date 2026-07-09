import React, { useState, useEffect, useRef, useCallback } from "react";
import axios from "axios";

const API = process.env.REACT_APP_API_URL || "http://127.0.0.1:5000/api";

// Auth Form Component (outside App to prevent re-renders)
const AuthInput = ({ label, type, placeholder, value, onChange, onKeyDown }) => {
  // Use the controlled value directly. Having an internal state here can cause the
  // input to desync with the parent state.
  return (
    <div style={{ marginBottom: "16px" }}>
      <label style={{ fontSize: "13px", color: "#8888aa", marginBottom: "6px", display: "block" }}>{label}</label>
      <input
        type={type || "text"}
        style={{ width: "100%", padding: "12px", borderRadius: "10px", border: "1px solid #1e1e3f", background: "#080814", color: "#e8e8ff", fontSize: "14px", outline: "none", boxSizing: "border-box" }}
        placeholder={placeholder}
        value={value ?? ''}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={onKeyDown}
        autoComplete="new-password"
        inputMode={type === 'password' ? 'text' : undefined}
        spellCheck={false}
      />
    </div>
  );
};



// ── Voice ─────────────────────────────────────────────
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
    ];
    for (const fn of preferred) {
      const found = voices.find(fn);
      if (found) { utterance.voice = found; break; }
    }
    window.speechSynthesis.speak(utterance);
  };
  if (window.speechSynthesis.getVoices().length === 0) {
    window.speechSynthesis.onvoiceschanged = setVoice;
  } else { setVoice(); }
};

// ── Task Input (outside App to prevent re-render) ─────
const TaskInput = ({ onAdd, dark }) => {
  const [task, setTask] = useState("");
  const [time, setTime] = useState("");
  const border = dark ? "#1e1e3f" : "#e0e0ff";
  const bg = dark ? "#080814" : "#f5f5ff";
  const text = dark ? "#e8e8ff" : "#12122a";
  const accent = "#7c5cfc";

  const handleAdd = () => {
    if (!task.trim()) return;
    onAdd(task, time);
    setTask(""); setTime("");
  };

  return (
    <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
      <input
        style={{ flex: "2 1 140px", padding: "9px 14px", borderRadius: "9px", border: `1px solid ${border}`, background: bg, color: text, fontSize: "13px", outline: "none", minWidth: "120px" }}
        placeholder="Task name..."
        value={task}
        onChange={e => setTask(e.target.value)}
        onKeyDown={e => e.key === "Enter" && handleAdd()}
        autoComplete="off"
        spellCheck="false"
      />
      <input
        style={{ flex: "1 1 100px", padding: "9px 14px", borderRadius: "9px", border: `1px solid ${border}`, background: bg, color: text, fontSize: "13px", outline: "none", minWidth: "90px" }}
        placeholder="8:00 AM"
        value={time}
        onChange={e => setTime(e.target.value)}
        autoComplete="off"
      />
      <button
        style={{ padding: "9px 18px", borderRadius: "9px", background: accent, color: "white", border: "none", cursor: "pointer", fontSize: "13px", fontWeight: "600", whiteSpace: "nowrap" }}
        onClick={handleAdd}
      >Add</button>
    </div>
  );
};

// ── Main App ──────────────────────────────────────────
export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem('mawa_token'));
  const [authMode, setAuthMode] = useState('login');
  const [authForm, setAuthForm] = useState({ name: '', email: '', password: '' });
  const [authError, setAuthError] = useState('');
  const [authLoading, setAuthLoading] = useState(false);
  const [dark, setDark] = useState(true);
  const [tab, setTab] = useState("home");
  const [messages, setMessages] = useState([
    { from: "mawa", text: `Namaste ${localStorage.getItem('mawa_name') || 'Krishna'}! Main Mawa hoon 🙏 Aaj main aapki kya madad kar sakti hoon?` }
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
  const [musicResults, setMusicResults] = useState([]);
  const [currentSong, setCurrentSong] = useState(null);
  // eslint-disable-next-line
  const [isPlaying, setIsPlaying] = useState(false);
  const [showMusic, setShowMusic] = useState(false);
  const audioRef = useRef(null);
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const bottomRef = useRef(null);
  const recogRef = useRef(null);

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth <= 768);
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);
  const handleRegister = async () => {
    setAuthLoading(true);
    setAuthError('');
    try {
      const res = await axios.post(`${API}/register`, authForm);
      if (res.data.success) {
        localStorage.setItem('mawa_token', res.data.token);
        localStorage.setItem('mawa_name', res.data.name);
        setUserName(res.data.name);
        setIsLoggedIn(true);
      } else {
        setAuthError(res.data.error);
      }
    } catch (e) {
      setAuthError('Something went wrong!');
    }
    setAuthLoading(false);
  };

  const handleLogin = async () => {
    setAuthLoading(true);
    setAuthError('');
    try {
      const res = await axios.post(`${API}/login`, {
        email: authForm.email,
        password: authForm.password
      });
      if (res.data.success) {
        localStorage.setItem('mawa_token', res.data.token);
        localStorage.setItem('mawa_name', res.data.name);
        setUserName(res.data.name);
        setIsLoggedIn(true);
      } else {
        setAuthError(res.data.error);
      }
    } catch (e) {
      setAuthError('Something went wrong!');
    }
    setAuthLoading(false);
  };

  const handleLogout = () => {
    localStorage.removeItem('mawa_token');
    localStorage.removeItem('mawa_name');
    setIsLoggedIn(false);
    setUserName('');
  };
  const fetchAll = useCallback(async () => {
    try {
      // Fetch tasks, reminders, habits, routine first
      const [t, r, h, ro] = await Promise.all([
        axios.get(`${API}/tasks`),
        axios.get(`${API}/reminders`),
        axios.get(`${API}/habits`),
        axios.get(`${API}/routine`),
      ]);
      setTasks(t.data);
      setReminders(r.data);
      setHabits(h.data);
      setRoutine(ro.data);
    } catch (e) { console.error("Data fetch error:", e); }

    // Fetch weather separately
    try {
      const w = await axios.get(`${API}/weather`, { timeout: 15000 });
      setWeather(w.data.weather);
    } catch (e) {
      console.error("Weather fetch error:", e);
      setWeather("Weather temporarily unavailable. Please refresh!");
    }

    // Fetch briefing separately
    try {
      const br = await axios.get(`${API}/briefing`, { timeout: 15000 });
      setBriefing(br.data.briefing);
    } catch (e) {
      console.error("Briefing fetch error:", e);
      setBriefing("Briefing temporarily unavailable. Please refresh!");
    }
  }, []);

  useEffect(() => { fetchAll(); }, [fetchAll]);
  // Keep Render server awake
  useEffect(() => {
    const keepAlive = setInterval(() => {
      axios.get(`${API.replace('/api', '')}/ping`).catch(() => {});
    }, 10 * 60 * 1000); // ping every 10 minutes
    return () => clearInterval(keepAlive);
  }, []);
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const sendMessage = useCallback(async (text) => {
    if (!text.trim()) return;
    setMessages(prev => [...prev, { from: "user", text }]);
    setChatInput("");
    setLoading(true);
    try {
      const hindiWords = ["namaste","namaskar","kya","hai","mera","tera","aaj","kal","karo","batao","dikhao","accha","haan","nahi","mausam","abhi","bahut","aur","alvida","madad","chahiye","hain","gaya","mein","kaisa","kaise","subah","shaam"];
      const words = text.toLowerCase().split(" ");
      const hindiCount = words.filter(w => hindiWords.includes(w)).length;
      const hindiChars = [...text].filter(c => c >= '\u0900' && c <= '\u097F').length;
      const detectedLang = (hindiCount >= 1 || hindiChars > 0) ? "hindi" : "english";

      const res = await axios.post(`${API}/chat`, { message: text, language: detectedLang });
      const responseData = res.data.response;
      let reply = "";
      console.log("Response data:", responseData);
      console.log("Response type:", typeof responseData);

      if (typeof responseData === "string") {
        reply = responseData;
      } else if (responseData?.type === "tasks") {
        const isHindi = responseData.language === "hindi";
        reply = isHindi ? "Krishna, aapke tasks:\n" : "Here are your tasks Krishna:\n";
        responseData.data.forEach(t => { reply += `• ${t.task}${t.time ? ` at ${t.time}` : ""}\n`; });
      } else if (responseData?.type === "reminders") {
        reply = "Here are your reminders Krishna:\n";
        responseData.data.forEach(r => { reply += `• ${r.title} at ${r.time}\n`; });
      } else if (responseData?.type === "habits") {
        reply = "Here are your habits Krishna:\n";
        responseData.data.forEach(h => { reply += `• ${h.done ? "✅" : "⬜"} ${h.name}\n`; });
      } else if (responseData?.type === "routine") {
} else if (responseData?.type === "music") {
        setCurrentSong(null);
        setMusicResults(responseData.data);
        setShowMusic(true);
        reply = `Found ${responseData.data.length} songs Krishna! Check the music player below! 🎵`;
      }
  

      setMessages(prev => [...prev, { from: "mawa", text: reply }]);
      speakText(reply);
      fetchAll();
    } catch {
      setMessages(prev => [...prev, { from: "mawa", text: "Sorry Krishna, something went wrong!" }]);
    }
    setLoading(false);
  }, [fetchAll]);
  

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

  const fmtTime = (t) => {
    try { return new Date(t).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", hour12: true }); }
    catch { return t; }
  };

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
  };

  const s = {
    app: { display: "flex", height: "100vh", background: c.bg, color: c.text, fontFamily: "'Segoe UI', Tahoma, sans-serif", overflow: "hidden", flexDirection: isMobile ? "column" : "row" },
    sidebar: { width: "210px", minWidth: "210px", background: c.sidebar, borderRight: `1px solid ${c.border}`, display: "flex", flexDirection: "column" },
    mobileSidebar: { position: "fixed", top: 0, left: 0, right: 0, bottom: 0, background: c.sidebar, zIndex: 1000, display: "flex", flexDirection: "column", padding: "20px" },
    bottomNav: { display: "flex", position: "fixed", bottom: 0, left: 0, right: 0, background: c.sidebar, borderTop: `1px solid ${c.border}`, padding: "8px 0 12px", justifyContent: "space-around", alignItems: "center", zIndex: 100 },
    bottomNavItem: (active) => ({ display: "flex", flexDirection: "column", alignItems: "center", gap: "3px", cursor: "pointer", padding: "4px 8px", borderRadius: "10px", background: active ? `${c.accent}20` : "transparent", color: active ? c.accent : c.sub }),
    main: { flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" },
    topbar: { padding: isMobile ? "12px 16px" : "14px 24px", borderBottom: `1px solid ${c.border}`, display: "flex", justifyContent: "space-between", alignItems: "center", background: c.sidebar },
    scroll: { flex: 1, overflowY: "auto", padding: isMobile ? "12px 14px 80px" : "20px 24px" },
    card: { background: c.card, border: `1px solid ${c.border}`, borderRadius: "14px", padding: isMobile ? "14px" : "18px", marginBottom: "14px" },
    cardTitle: { fontSize: "15px", fontWeight: "600", color: c.accent, marginBottom: "12px", display: "flex", alignItems: "center", gap: "8px" },
    row: { display: "flex", alignItems: "center", gap: "10px", padding: "9px 0", borderBottom: `1px solid ${c.border}`, fontSize: "14px" },
    btn: (bg) => ({ padding: "7px 14px", borderRadius: "8px", background: bg, color: "white", border: "none", cursor: "pointer", fontSize: "12px", fontWeight: "600" }),
    inp: { padding: "9px 14px", borderRadius: "9px", border: `1px solid ${c.border}`, background: c.bg, color: c.text, fontSize: "13px", outline: "none", width: "100%" },
    grid2: { display: "grid", gridTemplateColumns: isMobile ? "1fr" : "1fr 1fr", gap: "14px" },
    logoText: { fontSize: "18px", fontWeight: "800", background: `linear-gradient(135deg, ${c.accent}, ${c.pink})`, WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" },
    nav: (active) => ({ display: "flex", alignItems: "center", gap: "10px", padding: "11px 18px", margin: "2px 8px", borderRadius: "10px", cursor: "pointer", fontSize: "14px", fontWeight: active ? "600" : "400", background: active ? `${c.accent}20` : "transparent", color: active ? c.accent : c.sub, transition: "all 0.15s" }),
  };

  const navItems = [
    { id: "home", emoji: "🏠", label: "Home" },
    { id: "chat", emoji: "💬", label: "Chat" },
    { id: "tasks", emoji: "📋", label: "Tasks" },
    { id: "habits", emoji: "🌟", label: "Habits" },
    { id: "routine", emoji: "🔄", label: "Routine" },
    { id: "news", emoji: "📰", label: "News" },
  ];

  const HomeView = () => (
    <div>
      <div style={{ background: "linear-gradient(135deg, #1a0a4a, #2a0a5a)", borderRadius: "14px", padding: "16px", marginBottom: "14px", color: "white" }}>
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
        <TaskInput dark={dark} onAdd={async (task, time) => {
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
            <button style={s.btn(c.green)} onClick={() => axios.post(`${API}/tasks/${t.id}/complete`).then(fetchAll)}>✓</button>
            <button style={{ ...s.btn("#ef4444"), marginLeft: "6px" }} onClick={() => axios.delete(`${API}/tasks/${t.id}`).then(fetchAll)}>✕</button>
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
            ? <button style={s.btn(c.accent)} onClick={() => axios.post(`${API}/habits/${h.id}/complete`).then(fetchAll)}>Complete</button>
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

  const SidebarContent = () => (
    <>
      <div style={{ padding: "20px 20px 16px", borderBottom: `1px solid ${c.border}`, textAlign: "center" }}>
        <img src="/Mawa-logo.png" alt="Mawa Logo" style={{ width: "60px", height: "60px", objectFit: "contain", borderRadius: "12px", mixBlendMode: "screen" }} />
        <div style={s.logoText}>MAWA</div>
        <div style={{ fontSize: "10px", color: c.sub, marginTop: "2px" }}>Your Personal AI Assistant</div>
      </div>
      <div style={{ flex: 1, padding: "10px 0", overflowY: "auto" }}>
        {navItems.map(item => (
          <div key={item.id} style={s.nav(tab === item.id)} onClick={() => { setTab(item.id); setSidebarOpen(false); }}>
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
    </>
  );
const AuthPage = () => (
    <div style={{ minHeight: "100vh", background: c.bg, display: "flex", alignItems: "center", justifyContent: "center", padding: "20px" }}>
      <div style={{ width: "100%", maxWidth: "400px" }}>
        {/* Logo */}
        <div style={{ textAlign: "center", marginBottom: "32px" }}>
          <img src="/Mawa-logo.png" alt="Mawa" style={{ width: "80px", height: "80px", objectFit: "contain", mixBlendMode: "screen" }} />
          <div style={{ fontSize: "28px", fontWeight: "800", background: `linear-gradient(135deg, ${c.accent}, ${c.pink})`, WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>MAWA</div>
          <div style={{ fontSize: "13px", color: c.sub }}>Your Personal AI Assistant</div>
        </div>

        {/* Card */}
        <div style={{ background: c.card, border: `1px solid ${c.border}`, borderRadius: "16px", padding: "28px" }}>
          <div style={{ display: "flex", marginBottom: "24px", background: c.bg, borderRadius: "10px", padding: "4px" }}>
            <button onClick={() => setAuthMode('login')} style={{ flex: 1, padding: "8px", borderRadius: "8px", border: "none", background: authMode === 'login' ? c.accent : "transparent", color: authMode === 'login' ? "white" : c.sub, cursor: "pointer", fontWeight: "600", fontSize: "14px" }}>Login</button>
            <button onClick={() => setAuthMode('register')} style={{ flex: 1, padding: "8px", borderRadius: "8px", border: "none", background: authMode === 'register' ? c.accent : "transparent", color: authMode === 'register' ? "white" : c.sub, cursor: "pointer", fontWeight: "600", fontSize: "14px" }}>Register</button>
          </div>

          {/* Show name only during register, not login */}
          {authMode === 'register' && (
            <AuthInput
              label="Your Name"
              placeholder="Joffrey Smith"
              value={authForm.name}
              onChange={val => setAuthForm(prev => ({ ...prev, name: val }))}
            />
          )}


          <AuthInput
                label="Email"
                placeholder="your@email.com"
                value={authForm.email}
                onChange={val => setAuthForm(prev => ({ ...prev, email: val }))}
              />

          <AuthInput
                label="Password"
                type="password"
                placeholder="••••••••"
                value={authForm.password}
                onChange={val => setAuthForm(prev => ({ ...prev, password: val }))}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    authMode === 'login' ? handleLogin() : handleRegister();
                  }
                }}
              />


          {authError && (
            <div style={{ background: "#fee2e2", border: "1px solid #fca5a5", borderRadius: "8px", padding: "10px 14px", fontSize: "13px", color: "#dc2626", marginBottom: "16px" }}>
              {authError}
            </div>
          )}

          <button
            onClick={authMode === 'login' ? handleLogin : handleRegister}
            disabled={authLoading}
            style={{ width: "100%", padding: "14px", borderRadius: "10px", background: `linear-gradient(135deg, ${c.accent}, ${c.pink})`, color: "white", border: "none", cursor: "pointer", fontWeight: "700", fontSize: "15px" }}
          >
            {authLoading ? "Please wait..." : authMode === 'login' ? "Login to Mawa" : "Create Account"}
          </button>

          <div style={{ textAlign: "center", marginTop: "16px", fontSize: "13px", color: c.sub }}>
            {authMode === 'login' ? "Don't have an account? " : "Already have an account? "}
            <span onClick={() => setAuthMode(authMode === 'login' ? 'register' : 'login')} style={{ color: c.accent, cursor: "pointer", fontWeight: "600" }}>
              {authMode === 'login' ? 'Register' : 'Login'}
            </span>
          </div>
        </div>

        <div style={{ textAlign: "center", marginTop: "16px" }}>
          <div onClick={() => setDark(!dark)} style={{ fontSize: "12px", color: c.sub, cursor: "pointer" }}>
            {dark ? "☀️ Light mode" : "🌙 Dark mode"}
          </div>
        </div>
      </div>
    </div>
  );  
const MusicPlayer = () => (
    <div>
      {showMusic && (
        <div style={{ position: "fixed", bottom: isMobile ? "70px" : "20px", right: "20px", width: isMobile ? "calc(100% - 40px)" : "320px", background: c.card, border: `1px solid ${c.border}`, borderRadius: "16px", padding: "16px", zIndex: 200, boxShadow: "0 4px 24px rgba(0,0,0,0.3)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
            <div style={{ fontSize: "14px", fontWeight: "600", color: c.accent }}>🎵 Music Player</div>
            <button onClick={() => setShowMusic(false)} style={{ background: "transparent", border: "none", color: c.sub, cursor: "pointer", fontSize: "18px" }}>✕</button>
          </div>
          {currentSong && (
            <div style={{ marginBottom: "12px", padding: "10px", background: c.bg, borderRadius: "10px" }}>
              <div style={{ fontSize: "13px", fontWeight: "600", color: c.text }}>{currentSong.name}</div>
              <div style={{ fontSize: "11px", color: c.sub }}>{currentSong.artist}</div>
              <audio
                ref={audioRef}
                src={currentSong.url}
                autoPlay
                controls
                style={{ width: "100%", marginTop: "8px" }}
                onPlay={() => setIsPlaying(true)}
                onPause={() => setIsPlaying(false)}
              />
            </div>
          )}
          <div style={{ maxHeight: "200px", overflowY: "auto" }}>
            {musicResults.map((song, i) => (
              <div key={i} onClick={() => setCurrentSong(song)}
                style={{ display: "flex", alignItems: "center", gap: "10px", padding: "8px", borderRadius: "8px", cursor: "pointer", background: currentSong?.id === song.id ? `${c.accent}20` : "transparent", marginBottom: "4px" }}>
                {song.image && <img src={song.image} alt={song.name} style={{ width: "36px", height: "36px", borderRadius: "6px", objectFit: "cover" }} />}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: "12px", fontWeight: "600", color: c.text, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{song.name}</div>
                  <div style={{ fontSize: "11px", color: c.sub }}>{song.artist}</div>
                </div>
              <div style={{ display: "flex", gap: "4px" }}>
                  <span style={{ fontSize: "16px", cursor: "pointer" }} onClick={() => setCurrentSong(song)}>{currentSong?.id === song.id ? "🔊" : "▶️"}</span>
                  <a href={`https://www.youtube.com/results?search_query=${song.name}+${song.artist}`} target="_blank" rel="noopener noreferrer" style={{ fontSize: "12px", color: c.accent }} onClick={e => e.stopPropagation()}>YT</a>
                </div>  
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  
  if (!isLoggedIn) {
    return <AuthPage />;
  }

  return (
    <div style={s.app}>
      {/* Desktop Sidebar */}
      {!isMobile && (
        <div style={s.sidebar}>
          <SidebarContent />
        </div>
      )}

      {/* Mobile Sidebar Overlay */}
      {isMobile && sidebarOpen && (
        <div style={s.mobileSidebar}>
          <button onClick={() => setSidebarOpen(false)} style={{ alignSelf: "flex-end", background: "transparent", border: "none", color: c.text, fontSize: "24px", cursor: "pointer", marginBottom: "10px" }}>✕</button>
          <SidebarContent />
        </div>
      )}

      {/* Main */}
      <div style={s.main}>
        <div style={s.topbar}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            {isMobile && (
              <button onClick={() => setSidebarOpen(true)} style={{ background: "transparent", border: "none", color: c.text, fontSize: "22px", cursor: "pointer" }}>☰</button>
            )}
            <div>
              <div style={{ fontWeight: "700", fontSize: isMobile ? "14px" : "15px" }}>
                {navItems.find(n => n.id === tab)?.emoji} {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </div>
              <div style={{ fontSize: "11px", color: c.sub }}>{new Date().toLocaleDateString("en-IN", { weekday: "long", month: "long", day: "numeric" })}</div>
            </div>
          </div>
          <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
            {isMobile && (
              <button onClick={() => setDark(!dark)} style={{ background: "transparent", border: `1px solid ${c.border}`, color: c.sub, borderRadius: "8px", padding: "6px 10px", cursor: "pointer", fontSize: "14px" }}>
                {dark ? "☀️" : "🌙"}
              </button>
            )}
            <button onClick={fetchAll} style={{ ...s.btn("transparent"), border: `1px solid ${c.border}`, color: c.sub }}>🔄</button>
            <button onClick={handleLogout} style={{ ...s.btn("transparent"), border: `1px solid ${c.border}`, color: c.sub }}>🚪</button>
          </div>
        </div>

        {tab === "chat" ? (
          <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
            <div style={{ flex: 1, overflowY: "auto", padding: isMobile ? "12px 14px" : "20px 24px", display: "flex", flexDirection: "column", gap: "12px", paddingBottom: isMobile ? "80px" : "20px" }}>
              {messages.map((m, i) => (
                <div key={i} style={{ alignSelf: m.from === "user" ? "flex-end" : "flex-start", maxWidth: isMobile ? "85%" : "68%" }}>
                  {m.from === "mawa" && <div style={{ fontSize: "11px", color: c.accent, fontWeight: "700", marginBottom: "4px" }}>✨ Mawa</div>}
                  <div style={{ padding: "11px 16px", borderRadius: m.from === "user" ? "18px 18px 4px 18px" : "18px 18px 18px 4px", background: m.from === "user" ? `linear-gradient(135deg, ${c.accent}, ${c.pink})` : c.card, border: m.from === "mawa" ? `1px solid ${c.border}` : "none", fontSize: isMobile ? "13px" : "14px", lineHeight: "1.6",}}>
                    {m.text.split(/(https?:\/\/[^\s]+)/g).map((part, i) =>
                      part.match(/https?:\/\/[^\s]+/) ?
                        <a key={i} href={part} target="_blank" rel="noopener noreferrer"
                           style={{ color: "#7c5cfc", textDecoration: "underline" }}>
                        🔗 Open Link
                        </a> : part
                    )}
                  </div>
                </div>
              ))}
              {loading && (
                <div style={{ alignSelf: "flex-start" }}>
                  <div style={{ fontSize: "11px", color: c.accent, fontWeight: "700", marginBottom: "4px" }}>✨ Mawa</div>
                  <div style={{ padding: "11px 16px", borderRadius: "18px 18px 18px 4px", background: c.card, border: `1px solid ${c.border}`, fontSize: "14px", color: c.sub }}>Thinking... 💭</div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>
            <div style={{ padding: isMobile ? "10px 14px 70px" : "14px 24px", borderTop: `1px solid ${c.border}`, display: "flex", gap: "8px", alignItems: "center", background: c.sidebar }}>
              <input
                style={{ flex: 1, padding: "12px 18px", borderRadius: "25px", border: `1px solid ${c.border}`, background: c.bg, color: c.text, fontSize: isMobile ? "13px" : "14px", outline: "none" }}
                value={chatInput}
                onChange={e => setChatInput(e.target.value)}
                onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(chatInput); } }}
                placeholder="Type your message..."
                autoComplete="off"
                spellCheck="false"
              />
              <button onClick={toggleListen} style={{ width: "44px", height: "44px", borderRadius: "50%", background: listening ? c.pink : c.accent, color: "white", border: "none", cursor: "pointer", fontSize: "16px", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                {listening ? "⏹" : "🎤"}
              </button>
              <button onClick={() => sendMessage(chatInput)} style={{ padding: "12px 20px", borderRadius: "25px", background: `linear-gradient(135deg, ${c.accent}, ${c.pink})`, color: "white", border: "none", cursor: "pointer", fontWeight: "700", fontSize: isMobile ? "13px" : "14px", flexShrink: 0 }}>
                Send
              </button>
            </div>
          </div>
        ) : (
          <div style={{ ...s.scroll, paddingBottom: isMobile ? "80px" : "20px" }}>
            {tabViews[tab]}
          </div>
        )}
      </div>

      {/* Mobile Bottom Navigation */}
      {isMobile && (
        <div style={s.bottomNav}>
          {navItems.map(item => (
            <div key={item.id} style={s.bottomNavItem(tab === item.id)} onClick={() => setTab(item.id)}>
              <span style={{ fontSize: "22px" }}>{item.emoji}</span>
              <span style={{ fontSize: "10px", fontWeight: tab === item.id ? "600" : "400" }}>{item.label}</span>
            </div>
          ))}
        </div>
      )}
    <MusicPlayer />
    </div>
  );
}
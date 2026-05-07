<p align="center">
  <img src="https://img.shields.io/badge/RiseAgent-AI%20Voice%20Agent-00C896?style=for-the-badge&labelColor=0a0a0a" alt="RiseAgent AI" />
</p>

<h1 align="center">Rise.AI — Intelligent Multilingual Voice Agent</h1>

<p align="center">
  <em>Every lead. Every language. Every time.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-3776AB?logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/react-18-61DAFB?logo=react&logoColor=black" alt="React" />
  <img src="https://img.shields.io/badge/fastapi-0.104-009688?logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/tailwindcss-3-06B6D4?logo=tailwindcss&logoColor=white" alt="Tailwind" />
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License" />
</p>

---

## 🚀 What is RiseAgent?

**RiseAgent** is a production-grade, multilingual AI voice agent system built for **Rupeezy's** Authorized Person (AP) lead conversion program. It automatically calls every new lead within 5 minutes, conducts intelligent sales conversations in **7 Indian languages**, handles objections with RAG-backed rebuttals, scores leads as Hot/Warm/Cold, and routes them to RM queues or WhatsApp follow-ups.

> **82% of sales leads go cold before anyone picks up the phone.**
> RiseAgent calls every lead within 5 minutes — in their language, with the right answer, every time.

**Built by Team MINDBOT** at Technocrats Institute of Technology, Bhopal.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🗣️ **Multilingual AI Calls** | Speaks Hindi, Tamil, Telugu, Marathi, Gujarati, Bengali & English — detects language automatically |
| ⚡ **5-Minute Response** | Calls every lead within 5 minutes of arrival — no lead goes cold |
| 🧠 **Context-Aware Conversations** | RAG over Rupeezy's AP sales script; handles all 5 core objections |
| 🔀 **Code-Mix Detection** | Switches language mid-call if the lead code-mixes |
| 📊 **Weighted Lead Scoring** | 5-signal scoring engine: Hot → RM queue, Warm → WhatsApp, Cold → Re-engage |
| 🤖 **Dual LLM Failover** | Powered by Groq + Gemini with automatic failover for 99.9% uptime |
| 📱 **Real-Time Dashboard** | Live analytics, call transcripts, RM queue, and provider health monitoring |
| 🔒 **Demo Mode** | Full pipeline simulation without real calls — perfect for demos and testing |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React 18)                       │
│  Landing Page ─── Dashboard ─── Leads ─── RM Queue ─── Call View │
└──────────────────────────┬───────────────────────────────────────┘
                           │ REST API
┌──────────────────────────▼───────────────────────────────────────┐
│                      BACKEND (FastAPI)                            │
│                                                                   │
│  POST /leads/new → Insert lead → Trigger call (background)       │
│                                       │                           │
│                     ┌─────────────────▼──────────────────┐       │
│                     │ [Demo] Simulate conversation        │       │
│                     │ [Prod] Exotel/Twilio outbound       │       │
│                     └─────────────────┬──────────────────┘       │
│                                       │                           │
│                     Voice loop: STT → LLM → TTS                  │
│                            (Sarvam AI)  (Groq/Gemini)             │
│                                       │                           │
│                     Objection detection + RAG rebuttal            │
│                            (ChromaDB + HuggingFace)               │
│                                       │                           │
│                     Score lead (Hot / Warm / Cold)                │
│                                       │                           │
│            Hot → RM Queue  │  Warm → WhatsApp  │  Cold → Re-engage│
└──────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | FastAPI, Uvicorn, Pydantic v2, Python 3.11+ |
| **LLM** | Groq (Llama 3) + Google Gemini with auto-failover via LangChain |
| **RAG** | ChromaDB + HuggingFace multilingual embeddings |
| **Voice** | Sarvam AI (STT + TTS + Translate) |
| **Phone** | Exotel / Twilio (configurable) |
| **WhatsApp** | Meta Cloud API (Graph API v18.0) |
| **Database** | Supabase (PostgreSQL) or in-memory for demo |
| **Frontend** | React 18, Vite 5, Tailwind CSS 3, Recharts, TanStack Query, Zustand |
| **Animations** | Framer Motion, Lenis (smooth scroll) |

---

## 📁 Project Structure

```
Rise-Agent/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Environment & settings
│   ├── database.py              # Supabase / in-memory DB layer
│   ├── requirements.txt
│   ├── models/                  # Pydantic data models
│   ├── routers/                 # API route handlers
│   ├── services/
│   │   ├── call_service.py      # Outbound call orchestration
│   │   ├── conversation.py      # Multi-turn conversation engine
│   │   ├── language.py          # Language detection & switching
│   │   ├── llm.py               # LLM provider (Groq/Gemini failover)
│   │   ├── memory.py            # Conversation memory & context
│   │   ├── objection_handler.py # RAG-backed objection rebuttals
│   │   ├── scoring.py           # 5-signal lead scoring engine
│   │   ├── sarvam.py            # Sarvam AI voice integration
│   │   ├── rm_handoff.py        # RM queue routing
│   │   └── whatsapp.py          # WhatsApp follow-up service
│   ├── knowledge/               # RAG knowledge base documents
│   ├── prompts/                 # LLM system prompts
│   └── demo/                    # Demo personas & simulation
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LandingPage.jsx  # Cinematic landing experience
│   │   │   ├── Dashboard.jsx    # Real-time analytics dashboard
│   │   │   ├── Leads.jsx        # Lead management table
│   │   │   ├── RMQueue.jsx      # RM handoff queue
│   │   │   └── CallDetail.jsx   # Individual call transcript view
│   │   ├── components/
│   │   │   └── landing/         # Landing page components
│   │   │       ├── VideoBackground.jsx
│   │   │       ├── LiquidGlassCard.jsx
│   │   │       ├── WordsPullUp.jsx
│   │   │       ├── ScrollRevealText.jsx
│   │   │       ├── AboutSection.jsx
│   │   │       ├── FeaturesSection.jsx
│   │   │       ├── Navbar.jsx
│   │   │       └── LenisProvider.jsx
│   │   └── index.css
│   ├── tailwind.config.js
│   └── vite.config.js
│
└── README.md
```

---

## ⚡ Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn

### 1. Clone the repository

```bash
git clone https://github.com/Amit-Mahaseth/Rise-Agent.git
cd Rise-Agent
```

### 2. Backend Setup

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Configure your API keys in .env
uvicorn main:app --reload
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The app will be available at **http://localhost:5173**

### 4. Test Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Seed all 5 demo personas
curl -X POST http://localhost:8000/leads/demo/seed

# Create a single lead (triggers demo call simulation)
curl -X POST http://localhost:8000/leads/new \
  -H "Content-Type: application/json" \
  -d '{"name": "Priya Sharma", "phone": "+919876543211", "source": "test"}'

# Dashboard stats
curl http://localhost:8000/dashboard/stats

# List all leads
curl http://localhost:8000/leads

# RM queue
curl http://localhost:8000/dashboard/rm-queue
```

---

## 🎭 Demo Mode

Set `DEMO_MODE=true` in `.env` (default). In demo mode:

- ✅ No real phone calls are made
- ✅ Full conversation pipeline runs with real LLM calls
- ✅ Lead responses are simulated based on persona personality
- ✅ Full scoring, memory, and routing work end-to-end
- ✅ Dashboard updates in real-time

### Demo Personas

| Name | Language | Personality | Expected Score |
|------|----------|-------------|----------------|
| 🇮🇳 Rajesh Kumar | Hindi | Skeptical | Warm |
| 🇬🇧 Priya Sharma | English | Enthusiastic | Hot |
| 🇮🇳 Karthik Rajan | Tamil | Neutral | Warm |
| 🇮🇳 Meena Patil | Marathi | Disengaged | Cold |
| 🇮🇳 Arjun Reddy | Telugu | Interested | Hot |

---

## 🔐 Environment Variables

See `backend/.env.example` for the full list. Minimum required for demo mode:

| Variable | Required | Description |
|----------|----------|-------------|
| `DEMO_MODE` | Yes | Set to `true` for demo simulation |
| `GROQ_API_KEY` | Yes | Primary LLM provider |
| `GOOGLE_API_KEY` | Yes | Failover LLM provider (Gemini) |
| `SARVAM_API_KEY` | Yes | Voice services (STT/TTS/Translate) |
| `SUPABASE_URL` | No | PostgreSQL database (uses in-memory if unset) |
| `SUPABASE_KEY` | No | Supabase service role key |

---

## 🎨 Landing Page

The landing page features a cinematic, studio-grade design with:

- **HLS video background** with gradient overlays and grid lines
- **Liquid glass card** with glassmorphism effects
- **Framer Motion animations** — staggered word pull-ups, scroll-linked opacity reveals
- **Lenis smooth scrolling** for buttery-smooth navigation
- **Responsive 12-column grid** layout with mobile-first breakpoints

---

## 🤝 Team MINDBOT

Built at **Technocrats Institute of Technology, Bhopal** using:

- **Groq** — Ultra-fast LLM inference
- **Google Gemini** — Failover LLM with multimodal capabilities  
- **Sarvam AI** — Indian-language speech & translation
- **LangChain** — LLM orchestration & RAG pipeline
- **React 18** — Modern, reactive frontend

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

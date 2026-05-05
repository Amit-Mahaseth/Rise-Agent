# RiseAgent AI

Production-grade multilingual AI voice agent system for Rupeezy's Authorized Person (AP) lead conversion program. Automatically calls new leads, conducts multilingual sales conversations, handles objections with RAG-backed rebuttals, scores leads as Hot/Warm/Cold, and routes them to RM queue or WhatsApp follow-up.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI, Uvicorn, Pydantic v2, Python 3.11+ |
| **LLM** | Claude Sonnet (Anthropic) via LangChain |
| **RAG** | ChromaDB + HuggingFace multilingual embeddings |
| **Voice** | Sarvam AI (STT + TTS + Translate) |
| **Phone** | Exotel / Twilio (configurable) |
| **WhatsApp** | Meta Cloud API (Graph API v18.0) |
| **Database** | Supabase (PostgreSQL) or in-memory for demo |
| **Frontend** | React 18, Vite 5, Tailwind CSS 3, Recharts, TanStack Query, Zustand |

## Quick Start

### 1. Backend

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
uvicorn main:app --reload
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

### 3. Test Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Create a single lead (triggers demo simulation)
curl -X POST http://localhost:8000/leads/new \
  -H "Content-Type: application/json" \
  -d '{"name": "Priya Sharma", "phone": "+919876543211", "source": "test"}'

# Seed all 5 demo personas
curl -X POST http://localhost:8000/leads/demo/seed

# Get dashboard stats
curl http://localhost:8000/dashboard/stats

# List all leads
curl http://localhost:8000/leads

# Get RM queue
curl http://localhost:8000/dashboard/rm-queue
```

## Demo Mode

Set `DEMO_MODE=true` in `.env` (default). In demo mode:

- No real phone calls are made
- Full conversation pipeline runs with Claude (real LLM calls)
- Lead responses are simulated based on persona personality
- Full scoring, memory, and routing work end-to-end
- Dashboard updates in real-time

### Demo Personas

| Name | Language | Personality | Expected Result |
|------|----------|-------------|----------------|
| Rajesh Kumar | Hindi | Skeptical | Warm |
| Priya Sharma | English | Enthusiastic | Hot |
| Karthik Rajan | Tamil | Neutral | Warm |
| Meena Patil | Marathi | Disengaged | Cold |
| Arjun Reddy | Telugu | Interested | Hot |

## Architecture

```
POST /leads/new → Insert lead → Trigger call (background)
                                      ↓
                              [Demo] Simulate conversation
                              [Prod] Exotel/Twilio outbound
                                      ↓
                              Voice loop: STT → LLM → TTS
                                      ↓
                              Objection detection + RAG rebuttal
                                      ↓
                              Score lead (Hot/Warm/Cold)
                                      ↓
                     Hot → RM Queue | Warm → WhatsApp | Cold → Re-engage
```

## Environment Variables

See `backend/.env.example` for all required variables. In demo mode, only `ANTHROPIC_API_KEY` and `SARVAM_API_KEY` are required.

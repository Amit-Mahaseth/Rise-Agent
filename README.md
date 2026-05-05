# RiseAgent AI

RiseAgent AI is a production-oriented multilingual voice-agent system for Rupeezy. It instantly calls new leads, detects their language in real time, handles loan objections with a retrieval-backed conversation engine, classifies each lead as Hot/Warm/Cold, and routes the next action to sales or nurture workflows.

## What is included

- FastAPI backend with modular orchestration services
- LangChain conversation engine with RAG over base scripts and FAQs
- ChromaDB memory for per-lead, multi-call continuity
- Rule-based scoring and classification with explainable breakdowns
- Twilio adapters for outbound calling and WhatsApp follow-ups
- React + Vite dashboard scaffold for funnel, summaries, and RM tracking
- Architecture and setup docs for local development and production rollout

## Monorepo layout

```text
.
├── backend
│   ├── app
│   ├── data
│   ├── tests
│   └── pyproject.toml
├── docs
│   └── architecture.md
└── frontend
    └── src
```

## Quick start

### 1. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -e .
copy .env.example .env
uvicorn app.main:app --reload
```

### 2. Frontend

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

### 3. Seed a lead

```bash
curl -X POST http://localhost:8000/api/v1/leads ^
  -H "Content-Type: application/json" ^
  -d "{\"lead_id\":\"LD-1001\",\"full_name\":\"Priya Sharma\",\"phone_number\":\"+919999999999\",\"source\":\"landing-page\",\"product_interest\":\"personal-loan\",\"notes\":\"Asked for a callback about rate options\"}"
```

The backend will create the lead, queue the outbound call, and expose turn-processing endpoints that a telephony/media gateway can use.

## Core flow

1. Lead is created via API.
2. Orchestrator stores the lead and queues an outbound call.
3. Telephony provider places the call and streams conversation turns to the backend.
4. LangChain retrieves base script + FAQ + lead memory before generating the next response.
5. The scoring engine classifies the lead as Hot/Warm/Cold.
6. Hot leads are handed to a relationship manager, Warm leads get WhatsApp nurture, Cold leads go to re-engagement.

## Environment files

- Backend: [backend/.env.example](backend/.env.example)
- Frontend: [frontend/.env.example](frontend/.env.example)

## Documentation

- Detailed architecture: [docs/architecture.md](docs/architecture.md)


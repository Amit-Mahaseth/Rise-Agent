# RiseAgent AI Architecture

## 1. Business objective

Rupeezy needs to react to inbound demand in seconds, not hours. RiseAgent AI is designed to call a new lead immediately, continue in the language the customer naturally uses, qualify buying intent, capture objections, and hand qualified opportunities to human sales with full context.

## 2. High-level architecture

```text
CRM / Lead Source
       |
       v
 FastAPI Lead API ------------------------------+
       |                                        |
       v                                        |
 Orchestrator                                   |
       |                                        |
       +--> SQL lead/call state                 |
       +--> Chroma memory + KB                  |
       +--> Telephony adapter (Twilio Voice)    |
                                                 |
Customer Phone <-> Media Stream / Voice Gateway -+-> Sarvam STT/TTS
                                                 |
                                                 v
                                           LangChain Engine
                                                 |
                                                 v
                                         Lead Scoring / Routing
                                                 |
             +-------------------+---------------+--------------------+
             |                   |                                    |
             v                   v                                    v
     Human RM handoff     WhatsApp follow-up                  Re-engagement queue
```

## 3. Component responsibilities

### FastAPI API layer

- Accept lead creation requests
- Expose telephony and conversation endpoints
- Serve dashboard analytics
- Coordinate background call initiation

### Orchestrator

- Creates lead and call records
- Starts outbound call via the telephony provider
- Processes each user utterance
- Finalizes scoring and next-action routing

### Conversation engine

- Detects the active language on each turn
- Retrieves relevant FAQs and sales guidance
- Retrieves prior call memory for the same `lead_id`
- Produces a natural response instead of rigid script playback

### RAG layer

- Base script provides brand-safe positioning
- FAQ provides objection-handling and eligibility answers
- ChromaDB vector retrieval injects only the most relevant snippets

### Memory layer

- Stores every lead utterance, assistant reply, and final call summary
- Enables cross-call continuity for the same `lead_id`
- Allows the agent to remember past objections, preferred time, and product interest

### Scoring engine

- Scores intent, engagement, objections, and tone
- Produces a transparent score breakdown
- Converts score to `HOT`, `WARM`, or `COLD`

### Routing layer

- `HOT`: webhook or CRM handoff to the assigned RM with transcript and insights
- `WARM`: Twilio WhatsApp follow-up with personalized CTA
- `COLD`: store for later nurture or retargeting

## 4. Recommended production deployment

### Runtime services

- `backend-api`: FastAPI application
- `voice-gateway`: media bridge translating call audio into transcript events
- `frontend-dashboard`: React + Vite static app
- `postgres` or managed SQL: structured lead/call data in production
- `persistent-volume`: ChromaDB data directory
- `redis` or queue worker: optional for retries and delayed follow-ups

### Security and reliability

- Store secrets in a vault or deployment secret manager
- Validate Twilio signatures on webhook endpoints
- Use idempotency keys when creating leads from CRM
- Add retry policies for Sarvam/Twilio transient failures
- Emit structured logs with `lead_id`, `call_id`, and provider IDs
- Push call summaries to CRM after completion

## 5. End-to-end call lifecycle

1. A lead enters FastAPI through `POST /api/v1/leads`.
2. The backend stores the lead, creates a queued call record, and triggers outbound dial.
3. Twilio starts the PSTN call and streams audio or transcript events through the media gateway.
4. The gateway sends transcript turns into the FastAPI conversation endpoint or WebSocket.
5. The conversation engine:
   - detects language
   - retrieves lead memory
   - retrieves the most relevant sales guidance
   - generates the next response
   - optionally synthesizes audio with Sarvam TTS
6. On call end, the scoring service classifies the lead.
7. The router executes the next action and updates the dashboard state.

## 6. Why this design works for Rupeezy

- Fast reaction time increases contact rates
- Multilingual turn detection reduces drop-off from forced language menus
- RAG keeps the agent aligned with approved sales messaging
- Per-lead memory avoids repetitive follow-ups across multiple call attempts
- Explainable scoring helps sales leaders trust the automation


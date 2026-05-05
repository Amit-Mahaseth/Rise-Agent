# Backend Folder Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Configuration management
│   ├── database.py                # Database connection and session management
│   ├── models/                    # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── lead.py               # Lead model
│   │   ├── conversation.py       # Conversation model
│   │   ├── call.py               # Call session model
│   │   └── scoring.py            # Scoring model
│   ├── schemas/                  # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── lead.py               # Lead schemas
│   │   ├── conversation.py       # Conversation schemas
│   │   └── scoring.py            # Scoring schemas
│   ├── api/                      # API routes
│   │   ├── __init__.py
│   │   ├── v1/                   # API version 1
│   │   │   ├── __init__.py
│   │   │   ├── leads.py          # Lead management endpoints
│   │   │   ├── calls.py          # Call management endpoints
│   │   │   ├── conversations.py  # Conversation endpoints
│   │   │   ├── analytics.py      # Analytics endpoints
│   │   │   └── webhooks.py       # External webhook handlers
│   │   └── dependencies.py       # API dependencies
│   ├── services/                 # Business logic services
│   │   ├── __init__.py
│   │   ├── lead_service.py       # Lead management service
│   │   ├── voice_service.py      # Voice processing service
│   │   ├── conversation_service.py # Conversation orchestration
│   │   ├── scoring_service.py    # Lead scoring service
│   │   ├── routing_service.py    # Lead routing service
│   │   ├── whatsapp_service.py   # WhatsApp integration
│   │   └── analytics_service.py  # Analytics service
│   ├── core/                     # Core functionality
│   │   ├── __init__.py
│   │   ├── llm/                  # LLM integration
│   │   │   ├── __init__.py
│   │   │   ├── claude_client.py  # Claude API client
│   │   │   ├── mistral_client.py # Mistral API client
│   │   │   └── langchain_setup.py # LangChain configuration
│   │   ├── stt_tts/              # Speech processing
│   │   │   ├── __init__.py
│   │   │   ├── sarvam_client.py  # Sarvam AI client
│   │   │   └── language_detection.py # Language detection
│   │   ├── memory/               # Memory management
│   │   │   ├── __init__.py
│   │   │   ├── chromadb_client.py # ChromaDB client
│   │   │   └── memory_manager.py # Memory operations
│   │   ├── rag/                  # RAG system
│   │   │   ├── __init__.py
│   │   │   ├── knowledge_base.py # Knowledge base management
│   │   │   ├── script_loader.py  # Script and FAQ loading
│   │   │   └── retriever.py      # Document retrieval
│   │   ├── telephony/            # Telephony integration
│   │   │   ├── __init__.py
│   │   │   ├── twilio_client.py  # Twilio client
│   │   │   └── call_manager.py   # Call orchestration
│   │   └── security/             # Security utilities
│   │       ├── __init__.py
│   │       ├── auth.py           # Authentication
│   │       └── encryption.py     # Data encryption
│   ├── utils/                    # Utility functions
│   │   ├── __init__.py
│   │   ├── logger.py             # Logging configuration
│   │   ├── validators.py         # Data validation
│   │   ├── helpers.py            # Helper functions
│   │   └── constants.py          # Application constants
│   └── repositories/             # Data access layer
│       ├── __init__.py
│       ├── lead_repository.py    # Lead data operations
│       ├── conversation_repository.py # Conversation data operations
│       └── scoring_repository.py # Scoring data operations
├── data/                        # Data files and knowledge base
│   ├── scripts/                  # Conversation scripts
│   │   ├── base_script.txt       # Base conversation script
│   │   └── language_variants/    # Language-specific scripts
│   └── faq/                      # FAQ knowledge base
│       ├── objections.txt        # Common objections
│       ├── products.txt          # Product information
│       └── policies.txt          # Company policies
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   ├── e2e/                      # End-to-end tests
│   └── fixtures/                 # Test data
├── alembic/                      # Database migrations
│   ├── versions/                 # Migration files
│   └── env.py                    # Migration environment
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker configuration
├── docker-compose.yml            # Local development setup
└── .env.example                  # Environment variables template
```
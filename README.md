# LoanPilot — AI Loan Document Processing & Verification Agent

**LoanPilot** is an intelligent, agentic AI platform designed to automate loan document processing, cross-document verification, and risk assessment with Human-in-the-Loop oversight.

---

## Architecture Overview

```
[ Loan Officer / Underwriter ]
              │
              ▼
   [ React + Vite Frontend ] (Tailwind CSS, Status Dashboard, Review UI, Agent Chat)
              │  HTTP / REST
              ▼
    [ FastAPI Backend Gateway ] (CORS, Request Validation, Async Handlers)
              │
   ┌──────────┴───────────────────────────────────────────────────────┐
   │                     PROCESSING PIPELINE                          │
   │                                                                  │
   │  1. Ingestion         Upload PDF/images & generate app tracking  │
   │  2. OCR Engine        PyMuPDF / Tesseract text extraction        │
   │  3. Classification    LLM identifies document types              │
   │  4. Field Extraction  Canonical JSON structured schema parser    │
   │  5. Field Validation  Data sanity & formatting checks            │
   │  6. Cross-Check       Cross-document consistency engine          │
   │  7. Risk Assessment   Scoring, flag detection & evidence logging │
   │  8. Agent & Report    Conversational query assistant & PDF report│
   └──────────────────────────────────┬───────────────────────────────┘
                                      │
                   [ SQLite / PostgreSQL Database ]
```

---

## Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy 2.0 (Async), Pydantic v2, Uvicorn |
| **Document Processing** | PyMuPDF (fitz), Tesseract OCR, Pillow |
| **AI / LLM** | OpenAI API / LangChain, RapidFuzz (matching) |
| **Frontend** | React 19, Vite, Tailwind CSS v4, Lucide Icons, Axios, React Router |
| **DevOps / Container** | Docker, Docker Compose |

---

## Repository Structure

```
LoanPilot/
├── backend/
│   ├── alembic/              # DB migration configurations
│   ├── middleware/           # Logging and error handling middleware
│   ├── models/               # SQLAlchemy ORM models (Application, Document, Verification, Risk)
│   ├── routers/              # FastAPI APIRouters for all endpoints
│   ├── schemas/              # Pydantic schemas (request/response validation)
│   ├── services/             # Core business logic and processing pipeline
│   ├── tests/                # Automated pytest test suites
│   ├── utils/                # Evidence, fuzzy matching, LLM client helpers
│   ├── config.py             # App settings loaded from environment
│   ├── database.py           # Async DB session management
│   ├── Dockerfile            # Backend container definition
│   ├── main.py               # FastAPI entry point
│   └── requirements.txt      # Python dependencies
├── data/
│   ├── dummy_generator/      # Synthetic document generation scripts
│   ├── kaggle/               # Kaggle loan dataset loaders
│   └── sample_applications/  # Demo document sets
├── frontend/
│   ├── src/
│   │   ├── api/              # Axios API service clients
│   │   ├── components/       # Reusable UI components (Risk, Documents, Agent)
│   │   ├── pages/            # Dashboard, NewApplication, ApplicationReview, ReportView
│   │   ├── App.jsx           # Application routing setup
│   │   └── index.css         # Styling with Tailwind CSS
│   ├── Dockerfile            # Frontend container definition
│   └── package.json          # Node dependencies and scripts
├── .env.example              # Environment variables template
├── docker-compose.yml        # Multi-container orchestration
└── README.md                 # Project documentation
```

---

## Quick Start Guide

### Prerequisites
* Python 3.11+
* Node.js 20+ & npm
* (Optional) Docker & Docker Compose
* (Optional) Tesseract OCR installed locally for image OCR

---

### Option 1: Running with Docker Compose (Recommended)

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd LoanPilot
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   Add your `OPENAI_API_KEY` in `.env`.

3. **Start the containers:**
   ```bash
   docker compose up --build
   ```

4. **Access the application:**
   * **Frontend UI:** http://localhost:5173
   * **Backend API Docs:** http://localhost:8000/docs

---

### Option 2: Running Locally

#### 1. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Run FastAPI dev server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Interactive API documentation will be available at [http://localhost:8000/docs](http://localhost:8000/docs).

#### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
Frontend UI will be running at [http://localhost:5173](http://localhost:5173).

---

## Pipeline & Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/applications` | POST | Create a new loan application |
| `/api/v1/applications` | GET | List applications with status filter |
| `/api/v1/applications/{id}` | GET | Get full application details and progress |
| `/api/v1/applications/{id}/documents` | POST | Upload documents (PDF, JPG, PNG) |
| `/api/v1/applications/{id}/process` | POST | Trigger end-to-end processing pipeline |
| `/api/v1/applications/{id}/status` | GET | Check real-time pipeline status |
| `/api/v1/applications/{id}/verification` | GET | Fetch cross-document consistency checks |
| `/api/v1/applications/{id}/risk` | GET | Fetch risk score and flagged discrepancies |
| `/api/v1/applications/{id}/agent` | POST | Query the conversational assistant |
| `/api/v1/applications/{id}/report` | GET | Generate verification report |
| `/api/v1/applications/{id}/decide` | POST | Record underwriter approval or rejection |

---

## Contributing

1. Create a feature branch for your task:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Write clean code with appropriate tests under `backend/tests/`.
3. Verify syntax and tests before committing:
   ```bash
   pytest backend/tests
   ```
4. Open a pull request against `main`.
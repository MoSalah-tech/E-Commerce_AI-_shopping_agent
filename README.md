# 🛒 E-Commerce AI Shopping Agent

An AI-powered shopping assistant that helps users find products to buy online. Describe what you're looking for in natural language — the agent extracts your requirements, searches multiple sources, and returns curated recommendations with direct purchase links and a budget-verified total.

## ✨ Features

- **Natural language understanding** — Tell the agent what you want in plain English (or Arabic). It extracts product names, categories, and budget automatically.
- **Multi-turn conversations** — The agent remembers your previous requests. Budgets and products persist across messages, so you don't have to repeat yourself.
- **Smart search with fallback** — Uses Google Shopping via Serper API, with automatic fallback to site-filtered organic searches for Egyptian retailers (noon, Jumia, B.TECH, 2B, Amazon.eg) when Google Shopping coverage is sparse.
- **Deterministic budget verification** — A code-based verifier recomputes the actual total from recommended products and compares it to your stated budget — no relying on LLM arithmetic.
- **JWT authentication** — Secure user sessions with token-based auth.
- **Chat persistence** — Conversations are stored and retrieved via LangGraph checkpointer with Postgres.
- **Modern web UI** — A Next.js frontend with a clean chat interface.

## 🏗️ Architecture

The system has three layers:

1. **AI Agent (LangGraph)** — A state machine with a **Planner node** (extracts structured search criteria from user input) and an **Executer node** (searches for products and generates recommendations). Powered by Groq's `openai/gpt-oss-120b` model.
2. **Backend API (FastAPI)** — REST endpoints for authentication, chat sessions, and agent invocation. Includes rate limiting and JWT middleware.
3. **Frontend (Next.js)** — A responsive chat interface that communicates with the backend API.

### Agent Flow
```text
User Message
│
▼
┌─────────────┐
│ Planner Node │ ── Extracts product names, categories, budget
└─────────────┘ Carries forward previous context
│
▼
┌──────────────┐
│ Search Tools │ ── Serper API (Google Shopping + organic fallback)
└──────────────┘ Tavily search
│
▼
┌──────────────┐
│ Executer Node│ ── Generates recommendations with purchase links
└──────────────┘
│
▼
┌──────────────┐
│Budget Verifier│ ── Recomputes total, annotates summary
└──────────────┘
│
▼
Final Answer (recommendations + verified budget)
```

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **PostgreSQL**
- API keys for:
  - [Groq](https://console.groq.com/) (LLM)
  - [Serper](https://serper.dev/) (Google search)
  - [Tavily](https://tavily.com/) (optional, for additional search)

### Backend Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/MoSalah-tech/E-Commerce_AI-_shopping_agent.git
   cd E-Commerce_AI-_shopping_agent
   ```
2. Create a virtual environment and install dependencies:
    ```bash
       python -m venv venv
       source venv/bin/activate  # On Windows: venv\Scripts\activate
       pip install -r requirements.txt
     ```
3. Set up environment variables:
   Create a .env file in the project root:
   ```env
     GROQ_API_KEY=your_groq_api_key
     SERPAPI_API_KEY=your_serper_api_key
    TAVILY_API_KEY=your_tavily_api_key
    DATABASE_URL=postgresql://user:password@localhost:5432/shopping_agent
    JWT_SECRET_KEY=your_jwt_secret
   ```
4. ```bash
      uvicorn app.main:app --reload
   ```    

### Frontend Setup:

1. Navigate to the frontend directory:
   ```bash
     cd shopping-agent-frontend
   ```
2. Install dependencies:
   ```bash
    npm install
   ```
3. Set up environment variables:  
    Copy .env.local.example to .env.local and fill in the API URL:
   ```env
    NEXT_PUBLIC_API_URL=http://localhost:8000
   ```
4. Run the development server:
   ```bash
      npm run dev
   ```
5. Open http://localhost:3000 in your browser.


### Docker Setup 

Run the full stack with Docker Compose:

```bash
  docker-compose -f dockercompose.yml up --build
```


### 🧰 Tech Stack
```text
Layer	Technology
AI Framework	LangGraph, LangChain
LLM	Groq (openai/gpt-oss-120b)
Search	Serper API (Google Shopping + organic), Tavily
Browser Automation	Playwright (Chromium)
Backend	FastAPI, Pydantic, SQLAlchemy
Auth	JWT (python-jose)
Database	PostgreSQL
Frontend	Next.js 14+, React, TypeScript
Deployment	Docker, Docker Compose, Jenkins
```

### 📁 Project Structure:
 ```text

   ├── app/                          # Python backend
│   ├── agent/                    # Core AI agent (LangGraph)
│   ├── api/                      # FastAPI routes
│   ├── auth/                     # JWT authentication
│   ├── chat/                     # Chat persistence
│   ├── core/                     # Config, DB, rate limiting
│   ├── schemas/                  # API schemas
│   └── tools/                    # Search tool integrations
├── shopping-agent-frontend/      # Next.js frontend
├── Dockerfile                    # Backend container
├── dockercompose.yml             # Multi-container orchestration
├── Jenkinsfile                   # CI/CD pipeline
└── LICENSE                       # MIT

```

### 🔑 API Keys
Service	Purpose	Free Tier
Groq	LLM inference	Yes
Serper	Google search (shopping + organic)	Yes (2,500 queries)
Tavily	AI-optimized web search	Yes (1,000 queries/month)

### 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.


       

# Insight_Engine

Insight_Engine is a next-gen portfolio automation and AI-driven stock analysis platform. It integrates with major brokerages (starting with Angel One) to sync portfolios and provide deep insights using local LLMs.

## Features

- **Portfolio Sync**: Real-time synchronization of your holdings from Angel One.
- **AI Analysis**: Deep research on specific stocks using local LLMs (via Ollama) and real-time web search.
- **Robo Trading**: Automated order execution with target and stop-loss management.
- **Secure**: Sensitive broker credentials are encrypted at rest.
- **Modern Dashboard**: High-performance UI built with React, Tailwind CSS, and Framer Motion.

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy (PostgreSQL), Redis, Ollama.
- **Frontend**: React (Vite), TypeScript, Tailwind CSS, Lucide Icons, Framer Motion.
- **Security**: JWT Authentication, Bcrypt password hashing, Fernet encryption for secrets.

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js & npm
- PostgreSQL
- Redis
- [Ollama](https://ollama.com/) (with `llama3.2:3b` model)

### Backend Setup

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables:
   Create a `.env` file in the `backend` directory based on the following:
   ```env
   DATABASE_URL=postgresql://user:pass@localhost/insight_db
   SECRET_KEY=your_jwt_secret_key
   ENCRYPTION_KEY=your_fernet_encryption_key
   REDIS_HOST=localhost
   REDIS_PORT=6379
   OLLAMA_URL=http://localhost:11434/api/generate
   AI_MODEL=llama3.2:3b
   ```
5. Run the backend:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8001
   ```

### Frontend Setup

1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```

## Deployment with Docker

You can use the provided `docker-compose.yml` (coming soon) to run the entire stack including PostgreSQL and Redis.

## License

MIT

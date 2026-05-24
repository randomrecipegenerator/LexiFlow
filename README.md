# LexiFlow: AI-Powered Legal Intake & Lead Qualification

LexiFlow is an intelligent legal intake platform designed to automate client screening and lead qualification for law firms. It uses Large Language Models (LLMs) to engage potential clients in natural conversation, score leads based on custom legal criteria, and provide attorneys with a prioritized dashboard of qualified opportunities.

## 🚀 Key Features

- **Intelligent Intake Agent:** A conversational AI widget that captures lead information naturally.
- **Automated Qualification:** AI-driven scoring (0-100) and categorization based on firm-specific criteria.
- **Document Analysis (OCR):** Extracts key facts from uploaded medical records or legal documents using AI.
- **Attorney Dashboard:** Unified interface for managing leads, viewing AI summaries, and tracking qualification scores.
- **CRM Integrations:** Ready-to-sync connectors for Clio, MyCase, and Filevine (Simulated/Demo mode).
- **Embedded eSign:** Integration with Dropbox Sign for immediate retainer or intake form signing.
- **Unified Vercel Hosting:** Optimized for deployment on Vercel with zero-config serverless functions.

## 📂 Project Structure

```text
├── api/                # Vercel Serverless Function entry points
├── backend/            # Core FastAPI logic (Models, AI Engine, Integrations)
├── docs/               # Technical documentation and migration guides
├── screenshots/        # Product visuals and dashboard previews
├── index.html          # Main landing page & floating chat widget
├── dashboard.html      # Attorney lead management portal
├── demo.html           # Live interactive demo environment
├── config.js           # Frontend environment configuration
├── vercel.json         # Vercel deployment and routing rules
└── requirements.txt    # Python dependencies
```

## 🛠️ Local Development

### Prerequisites

- Python 3.9+
- An API key for Groq (default) or OpenAI.

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd lexiflow-mvp
   ```

2. **Set up Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Copy `.env.example` to `.env` and add your API keys:
   ```bash
   cp .env.example .env
   ```

4. **Run the Application:**
   ```bash
   python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```

### Access

- **Landing Page & Chatbot:** [http://localhost:8000](http://localhost:8000)
- **Attorney Dashboard:** [http://localhost:8000/dashboard.html](http://localhost:8000/dashboard.html)

## ☁️ Deployment

This project is optimized for **Vercel**. To deploy:

1. Push your code to a GitHub repository.
2. Connect your repository to Vercel.
3. Configure the environment variables in the Vercel Dashboard.
4. Deployment happens automatically on push.

## ⚖️ License

Private / Confidential. Built by Ai Future Team.

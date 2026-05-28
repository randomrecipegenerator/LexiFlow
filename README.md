# LexiFlow Legal Suite: Reasoning AI Intake & Lead Qualification

LexiFlow transforms law firm intake from a manual, leaky bucket into a 24/7 high-conversion revenue engine using **Reasoning AI**. We solve the "wasted billable hours" problem by qualifying leads with the nuance of a senior attorney but the speed and availability of a machine.

## 🚀 Key Features

- **Multi-Channel AI Intake (LexiFlow):** 
  - **Conversational Chat:** Natural language web widget for high-conversion capture.
  - **Voice AI Receptionist (Beta):** Handle inbound calls with low-latency reasoning agents (via Vapi).
  - **Email Intake & Triage:** Automatically parse and summarize inbound lead emails (via Postmark).
- **Medical & Legal Intelligence:**
  - **MeritScan:** AI Medical Merit Review for MedMal/PI cases. Generates automated chronologies and negligence alerts.
  - **DepoLens:** Advanced AI deposition analysis and summary engine.
- **Intelligent Qualification & Scoring:**
  - Proprietary **Narrative Synthesis** that captures the "story" behind the lead.
  - Automated scoring (0-100) based on firm-specific case criteria.
  - Instant conflict check against existing lead database.
- **Production CRM Integrations:**
  - **Clio Grow (Lexicata):** Direct sync to the intake inbox for seamless attorney review.
  - **Filevine & LeadDock:** Enterprise-ready lead pushing with custom field support.
  - **Simulation Mode:** Test and demo lead mapping without affecting production data.
- **Document Intelligence (OCR):**
  - Instant extraction of facts from medical records and legal documents.
  - Generates professional Medical Chronologies for personal injury cases.
- **Embedded eSign & Billing:**
  - Integrated Dropbox Sign (HelloSign) for immediate retainer signing.
  - Integrated LawPay/Stripe for instant consultation fee capture.

## 📂 Project Structure

```text
├── api/                # Vercel Serverless Function entry points
├── backend/            # Core FastAPI logic (Models, AI Engine, Integrations)
│   ├── integration_engine.py  # Production CRM & Webhook logic
│   ├── ai_engine.py           # LLM Prompting & Reasoning logic
│   └── models.py              # SQLAlchemy database schema
├── branding/           # Logos, icons, and social media assets
├── dashboard.html      # Professional Attorney Lead Dashboard
├── dashboard.js        # Dynamic management of leads and CRM settings
├── index.html          # Main landing page & floating chat widget
├── widget.js           # Lightweight embeddable intake script
└── requirements.txt    # Python dependencies
```

## 🛠️ Quick Start

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd lexiflow-mvp
   ```

2. **Set up Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure Environment:**
   Create a `.env` file with your API keys:
   ```env
   GROQ_API_KEY=your_key
   OPENAI_API_KEY=your_key
   POSTMARK_SERVER_TOKEN=your_token
   VAPI_API_KEY=your_key
   ```

4. **Run Locally:**
   ```bash
   python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```

## ☁️ Production Deployment

LexiFlow is optimized for **Vercel** and **FastAPI**.

- **Frontend:** Static files served via Vercel or FastAPI.
- **Backend:** Serverless endpoints and a persistent SQLite database (syncable via Turso for distributed teams).

## ⚖️ License

Proprietary & Confidential. Built by the LexiFlow AI Team.

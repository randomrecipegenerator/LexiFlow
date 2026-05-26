# LexiFlow MVP Walkthrough

This document provides a walkthrough of the LexiFlow MVP, an AI-powered legal intake assistant.

## 1. Client Intake Chatbot
The intake chatbot is a conversational interface designed to be embedded on a law firm's website. It greets potential clients and gathers essential information about their legal needs.

**Screenshot:** `screenshots/intake-chatbot.png`

### Conversational Flow
The AI is programmed to be professional and empathetic. It asks for:
- Full name and contact information.
- Details of the legal incident (type of case, dates, locations).
- Specific injuries or damages.

**Screenshot (In Action):** `screenshots/intake-chatting.png`

## 2. Lead Qualification Engine
After the client completes the intake, the system uses an LLM (OpenAI GPT-4o or Groq) to analyze the transcript.
- **Fact Extraction:** Extracts names, dates, and key legal facts.
- **Scoring:** Assigns a qualification score (0-100) based on firm-defined criteria.
- **Categorization:** Tags the lead as "High Priority", "Requires Review", or "Disqualified".
- **AI Summary:** Generates a concise summary for the attorney.

## 3. Attorney Dashboard
Attorneys can log in to the dashboard to see all incoming leads in real-time.

**Screenshot:** `screenshots/attorney-dashboard.png`

### Features:
- **Lead List:** High-level view of all leads with their scores and status.
- **Detail View:** Click "View" to see the full AI summary, complete chat transcript, and any uploaded documents.
- **Real-time Updates:** The dashboard automatically refreshes to show new leads.

---

## Technical Details for Demo
- **Live Demo URL:** `http://<sandbox-hostname>:8000/` (Intake)
- **Dashboard URL:** `http://<sandbox-hostname>:8000/dashboard.html`

*Note: Ensure the backend server is running using the instructions in the main README.md.*

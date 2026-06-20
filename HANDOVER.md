# LexiFlow Technologies Inc Legal Suite - Manual Handover & Deployment Guide

This document provides instructions for manually deploying the LexiFlow Technologies Inc Suite using the provided ZIP archive. This is a fallback method while GitHub push access is being resolved.

## 1. Handover Artifacts
The latest and most complete codebase is located at:
`/home/team/shared/lexiflow_update_20260526_final.zip`

**Key Features Included:**
- **Weekly Lead Reports**: Automated KPI tracking and email summaries for law firm partners.
- **MeritScan**: AI-powered medical merit review for personal injury cases.
- **Veritas Deposition™**: AI deposition conflict detector and chronology generator.
- **Refined Frontend**: Professional, product-centric landing pages and localized SEO city pages.
- **Consultation Flow**: Unified lead capture system routing to the backend dashboard.

## 2. Deployment Steps (Vercel)

LexiFlow is pre-configured for Vercel deployment.

1. **Unzip the Archive**: Extract the contents of `lexiflow_update_20260526_final.zip` to a local directory.
2. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```
3. **Initialize Project**:
   Run `vercel` in the root directory and follow the prompts to create a new project.
4. **Environment Variables**:
   Set the following variables in the Vercel Dashboard (Settings > Environment Variables):
   - `OPENAI_API_KEY`: Your OpenAI production key.
   - `GROQ_API_KEY`: (Optional) For faster/cheaper inference if configured.
   - `POSTMARK_SERVER_TOKEN`: Required for sending lead reports and notifications.
   - `DATABASE_URL`: Use a persistent Turso URL (see below) for production.
5. **Deploy**:
   ```bash
   vercel --prod
   ```

## 3. Database Strategy (Persistence)

Vercel functions are stateless. A local `lexiflow.db` file will **not** persist data between requests.

### Recommended: Turso (Serverless SQLite)
1. Create a free database at [Turso](https://turso.tech).
2. Set the following environment variables in Vercel:
   - `DATABASE_URL`: `libsql://your-db-name.turso.io`
   - `DATABASE_AUTH_TOKEN`: `your-auth-token`
3. The LexiFlow backend uses `SQLAlchemy` with `libsql` support. Ensure `libsql` is in your `requirements.txt` (it should be in the ZIP).

### Alternative: Persistent Volume
If deploying to a VPS (DigitalOcean, Railway, etc.), you can use the local `sqlite:///./lexiflow.db` provided you mount a persistent volume to the backend directory.

## 4. Initializing the Database

Once your environment variables are set:
1. Run the initialization script locally (pointing to your production DB via `.env`):
   ```bash
   python backend/scripts/init_db.py
   ```
2. Provision your first firm account:
   ```bash
   python backend/scripts/provision_firm.py --name "Your Law Firm" --email "partner@firm.com"
   ```

## 5. Next Steps for Pilot Batch 1
- **Domain Mapping**: Point your production domain (e.g., `app.lexiflow.co`) to the Vercel deployment.
- **SMTP Setup**: Ensure the Postmark token is valid so partners receive their Weekly Lead Reports.
- **Lead Intake**: Embed the intake form (found in the dashboard settings) on the firm's website.

---
*Created by the LexiFlow Technologies Inc Engineering Team - May 26, 2026*

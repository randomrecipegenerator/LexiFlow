# LexiFlow Production Deployment Guide

This guide covers the steps required to deploy LexiFlow to a production environment using Vercel for the frontend/API and Turso (or a persistent volume) for the SQLite database.

## 1. Prerequisites

- A [Vercel](https://vercel.com) account.
- (Optional but recommended) A [Turso](https://turso.tech) account for a distributed/serverless SQLite database.
- Production API keys for:
  - OpenAI or Groq
  - Clio Grow / Filevine (if using Production Sync)
  - Postmark (for email intake)
  - Vapi (for voice AI)
  - Dropbox Sign (for eSign)

## 2. Environment Variables

Create a `.env` file (or set these in your Vercel project settings):

```env
# Database
DATABASE_URL=sqlite:///./lexiflow.db  # For local/persistent volume
# OR for Turso:
# DATABASE_URL=libsql://your-db-name.turso.io
# DATABASE_AUTH_TOKEN=your-auth-token

# AI Providers
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...

# Integration Secrets
POSTMARK_SERVER_TOKEN=...
VAPI_API_KEY=...
ESIGN_API_KEY=...
```

## 3. Database Initialization

Before the first run, you must initialize the database schema.

1. Ensure you have the dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the initialization script:
   ```bash
   python create_tables.py
   ```

## 4. Deploying to Vercel

LexiFlow is optimized for Vercel deployment via the included `vercel.json` and `api/` directory.

1. Install the Vercel CLI: `npm i -g vercel`
2. Run `vercel` in the root directory.
3. Follow the prompts to link your project.
4. Add your Environment Variables in the Vercel Dashboard.
5. Deploy: `vercel --prod`

## 5. Persistence Note (SQLite)

Vercel functions are stateless. If you use a local `sqlite:///./lexiflow.db`, data will **not** persist between function invocations.

**Recommended Production Database:**
Use **Turso** with the `libsql` driver. LexiFlow is compatible with Turso. Simply update your `DATABASE_URL` and ensure the `libsql` package is in your `requirements.txt`.

## 6. Post-Deployment Setup

1. **Provision Firms:** Use the `backend/scripts/provision_firm.py` script to create your initial law firm accounts.
2. **Webhooks:**
   - Configure Vapi to point to `https://your-domain.com/api/webhooks/vapi`
   - Configure Postmark to point to `https://your-domain.com/api/webhooks/postmark`

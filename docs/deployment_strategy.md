# LexiFlow Production Deployment Strategy

This document outlines the recommended hosting and deployment architecture for LexiFlow, optimized for US-based hosting and data residency.

## 1. Hosting Architecture

### Frontend (User Interface)
- **Provider**: [Vercel](https://vercel.com) or [Netlify](https://netlify.com)
- **Region**: Global Edge (with focus on US East/West)
- **Reason**: Excellent for React/Vite/Static sites, automatic CI/CD from GitHub, and free SSL.
- **Cost**: $0 (Hobby) or $20/month (Pro) for team collaboration.

### Backend (FastAPI API)
- **Provider**: [Render](https://render.com) or [Fly.io](https://fly.io)
- **Region**: US East (`us-east-1` / Northern Virginia) or US West (`us-west-2` / Oregon)
- **Reason**: 
    - **Render**: Extremely easy to set up for FastAPI. Native support for Python.
    - **Fly.io**: Runs close to the users. Good for low latency.
- **Cost**: ~$7/month for a "Starter" instance on Render.

### Database (Lead Storage)
- **Provider**: [Turso](https://turso.tech)
- **Reason**: Distributed SQLite. Allows for "Edge" data placement.
- **Compliance**: Configured to keep data within US-based regions for low latency and data residency.
- **Cost**: $0 (Starter) or $29/month (Scaler).

## 2. Infrastructure Setup

### Environment Variables
All sensitive data (API keys, DB URLs) must be stored as environment variables:
- `DATABASE_URL`: Turso connection string.
- `TURSO_AUTH_TOKEN`: Token for DB access.
- `OPENAI_API_KEY`: For the AI Engine.
- `FRONTEND_URL`: For CORS configuration.

### Domain & SSL
- **Domain**: LexiFlow.law or LexiFlow.ai
- **SSL**: Automated via Vercel (Frontend) and Render (Backend).

## 3. Data Residency & Security Compliance

- **Data Residency**: All backend services and databases are pinned to US regions (e.g., Northern Virginia).
- **Encryption**: 
    - Data at rest: Handled by Turso (encrypted storage).
    - Data in transit: TLS 1.3 enforced by Vercel/Render.
- **Audit Logs**: Persistent logs of all PII access are already implemented in the MVP.
- **Data Deletion**: "Right to be Forgotten" endpoint is implemented for privacy compliance.

## 4. Deployment Pipeline

1. **Push to GitHub**: Triggers automatic builds.
2. **Preview Deploys**: Every Pull Request gets a unique URL for testing.
3. **Production Deploy**: Merging to `main` updates the live site.

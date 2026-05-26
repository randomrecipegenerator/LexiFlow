# LexiFlow Vercel Migration Guide

This guide explains how to deploy the LexiFlow platform to Vercel as a unified application (both Frontend and Backend on one domain).

## Prerequisites
- A Vercel account.
- Your GitHub repository connected to Vercel.
- OpenAI API Key.

## Project Structure for Vercel
The project has been configured with a `vercel.json` file that handles routing:
- Requests to `/api/*` are routed to the FastAPI backend (`api/index.py`).
- All other requests are routed to the `frontend/` directory.

## Deployment Steps

1. **Import Project in Vercel:**
   - Go to [vercel.com/new](https://vercel.com/new).
   - Select your LexiFlow repository.

2. **Configure Environment Variables:**
   In the Vercel project settings, add the following environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key.
   - `DATABASE_URL`: (Optional) A remote SQLite or PostgreSQL URL. 
     *Note: If not provided, a local `lexiflow.db` will be used, but it will NOT persist across deployments or serverless function restarts.*
   - `ALLOWED_ORIGINS`: `*` (or your custom domain).

3. **Deploy:**
   - Click **Deploy**. Vercel will automatically detect the Python backend and the static frontend.

## Connecting Your Domain (`lexiflow.co`)

1. In the Vercel Dashboard, go to **Settings > Domains**.
2. Add `lexiflow.co` and `www.lexiflow.co`.
3. Vercel will provide DNS records (usually an A record and a CNAME).
4. Go to your domain registrar (e.g., Namecheap) and update the DNS records as instructed by Vercel.

## Important Note on Persistence
Vercel's serverless functions have a read-only filesystem (except for `/tmp`). 
**SQLite files stored in the project directory will not persist data.**

To have a fully functional CRM and Lead database, you should use a persistent database:
- **Turso (SQLite):** Recommended for maintaining the current SQLite compatibility.
- **Vercel Postgres:** A great alternative if you want to stay within the Vercel ecosystem.

To use a persistent database, simply update the `DATABASE_URL` environment variable.

## Functionality Check
Once deployed, verify the following:
- **Chat Widget:** Open `lexiflow.co` and interact with Lexi.
- **Attorney Dashboard:** Go to `lexiflow.co/dashboard` to see leads.
- **CRM Sync:** Try syncing a lead to Clio/MyCase/Filevine (simulated).

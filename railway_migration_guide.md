# LexiFlow Railway Migration & Setup Guide

This guide details how to deploy the LexiFlow platform (Frontend and Backend) to **Railway.app** as separate services within a single project. This provides a "single-pane-of-glass" management experience while maintaining clean separation between your API and Landing Page.

## 1. Project Preparation
The repository has been updated with the following:
- `Procfile`: Defines the start command for the Backend.
- `requirements.txt`: Includes all necessary Python dependencies.
- `frontend/config.js`: Pointed to `https://api.lexiflow.co`.

## 2. Deployment Steps

### Step 1: Create a Railway Project
1. Log in to [Railway.app](https://railway.app/) using your GitHub account (`goudzrj@gmail.com`).
2. Click **New Project** > **Deploy from GitHub repo**.
3. Select the `lexiflow-mvp` repository.

### Step 2: Deploy the Backend Service
1. Once the repo is connected, Railway will create a default service. Rename it to **Backend**.
2. **Environment Variables**: Go to the **Variables** tab for the Backend service and add:
   - `OPENAI_API_KEY`: (Your OpenAI Key) - *Required for 'Lexi' AI*
   - `DATABASE_URL`: `sqlite:///./lexiflow.db` (Or your Turso URL)
   - `ALLOWED_ORIGINS`: `https://lexiflow.co,https://www.lexiflow.co`
3. **Custom Domain**:
   - Go to **Settings** > **Networking**.
   - Click **Custom Domains** and add `api.lexiflow.co`.
   - Update your Namecheap DNS CNAME for `api` to point to the Railway provided URL.

### Step 3: Deploy the Frontend Service
1. In the same Railway project, click **New** > **GitHub Repo** (select the same repo again).
2. Rename this second service to **Frontend**.
3. **Settings**:
   - Under **General**, set the **Root Directory** to `/frontend`.
   - Railway will automatically detect the `index.html` and serve it as a static site.
4. **Custom Domain**:
   - Go to **Settings** > **Networking**.
   - Click **Custom Domains** and add `lexiflow.co` and `www.lexiflow.co`.
   - Update your Namecheap DNS A Record (@) and CNAME (www) to point to the Railway provided URLs.

## 3. SSL & Domains (Namecheap Instructions)
Ensure your Namecheap DNS records match the Railway settings:

| Host | Type | Value | Purpose |
|------|------|-------|---------|
| @ | A | (Railway IP) OR CNAME | Points root domain to Frontend |
| www | CNAME | (Railway URL) | Points www to Frontend |
| api | CNAME | (Railway URL) | Points api to Backend |

*Note: Railway automatically provisions SSL certificates once the DNS records propagate.*

## 4. Verification
- **Lexi AI**: Visit `https://lexiflow.co` and interact with the floating chat bubble. It will connect to the backend at `api.lexiflow.co`.
- **API Docs**: Visit `https://api.lexiflow.co/docs` to verify the backend is healthy.
- **Dashboard**: Access the attorney dashboard at `https://lexiflow.co/dashboard.html`.

---
**Migration Status**: Repository Ready for Railway.
**Owner Account**: goudzrj@gmail.com

# Vercel Deployment Guide for LexiFlow AI

The error "Extract path must be within an htdocs folder" suggests you are trying to use a traditional PHP hosting file manager. **Vercel does not use htdocs.**

Follow these steps to deploy correctly:

### 1. The Right Way to Deploy
The best way to deploy to Vercel is via the **GitHub Integration** or the **Vercel CLI**.
- **GitHub:** Push your code to a GitHub repo and import it at [vercel.com/new](https://vercel.com/new).
- **CLI:** Run `npm install -g vercel` then `vercel` in your project root.

### 2. Environment Variables
You MUST set these variables in the Vercel Dashboard (Project Settings > Environment Variables):
- `AI_API_KEY`: Your OpenAI or Groq API Key.
- `DATABASE_URL`: (Optional) Use a Turso URL for persistent database storage. If not set, it uses `/tmp/lexiflow.db` (ephemeral).

### 3. Database Persistence
By default, I've configured the app to copy `lexiflow.db` from your repo to `/tmp/lexiflow.db` on startup. 
*Note: Any data added via the website on Vercel will be lost when the server restarts unless you use a remote database like Turso.*

### 4. Technical Fixes Applied
I have already fixed the following in your codebase:
- **`api/index.py`**: Fixed a bug where a failed backend import would crash the fallback app.
- **`backend/database.py`**: Added logic to seed the Vercel `/tmp` database from your repository file.
- **`.vercelignore`**: Created this file to prevent uploading unnecessary files (like your local virtual environment), which keeps the deployment small and fast.

**Next Step:** Try deploying again using the **Vercel CLI** or by connecting your **GitHub repository** to Vercel.

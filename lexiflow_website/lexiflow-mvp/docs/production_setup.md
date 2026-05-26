# LexiFlow Production Setup Guide (Namecheap Edition)

This guide details the final production configuration for the `lexiflow.co` domain, connecting your Vercel (Frontend) and Render (Backend) environments using **Namecheap**.

## 1. DNS Records in Namecheap

To set up your domain, follow these steps in your Namecheap dashboard:

1.  Log in to your **Namecheap** account.
2.  Go to **Domain List** and click the **Manage** button next to `lexiflow.co`.
3.  Click on the **Advanced DNS** tab.
4.  In the **Host Records** section, click **Add New Record** for each of the following:

| Type  | Host | Value                          | TTL        | Purpose                        |
|-------|------|--------------------------------|------------|--------------------------------|
| A Record | @    | 76.76.21.21                    | Automatic  | Points root domain to Vercel   |
| CNAME Record | www  | cname.vercel-dns.com           | Automatic  | Points www subdomain to Vercel |
| CNAME Record | api  | lexiflow-backend.onrender.com | Automatic  | Points api subdomain to Render |

*Important: If there are any existing 'URL Redirect Records' or 'Parking' records for the @ or www hosts, please delete them to avoid conflicts.*

## 2. Environment Configuration

Ensure the following environment variables are set in your Render and Vercel dashboards:

### Backend (Render)
- `FRONTEND_URL`: `https://lexiflow.co`
- `BACKEND_URL`: `https://api.lexiflow.co`
- `ALLOWED_ORIGINS`: `https://lexiflow.co,https://www.lexiflow.co`
- `DATABASE_URL`: (Your Turso connection string)

### Frontend (Vercel)
- `API_BASE`: `https://api.lexiflow.co`

## 3. Verification

Once DNS records are saved (propagation typically takes 1-24 hours):
1.  **Add Domains to Vercel (Frontend):**
    - Go to your Vercel Project Settings > Domains.
    - Add `lexiflow.co` and `www.lexiflow.co`.
    - If Vercel provides a TXT record for verification (e.g., `_vercel`), add it to Namecheap.
2.  **Add Domain to Render (Backend):**
    - Go to your Render Web Service > Settings > Custom Domains.
    - Add `api.lexiflow.co`.
3.  **Verification:**
    - Visit `https://lexiflow.co` to ensure the landing page is live.
    - Check `https://api.lexiflow.co/docs` to verify the API is reachable.
    - Test the chatbot and dashboard to ensure data is flowing correctly.

## 4. Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| `DEPLOYMENT_NOT_FOUND` | DNS points to Vercel, but domain is not added to project. | Add `lexiflow.co` in Vercel Project Settings > Domains. |
| `SSL Handshake Failure` / `Error 1001` | Domain is not added to the provider's dashboard. | Ensure the domain is added in BOTH Vercel (frontend) and Render (backend). |
| `Parking Page` | Default Namecheap records are still active. | Delete any existing A or CNAME records for `@` and `www` that point to Namecheap IPs. |

---
**Status**: DNS Configured; Awaiting Provider Dashboard Activation.
**Domain**: `lexiflow.co`

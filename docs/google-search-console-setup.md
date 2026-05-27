# LexiFlow Google Search Console & Indexing Guide

## Prerequisites
- Domain: `lexiflow.co` — deployed to Vercel
- Google account (any Gmail works)
- All city landing pages created at `/cities/*.html`
- Updated sitemap at `/sitemap.xml`
- Updated `robots.txt` at `/robots.txt`

---

## Step 1: Deploy the Latest Code to Vercel

Before submitting to Google, ensure the latest version is live:

```bash
# From the project root (already deployed via Vercel Git integration)
git add .
git commit -m "feat: add 10 local SEO landing pages + update sitemap"
git push origin main
```

Vercel will auto-deploy. Verify:
- https://lexiflow.co/robots.txt — should show `Allow: /` and point to sitemap
- https://lexiflow.co/sitemap.xml — should list all 10 city pages
- https://lexiflow.co/cities/nyc — should load the NYC landing page
- https://lexiflow.co/cities/chicago — should load Chicago page
- (repeat for all 10 cities)

---

## Step 2: Google Search Console — Domain Verification

### Option A: DNS TXT Record (Recommended)
1. Go to https://search.google.com/search-console
2. Sign in with your Google account
3. Add property → Select **"Domain"** → Enter `lexiflow.co`
4. Google will give you a **TXT record** like: `google-site-verification=xxxxxxxx`
5. Add this TXT record to your **DNS provider** (Cloudflare, Namecheap, etc.):
   - Type: `TXT`
   - Name: `@` or `lexiflow.co`
   - Value: `google-site-verification=xxxxxxxx`
6. Click **Verify** in Search Console

### Option B: HTML File Upload (Alternative)
If DNS is unavailable:
1. Add property → Select **"URL prefix"** → Enter `https://lexiflow.co`
2. Download the `google123456789.html` verification file
3. Upload it to the root directory of the project
4. Deploy to Vercel
5. Click **Verify** in Search Console

---

## Step 3: Submit the Sitemap

1. In Google Search Console, select your property
2. Go to **Sitemaps** (under Indexing)
3. In "Enter sitemap URL", type: `sitemap.xml`
4. Click **Submit**

Google will show:
- **Status**: Success
- **URLs submitted**: ~15 (homepage + 10 cities + features + depolens + etc.)

---

## Step 4: Request Indexing for Priority Pages

### Manual URL Inspection
1. In Search Console, go to **URL Inspection**
2. Enter: `https://lexiflow.co/`
3. Click **Request Indexing**
4. Repeat for priority city landing pages:

| Page | URL |
|------|-----|
| Homepage | `https://lexiflow.co/` |
| NYC | `https://lexiflow.co/cities/nyc` |
| Los Angeles | `https://lexiflow.co/cities/la` |
| Chicago | `https://lexiflow.co/cities/chicago` |
| Houston | `https://lexiflow.co/cities/houston` |
| DepoLens | `https://lexiflow.co/depolens` |
| MeritScan | `https://lexiflow.co/meritscan` |

---

## Step 5: Verify Robots.txt & Crawlability

Current `robots.txt` (already correct):
```
User-agent: *
Allow: /
Sitemap: https://lexiflow.co/sitemap.xml
```

✅ **Allows** crawling of all pages including city landing pages
✅ **Points** to the sitemap for discovery
✅ **No disallowed paths** that would block city content

To double-check in Search Console:
1. Go to **Settings** → **Crawl stats**
2. Ensure no 404 errors on city pages

---

## Step 6: Monitor & Track

After submission, monitor these Search Console reports:

| Report | What to Look For |
|--------|-----------------|
| **Performance** | Impressions/clicks for city keywords |
| **Index Coverage** | All city pages indexed (status: "Valid") |
| **Sitemaps** | Successful submission with no errors |
| **Mobile Usability** | No mobile errors (pages are responsive) |

### Expected Timeline
- **Sitemap processing**: 1–3 days
- **Initial indexing of new pages**: 1–7 days
- **Keyword ranking for city terms**: 2–12 weeks (depends on competition)

---

## Step 7 (Optional): Google My Business

For local SEO synergy, also:
1. Claim/verify your **Google Business Profile** for LexiFlow
2. Set location to Chicago, IL (matching the footer address)
3. Add website URL: `https://lexiflow.co`
4. This helps local searches for "AI legal intake" in Chicago

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Sitemap has errors | Validate at https://www.xml-sitemaps.com/validate-xml-sitemap.html |
| City pages not found | Check Vercel rewrites in `vercel.json` |
| Verification fails | Ensure TXT record or HTML file is exactly as Google specified |
| Pages not indexed | Use URL Inspection → Request Indexing for each |
| 404 errors on city pages | Deploy the latest code with city pages and vercel rewrites |

---

## Files Included in This Setup

| File | Purpose |
|------|---------|
| `robots.txt` | Allows all bots, points to sitemap |
| `sitemap.xml` | Lists all pages (home + 10 cities + features + more) |
| `vercel.json` | Rewrites clean URLs `/cities/nyc` → `/cities/nyc.html` |
| `googleREPLACE_ME_WITH_YOUR_VERIFICATION_CODE.html` | Placeholder for GSC HTML verification |

---

## Team Contact

For any SEO or indexing questions, contact the Content & SEO Specialist.

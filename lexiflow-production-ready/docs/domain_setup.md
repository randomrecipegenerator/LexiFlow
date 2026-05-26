# 2-Step Custom Domain Setup for LexiFlow

Since you are using Vercel (login: goudzrj@gmail.com), follow these two steps to go live:

### Step 1: Add Domain in Vercel
In your Vercel project dashboard, go to **Settings > Domains**. Type `lexiflow.co` and click **Add**. If it asks about a redirect from `www`, select the recommended option.

### Step 2: Update Namecheap DNS
Vercel will show you two records (an **A record** for `lexiflow.co` and a **CNAME record** for `www`). 
Log into your **Namecheap** account and update the DNS settings for `lexiflow.co` to match the exact values shown in Vercel.

Once saved, it may take a few minutes for the "Valid Configuration" checkmark to appear in Vercel.

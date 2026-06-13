# LexiFlow Perfect Demo — NYC Bar Association Meeting
## Rodriguez v. Mount Sinai — 8-Minute Presentation Walkthrough
### Tuesday, July 7, 2026 — 10:00 AM ET

---

## Presenter Quick Start

**Credentials:**
- Dashboard: https://lexiflow.co/dashboard.html
- Attorney: `attorney@lexiflow.tech` / `TestPass123!`
- Admin: `admin@lexiflow.tech` / `AdminPass123!`
- Firm slug: `lexiflow-tech`

**Demo Data Files (pre-staged):**
All in `/home/team/shared/LexiFlow-Final/demo_data/`:
- `rodriguez_chronology.json` — Medical chronology with 14-hour treatment gap
- `depolens_scenario.json` — Deposition contradictions & AI cross-exam questions
- `crm_sync_demo.json` — Filevine sync simulation log
- `QUICK_START_CHEATSHEET.txt` — One-page reference for the presenter
- `verify_demo.sh` — Post-demo API verification script

---

## Walkthrough (8 minutes)

### Step 1: AI Intake (1:00) → [demo.html]

1. Navigate to **https://lexiflow.co/demo.html**
2. Click **"Try the AI Intake Agent"**
3. Enter the lead:
   - Name: *Elena Rodriguez*
   - Phone: *(212) 555-0147*
   - Email: *e.rodriguez@email.com*
4. Describe the incident:
   > "My mother went to Mount Sinai ER for severe leg pain and a high fever. The hospital waited 14 hours before giving her any antibiotics. Now she has lost both legs below the knee."

**What the audience sees:** AI chatbot responds naturally, asks follow-ups, begins qualifying the lead in real-time.

---

### Step 2: Attorney Dashboard — Lead Review (1:00) → [/dashboard.html]

1. Log in to the dashboard with attorney credentials
2. Click the **"Leads"** tab
3. Find "Rodriguez, Elena" — click to open

**Presenter script:**
> "In 3 seconds, LexiFlow's AI has already scored this case 87 out of 100, flagged it as 'High Priority,' and estimated the case value at $3.5M–$5.2M based on the specific facts — delayed sepsis diagnosis in New York."

**Key points to show:**
- Qualification score: **87/100** (High Priority)
- Case type: Medical Malpractice — Delayed Diagnosis
- Estimated value: **$3,500,000 – $5,200,000**
- AI Summary auto-generated from the chat transcript

---

### Step 3: Settlement Predictor with NY Damage Caps (1:30) → Lead Detail → [Settlement Predictor]

1. From the lead detail page, click **"AI Settlement Predictor"**

**Presenter script:**
> "Here's where LexiFlow really differentiates for New York firms. The AI knows that New York has NO cap on non-economic damages — no limit on pain and suffering. This is critical because a CA firm using the same platform would see their $5M estimate capped at $353,000 under MICRA."

**Show this comparison:**
| Jurisdiction | Estimated Value | Cap Applied | Max Recovery |
|-------------|----------------|------------|-------------|
| **New York** (this case) | $4,200,000 | **No cap** | $4,200,000 |
| California (if same case) | $4,200,000 | $353,000 MICRA | $353,000 |
| Texas (if same case) | $4,200,000 | $250k/defendant | $750,000 |

**Demo the caps API:**
```bash
# NY — No cap (full value)
curl https://lexiflow.co/api/enterprise/settlement/caps/NY

# CA — $353k MICRA cap
curl https://lexiflow.co/api/enterprise/settlement/caps/CA

# TX — $250k per defendant
curl https://lexiflow.co/api/enterprise/settlement/caps/TX
```

**Live API endpoints to show:**
- `GET /api/enterprise/settlement/caps` — All 50 states + DC
- `GET /api/enterprise/settlement/caps/no-cap-states` — 15 plaintiff-friendly states
- `GET /api/enterprise/settlement/caps/cap-states` — 36 states with caps

---

### Step 4: Discovery-Vault — Medical Chronology (1:30) → [/discovery-vault or /enterprise]

1. Click **"Discovery-Vault™"** in the sidebar
2. The Rodriguez case appears with document count and processing status
3. Click **"View Chronology"** to show the AI-generated timeline

**The 14-Hour Gap (Core of the Case):**

| Time | Event | Evidence |
|------|-------|----------|
| May 10, 18:30 | Admitted — 103.2°F, HR 115, qSOFA 2/3 | ER Triage |
| May 10, 19:15 | Resident orders blood cultures + antibiotics | Physician Notes |
| **May 10 20:00 → May 11 09:30** | **⚠️ 14-HOUR GAP — No antibiotics given** | **MAR, Nursing Logs** |
| May 11, 10:00 | Code Blue — Septic shock (BP 70/40) | Code Sheet |
| May 12 | Bilateral foot necrosis | Surgical Consult |
| May 15 | Double below-knee amputation | Op Report |

**Presenter script:**
> "The AI reviewed thousands of pages of medical records and constructed this chronology in under 30 seconds. It automatically flagged the 14-hour gap where antibiotics were ordered but never administered — that's the deviation from the standard of care that a jury will focus on. A paralegal would take 3–5 hours to do this manually."

**Merit Score:** 92/100 — 4 negligence markers identified

---

### Step 5: DepoLens™ — Impeachment Preparation (1:00) → [/depolens or /enterprise]

1. Click **"DepoLens™"** in the sidebar
2. Select the "Dr. Alan Miller (ER Attending)" deposition

**Key Contradictions Flagged by AI:**

| Doctor's Testimony | Evidence Contradiction |
|-------------------|----------------------|
| "I confirmed antibiotics at 19:45" | MAR shows zero administration until 10:15 next day |
| "Patient was stable overnight" | qSOFA score of 2 = 10% in-hospital mortality risk |

**AI-Generated Cross-Examination Questions:**
1. "Does the hospital's Sepsis Protocol require the 3-Hour Bundle for patients meeting qSOFA criteria?"
2. "If the 3-Hour Bundle was not completed within 14 hours, would you agree that is a deviation?"
3. "Who was the nurse assigned to Bed 4 between 20:00 and 08:00?"

**Presenter script:**
> "DepoLens scanned 94 pages of deposition testimony, found 7 contradictions with the medical records, and generated these cross-examination questions — all before the attorney has even finished reviewing the case."

---

### Step 6: One-Click CRM Sync — Filevine (1:00) → Lead Detail → [Sync to CRM]

1. Click **"Sync to CRM"** → select **"Filevine"**
2. Show the sync result confirmation

**Sync sends to Filevine:**
```
✓ Lead: "Rodriguez, Elena" created in Filevine
✓ Case Type: Medical Malpractice
✓ AI Score: 87 (custom field)
✓ Case Value: $4,200,000 (custom field)
✓ Merit Score: 92 (custom field)
✓ Medical chronology: attached as project note
✓ Status: "Intake - High Priority"
✓ Notification sent to: sarah.johnson@lexiflow.tech
```

**Presenter script:**
> "One click. The entire lead — with AI score, case value, medical chronology, and merit analysis — is synced to Filevine. The attorney gets a notification. No data entry, no copy-paste, no spreadsheets. The case is in their workflow instantly."

**Show sync history:** Navigate to **Settings → CRM Sync Log** → shows timestamped audit trail of all syncs.

---

## Post-Demo Verification

Run `verify_demo.sh` or these commands:

```bash
# 1. API Health
curl https://lexiflow.co/api/health

# 2. NY Damage Caps
curl https://lexiflow.co/api/enterprise/settlement/caps/NY

# 3. No-Cap States (plaintiff-friendly)
curl https://lexiflow.co/api/enterprise/settlement/caps/no-cap-states

# 4. Enterprise Dashboard
curl https://lexiflow.co/api/enterprise/dashboard

# 5. Discovery Overview
curl https://lexiflow.co/api/enterprise/discovery/overview
```

---

## Partnership Talking Points

| Topic | Message |
|-------|---------|
| **NY Bar Member Pricing** | 20% discount on all tiers for NYC Bar members |
| **CLE Credit** | Each Enterprise module qualifies for 1-hour CLE in NY (ethics/technology) |
| **White-Label Option** | NYC Bar can offer LexiFlow as a member benefit with co-branding |
| **Data Residency** | All NY case data hosted in US-East (AWS) — meets NY data privacy requirements |
| **HIPAA** | BAAs on file, SOC 2 Type II, AES-256 encryption |

---

## Files Reference

| File | Location | Purpose |
|------|----------|---------|
| NYC_BAR_DEMO_SCRIPT.md | `/home/team/shared/` | Full demo script (lead-saved) |
| DEMO_WALKTHROUGH.md | `/home/team/shared/LexiFlow-Final/` | This file — step-by-step presenter guide |
| QUICK_START_CHEATSHEET.txt | `demo_data/` | One-page reference card |
| rodriguez_chronology.json | `demo_data/` | Medical chronology for Discovery-Vault |
| depolens_scenario.json | `demo_data/` | DepoLens contradictions & AI questions |
| crm_sync_demo.json | `demo_data/` | Filevine sync simulation |
| verify_demo.sh | `demo_data/` | Post-demo API verification |
| nyc-bar-meeting-prep.md | `/home/team/shared/lexiflow-sales/outreach/` | Meeting prep materials |
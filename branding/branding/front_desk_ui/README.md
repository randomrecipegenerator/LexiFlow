# AI Front Desk Settings — UI Design Mockup

**Location:** `/home/team/shared/branding/front_desk_ui/index.html`

## Overview
High-fidelity HTML/CSS prototype for the LexiFlow "AI Front Desk" settings dashboard. Designed to match the existing LexiFlow dashboard aesthetic (Bootstrap 5 + Bootstrap Icons + Chart.js + Inter font) while introducing new configuration panels for voice, email, and analytics.

## Sections

### 1. Voice Settings (`#voice-tab`)
- **Voice Agent Toggle** — Master on/off switch for the voice AI.
- **Voice Selection** — Card-based grid showing 6 voice profiles (Sarah, James, Elena, Michael, Sofia, Custom) with play-preview buttons. Currently selected: "Sarah (American, Warm)".
- **Call Routing** — After-hours action dropdown (voicemail, answering service, partner on-call, callback).
- **Emergency Keyword Detection** — Comma-separated keywords (emergency, urgent, crash) that trigger SMS alerts.
- **Vapi.ai Integration Status** — Shows "Connected" with latency (~450ms), HIPAA compliance badge.

### 2. Email Settings (`#email-tab`)
- **Email Toggle** — Master on/off for email intake.
- **Inbound Address Display** — Shows `intake@[firm].lexiflow.co` with copy button.
- **Auto-Reply Template Editor** — Rich textarea with variable insertion chips ({{first_name}}, {{firm_name}}, {{case_type}}, {{intake_url}}, {{tracking_id}}).
- **Postmark Integration Card** — Status indicator showing "Connected" with weekly volume.

### 3. Active Hours (`#hours-tab`)
- **Weekly Grid** — Monday–Friday with time inputs (08:00–18:00).
- **Weekend Toggle** — Saturday/Sunday have toggle switches to enable/disable with time inputs that disable when unchecked.
- **Clean grid layout** — Day / Open / Close columns.

### 4. Custom Greeting (`#greeting-tab`)
- **Voicemail Greeting Editor** — Textarea for custom AI greeting message.
- **Preview Button** — Play greeting via ElevenLabs TTS.
- **Character guidance** — 250 char recommendation.

### 5. Quick Stats (Top Row)
- Voice Calls Taken (247, +12.5%)
- Emails Processed (183, +8.3%)
- Web Leads (412, +5.2%)
- Qualification Rate (68%, +3.1%)

### 6. Lead Source Analytics (Right Panel)
- **Donut Chart** (Chart.js) — Web Widget (54%), Voice Call (32%), Email Intake (14%).
- **Source Breakdown List** — Per-source counts, percentages, and week-over-week trends.
- **Recent AI Activity Feed** — Timestamped activity log showing voice calls, emails, and web intakes with status indicators.

## Design Decisions
- **Consistent with LexiFlow dashboard**: Dark gradient navbar, white card-based layout, same border-radius (12px), shadow patterns, and color system.
- **Bootstrap Pills navigation** for tab switching (familiar UX pattern).
- **Stat cards** use color-coded left borders (blue=voice, green=email, yellow=web, info=conversion).
- **Toggle switches** for all activation controls (consistent with modern SaaS settings).
- **Source badges** with distinct colors (blue/web, green/voice, yellow/email) for quick visual scanning.

## Next Steps for Engineering
1. Wire up the Vapi.ai API to the "Voice Agent" toggle and voice profile selection.
2. Connect Postmark inbound webhook to the email tab's status indicator.
3. Replace the static Chart.js data with live API data from the backend.
4. Implement SMS alerting for emergency keyword detection.
5. Connect "Active Hours" to the call routing logic in the FastAPI backend.
# LexiFlow Enterprise CRM Integration

## Overview
Dedicated CRM integration package for legal practice management CRMs.
Supports Filevine, Clio Grow (Lexicata), and LeadDock with bidirectional sync.

## Architecture

```
backend/crm/
├── __init__.py      # Package init
├── README.md        # This file
├── api.py           # FastAPI router (config, sync, webhook endpoints)
├── filevine.py      # Filevine client (OAuth, projects, contacts, docs)
├── clio.py          # Clio Grow client (OAuth, leads, contacts)
└── webhooks.py      # Webhook receivers (bidirectional sync handlers)
```

## Features

### Filevine Client (`filevine.py`)
- OAuth2 session-based authentication with auto-refresh
- Project (case) CRUD: create, get, update, search
- Contact CRUD: create, search (dedup), get
- Document upload to project
- Custom field get/set
- Webhook signature verification (HMAC-SHA256)
- Lead-to-project mapping with standard fields

### Clio Grow Client (`clio.py`)
- OAuth2 PKCE flow: authorization URL generation, code exchange, token refresh
- Lead (inbox_lead) CRUD: create, get, update, convert to matter
- Contact search for deduplication
- Activity logging on leads
- Lead-to-inbox mapping

### Webhook Handler (`webhooks.py`)
- Normalized `WebhookEvent` dataclass across all CRMs
- Signature verification for Filevine, Clio, LeadDock
- FastAPI route handlers for each CRM's webhook format
- Extensible handler registry for custom event processing

### API Endpoints (`api.py`)
| Endpoint | Description |
|---|---|
| `GET  /api/crm/config` | Get firm CRM config (masked) |
| `PUT  /api/crm/config` | Update firm CRM config |
| `POST /api/crm/config/test` | Test connection to a CRM |
| `POST /api/crm/sync/{lead_id}` | Sync a lead to CRM |
| `POST /api/crm/sync-all` | Sync all qualified leads |
| `GET  /api/crm/sync-status/{lead_id}` | Get lead sync status |
| `GET  /api/crm/history` | Get sync audit log |
| `GET  /api/crm/stats` | Get CRM statistics |

## Configuration

Store CRM credentials per firm in the `Firm.api_config_json` field:

```json
{
  "filevine_api_key": "abc123",
  "filevine_api_secret": "def456",
  "filevine_session_id": "",
  "filevine_org_id": "org_123",

  "clio_client_id": "abc123",
  "clio_client_secret": "def456",
  "clio_access_token": "",
  "clio_refresh_token": "",
  "clio_redirect_uri": "https://lexiflow.co/api/crm/clio/callback",

  "leaddock_api_key": "abc123",

  "sync_min_score": 70,
  "sync_targets": ["filevine", "leaddock"],
  "postmark_api_key": "abc123"
}
```

## Score-Based Routing

- **>= 70**: Sync to Filevine + LeadDock
- **>= 50**: Sync to LeadDock only
- **< 50**: Hold for manual review

## Adding New CRM Systems

1. Create a new client file in `backend/crm/` (e.g., `mycase.py`)
2. Implement the client class with `_request()`, auth, and CRUD methods
3. Add mapping in `UniversalLeadMapper` in `backend/integration_engine.py`
4. Register webhook handlers in `backend/crm/webhooks.py`
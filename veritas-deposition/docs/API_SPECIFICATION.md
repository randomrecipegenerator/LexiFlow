# Veritas Deposition™ — API Specification v1.0

## Evidence Intelligence System™ Backend API Reference

---

## Overview

- **Base URL (Production):** `https://lexiflow.co/api/veritas`
- **Base URL (Development):** `http://localhost:4000/api/veritas`
- **Authentication:** JWT Bearer token (`Authorization: Bearer <token>`) or X-API-Key header
- **Content Type:** `application/json`

---

## Data Model (PostgreSQL via Prisma ORM)

### Core Entity Structure

```
Matter (Case)
 ├── Depositions (Transcripts w/ metadata)
 │     ├── Testimony (Structured segments, pgvector embeddings for RAG)
 │     └── Contradictions (AI-detected conflicts)
 ├── Evidence (Uploaded exhibits, documents, records)
 ├── Witnesses (Profiles, credibility scores)
 └── Documents (Raw uploaded files, OCR pipeline)
```

### Key Models

| Model | Fields | Purpose |
|-------|--------|---------|
| **Matter** | id, title, caseNumber, caseType, jurisdiction, status, firmId | Top-level case container |
| **Deposition** | id, matterId, witnessName, date, durationMinutes, pageCount, transcriptText, credibilityScore | Single deposition transcript |
| **Testimony** | id, depositionId, pageNumber, lineNumber, speaker, text, topic, embedding (vector(1536)) | Structured testimony segment with pgvector for RAG |
| **Contradiction** | id, matterId, depositionId, testimonyIdA, testimonyIdB, evidenceId, type (4 types), severity, reasoning, confidence | AI-flagged conflict between testimony/evidence |
| **Evidence** | id, matterId, depositionId, title, evidenceType (7 types), filePath, exhibitNumber | Uploaded evidence documents |
| **Witness** | id, matterId, name, role, specialty, credibilityScore | Witness profile |
| **AiAnalysis** | id, depositionId, contradictions, keyAdmissions, credibilityScore, summary | Cached AI analysis results |

---

## API Endpoints

### 🔷 Matter Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/matters` | List matters (filter: status, firmId, search, page, limit) |
| `GET` | `/matters/:id` | Get matter detail with depositions, evidence, contradictions |
| `POST` | `/matters` | Create new matter |
| `PUT` | `/matters/:id` | Update matter |
| `DELETE` | `/matters/:id` | Delete matter |
| `POST` | `/matters/:id/sync` | Sync matter from CRM (Filevine/Clio) |

**Example: Create Matter**
```json
POST /api/veritas/matters
{
  "title": "Rodriguez v. Mount Sinai Hospital",
  "caseType": "MEDICAL_MALPRACTICE",
  "jurisdiction": "New York, New York County",
  "plaintiffName": "Elena Rodriguez",
  "defendantName": "Mount Sinai Hospital",
  "firmId": "lexiflow-tech"
}
```

---

### 🔷 Deposition Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/depositions` | List depositions (filter: matterId, witnessName, status) |
| `GET` | `/depositions/:id` | Get deposition with testimony, contradictions, evidence |
| `POST` | `/depositions` | Create deposition record |
| `POST` | `/depositions/:id/upload` | Upload transcript file/URL |
| `POST` | `/depositions/:id/process` | Trigger AI processing pipeline |

**Example: Create and Upload Deposition**
```json
POST /api/veritas/depositions
{
  "matterId": "<uuid>",
  "witnessName": "Dr. Alan Miller",
  "witnessRole": "ER Attending Physician",
  "date": "2026-06-15",
  "durationMinutes": 187,
  "pageCount": 94
}
```

---

### 🔷 Contradiction Detection

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/contradictions` | List contradictions (filter: matterId, depositionId, severity, isResolved) |
| `GET` | `/contradictions/:id` | Get contradiction with testimony comparison |
| `PATCH` | `/contradictions/:id/resolve` | Mark contradiction as resolved |
| `POST` | `/contradictions/detect` | Trigger AI contradiction detection on deposition |

**Contradiction Types:**
| Type | Description |
|------|-------------|
| `INTERNAL` | Witness contradicts own earlier testimony |
| `EXTERNAL` | Witness contradicts another witness |
| `EVIDENCE` | Testimony contradicts documentary evidence |
| `IMPOSSIBILITY` | Witness claims something physically impossible |

**Example: AI-Detected Contradiction Response**
```json
{
  "id": "uuid",
  "type": "EVIDENCE",
  "severity": "HIGH",
  "testimonyTextA": "I personally confirmed the start of the IV antibiotic protocol at 19:45.",
  "evidence": { "title": "MAR Table", "exhibitNumber": "Exhibit C" },
  "reasoning": "The Medication Administration Record (MAR) shows zero antibiotic dosage entries until 10:15 the following morning — a 14-hour gap.",
  "confidence": 0.94
}
```

---

### 🔷 AI Analysis & Cross-Examination

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/analysis/summary/:depositionId` | Get AI analysis summary (contradictions, credibility) |
| `POST` | `/analysis/contradictions` | Run full contradiction detection pipeline for a matter |
| `POST` | `/analysis/cross-examine` | Generate cross-examination questions from contradictions |
| `POST` | `/analysis/credibility` | Calculate and update witness credibility score |

**Example: Cross-Examination Generation**
```json
POST /api/veritas/analysis/cross-examine
{ "depositionId": "<uuid>" }

// Response:
{
  "depositionId": "<uuid>",
  "questionsCount": 7,
  "questions": [
    {
      "contradictionId": "<uuid>",
      "severity": "HIGH",
      "question": "Regarding your testimony that 'I personally confirmed the start of the IV antibiotic protocol at 19:45...' — can you reconcile this with the MAR showing zero antibiotic administration for 14 hours?"
    }
  ]
}
```

---

### 🔷 Evidence Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/evidence` | List evidence (filter: matterId, evidenceType) |
| `POST` | `/evidence` | Create evidence record |
| `POST` | `/evidence/:id/upload` | Upload evidence file and assign exhibit number |

---

## RAG Architecture

Veritas Deposition™ uses a Retrieval-Augmented Generation pipeline:

1. **Ingestion**: Deposition transcripts are parsed into `Testimony` segments
2. **Embedding**: Each segment gets a vector embedding (OpenAI ada-002 / 1536-dim)
3. **Storage**: Embeddings stored in PostgreSQL via `pgvector` extension on `Testimony.embedding`
4. **Retrieval**: Cross-reference testimony segments against evidence using cosine similarity
5. **Generation**: AI synthesizes contradictions, credibility scores, and cross-exam questions

### SQL Indexes for RAG Performance
```sql
-- pgvector extension
CREATE EXTENSION vector;
CREATE INDEX ON testimony USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
-- Standard indexes
CREATE INDEX idx_contradictions_unresolved ON contradictions(is_resolved) WHERE is_resolved = false;
CREATE INDEX idx_testimony_deposition ON testimony(deposition_id);
```

---

## Environment Setup

```bash
# 1. Install dependencies
cd veritas-deposition/backend
npm install

# 2. Copy environment
cp .env.example .env
# Edit .env with your DATABASE_URL and OPENAI_API_KEY

# 3. Setup database
npx prisma migrate dev --name init
npx prisma generate

# 4. Run seed data (optional)
npm run prisma:seed

# 5. Start development server
npm run dev
```

---

## Error Handling

All endpoints return standard HTTP status codes:
- `200` — Success
- `201` — Created
- `204` — Deleted (no content)
- `400` — Bad request (validation error)
- `401` — Unauthorized (missing/invalid token)
- `403` — Forbidden (insufficient permissions)
- `404` — Not found
- `500` — Internal server error

Error response format:
```json
{ "error": "Error message", "message": "Detailed description" }
```
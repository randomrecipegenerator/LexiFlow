# LexiFlow — Technical Product Copy: Landing Pages

> **Purpose:** Technical and explanatory copy for attorney audience. Use this as source material when augmenting or rewriting product landing pages. Target: senior partners, trial attorneys, and legal ops directors at plaintiff-side PI, MedMal, and mass tort firms.

---

## 1. AI Intake Suite — Reasoning AI vs. Decision-Tree Bots

### The Technical Distinction

Most "AI" intake tools on the market today are not AI at all — they are **decision-tree bots**. A decision-tree bot operates on pre-programmed if/then logic: if the caller selects "auto accident," show questions 1-5; if they select "medical malpractice," show questions 6-10. These systems cannot understand nuance, follow a caller's narrative, or adapt when the caller provides information out of order. They break the moment a caller says something the programmer didn't anticipate.

**LexiFlow's Reasoning AI** is fundamentally different. It uses a large language model (LLM) fine-tuned specifically on:
- Legal intake transcripts (tens of thousands of real intake conversations)
- Medical records and clinical terminology
- State-specific statutes of limitations and certificate of merit requirements
- Liability assessment frameworks for personal injury, medical malpractice, and mass tort

Instead of forcing a caller through a rigid menu, Reasoning AI listens to the caller's full narrative in natural language, extracts key case elements (date of incident, treating facilities, injury types, opposing parties), and dynamically generates follow-up questions to probe for liability, causation, and damages — just as a senior partner would.

### The 0-100 Merit Scoring System

Every qualified lead is assigned a **Case Merit Score** from 0–100, calculated across four weighted vectors:

| Vector | Weight | What It Measures |
|--------|--------|-----------------|
| **Liability Strength** | 35% | Clearness of fault, existence of direct evidence, admission by opposing party, regulatory violation |
| **Damages Severity** | 30% | Medical bill totals, permanency of injury, pain and suffering indicators, lost wage documentation |
| **Causation Clarity** | 20% | Direct temporal link between incident and injury, pre-existing condition separation, expert report availability |
| **Statute & Procedural** | 15% | Remaining SOL window, certificate of merit requirements met, jurisdiction filing status |

Each vector is scored individually and backed by **specific citations** from the caller's conversation transcript. An attorney reviewing the score can click through to hear the exact audio snippet or read the transcript lines that drove each sub-score.

**Merit Score Tiers:**
- **80–100:** High-Value — Auto-qualify, route to senior partner, trigger immediate consultation scheduling
- **50–79:** Moderate — Flag for intake team review, schedule standard consultation
- **20–49:** Low — Review for niche practice area fit, may need additional information
- **0–19:** Decline — Clearly outside firm's practice areas or below minimum case value threshold

### CRM Data Sync (Clio & Filevine)

When a lead is qualified and approved, the following data fields sync automatically to the firm's CRM:

**Clio Grow / Clio Manage:**
- Full contact details (name, phone, email, address)
- Case type and practice area classification
- Incident date and location
- AI Merit Score (stored as custom field)
- Summary of liability narrative (mapped to intake notes)
- Statute of limitations deadline (creates calendar reminder)
- Referral source (web chat, SMS, voice, etc.)

**Filevine / Lead Docket:**
- All of the above, plus:
- Treating facility names and addresses
- Insurance carrier information (if disclosed)
- Opposing party name and counsel (if known)
- Damage amount estimated range
- Custom project template assignment based on case type

The sync is bidirectional for approved contacts: any updates made by the firm in the CRM (e.g., retainer signed, case number assigned) flow back to LexiFlow's dashboard for reporting and pipeline tracking.

---

## 2. Veritas Deposition™ — Evidence Intelligence System

### Contradiction Detection Engine™

The Contradiction Detection Engine™ is the core forensic capability of Veritas Deposition™. It performs **structured cross-referencing** across all deposition transcripts, prior testimony, and the evidentiary record to surface inconsistencies.

**How it works:**

1. **Ingest.** The engine ingests deposition transcripts (PDF, text, or audio-to-text), prior testimony (from the same witness or related witnesses), and all uploaded evidentiary documents (medical records, discovery responses, police reports, surveillance footage descriptions, etc.).

2. **Entity Extraction.** The engine identifies key entities across all sources: dates, times, locations, measurements, dollar amounts, procedure names, medication dosages, and witness statements about specific events.

3. **Conflict Detection.** Using semantic comparison, the engine compares each factual assertion in the deposition against:
   - The same witness's prior testimony (deposition, affidavit, or pre-trial hearing)
   - Documented evidence (medical records, accident reports, financial records)
   - Co-witness testimony (statements from other witnesses about the same event)
   - Physical impossibilities (e.g., claiming to be in two locations simultaneously)

4. **Severity Classification.** Each contradiction is classified:
   - **Critical:** Directly undermines the witness's credibility on a material fact
   - **Significant:** Contradicts key evidence but may have innocent explanation
   - **Minor:** Inconsistency on peripheral detail (may still be useful for impeachment)

5. **Citation Generation.** Every contradiction is presented with a side-by-side comparison view showing the conflicting statements and their source citations (deposition page:line, medical record page, etc.).

### Sample "Testimony vs. Evidence" Comparison

**Scenario:** Auto accident personal injury case. Plaintiff claims chronic back pain limiting daily activities.

| Testimony (Deposition) | Evidence (Medical Records) | Contradiction Type |
|------------------------|--------------------------|--------------------|
| "I haven't been able to work out since the accident." | Physical therapy notes show "patient reports jogging 3x/week without difficulty" (dated 2 months post-accident) | Critical |
| "I take prescription pain medication every single day." | Pharmacy records show 30-day supply filled once in 6 months | Critical |
| "The pain started immediately at the scene." | ER triage notes: "patient denies pain at initial assessment, pain reported 3 hours later" | Significant |
| "I saw Dr. Chen for about a year after the accident." | Billing records show 3 visits over 4 months | Minor |

**Cross-Examination Builder™** then generates suggested questions based on each contradiction, following the standard impeachment protocol:
1. Confirm the witness's current testimony
2. Establish the reliability of the contradicting evidence
3. Present the contradiction
4. Lock in the inconsistency

### Witness Intelligence Dashboard™

The Witness Intelligence Dashboard™ provides a 360-degree view of each witness before, during, and after their deposition.

**Pre-Deposition Module:**
- **Prior Testimony Analysis:** Flags every statement the witness has made in prior depositions, affidavits, or hearings that could be used for impeachment
- **Liability Exposure Assessment:** Predicts high-risk areas based on case theory and known facts
- **Question Strategy Generator:** Suggests deposition topics ranked by information value and impeachment potential
- **Expert Witness Conflict Checker:** Cross-references expert witnesses against a national database of prior testimony to identify contradictory opinions

**Live Deposition Module:**
- **Real-Time Contradiction Flagging:** As the reporter types, the engine surfaces contradictions against the evidentiary record in seconds
- **Issue Tracking:** Mark topics for follow-up, flag unanswered questions
- **Time Management:** Track time spent on each topic versus planned allocation

**Post-Deposition Module:**
- **Instant Deposition Summary:** Organizes testimony by issue, witness, and timeline — delivered within minutes of the transcript being finalized
- **Key Admissions Report:** Extracts every statement favorable to your case, organized by legal element
- **Contradiction Log:** Complete list of all detected contradictions with citations, ready for trial notebook
- **Medical Record Cross-Reference:** Links every medical statement in the testimony back to the specific record page

---

## 3. Auto-Document Drafter — Supported Document Types & Source Citation

### Supported Document Types

The Auto-Document Drafter currently supports the following document types, with more added regularly:

**Demand Letters:**
- Pre-litigation demand letter (personal injury)
- Pre-litigation demand letter (medical malpractice)
- Wrongful death demand letter
- Insurance bad faith demand letter
- Product liability demand letter

**Pleadings & Filings:**
- Notice of Claim
- Complaint (personal injury)
- Complaint (medical malpractice)
- Motion for summary judgment (plaintiff's opposition)
- Motion to compel discovery

**Case Documents:**
- Settlement brochure
- Mediation statement
- Case summary for settlement conference
- Liability analysis memorandum
- Damages analysis memorandum

**Medical Documents:**
- Medical chronology
- Medical narrative summary
- Independent medical examination summary
- Medical expense summary

**Client Communications:**
- Retainer agreement (with AI-calculated fee structure suggestions)
- Representation acknowledgment letter
- Case status letter
- Settlement recommendation letter

### Source Citation System

Every statement in a LexiFlow-drafted document includes a **Source Citation** — a hyperlinked reference back to the original source document and page number. This is critical for attorney review, opposing counsel challenges, and trial admissibility.

**Citation Format (Demand Letter Example):**
```
"Ms. Rodriguez underwent an L4-L5 laminectomy on March 15, 2024,
performed by Dr. James Chen at Mount Sinai West.
[Source: Operative Report, Mount Sinai West, p. 3 — March 15, 2024]"
```

**Citation Types by Source:**
| Source Type | Citation Format |
|-------------|-----------------|
| Medical Records | `[Source: [Record Type], [Facility], p. [Page#] — [Date]]` |
| Deposition Testimony | `[Source: Deposition of [Witness], p. [Page#]:[Line#]]` |
| Discovery Responses | `[Source: [Party]'s Response to [Discovery Type], p. [Page#]]` |
| Billing Records | `[Source: UB-04 Billing Summary, [Facility], Service Date: [Date]]` |
| Police/Accident Report | `[Source: [Agency] Report #[Report#], p. [Page#] — [Date]]` |
| Employment Records | `[Source: [Employer] Personnel File, p. [Page#]]` |
| Expert Report | `[Source: [Expert Name] Expert Report, p. [Page#] — [Date]]` |

**How citations are generated:**
1. When the user uploads a document, LexiFlow indexes it page-by-page and creates a searchable vector embedding for each page
2. When the AI generates a factual statement, it performs a semantic retrieval against the indexed documents to find the exact source passage
3. The AI only generates statements for which it can find a supporting source — it does not fabricate or extrapolate
4. The citation is embedded in the document as a hyperlink; clicking opens the source PDF at the exact page

**Attorney Review Benefits:**
- **Fact-checking in seconds:** Click any citation to verify the source
- **Authoritative production:** Opposing counsel cannot challenge a statement backed by a page-number citation
- **Audit-ready:** Every document includes a complete citation appendix listing all sources used

---

## 4. LexiFlow Strategist™ — Settlement-Predictor Pro™ & Liability Score

### Settlement-Predictor Pro™ Logic

Settlement-Predictor Pro™ is a multi-factor predictive model that estimates case value and settlement probability based on five analysis layers:

#### Layer 1: Case Classification
The system first classifies the case into one of 42 practice-area categories (e.g., auto accident, slip-and-fall, surgical error, delayed diagnosis, birth injury, product liability). Each category has a distinct prediction model trained on anonymized settlement data from thousands of comparable cases.

#### Layer 2: Liability Score Integration
The Liability Score (0–100, detailed below) is the primary input to the settlement model. A 75+ Liability Score cases typically command 2-3x higher settlement values than 40-50 score cases within the same damages range.

#### Layer 3: Damages Quantification
The model processes:
- **Special damages:** Total medical bills (past and projected), lost wages, out-of-pocket expenses
- **General damages:** Pain and suffering multiplier (adjusted for jurisdiction), loss of consortium, loss of enjoyment of life
- **Punitive damages:** Applicability assessment based on jurisdiction law and evidence of recklessness

#### Layer 4: Venue & Jurisdiction Adjustments
The model applies real-time adjustments based on:
- **Venue history:** Jury verdict trends in the specific county/court (sourced from published verdict databases)
- **Judge assignment:** Historical settlement and trial patterns for the assigned judge (if available)
- **Defendant profile:** Insurance carrier settlement tendencies, self-insured vs. insured status, prior bad faith findings
- **ADR requirements:** Mandatory mediation jurisdictions, arbitration caps, early offer provisions

#### Layer 5: Timeline & Probability Projection
The model produces:
- **Expected settlement range** (10th, 50th, and 90th percentile estimates)
- **Probability of settlement by phase:** Pre-litigation (45%), after complaint filed (30%), after discovery (15%), after mediation (8%), trial (2%)
- **Months to resolution estimate** based on court congestion data and case complexity
- **Net-to-client projection** after attorney fees, costs, and liens

### Liability Score Factors

The **Liability Score** (0–100) is computed from 12 sub-factors across three categories:

#### Factor Group A: Evidence Strength (50% of total)

| Factor | Weight | Scoring Criteria |
|--------|--------|------------------|
| Direct Evidence of Fault | 20% | Video, photo, or admission directly showing defendant's fault (score: 70-100) vs. purely circumstantial (score: 20-40) |
| Independent Witness Support | 15% | Multiple credible witnesses corroborate plaintiff's version (score: 70-100) vs. only plaintiff's testimony (score: 20-40) |
| Expert Report Strength | 15% | Causation expert with strong credentials, report with specific findings (score: 70-100) vs. disputed expert (score: 20-40) |

#### Factor Group B: Legal Merits (30% of total)

| Factor | Weight | Scoring Criteria |
|--------|--------|------------------|
| Standard of Care Clarity | 10% | Clear, well-established standard violated (score: 70-100) vs. evolving or disputed standard (score: 20-40) |
| Proximate Causation | 10% | Direct temporal/procedural link (score: 70-100) vs. attenuated or multiple intervening causes (score: 20-40) |
| Statute of Limitations | 5% | Years remaining (score: 100), months remaining (score: 50-70), days remaining (score: 10-30) |
| Certificate of Merit | 5% | Compliant affidavit obtained (score: 100) vs. pending (score: 40) vs. not yet obtained (score: 10) |

#### Factor Group C: Risk Assessment (20% of total)

| Factor | Weight | Scoring Criteria |
|--------|--------|------------------|
| Plaintiff Credibility Risks | 8% | Clean record (score: 90-100) vs. prior inconsistent statements (score: 50-60) vs. felony record/credibility issues (score: 10-30) |
| Pre-existing Condition Apportionment | 7% | No pre-existing (score: 100) vs. well-documented pre-existing (score: 30-50) |
| Comparative Fault Exposure | 5% | No plaintiff fault (score: 100) vs. contributory/comparative exposure (score: 30-70) |

**Final Liability Score Formula:**
```
Liability Score = (FactorGroupA × 0.50) + (FactorGroupB × 0.30) + (FactorGroupC × 0.20)
```

**Score Interpretation:**
- **80–100:** Strong Liability — Recommend aggressive settlement posture
- **60–79:** Moderate Liability — Recommend standard negotiation with reservation
- **40–59:** Marginal Liability — Recommend early mediation, prepare for defense verdict
- **0–39:** Weak Liability — Recommend thorough pre-suit investigation before filing

### Output Format

Settlement-Predictor Pro™ generates a one-page executive summary suitable for sharing with the client, plus a detailed methodology appendix for the attorney's work file. The summary includes:

1. **Case caption and type**
2. **Liability Score** (numerical and categorical)
3. **Expected settlement range** (10th/50th/90th percentile)
4. **Timeline projection** (months to resolution)
5. **Recommendation** (proceed as-is, gather additional evidence, decline)
6. **Top 3 risk factors** (specific to this case)
7. **Top 3 strengths** (specific to this case)
8. **Comparable cases** (anonymized summaries of the 5 most similar resolved cases in the model's database)

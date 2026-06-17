# LexiFlow Homepage Copy & SEO Meta Update Draft
**Target Keyword Focus**: AI Legal Intake Software
**Status**: Ready for Frontend Implementation
**File Directory**: `/home/team/shared/LexiFlow-Final/homepage_draft.md`

---

## 1. SEO Metadata

### Title Tag
```text
AI Legal Intake Software for Law Firms | LexiFlow
```

### Meta Description
```text
LexiFlow answers calls, qualifies leads, scores cases, and syncs intake data into Clio, Filevine, and MyCase, helping high-volume law firms respond faster and convert more qualified matters.
```

### Canonical Tag
```html
<link rel="canonical" href="https://lexiflow.co/" />
```

---

## 2. Hero Section Copy

### Pre-Header / Badge
```text
Enterprise Legal AI
```

### Main Heading (H1)
```text
AI Legal Intake Software for High-Volume Law Firms
```

### Hero Sub-Heading / Paragraph
```text
As the premier AI legal intake software for plaintiff-side practices, LexiFlow answers calls, qualifies leads, scores cases, and syncs intake data into Clio, Filevine, and MyCase, helping high-volume law firms respond faster and convert more qualified matters.
```

### Hero Call-To-Action (CTA) Buttons
- **Primary Button**: `View Plans` (links to `/pricing.html`)
- **Secondary Button**: `Calculate ROI` (links to `/roi-calculator.html`)

---

## 3. Features Section Copy

### Card 1 (Upgraded Focus)
- **Icon**: `bi bi-robot`
- **Heading**: `AI Legal Intake Software`
- **Body**: `Deploy our advanced AI legal intake software to capture and qualify prospective clients with the nuance of a senior attorney, 24/7. Never miss a meritorious case again.`

---

## 4. Visual FAQ Section Copy (To Be Rendered on Homepage)

### Section Badge
```text
Common Questions
```

### Section Heading (H2)
```text
AI Legal Intake FAQs
```

### Section Sub-Heading
```text
Everything you need to know about implementing secure, high-conversion AI legal intake software at your law firm.
```

### FAQ List (6 High-Value Q&As)

#### Q1: What is AI legal intake software?
> **Answer:** AI legal intake software uses specialized artificial intelligence to automate the capture, qualification, and routing of prospective client inquiries. Unlike static forms or rigid decision trees, it carries out dynamic, empathetic conversations via voice, web chat, and SMS, qualifying leads in real-time according to specific legal merit criteria.

#### Q2: How does LexiFlow integrate with my existing legal CRM?
> **Answer:** LexiFlow features native, direct API integrations with leading legal CRMs including Clio Grow, Clio Manage, Filevine, and MyCase. Qualified leads, call recordings, and AI-extracted clinical details are synchronized instantly, preventing data entry duplicate errors.

#### Q3: Is AI legal intake compliant under HIPAA and state bar ethics rules?
> **Answer:** Yes. LexiFlow is designed with security and compliance first. We sign Business Associate Agreements (BAAs) with firms handling Protected Health Information (PHI), maintain SOC2 Type II security alignment, and provide built-in attorney-in-the-loop staging controls that align with state bar ethics guidelines.

#### Q4: Can LexiFlow handle bilingual intake for Spanish-speaking callers?
> **Answer:** Absolutely. Our voice and text AI models are fully bilingual. The system dynamically detects when a caller transitions to Spanish, adjusting its responses seamlessly to ensure Spanish-speaking claimants receive immediate, clear, and empathetic screening.

#### Q5: How does the 'Attorney-in-the-Loop' workflow operate?
> **Answer:** We prioritize professional oversight. LexiFlow doesn't automatically modify active CRM records without permission. Qualified prospective clients are held in a secure staging queue inside your LexiFlow dashboard. Your intake staff can review the AI-extracted summaries and click once to authorize transfer directly to your primary CRM database.

#### Q6: Can the AI answering system operate 24/7 to replace traditional call centers?
> **Answer:** Yes. LexiFlow can act as a complete replacement or a supportive after-hours layer for traditional legal call centers. It has infinite concurrent capacity, answering 100% of incoming web messages and voice calls simultaneously, eliminating hold times and lead leakage.

---

## 5. FAQ Structured Data (JSON-LD)

Place the following script block within the `<head>` of the homepage:

```html
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [{
      "@type": "Question",
      "name": "What is AI legal intake software?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "AI legal intake software uses specialized artificial intelligence to automate the capture, qualification, and routing of prospective client inquiries. Unlike static forms or rigid decision trees, it carries out dynamic, empathetic conversations via voice, web chat, and SMS, qualifying leads in real-time according to specific legal merit criteria."
      }
    }, {
      "@type": "Question",
      "name": "How does LexiFlow integrate with my existing legal CRM?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "LexiFlow features native, direct API integrations with leading legal CRMs including Clio Grow, Clio Manage, Filevine, and MyCase. Qualified leads, call recordings, and AI-extracted clinical details are synchronized instantly, preventing data entry duplicate errors."
      }
    }, {
      "@type": "Question",
      "name": "Is AI legal intake compliant under HIPAA and state bar ethics rules?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes. LexiFlow is designed with security and compliance first. We sign Business Associate Agreements (BAAs) with firms handling Protected Health Information (PHI), maintain SOC2 Type II security alignment, and provide built-in attorney-in-the-loop staging controls that align with state bar ethics guidelines."
      }
    }, {
      "@type": "Question",
      "name": "Can LexiFlow handle bilingual intake for Spanish-speaking callers?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Absolutely. Our voice and text AI models are fully bilingual. The system dynamically detects when a caller transitions to Spanish, adjusting its responses seamlessly to ensure Spanish-speaking claimants receive immediate, clear, and empathetic screening."
      }
    }, {
      "@type": "Question",
      "name": "How does the 'Attorney-in-the-Loop' workflow operate?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "We prioritize professional oversight. LexiFlow doesn't automatically modify active CRM records without permission. Qualified prospective clients are held in a secure staging queue inside your LexiFlow dashboard. Your intake staff can review the AI-extracted summaries and click once to authorize transfer directly to your primary CRM database."
      }
    }, {
      "@type": "Question",
      "name": "Can the AI answering system operate 24/7 to replace traditional call centers?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes. LexiFlow can act as a complete replacement or a supportive after-hours layer for traditional legal call centers. It has infinite concurrent capacity, answering 100% of incoming web messages and voice calls simultaneously, eliminating hold times and lead leakage."
      }
    }]
  }
  </script>
```

#!/usr/bin/env python3
"""
LexiFlow Weekly Blog Post Generator
Scaffolds a new blog post from the template.
Usage: python3 scripts/generate-blog-post.py
"""

CLUSTERS = [
    {"name": "Medical Merit Review", "primary_kw": "AI medical merit review", "secondary_kws": "medical malpractice screening tool, medical record review AI", "product": "MeritScan", "product_url": "https://lexiflow.co/meritscan", "audience": "Personal Injury Attorneys"},
    {"name": "Legal Intake Automation", "primary_kw": "legal intake software", "secondary_kws": "AI legal intake, law firm lead qualification, automated intake system", "product": "LexiFlow Intake", "product_url": "https://lexiflow.co/lexiflow-intake", "audience": "Law Firm Partners"},
    {"name": "Deposition Analysis", "primary_kw": "AI deposition analysis", "secondary_kws": "deposition conflict detector, witness contradiction finder, AI deposition summary", "product": "DepoLens", "product_url": "https://lexiflow.co/depolens", "audience": "Litigation Attorneys"},
    {"name": "Medical Chronology", "primary_kw": "medical chronology software", "secondary_kws": "automated medical chronology, medical timeline software", "product": "Medical Chronologies", "product_url": "https://lexiflow.co/medical-chronologies", "audience": "Paralegals & Litigation Support"},
    {"name": "CRM & Legal Tech Integration", "primary_kw": "legal CRM integration", "secondary_kws": "Filevine integration, Clio integration, law firm workflow automation", "product": "CRM Integrations", "product_url": "https://lexiflow.co/crm-integrations", "audience": "Law Firm Administrators"},
]

POST_IDEAS = {
    "Medical Merit Review": [
        "How AI Medical Merit Review Cuts Case Screening from 8 Hours to 3 Minutes",
        "Medical Malpractice Screening: Why 60% of Meritorious Cases Get Missed",
    ],
    "Legal Intake Automation": [
        "Legal Intake Automation: How AI Qualifies Leads with the Nuance of a Senior Attorney",
        "Why Your Law Firm Is Losing 40% of Leads (And How AI Fixes It)",
    ],
    "Deposition Analysis": [
        "AI Deposition Analysis: Find Witness Contradictions in Seconds, Not Hours",
        "How AI Deposition Summaries Save Litigation Teams 12+ Hours Per Case",
    ],
    "Medical Chronology": [
        "Medical Chronology Software: How AI Auto-Generates Case Timelines in Seconds",
        "Why Paralegals Spend 12 Hours on Medical Chronologies (And How AI Changes This)",
    ],
    "CRM & Legal Tech Integration": [
        "Filevine Integration: How AI-Powered Intake Syncs Leads Directly to Your CRM",
        "How to Choose Legal Intake Software That Integrates With Your Existing CRM",
    ],
}

import os, re
from datetime import datetime, timedelta

BLOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "blog")

def main():
    print("LexiFlow Weekly Blog Post Generator\n")
    for i, c in enumerate(CLUSTERS, 1):
        print(f"  {i}. {c['name']} (kw: {c['primary_kw']})")
    idx = int(input("\nCluster number: ")) - 1
    cluster = CLUSTERS[idx]

    ideas = POST_IDEAS[cluster["name"]]
    for i, idea in enumerate(ideas, 1):
        print(f"  {i}. {idea}")
    idea_idx = int(input("\nIdea number (0 for custom): ")) - 1
    title = ideas[idea_idx] if idea_idx >= 0 else input("Custom title: ")

    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:80]
    today = datetime.now()
    next_mon = today + timedelta(days=(7 - today.weekday()))
    pub_date = next_mon.strftime("%Y-%m-%d")

    print(f"\nTitle: {title}")
    print(f"Slug:  {slug}")
    print(f"Date:  {pub_date}")

    # Create markdown file
    md = f"""# {title}

**Meta Description:** Learn how {cluster['primary_kw']} is transforming {cluster['name'].lower()} for plaintiff firms.
**Slug:** {slug}
**Published:** {pub_date}
**Reading Time:** 10 min
**Primary Keyword:** {cluster['primary_kw']}
**Secondary Keywords:** {cluster['secondary_kws']}

---

## The Challenge Every {cluster['audience']} Faces

{{Write hook}}

## Why Traditional {cluster['name']} Falls Short

{{Write problem deep dive}}

## How AI Is Transforming {cluster['name']}

{{Write solution}}

> **LexiFlow's approach:** {{LexiFlow angle}} The full LexiFlow Suite is available for just **$69/month**. [Learn more →]({cluster['product_url']})

## Key Benefits

1. **Benefit 1** — Detail
2. **Benefit 2** — Detail
3. **Benefit 3** — Detail

## Frequently Asked Questions

### Q1?
A1.

## The Bottom Line

{{Conclusion}}

---

**Ready to transform your firm?** [Email our team →](mailto:leads@lexiflow.co) for a free audit.
"""
    path = os.path.join(BLOG_DIR, f"{slug}.md")
    with open(path, "w") as f:
        f.write(md)
    print(f"✅ Created: {path}")

if __name__ == "__main__":
    main()

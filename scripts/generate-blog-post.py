#!/usr/bin/env python3
"""
LexiFlow Weekly Blog Post Generator
Usage: python3 scripts/generate-blog-post.py
This script scaffolds a new blog post from the template.
"""

import json
import os
import re
from datetime import datetime, timedelta

# ─── CONFIG ───────────────────────────────────────────────────────────────────
BLOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "blog")
TEMPLATE_DIR = os.path.join(BLOG_DIR, "templates")
SOCIAL_DIR = os.path.join(BLOG_DIR, "social")
IMAGES_DIR = os.path.join(BLOG_DIR, "images")

# ─── KEYWORD DATA ─────────────────────────────────────────────────────────────
# Weekly rotation of 5 content clusters, aligned with LexiFlow products
CLUSTERS = [
    {
        "name": "Medical Merit Review",
        "primary_kw": "AI medical merit review",
        "secondary_kws": "medical malpractice screening tool, medical record review AI, standard of care analysis",
        "product": "MeritScan",
        "product_url": "https://lexiflow.com/meritscan",
        "audience": "Personal Injury Attorneys",
        "free_offer": "free MeritScan sample report",
        "article_section": "Medical Merit"
    },
    {
        "name": "Legal Intake Automation",
        "primary_kw": "legal intake software",
        "secondary_kws": "AI legal intake, law firm lead qualification, automated intake system",
        "product": "LexiFlow Intake",
        "product_url": "https://lexiflow.com/lexiflow-intake",
        "audience": "Law Firm Partners & Intake Managers",
        "free_offer": "free intake audit",
        "article_section": "Intake Automation"
    },
    {
        "name": "Deposition Analysis",
        "primary_kw": "AI deposition analysis",
        "secondary_kws": "deposition conflict detector, witness contradiction finder, AI deposition summary",
        "product": "DepoLens",
        "product_url": "https://lexiflow.com/depolens",
        "audience": "Litigation Attorneys",
        "free_offer": "free deposition analysis sample",
        "article_section": "Deposition Tech"
    },
    {
        "name": "Medical Chronology",
        "primary_kw": "medical chronology software",
        "secondary_kws": "automated medical chronology, medical timeline software, AI chronology for litigation",
        "product": "Medical Chronologies",
        "product_url": "https://lexiflow.com/medical-chronologies",
        "audience": "Paralegals & Litigation Support",
        "free_offer": "free sample chronology",
        "article_section": "Medical Chronology"
    },
    {
        "name": "CRM & Legal Tech Integration",
        "primary_kw": "legal CRM integration",
        "secondary_kws": "Filevine integration, Clio integration, law firm workflow automation",
        "product": "CRM Integrations",
        "product_url": "https://lexiflow.com/crm-integrations",
        "audience": "Law Firm Administrators",
        "free_offer": "free integration audit",
        "article_section": "Legal Tech"
    },
]

# ─── POST IDEAS BY CLUSTER ────────────────────────────────────────────────────
POST_IDEAS = {
    "Medical Merit Review": [
        "How AI Medical Merit Review Cuts Case Screening from 8 Hours to 3 Minutes",
        "Medical Malpractice Screening: Why 60% of Meritorious Cases Get Missed",
        "Standard of Care Analysis: How AI Spots Negligence Patterns Human Reviewers Miss",
        "The Cost of Manual Medical Record Review: $1,500/case vs AI at $75",
        "How to Screen Medical Malpractice Cases in 2026: A Step-by-Step Guide",
    ],
    "Legal Intake Automation": [
        "Legal Intake Automation: How AI Qualifies Leads with the Nuance of a Senior Attorney",
        "Why Your Law Firm Is Losing 40% of Leads (And How AI Fixes It)",
        "The Definitive Guide to AI-Powered Lead Qualification for Personal Injury Firms",
        "Response Time Wins: Why 30-Second AI Lead Qualification Beats 4-Hour Callbacks",
        "Law Firm Intake Software: What to Look for in 2026",
    ],
    "Deposition Analysis": [
        "AI Deposition Analysis: Find Witness Contradictions in Seconds, Not Hours",
        "How AI Deposition Summaries Save Litigation Teams 12+ Hours Per Case",
        "Witness Credibility Analysis: The AI Tool Every Trial Attorney Needs",
        "Deposition Conflict Detection: Why Manual Cross-Reference Misses 30% of Contradictions",
        "The Complete Guide to AI-Powered Deposition Preparation",
    ],
    "Medical Chronology": [
        "Medical Chronology Software: How AI Auto-Generates Case Timelines in Seconds",
        "Why Paralegals Spend 12 Hours on Medical Chronologies (And How AI Changes This)",
        "Medical Timeline Automation: A Step-by-Step Guide for Litigation Teams",
        "AI vs Manual Medical Chronology: Time, Cost, and Accuracy Compared",
        "The Future of Medical Record Summarization in Personal Injury Litigation",
    ],
    "CRM & Legal Tech Integration": [
        "Filevine Integration: How AI-Powered Intake Syncs Leads Directly to Your CRM",
        "Clio Integration for AI Legal Intake: Automate Your Lead Pipeline End-to-End",
        "Legal CRM Automation: Why Leading Firms Are Connecting Intake AI to Filevine and Clio",
        "How to Choose Legal Intake Software That Integrates With Your Existing CRM",
        "The Complete Guide to Legal Tech Stack Integration (Filevine, Clio, LeadDock)",
    ],
}


def sanitize_filename(text):
    """Convert text to kebab-case filename."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = text.strip('-')
    return text


def generate_slug(title):
    """Generate URL slug from title."""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug[:80]


def build_meta_description(title, primary_kw, cluster_name):
    """Build 150-160 char meta description."""
    base = f"Learn how {primary_kw} is transforming {cluster_name.lower()} for plaintiff firms. "
    desc = base + "Includes step-by-step guides, cost comparisons, and actionable insights."
    if len(desc) > 160:
        desc = desc[:157] + "..."
    return desc


def build_faq_schema(faqs):
    """Build FAQ JSON-LD schema from list of Q&A pairs."""
    items = []
    for q, a in faqs:
        items.append({
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {
                "@type": "Answer",
                "text": a
            }
        })
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": items
    }
    return json.dumps(schema, indent=2)


def main():
    print("=" * 60)
    print("LexiFlow Weekly Blog Post Generator")
    print("=" * 60)

    # Show clusters
    print("\nSelect a content cluster:")
    for i, cluster in enumerate(CLUSTERS, 1):
        print(f"  {i}. {cluster['name']} (primary kw: {cluster['primary_kw']})")

    cluster_idx = int(input("\nCluster number: ")) - 1
    cluster = CLUSTERS[cluster_idx]

    # Show post ideas
    ideas = POST_IDEAS[cluster["name"]]
    print(f"\nPost ideas for {cluster['name']}:")
    for i, idea in enumerate(ideas, 1):
        print(f"  {i}. {idea}")

    idea_idx = int(input("\nIdea number (or 0 for custom): ")) - 1
    if idea_idx >= 0:
        title = ideas[idea_idx]
    else:
        title = input("Custom title: ")

    # Generate metadata
    slug = generate_slug(title)
    today = datetime.now()
    next_monday = today + timedelta(days=(7 - today.weekday()))
    publish_date = next_monday.strftime("%Y-%m-%d")
    display_date = next_monday.strftime("%B %d, %Y")

    # Estimate read time (assume ~225 words/min for legal content)
    word_count = int(input("Target word count (default 1800): ") or "1800")
    read_time = max(7, round(word_count / 225))

    meta_desc = build_meta_description(title, cluster["primary_kw"], cluster["name"])

    print(f"\n{'='*60}")
    print(f"Title:     {title}")
    print(f"Slug:      {slug}")
    print(f"Publish:   {publish_date}")
    print(f"Meta Desc: {meta_desc}")
    print(f"Words:     {word_count}")
    print(f"Read time: {read_time} min")
    print(f"{'='*60}\n")

    # Create markdown post file
    post_md = f"""# {title}

**Meta Description:** {meta_desc}
**Slug:** {slug}
**Published:** {publish_date}
**Reading Time:** {read_time} min
**Primary Keyword:** {cluster['primary_kw']}
**Secondary Keywords:** {cluster['secondary_kws']}

---

## The Challenge Every {cluster['audience']} Faces

{{Write your hook — problem statement with compelling stat}}

## Why Traditional {cluster['name']} Falls Short

{{Expand on pain points — time, cost, missed opportunities}}

## How AI Is Transforming {cluster['name']}

{{Explain the AI/tech solution — tie to LexiFlow approach}}

> **LexiFlow's approach:** {{LexiFlow angle — 1-2 sentences}} [Learn more about {cluster['product']} →]({cluster['product_url']})

## How to Implement {cluster['name']} With AI: A Step-by-Step Guide

### Step 1: {{Step 1}}
{{Detail}}

### Step 2: {{Step 2}}
{{Detail}}

### Step 3: {{Step 3}}
{{Detail}}

## Key Benefits of AI-Powered {cluster['name']}

1. **{'{'}Benefit 1{'}'}** — {{Detail with data}}
2. **{'{'}Benefit 2{'}'}** — {{Detail with data}}
3. **{'{'}Benefit 3{'}'}** — {{Detail with data}}
4. **{'{'}Benefit 4{'}'}** — {{Detail with data}}
5. **{'{'}Benefit 5{'}'}** — {{Detail with data}}

## Frequently Asked Questions

### {{FAQ 1 Question}}
{{FAQ 1 Answer}}

### {{FAQ 2 Question}}
{{FAQ 2 Answer}}

### {{FAQ 3 Question}}
{{FAQ 3 Answer}}

### {{FAQ 4 Question}}
{{FAQ 4 Answer}}

### {{FAQ 5 Question}}
{{FAQ 5 Answer}}

## The Bottom Line

{{Conclusion — recap and call to action}}

---

**Ready to transform your firm's intake?** [Email our team →](mailto:leads@lexiflow.ai) for your {cluster['free_offer']}.
"""

    md_path = os.path.join(BLOG_DIR, f"{slug}.md")
    with open(md_path, "w") as f:
        f.write(post_md)
    print(f"✅ Created markdown: {md_path}")

    # Create social distribution hooks
    social_md = f"""# Social Distribution: {title}

## LinkedIn (Attorney-Focused)
**Headline:** {{Compelling stat or question — 1 line}}
**Body:**
{{Problem → Solution → CTA in 2-3 paragraphs}}
**Link:** https://lexiflow.com/blog/{slug}
**Best Time:** Tuesday-Thursday 8-10am

## X/Twitter (Thread)
1/ {{Hook tweet with stat}}
2/ {{Problem statement}}
3/ {{Solution highlight}}
4/ {{Bullet benefits}}
5/ CTA: "Read the full post → https://lexiflow.com/blog/{slug}"

## Email Newsletter
**Subject:** {{40-50 char intriguing subject}}
**Preview:** {{100 char compelling snippet}}
**Body:** Brief intro + link + CTA to reply for {cluster['free_offer']}

## Reddit (r/LawFirm, r/Lawyers)
**Post:** {{Discussion starter based on post topic}}
"""

    social_path = os.path.join(SOCIAL_DIR, f"{slug}-social.md")
    with open(social_path, "w") as f:
        f.write(social_md)
    print(f"✅ Created social hooks: {social_path}")

    print(f"\n{'='*60}")
    print(f"NEXT STEPS:")
    print(f"  1. Write the full post in: blog/{slug}.md")
    print(f"  2. Generate the HTML (with schema) from the template")
    print(f"  3. Add social distribution plan: blog/social/{slug}-social.md")
    print(f"  4. Create hero image: blog/images/{slug}-hero.png")
    print(f"  5. Update sitemap.xml")
    print(f"  6. Publish Monday: {publish_date}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

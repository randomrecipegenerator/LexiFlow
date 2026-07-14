#!/usr/bin/env python3
"""
Comprehensive SEO Meta Tag Fix for LexiFlow-Final
Fixes missing titles, descriptions, keywords, OG tags, Twitter cards, and canonical URLs
across ALL HTML pages.

Each page gets unique, keyword-rich metadata targeting personal injury law firms,
medical malpractice, deposition analysis, and legal tech audiences.
"""

import os
import re
import glob

REPO = "/home/team/shared/LexiFlow-Final"
SOCIAL_BANNER = "https://lexiflow.co/social-banner.png"
BASE_URL = "https://lexiflow.co"

# ─── Metadata definitions ───────────────────────────────────────────────
# Each entry key is the relative path from REPO.
# Values: (title, description, keywords_list, canonical_suffix)
# canonical_suffix is the URL path after BASE_URL (e.g., "/intake-app.html")
PAGE_META = {
    # ── Landing / Core pages ──
    "index.html": (
        "LexiFlow | AI Legal Operations & Matter Management — Active Workspace",
        "LexiFlow is AI-powered legal operations software for plaintiff firms. Automate intake, medical merit review, and deposition analysis. Experience the Rodriguez v. Mount Sinai live workspace — 92/100 Merit Score, 7 flagged contradictions, $4.2M trial value.",
        ["legal operations software", "AI legal intake", "legal matter management", "law firm automation", "medical merit review", "deposition analysis software", "personal injury law firm software"],
        "/"
    ),
    "features.html": (
        "Features | LexiFlow — AI Legal Intake, Merit Review & Deposition Intelligence",
        "Explore LexiFlow's full feature set: AI-powered legal intake with 0-100 merit scoring, Veritas Deposition contradiction detection, auto-document drafting, and LexiFlow Strategist settlement prediction.",
        ["AI legal intake features", "legal software features", "law firm automation tools", "AI deposition analysis", "medical merit review software", "legal intake platform"],
        "/features"
    ),
    "pricing.html": (
        "LexiFlow Pricing — $29/mo Starter | $129/mo Enterprise",
        "LexiFlow pricing: Starter ($29/mo), Professional ($99/mo) with 250 docs/mo, and Enterprise ($129/mo) for full Veritas Deposition and LexiFlow Strategist capabilities. Start your 30-day free trial.",
        ["LexiFlow pricing", "legal intake software cost", "law firm software pricing", "AI legal software plans", "deposition analysis pricing", "legal tech subscription"],
        "/pricing"
    ),
    "solutions.html": (
        "Solutions | LexiFlow — AI Legal Operations for Plaintiff Firms",
        "LexiFlow solutions for personal injury, medical malpractice, and mass tort firms. Automate intake qualification, medical record review, deposition analysis, and settlement strategy with Reasoning AI.",
        ["legal operations solutions", "law firm AI solutions", "plaintiff firm software", "medical malpractice software", "mass tort litigation software", "legal intake automation"],
        "/solutions"
    ),
    "demo.html": (
        "Demo | LexiFlow — Live Rodriguez v. Mount Sinai Active Workspace",
        "Experience the LexiFlow Active Workspace live. Interact with the Rodriguez v. Mount Sinai medical malpractice case — see AI merit scoring, contradiction detection, and deposition intelligence in real time.",
        ["LexiFlow demo", "legal AI demo", "law firm software demo", "medical malpractice AI demo", "deposition analysis demo", "legal tech demo"],
        "/demo"
    ),
    "signup.html": (
        "Sign Up | LexiFlow — Start Your 30-Day Free Trial",
        "Start your 30-day free trial of LexiFlow. No credit card required. Automate legal intake, medical merit review, and deposition analysis for your plaintiff law firm.",
        ["LexiFlow sign up", "legal software free trial", "law firm software trial", "AI legal intake trial", "free legal tech trial"],
        "/signup"
    ),
    "login.html": (
        "Login | LexiFlow Technologies Inc",
        "Log in to your LexiFlow account. Access your AI intake dashboard, medical merit reviews, deposition analysis tools, and case workspace. Secure attorney login portal.",
        ["LexiFlow login", "legal software login", "law firm portal login", "AI legal dashboard", "attorney login"],
        "/login"
    ),

    # ── Product pages ──
    "veritas-deposition.html": (
        "Legal Transcript Analysis & Deposition AI Software | Veritas Deposition™",
        "Veritas Deposition™ is an Evidence Intelligence System that transforms deposition transcripts into structured litigation intelligence. Automate contradiction detection, cross-examination prep, and witness analysis.",
        ["deposition analysis software", "legal transcript analysis", "AI deposition software", "contradiction detection", "deposition summary AI", "witness intelligence", "legal tech deposition"],
        "/veritas-deposition"
    ),
    "veritas-app.html": (
        "Veritas Deposition™ App — AI Deposition Analysis Dashboard",
        "Access the Veritas Deposition™ app dashboard. Upload deposition transcripts, run contradiction detection, build cross-examinations, and generate witness intelligence reports in minutes.",
        ["Veritas Deposition app", "deposition analysis dashboard", "AI deposition tool", "legal transcript AI", "deposition software"],
        "/veritas-app"
    ),
    "strategist.html": (
        "LexiFlow Strategist™ — AI Case Strategy & Settlement Intelligence",
        "LexiFlow Strategist™ uses Reasoning AI to analyze case strengths, identify evidentiary weaknesses, calculate liability scores, and predict settlement values based on jurisdictional case law.",
        ["legal case strategy AI", "settlement prediction software", "litigation strategy tool", "AI case analysis", "liability scoring", "legal reasoning AI", "case value calculator"],
        "/strategist"
    ),
    "ai-intake-agent.html": (
        "AI Intake Agent — Automate Law Firm Lead Qualification | LexiFlow",
        "LexiFlow's AI Intake Agent automates law firm lead qualification. Screen potential clients 24/7 with conversational AI, medical merit scoring, and instant CRM integration. Reduce intake costs by up to 60%.",
        ["AI legal intake", "law firm lead qualification", "automated client intake", "legal intake chatbot", "law firm call answering AI", "client intake automation"],
        "/ai-intake-agent"
    ),
    "intake-app.html": (
        "LexiFlow | AI Intake Manager — Lead Qualification Dashboard",
        "Manage and qualify law firm leads with LexiFlow's AI Intake Manager. Real-time lead scoring, medical merit evaluation, and CRM sync. Prioritize high-value cases instantly.",
        ["AI intake manager", "legal lead management", "law firm intake dashboard", "lead qualification software", "legal CRM intake"],
        "/intake-app"
    ),
    "settlement-app.html": (
        "LexiFlow | Settlement Estimator — AI Settlement Predictor Pro",
        "Estimate case settlement values with LexiFlow's AI Settlement Estimator. Analyze medical records, jurisdictional data, and verdict trends to project settlement ranges for personal injury and medmal cases.",
        ["settlement estimator", "AI settlement predictor", "case value calculator", "personal injury settlement software", "legal settlement analysis"],
        "/settlement-app"
    ),
    "settlement-predictor.html": (
        "Settlement Predictor Pro™ — AI Settlement Value Analysis | LexiFlow",
        "Settlement Predictor Pro™ uses AI to analyze case facts, medical damages, and jurisdictional history to project accurate settlement values. Built for plaintiff personal injury and medmal firms.",
        ["settlement predictor", "AI settlement value", "case valuation tool", "personal injury settlement AI", "legal settlement calculator"],
        "/settlement-predictor"
    ),
    "discovery-vault.html": (
        "Discovery-Vault™ — AI Mass Tort Document Intelligence | LexiFlow",
        "Discovery-Vault™ transforms mass tort document review with AI-powered document indexing, contradiction flagging, and key-evidence extraction. Process thousands of discovery documents in hours.",
        ["discovery vault", "mass tort document review", "AI discovery software", "legal document intelligence", "e-discovery AI", "mass tort litigation"],
        "/discovery-vault"
    ),
    "compliance-shield.html": (
        "Compliance-Shield™ — HIPAA & BAA-Compliant Legal AI | LexiFlow",
        "LexiFlow Compliance-Shield™ ensures enterprise-grade security with HIPAA compliance, SOC 2 controls, and signed Business Associate Agreements. Trusted by plaintiff law firms nationwide.",
        ["HIPAA compliant legal AI", "BAA legal software", "SOC 2 law firm", "legal data security", "compliance shield", "law firm data protection"],
        "/compliance-shield"
    ),
    "enterprise-app.html": (
        "Enterprise Suite | LexiFlow — Full-Scale Legal AI Platform",
        "LexiFlow Enterprise Suite combines AI Intake, Veritas Deposition™, LexiFlow Strategist™, and Discovery-Vault™ in one integrated platform. Designed for high-volume plaintiff and mass tort firms.",
        ["legal enterprise software", "law firm AI platform", "enterprise legal suite", "mass tort software", "AI legal platform enterprise"],
        "/enterprise-app"
    ),
    "auto-document-drafter.html": (
        "Auto-Document Drafter — AI Legal Document Generation | LexiFlow",
        "Generate demand letters, settlement agreements, and case summaries automatically with LexiFlow's Auto-Document Drafter. 25+ document templates with source citation. Reduce drafting time by 80%.",
        ["AI legal document drafting", "automated legal documents", "demand letter generator", "legal document automation", "AI document drafter"],
        "/auto-document-drafter"
    ),
    "drafter-app.html": (
        "Document Drafter App — AI Legal Document Generator | LexiFlow",
        "Access LexiFlow's document drafting dashboard. Generate demand letters, complaints, and medical chronologies with AI. Every citation includes source references for attorney review.",
        ["legal document generator", "AI document drafting app", "demand letter app", "legal document software", "medical chronology drafter"],
        "/drafter-app"
    ),

    # ── Industry / Vertical pages ──
    "personal-injury-software.html": (
        "Personal Injury Law Firm Software — AI Intake & Case Management | LexiFlow",
        "LexiFlow personal injury law firm software automates client intake, medical record review, and settlement analysis. AI-powered merit scoring helps PI firms qualify leads 24/7.",
        ["personal injury software", "PI law firm software", "personal injury case management", "AI personal injury intake", "plaintiff firm technology"],
        "/personal-injury-software"
    ),
    "medical-chronologies-app.html": (
        "Medical Chronology Software — AI Medical Record Review | LexiFlow",
        "Generate AI-powered medical chronologies from medical records. LexiFlow extracts key dates, treatments, diagnoses, and provider notes. Automate medical record review for PI and medmal cases.",
        ["medical chronology software", "AI medical record review", "medical chronology automation", "medical timeline software", "legal medical record analysis"],
        "/medical-chronologies-app"
    ),
    "medical-chronology-software.html": (
        "Medical Chronology Software for Law Firms — AI-Powered | LexiFlow",
        "LexiFlow's medical chronology software automatically extracts treatment timelines, diagnoses, and provider information from medical records. Built for plaintiff personal injury and medmal attorneys.",
        ["medical chronology for law firms", "AI chronology software", "medical timeline for lawyers", "medical record review AI", "plaintiff medical chronology"],
        "/medical-chronology-software"
    ),
    "medical-chronology-template.html": (
        "Medical Chronology Template — AI-Generated | LexiFlow",
        "View a sample AI-generated medical chronology from LexiFlow. Automated timeline extraction with treatment dates, diagnoses, medications, and provider notes from medical records.",
        ["medical chronology template", "sample medical chronology", "AI chronology example", "medical timeline template", "legal chronology sample"],
        "/medical-chronology-template"
    ),
    "medical-chronology-sample.html": (
        "Medical Chronology Sample — AI-Powered Timeline | LexiFlow",
        "Sample AI-generated medical chronology showing automated extraction of treatment history, diagnoses, and key medical events from patient records for legal case preparation.",
        ["medical chronology sample", "AI medical timeline", "medical record summary example", "legal chronology sample", "medical timeline sample"],
        "/medical-chronology-sample"
    ),
    "medical-record-review-checklist.html": (
        "Medical Record Review Checklist — AI-Powered | LexiFlow",
        "Comprehensive medical record review checklist for plaintiff attorneys. AI-powered extraction of critical timelines, gaps in treatment, and key medical findings. Streamline your record review process.",
        ["medical record review checklist", "legal record review", "medical chart review", "AI record review", "plaintiff medical review"],
        "/medical-record-review-checklist"
    ),
    "ssd-disability-medical-chronology-software.html": (
        "SSD Disability Medical Chronology Software — AI for Social Security | LexiFlow",
        "AI-powered medical chronology software for SSD and disability cases. Automatically extract treatment history, impairments, and functional limitations from medical records for Social Security appeals.",
        ["SSD medical chronology", "disability medical records", "Social Security AI software", "disability chronology software", "SSA medical record review"],
        "/ssd-disability-medical-chronology-software"
    ),
    "meritscan.html": (
        "MeritScan™ — AI Medical Merit Review | LexiFlow",
        "MeritScan™ analyzes medical records against case criteria to produce a 0-100 merit score. Identify strong cases instantly with AI-powered medical merit review for medmal and PI attorneys.",
        ["medical merit review", "AI medical case screening", "merit scoring software", "medical malpractice screening", "case merit analysis", "legal AI merit scan"],
        "/meritscan"
    ),
    "witness-testimony-analysis.html": (
        "Witness Testimony Analysis — AI Deposition Intelligence | LexiFlow",
        "Analyze witness testimony and deposition transcripts with AI. Identify inconsistencies, contradictions, and credibility issues. Built for trial attorneys preparing cross-examinations.",
        ["witness testimony analysis", "deposition analysis", "witness credibility AI", "testimony inconsistency detection", "trial preparation software"],
        "/witness-testimony-analysis"
    ),
    "deposition-analysis.html": (
        "Deposition Analysis Software — AI Transcript Review | LexiFlow",
        "LexiFlow deposition analysis software uses AI to review transcripts, flag contradictions, and identify key testimony. Reduce deposition review time by 70% with the Contradiction Detection Engine.",
        ["deposition analysis", "deposition review software", "AI transcript analysis", "deposition summary tool", "legal transcript review"],
        "/deposition-analysis"
    ),
    "contradiction-detection.html": (
        "Contradiction Detection Engine™ — AI Testimony Analysis | LexiFlow",
        "The Contradiction Detection Engine™ by LexiFlow automatically identifies inconsistencies across deposition transcripts, comparing testimony against medical records and prior statements.",
        ["contradiction detection", "AI testimony analysis", "deposition contradiction finder", "witness inconsistency detection", "legal AI contradiction"],
        "/contradiction-detection"
    ),
    "deposition-chronology.html": (
        "Deposition Chronology — AI Timeline Builder | LexiFlow",
        "Build deposition chronologies automatically with LexiFlow AI. Extract key dates, events, and testimony from transcripts to create searchable, cross-referenced timelines for trial preparation.",
        ["deposition chronology", "AI deposition timeline", "legal chronology builder", "transcript timeline tool", "trial preparation AI"],
        "/deposition-chronology"
    ),
    "deposition-summary.html": (
        "Deposition Summary — AI Transcript Summarization | LexiFlow",
        "Generate deposition summaries automatically with LexiFlow AI. Extract key testimony, admissions, and contradictions from transcripts. Summarize multi-hour depositions in minutes.",
        ["deposition summary", "AI deposition summarization", "transcript summary tool", "legal summary generation", "deposition digest"],
        "/deposition-summary"
    ),
    "key-admissions.html": (
        "Key Admissions — AI Deposition Analysis | LexiFlow Veritas Deposition™",
        "Identify key admissions in deposition transcripts automatically. LexiFlow's AI flags critical testimony, admissions against interest, and contradictory statements for attorneys.",
        ["key admissions", "deposition admissions", "AI testimony analysis", "legal admissions tracker", "deposition intelligence"],
        "/key-admissions"
    ),
    "hipaa-baa.html": (
        "HIPAA & BAA Compliance — Legal AI Security | LexiFlow",
        "LexiFlow maintains full HIPAA compliance with signed Business Associate Agreements for all customer data. Enterprise-grade encryption, access controls, and audit logging for law firms.",
        ["HIPAA compliance legal AI", "BAA law firm", "legal data security", "HIPAA legal software", "law firm BAA"],
        "/hipaa-baa"
    ),
    "soc2.html": (
        "SOC 2 Compliance — Enterprise Security | LexiFlow Technologies",
        "LexiFlow maintains SOC 2 compliance for enterprise security. Independent audits verify our controls for data confidentiality, availability, and processing integrity.",
        ["SOC 2 legal tech", "law firm SOC 2", "legal software security", "enterprise legal compliance", "SOC 2 AI platform"],
        "/soc2"
    ),

    # ── CRM / Integration pages ──
    "clio-intake-automation.html": (
        "Clio Intake Automation — AI Lead Sync for Clio | LexiFlow",
        "Automate Clio intake with LexiFlow. AI-qualified leads sync directly to Clio with merit scores, medical summaries, and contact data. Eliminate manual data entry from client intake.",
        ["Clio intake automation", "Clio AI integration", "legal CRM sync", "Clio lead management", "law firm Clio automation"],
        "/clio-intake-automation"
    ),
    "filevine-intake-automation.html": (
        "Filevine Intake Automation — AI Lead Sync | LexiFlow",
        "Automate Filevine intake with LexiFlow AI. Qualified leads sync directly to Filevine with merit scores, medical chronologies, and case data. Streamline your intake-to-case workflow.",
        ["Filevine intake automation", "Filevine AI integration", "legal CRM sync", "Filevine lead management", "case management automation"],
        "/filevine-intake-automation"
    ),
    "integrations.html": (
        "Integrations — CRM & Legal Software Sync | LexiFlow",
        "LexiFlow integrates with Clio, Filevine, and other leading legal CRMs. Sync qualified leads, medical chronologies, and case data automatically. Reduce manual data entry across your tech stack.",
        ["LexiFlow integrations", "legal CRM integration", "Clio sync", "Filevine sync", "law firm software integrations"],
        "/integrations"
    ),

    # ── Comparison / Alternative pages ──
    "lexiflow-vs-traditional-intake.html": (
        "LexiFlow vs Traditional Intake — AI vs Manual Lead Qualification",
        "Compare LexiFlow's AI-powered legal intake against traditional call-center and manual intake methods. See how Reasoning AI reduces cost-per-lead by 60% and improves response times.",
        ["LexiFlow vs traditional intake", "AI vs manual legal intake", "law firm intake comparison", "AI intake benefits", "legal intake efficiency"],
        "/lexiflow-vs-traditional-intake"
    ),
    "best-ai-intake-software-for-law-firms.html": (
        "Best AI Intake Software for Law Firms (2026) — LexiFlow",
        "Comprehensive guide to the best AI legal intake software for law firms in 2026. Compare features, pricing, and capabilities. LexiFlow leads with Reasoning AI, medical merit scoring, and Veritas Deposition.",
        ["best AI intake software", "top legal intake tools", "law firm AI comparison", "legal intake software 2026", "AI legal tech review"],
        "/best-ai-intake-software-for-law-firms"
    ),
    "ai-legal-intake-vs-call-center.html": (
        "AI Legal Intake vs Call Center — Which is Better for Law Firms?",
        "Compare AI legal intake vs traditional call centers for law firms. AI offers 24/7 availability, instant qualification, medical merit scoring, and 60% lower cost per lead.",
        ["AI legal intake vs call center", "law firm call center vs AI", "legal intake automation", "AI vs human intake", "law firm phone answering"],
        "/ai-legal-intake-vs-call-center"
    ),
    "law-firm-call-answering-ai.html": (
        "Law Firm Call Answering AI — 24/7 Client Intake Automation",
        "LexiFlow's law firm call answering AI captures and qualifies leads 24/7. Conversational AI handles initial screening, schedules consultations, and syncs data to your CRM. Never miss a lead.",
        ["law firm call answering AI", "legal call automation", "law firm phone AI", "24/7 legal intake", "automated law firm calls"],
        "/law-firm-call-answering-ai"
    ),
    "spanish-legal-intake-ai.html": (
        "Spanish Legal Intake AI — Bilingual Client Qualification | LexiFlow",
        "LexiFlow's Spanish legal intake AI qualifies Spanish-speaking leads with full conversational AI. Bilingual merit scoring, medical review, and CRM sync. Expand your firm's reach to Hispanic clients.",
        ["Spanish legal intake", "bilingual law firm AI", "Spanish client intake", "Hispanic legal marketing", "law firm Spanish support"],
        "/spanish-legal-intake-ai"
    ),
    "voice-ai-app.html": (
        "Voice AI Receptionist — AI Phone Intake for Law Firms | LexiFlow",
        "LexiFlow Voice AI receptionist handles inbound calls 24/7. AI-powered conversation, lead qualification, and scheduling. Never miss a potential client call again.",
        ["voice AI receptionist", "AI phone intake law firm", "virtual receptionist legal", "automated call handling law firm", "legal voice AI"],
        "/voice-ai-app"
    ),
    "voice-ai-receptionist.html": (
        "Voice AI Receptionist — Automated Legal Intake Calls | LexiFlow",
        "LexiFlow's Voice AI Receptionist answers calls 24/7, qualifies leads with conversational AI, and schedules consultations. HIPAA-compliant and CRM-integrated for plaintiff law firms.",
        ["voice AI receptionist law firm", "automated phone intake", "legal virtual receptionist", "AI call answering law firm", "24/7 legal intake calls"],
        "/voice-ai-receptionist"
    ),
    "ai-medical-chronologies.html": (
        "AI Medical Chronologies — Automate Record Review | LexiFlow",
        "Generate AI-powered medical chronologies from patient records. LexiFlow automatically extracts treatment timelines, diagnoses, medications, and provider notes for legal case preparation.",
        ["AI medical chronologies", "automated medical record review", "medical timeline AI", "legal medical chronology", "AI record analysis"],
        "/ai-medical-chronologies"
    ),

    # ── City / State pages ──
    "san-francisco-medical-malpractice-intake.html": (
        "San Francisco Medical Malpractice Intake — AI Lead Qualification | LexiFlow",
        "San Francisco medical malpractice attorneys: automate client intake with LexiFlow AI. Screen medmal cases 24/7 with medical merit scoring, California-specific MICRA analysis, and SF jurisdictional data.",
        ["San Francisco medical malpractice AI", "SF medmal intake", "California legal intake automation", "Bay Area law firm AI", "San Francisco legal tech"],
        "/san-francisco-medical-malpractice-intake"
    ),

    # ── Legal Ethics guides ──
    "blog/california-trial-lawyers-ai-ethics-legal-intake.html": (
        "AI Ethics in Legal Intake: California Guide for Trial Lawyers | LexiFlow",
        "California AI ethics guide for trial lawyers using AI in legal intake. Covers MICRA compliance, CCP § 364, Cal. R.P.C. 1.1 competency, and duty of supervision for State Bar of California.",
        ["California AI ethics legal intake", "MICRA AI compliance", "California bar AI rules", "Cal RPC AI competency", "CA legal ethics AI"],
        "/blog/california-trial-lawyers-ai-ethics-legal-intake"
    ),
    "blog/texas-trial-lawyers-ai-ethics-legal-intake.html": (
        "AI Ethics in Legal Intake: Texas Guide for Trial Lawyers | LexiFlow",
        "Texas AI ethics guide for trial lawyers using AI in legal intake. Covers Texas Disciplinary Rules, duty of competence, client confidentiality, and supervision requirements for State Bar of Texas.",
        ["Texas AI ethics legal intake", "Texas bar AI rules", "Texas disciplinary rules AI", "TX legal ethics AI", "Texas law firm AI compliance"],
        "/blog/texas-trial-lawyers-ai-ethics-legal-intake"
    ),
    "blog/florida-trial-lawyers-ai-ethics-legal-intake.html": (
        "AI Ethics in Legal Intake: Florida Guide for Trial Lawyers | LexiFlow",
        "Florida AI ethics guide for trial lawyers using AI in legal intake. Covers Florida Bar rules, duty of technological competence, client confidentiality, and supervision requirements.",
        ["Florida AI ethics legal intake", "Florida bar AI rules", "FL legal ethics AI", "Florida lawyer AI compliance", "Florida bar technology rules"],
        "/blog/florida-trial-lawyers-ai-ethics-legal-intake"
    ),
    "blog/new-jersey-trial-lawyers-ai-ethics-legal-intake.html": (
        "AI Ethics in Legal Intake: New Jersey Guide for Trial Lawyers | LexiFlow",
        "New Jersey AI ethics guide for trial lawyers using AI in legal intake. Covers NJ RPCs, duty of competence, client confidentiality, supervision of AI tools, and attorney obligations.",
        ["New Jersey AI ethics legal intake", "NJ bar AI rules", "New Jersey RPC AI", "NJ legal ethics AI", "New Jersey lawyer AI compliance"],
        "/blog/new-jersey-trial-lawyers-ai-ethics-legal-intake"
    ),

    # ── Other resource pages ──
    "ai-legal-intake-software.html": (
        "AI Legal Intake Software — Automate Client Qualification | LexiFlow",
        "LexiFlow AI legal intake software automates lead qualification for plaintiff law firms. Conversational AI, 0-100 medical merit scoring, and CRM integration. Reduce cost-per-lead by 60%.",
        ["AI legal intake software", "legal intake automation", "law firm AI intake", "client qualification AI", "legal lead generation software"],
        "/ai-legal-intake-software"
    ),
    "roi-calculator.html": (
        "ROI Calculator — Calculate Legal AI Savings | LexiFlow",
        "Calculate the ROI of implementing LexiFlow AI for your law firm. Estimate savings on intake staff, document review, deposition analysis, and case preparation with our interactive ROI calculator.",
        ["legal AI ROI calculator", "law firm AI savings", "legal tech ROI", "AI investment calculator law firm", "legal automation savings"],
        "/roi-calculator"
    ),
    "roi-report-template.html": (
        "ROI Report Template — Legal AI Investment Analysis | LexiFlow",
        "Download LexiFlow's ROI report template to analyze the financial impact of AI-powered legal intake, medical merit review, and deposition analysis for your plaintiff law firm.",
        ["ROI report legal AI", "legal tech investment report", "law firm AI ROI template", "legal automation ROI analysis", "AI legal business case"],
        "/roi-report-template"
    ),

    # ── Marketing & Lead Magnet pages ──
    "lead-magnet-section.html": (
        "Free Resources — Medical Chronology Templates & Guides | LexiFlow",
        "Download free law firm resources from LexiFlow: medical chronology templates, record review checklists, ROI analysis guides, and AI ethics compliance documents for plaintiff attorneys.",
        ["free legal resources", "medical chronology template download", "law firm guides", "legal AI resources", "plaintiff attorney tools"],
        "/lead-magnet-section"
    ),
    "marketing/crm-assets/demo-video-storyboard.html": (
        "Demo Video Storyboard — LexiFlow Legal AI Platform Walkthrough",
        "Storyboard for LexiFlow's product demo video showcasing AI intake, medical merit review, Veritas Deposition contradiction detection, and LexiFlow Strategist settlement intelligence.",
        ["LexiFlow demo video", "legal AI product demo", "law firm software storyboard", "legal tech demo script", "AI intake walkthrough"],
        "/marketing/crm-assets/demo-video-storyboard"
    ),

    # ── Privacy / Terms / Security ──
    "privacy.html": (
        "Privacy Policy | LexiFlow Technologies Inc",
        "LexiFlow privacy policy. Learn how we collect, use, and protect your personal data. We maintain strict data protection standards for law firms, attorneys, and their clients.",
        ["LexiFlow privacy policy", "legal software privacy", "law firm data privacy", "legal AI data protection", "privacy policy legal tech"],
        "/privacy"
    ),
    "terms.html": (
        "Terms of Service | LexiFlow Technologies Inc",
        "LexiFlow terms of service governing use of our AI-powered legal operations platform. Includes service terms, subscription details, data handling, and legal disclaimers for law firm users.",
        ["LexiFlow terms of service", "legal software terms", "law firm SaaS terms", "AI legal platform terms", "legal tech service agreement"],
        "/terms"
    ),
    "security.html": (
        "Security & Data Protection | LexiFlow Technologies Inc",
        "LexiFlow enterprise security: SOC 2 compliance, HIPAA-compliant data handling, signed BAAs, encryption at rest and in transit, and role-based access controls for plaintiff law firms.",
        ["legal AI security", "law firm data protection", "SOC 2 legal tech", "HIPAA compliance legal software", "law firm cybersecurity", "legal platform security"],
        "/security"
    ),

    # ── Whitepapers ──
    "whitepaper.html": (
        "Whitepaper — The Future of AI in Legal Intake | LexiFlow",
        "Download LexiFlow's whitepaper on the future of AI in legal intake and litigation. Learn how Reasoning AI is transforming medical merit review, deposition analysis, and case strategy.",
        ["AI legal whitepaper", "legal AI future", "legal technology trends", "AI litigation whitepaper", "law firm technology report"],
        "/whitepaper"
    ),
    "whitepaper-state-of-ai-legal-intake-2026.html": (
        "State of AI Legal Intake 2026 — Industry Report | LexiFlow",
        "The State of AI Legal Intake 2026 report: how plaintiff law firms are adopting AI for lead qualification, medical merit review, deposition analysis, and case strategy. Data-driven insights.",
        ["state of AI legal intake 2026", "legal AI industry report", "law firm AI adoption", "legal tech trends 2026", "AI legal intake research"],
        "/whitepaper-state-of-ai-legal-intake-2026"
    ),

    # ── Blog ──
    "blog/index.html": (
        "Blog — Legal AI Insights & Guides | LexiFlow Technologies",
        "LexiFlow blog: AI legal intake guides, deposition analysis tips, medical merit review best practices, and legal technology insights for plaintiff personal injury and medmal attorneys.",
        ["legal AI blog", "law firm technology blog", "legal intake tips", "deposition analysis guide", "medical merit review blog", "legal tech insights"],
        "/blog"
    ),
    "blog/deposition-summary-template.html": (
        "Deposition Summary Template — AI-Generated | LexiFlow",
        "View a sample AI-generated deposition summary from LexiFlow Veritas Deposition™. Automated transcript analysis, key testimony extraction, and contradiction flagging for trial prep.",
        ["deposition summary template", "sample deposition summary", "AI deposition summary example", "transcript summary template", "legal deposition sample"],
        "/blog/deposition-summary-template"
    ),

    # ── Case Studies ──
    "case-studies/rodriguez-v-mount-sinai.html": (
        "Rodriguez v. Mount Sinai — AI Medical Malpractice Case Study | LexiFlow",
        "Medical malpractice case study: How LexiFlow AI analyzed Rodriguez v. Mount Sinai. Merit score: 92/100. Veritas Deposition flagged 7 contradictions. Settlement-predictor projected $4.2M trial value.",
        ["medical malpractice case study", "AI litigation case study", "Rodriguez v Mount Sinai", "legal AI case analysis", "medmal AI demo case"],
        "/case-studies/rodriguez-v-mount-sinai"
    ),
    "case-study-clifford-law.html": (
        "Clifford Law Offices — AI Intake Case Study | LexiFlow",
        "How Clifford Law Offices uses LexiFlow AI to automate intake qualification, screen medical merit, and prioritize high-value personal injury cases. Real results from a leading PI firm.",
        ["Clifford Law AI case study", "law firm AI intake results", "personal injury AI case study", "legal automation success", "law firm AI adoption"],
        "/case-study-clifford-law"
    ),
    "case-study-smith-lacien.html": (
        "Smith & Lacien — AI Medical Merit Review Case Study | LexiFlow",
        "How Smith & Lacien uses LexiFlow's AI MeritScan to screen medical malpractice cases, reduce intake review time by 75%, and identify strong cases before investing in full case review.",
        ["Smith Lacien AI case study", "medical merit review results", "medmal AI screening", "law firm AI ROI", "legal AI case study"],
        "/case-study-smith-lacien"
    ),

    # ── Props / Utility pages ──
    "props.html": (
        "LexiFlow Brand Assets & Props — Logos, Screenshots & Graphics",
        "Download LexiFlow brand assets: company logos, product screenshots, icons, and marketing graphics for media, partners, and law firm technology presentations.",
        ["LexiFlow brand assets", "legal tech logos", "law firm software graphics", "LexiFlow screenshots", "legal AI marketing materials"],
        "/props"
    ),

    # ── Practice Area ──
    "practice-areas/medical-malpractice/index.html": (
        "Medical Malpractice Software — AI Case Intake & Analysis | LexiFlow",
        "Medical malpractice software for plaintiff attorneys. AI-powered case intake, medical record review, merit scoring, and deposition analysis. Built for medmal practitioners nationwide.",
        ["medical malpractice software", "medmal AI intake", "malpractice case management", "medical malpractice technology", "plaintiff medmal tools"],
        "/practice-areas/medical-malpractice"
    ),

    # ── Hardened Suite pages ──
    "hardened-suite/index.html": (
        "LexiFlow | Enterprise Legal Intelligence & Automation",
        "LexiFlow enterprise-grade AI orchestration for high-stakes litigation and high-volume intake. From initial contact to final settlement, automate legal operations with Reasoning AI.",
        ["enterprise legal AI", "legal operations platform", "law firm automation suite", "litigation intelligence", "legal AI enterprise"],
        "/hardened-suite/"
    ),
    "hardened-suite/ai-intake-agent.html": (
        "AI Intake Agent — Hardened Suite | LexiFlow",
        "LexiFlow AI Intake Agent for enterprise: 24/7 lead qualification, medical merit scoring, and CRM integration. Built for high-volume plaintiff law firms.",
        ["AI intake enterprise", "hardened suite intake", "law firm lead scoring", "enterprise legal intake"],
        "/hardened-suite/ai-intake-agent"
    ),
    "hardened-suite/ai-medical-chronologies.html": (
        "AI Medical Chronologies — Hardened Suite | LexiFlow",
        "Enterprise AI medical chronology generation. Automatically extract treatment timelines, diagnoses, and provider notes from medical records at scale.",
        ["enterprise medical chronology", "AI chronology hardened", "medical record automation", "legal timeline enterprise"],
        "/hardened-suite/ai-medical-chronologies"
    ),
    "hardened-suite/auto-document-drafter.html": (
        "Auto-Document Drafter — Hardened Suite | LexiFlow",
        "Enterprise document automation for law firms. Generate demand letters, settlement agreements, and case summaries with AI-powered document drafting at scale.",
        ["enterprise document drafting", "AI document generator", "legal document automation", "law firm document AI"],
        "/hardened-suite/auto-document-drafter"
    ),
    "hardened-suite/cities.html": (
        "Service Cities — LexiFlow Hardened Suite Coverage",
        "LexiFlow enterprise legal AI coverage across major US cities. AI-powered intake, medical review, and deposition analysis for plaintiff firms nationwide.",
        ["LexiFlow cities", "legal AI coverage", "law firm locations", "enterprise legal AI cities"],
        "/hardened-suite/cities"
    ),
    "hardened-suite/compliance-shield.html": (
        "Compliance Shield — Hardened Suite | LexiFlow Enterprise Security",
        "Enterprise-grade compliance for legal AI: HIPAA, SOC 2, BAA, encryption, and role-based access controls. LexiFlow Compliance-Shield for law firms.",
        ["enterprise compliance", "legal AI security", "HIPAA enterprise", "SOC 2 compliance legal"],
        "/hardened-suite/compliance-shield"
    ),
    "hardened-suite/dashboard.html": (
        "Enterprise Dashboard — LexiFlow Hardened Suite",
        "LexiFlow enterprise dashboard: AI intake metrics, medical review pipeline, deposition analysis, and settlement intelligence. Real-time litigation operations center.",
        ["enterprise dashboard", "legal AI metrics", "litigation dashboard", "law firm analytics"],
        "/hardened-suite/dashboard"
    ),
    "hardened-suite/demo.html": (
        "Enterprise Demo — LexiFlow Hardened Suite",
        "Request a demo of LexiFlow Hardened Suite for enterprise litigation. See AI intake, medical merit review, and deposition analysis in action.",
        ["enterprise legal demo", "AI litigation demo", "law firm AI demo", "hardened suite demo"],
        "/hardened-suite/demo"
    ),
    "hardened-suite/depolens-ai.html": (
        "DepoLens AI — Enterprise Deposition Intelligence | LexiFlow",
        "Enterprise deposition analysis with AI-powered contradiction detection, witness intelligence, and cross-examination builder. DepoLens for high-volume litigation.",
        ["enterprise deposition AI", "deposition analysis enterprise", "DepoLens", "litigation intelligence"],
        "/hardened-suite/depolens-ai"
    ),
    "hardened-suite/discovery-vault.html": (
        "Discovery Vault — Enterprise Document Intelligence | LexiFlow",
        "Enterprise discovery document management with AI-powered indexing, contradiction flagging, and key evidence extraction for mass tort and complex litigation.",
        ["enterprise discovery", "AI document review", "mass tort discovery", "e-discovery enterprise"],
        "/hardened-suite/discovery-vault"
    ),
    "hardened-suite/medical-chronology-sample.html": (
        "Medical Chronology Sample — Hardened Suite | LexiFlow",
        "Sample AI-generated medical chronology from LexiFlow enterprise suite. Automated timeline extraction from medical records for legal case preparation.",
        ["enterprise medical chronology sample", "AI chronology example", "medical timeline sample"],
        "/hardened-suite/medical-chronology-sample"
    ),
    "hardened-suite/medical-chronology-template.html": (
        "Medical Chronology Template — Hardened Suite | LexiFlow",
        "Enterprise medical chronology template showing AI-powered treatment timeline extraction. Standard format for plaintiff personal injury and medmal cases.",
        ["enterprise chronology template", "medical timeline template", "AI chronology format"],
        "/hardened-suite/medical-chronology-template"
    ),
    "hardened-suite/medical-record-review-checklist.html": (
        "Medical Record Review Checklist — Hardened Suite | LexiFlow",
        "Enterprise medical record review checklist for high-volume plaintiff firms. AI-powered extraction of critical timelines, treatment gaps, and medical findings.",
        ["enterprise record review", "medical checklist", "AI record audit", "legal medical review"],
        "/hardened-suite/medical-record-review-checklist"
    ),
    "hardened-suite/pricing.html": (
        "Enterprise Pricing — LexiFlow Hardened Suite Plans",
        "LexiFlow enterprise pricing for high-volume law firms and mass tort practices. Custom plans with unlimited document processing, dedicated support, and enterprise SLAs.",
        ["enterprise pricing legal AI", "law firm enterprise plan", "legal AI custom pricing"],
        "/hardened-suite/pricing"
    ),
    "hardened-suite/security.html": (
        "Enterprise Security — LexiFlow Hardened Suite",
        "LexiFlow enterprise security: SOC 2 Type II, HIPAA compliance, encryption at rest/transit, role-based access, audit logging, and signed BAAs for law firms.",
        ["enterprise security legal", "SOC 2 law firm", "HIPAA enterprise", "legal AI data protection"],
        "/hardened-suite/security"
    ),
    "hardened-suite/settlement-predictor.html": (
        "Settlement Predictor — Enterprise Case Valuation | LexiFlow",
        "Enterprise settlement prediction with AI-powered case valuation. Analyze medical records, jurisdictional trends, and verdict data for accurate settlement projections.",
        ["enterprise settlement prediction", "AI case valuation", "settlement AI enterprise", "legal damages calculator"],
        "/hardened-suite/settlement-predictor"
    ),

    # ── Admin pages ──
    "admin/index.html": (
        "Admin — LexiFlow Enterprise System Administration",
        "LexiFlow system administration panel. Manage users, subscriptions, integrations, and enterprise configuration for the AI-powered legal operations platform.",
        ["LexiFlow admin", "legal system administration", "enterprise admin panel"],
        "/admin/"
    ),
    "admin/login.html": (
        "Admin Login — LexiFlow Enterprise System",
        "Secure admin login for LexiFlow enterprise system administration. Authorized personnel only.",
        ["LexiFlow admin login", "enterprise admin portal", "system admin authentication"],
        "/admin/login"
    ),

    # ── Branding / Marketing pages ──
    "branding/crm-icons/demo.html": (
        "CRM Icons Demo — LexiFlow Brand Assets",
        "Preview LexiFlow CRM integration icons for Clio, Filevine, and other legal practice management platforms.",
        ["LexiFlow CRM icons", "legal CRM branding", "law firm software icons"],
        "/branding/crm-icons/demo"
    ),
    "branding/depolens/index.html": (
        "DepoLens Brand Assets — LexiFlow Veritas Deposition™",
        "Brand assets and marketing materials for LexiFlow Veritas Deposition™ DepoLens product line.",
        ["DepoLens branding", "Veritas Deposition assets", "legal tech brand"],
        "/branding/depolens/"
    ),
    "branding/front_desk_ui/index.html": (
        "Front Desk UI — LexiFlow Intake Interface",
        "LexiFlow front desk intake interface design showcase. AI-powered client intake and lead qualification user experience.",
        ["front desk UI", "legal intake interface", "law firm UI design"],
        "/branding/front_desk_ui/"
    ),
    "crm-icons/demo.html": (
        "CRM Integration Icons — LexiFlow",
        "LexiFlow CRM integration icon set for Clio, Filevine, and other legal practice management platforms.",
        ["CRM icons", "legal integration icons", "LexiFlow CRM"],
        "/crm-icons/demo"
    ),

    # ── Dashboard ──
    "dashboard.html": (
        "LexiFlow Dashboard | Enterprise Litigation Suite",
        "LexiFlow product dashboard showing all AI modules: Intake Agent, Voice AI, Medical Chronologies, Document Drafter, Veritas Deposition, Settlement Estimator. Central litigation command center.",
        ["LexiFlow dashboard", "legal AI dashboard", "litigation command center", "law firm analytics", "AI case management"],
        "/dashboard"
    ),

    # ── Desktop app pages ──
    "desktop/renderer/index.html": (
        "LexiFlow Desktop — Legal AI Desktop Application",
        "LexiFlow desktop application for Windows and Mac. Access AI-powered legal intake, medical review, and deposition analysis from your desktop.",
        ["LexiFlow desktop", "legal AI desktop app", "law firm desktop software"],
        "/desktop/"
    ),
    "desktop/renderer/login.html": (
        "Desktop Login — LexiFlow Legal AI Application",
        "Secure login for LexiFlow desktop application. Access your AI legal operations platform from your desktop.",
        ["LexiFlow desktop login", "legal app authentication", "law firm desktop login"],
        "/desktop/login"
    ),
    "desktop/renderer/desktop-settings.html": (
        "Desktop Settings — LexiFlow Legal AI Application",
        "Configure LexiFlow desktop application settings. Manage notifications, integrations, display preferences, and account settings.",
        ["LexiFlow desktop settings", "legal app configuration", "law firm desktop preferences"],
        "/desktop/settings"
    ),

    # ── ROI Report in assets ──
    "assets/report/roi-report-template.html": (
        "ROI Report Template — Legal AI Investment Analysis | LexiFlow",
        "Download LexiFlow's ROI report template to analyze the financial impact of AI-powered legal operations for your plaintiff law firm.",
        ["ROI report legal AI", "legal tech investment analysis", "law firm AI ROI template"],
        "/assets/report/roi-report-template"
    ),

    # ── Case Studies Index ──
    "case-studies/index.html": (
        "Case Studies — LexiFlow AI Legal Platform Success Stories",
        "Real-world case studies demonstrating how LexiFlow's AI-powered litigation platform uncovers treatment gaps, quantifies damages, and builds cross-examinations. See results from leading plaintiff firms.",
        ["LexiFlow case studies", "legal AI success stories", "law firm AI results", "litigation case studies"],
        "/case-studies/"
    ),

    # ── Lead Magnet ──
    "lead-magnet-section.html": (
        "Free Legal Resources — Medical Chronology Templates & Guides | LexiFlow",
        "Download free law firm resources from LexiFlow: medical chronology templates, record review checklists, ROI analysis guides, and AI ethics compliance documents for plaintiff attorneys.",
        ["free legal resources", "medical chronology template download", "law firm guides", "legal AI resources", "plaintiff attorney tools"],
        "/lead-magnet-section"
    ),
}

# ── Pages with duplicate resource pattern ──
RESOURCE_COPY_MAP = {
    "resources/medical-chronology-sample.html": "medical-chronology-sample.html",
    "resources/medical-chronology-template.html": "medical-chronology-template.html",
    "resources/medical-record-review-checklist.html": "medical-record-review-checklist.html",
}


def build_meta_block(title, desc, keywords, canonical_url, page_name):
    """Build the full meta block string to inject after <meta charset> and <meta viewport>."""
    kw_str = ", ".join(keywords)
    return f'''  <title>{title}</title>
  <meta name="description" content="{desc}" />
  <meta name="keywords" content="{kw_str}" />
  <link rel="canonical" href="{canonical_url}" />

  <!-- Open Graph / Social Sharing -->
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{desc}" />
  <meta property="og:url" content="{canonical_url}" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="LexiFlow Technologies Inc" />
  <meta property="og:image" content="{SOCIAL_BANNER}" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:locale" content="en_US" />

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{title}" />
  <meta name="twitter:description" content="{desc}" />
  <meta name="twitter:image" content="{SOCIAL_BANNER}" />'''


def inject_meta_block(content, meta_block):
    """Inject the meta block after the <meta name="viewport"> line.
    If there's an existing <title> or description, replace them instead.
    """
    # If <title> exists but missing description/OG, we need to replace/enhance
    # Strategy: Remove existing <title>, <meta name="description">, <meta name="keywords">,
    # <link rel="canonical">, <meta property="og:*">, <meta name="twitter:*">
    # then insert our complete block after viewport.
    
    # Remove all existing meta tags we're replacing
    lines = content.split('\n')
    
    # We'll build a new version by:
    # 1. Keep everything before <meta name="viewport"> line
    # 2. Keep the viewport line
    # 3. Inject our meta block
    # 4. Skip any existing title, meta desc, meta keywords, og tags, twitter tags, canonical
    # 5. Keep everything else
    
    patterns_to_skip = [
        r'<title>.*</title>',
        r'<meta\s+name=["\']description["\'].*',
        r'<meta\s+name=["\']keywords["\'].*',
        r'<meta\s+property=["\']og:[^"\']*["\'].*',
        r'<meta\s+name=["\']twitter:[^"\']*["\'].*',
        r'<link\s+rel=["\']canonical["\'].*',
    ]
    
    # Find the viewport line and everything before it
    in_head = False
    after_viewport = False
    new_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        # Check if this line matches any pattern to skip
        skip = False
        for pat in patterns_to_skip:
            if re.search(pat, stripped, re.IGNORECASE):
                skip = True
                break
        
        if skip:
            continue
        
        # Detect viewport line
        if 'name="viewport"' in stripped or "name='viewport'" in stripped:
            new_lines.append(line)
            new_lines.append(meta_block)
            after_viewport = True
            continue
        
        new_lines.append(line)
    
    return '\n'.join(new_lines)


def fix_html_file(filepath, meta_data):
    """Fix a single HTML file with proper SEO meta tags."""
    rel = os.path.relpath(filepath, REPO)
    title, desc, keywords, canonical_suffix = meta_data
    canonical_url = f"{BASE_URL}{canonical_suffix}"
    
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    
    meta_block = build_meta_block(title, desc, keywords, canonical_url, rel)
    new_content = inject_meta_block(content, meta_block)
    
    # Safety: ensure the content actually changed
    if new_content == content:
        print(f"WARNING: No changes made to {rel} — may need manual review")
    else:
        print(f"FIXED: {rel}")
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)


def fix_email_template(filepath, template_name):
    """Email templates get simpler metadata — just title + bare minimal."""
    titles = {
        "lead_notification.html": "New Lead Notification — LexiFlow AI Intake",
        "password_reset.html": "Password Reset — LexiFlow Account",
        "welcome.html": "Welcome to LexiFlow — Get Started with Your Free Trial",
    }
    title = titles.get(template_name, f"{template_name} — LexiFlow")
    
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    
    # Add title and description after <meta charset>
    meta_block = f'  <title>{title}</title>\n  <meta name="description" content="Email notification from LexiFlow Technologies Inc." />'
    
    # Insert after charset line
    lines = content.split('\n')
    new_lines = []
    inserted = False
    for line in lines:
        new_lines.append(line)
        if '<meta charset' in line and not inserted:
            new_lines.append(meta_block)
            inserted = True
    
    new_content = '\n'.join(new_lines)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print(f"FIXED (email template): {os.path.relpath(filepath, REPO)}")


def fix_veritas_subdir(filepath):
    """Fix files in veritas-deposition/frontend/ and veritas/ subdirectories."""
    rel = os.path.relpath(filepath, REPO)
    
    # Determine appropriate title based on the file
    if "veritas-deposition/frontend" in rel:
        title = "Veritas Deposition™ — Evidence Intelligence System"
        desc = "Veritas Deposition™ transforms deposition transcripts into structured litigation intelligence. Contradiction detection, cross-examination builder, and witness analysis for trial attorneys."
    elif "veritas/index" in rel:
        title = "Veritas — Evidence Intelligence | LexiFlow"
        desc = "Veritas by LexiFlow: AI-powered evidence intelligence for deposition analysis, contradiction detection, and trial preparation."
    else:
        # Generic fallback
        title = "LexiFlow | AI Legal Operations"
        desc = "LexiFlow AI-powered legal operations platform for plaintiff law firms."
    
    keywords = ["deposition analysis", "legal transcript AI", "evidence intelligence", "law firm software"]
    canonical_url = f"{BASE_URL}/{rel}"
    
    meta_block = build_meta_block(title, desc, keywords, canonical_url, rel)
    
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    
    new_content = inject_meta_block(content, meta_block)
    
    if new_content == content:
        print(f"WARNING: No changes to {rel}")
    else:
        print(f"FIXED: {rel}")
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)


# ─── Main execution ──────────────────────────────────────────────────────
def main():
    html_files = sorted(glob.glob(os.path.join(REPO, "**/*.html"), recursive=True))
    
    # First pass: fix pages with specific metadata
    for fp in html_files:
        rel = os.path.relpath(fp, REPO)
        
        # Email templates get special handling
        if rel.startswith("templates/email/"):
            template_name = os.path.basename(rel)
            fix_email_template(fp, template_name)
            continue
        
        # Veritas subdirectories
        if rel.startswith("veritas-deposition/frontend/") or rel == "veritas/index.html":
            fix_veritas_subdir(fp)
            continue
        
        # Resource copies
        if rel in RESOURCE_COPY_MAP:
            source_rel = RESOURCE_COPY_MAP[rel]
            if source_rel in PAGE_META:
                fix_html_file(fp, PAGE_META[source_rel])
            continue
        
        # Direct metadata lookup
        if rel in PAGE_META:
            fix_html_file(fp, PAGE_META[rel])
        else:
            # Check if it's a practice-area state page (they already pass audit)
            # or some other page we don't need to fix
            print(f"SKIPPED (no meta defined): {rel}")


if __name__ == "__main__":
    main()

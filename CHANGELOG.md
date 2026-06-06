# Changelog: LexiFlow Technologies Inc Suite Evolution

All notable changes to the LexiFlow Technologies Inc project will be documented in this file.

## [2026-05-26] - Professional Pivot & MeritScan Launch

### Added
- **MeritScan Product**: Launched the AI Medical Merit Review tool.
  - New landing page: `meritscan.html` with medical aesthetic and ROI stats.
  - New branding: Shield-based logos and icons in `/branding/meritscan/`.
  - Integration: Added MeritScan to the primary navigation dropdown on the homepage.
- **DepoLens Integration**: Integrated DepoLens (AI Deposition Analysis) into the primary product suite.
- **Local SEO Moat**: Initiated creation of 10 local-optimized landing pages for top US cities (e.g., Chicago, NYC, LA) in the `/cities/` directory.
- **GitHub Integration (In Progress)**: Developing a secure document export feature to push AI-generated reports directly to firm-owned GitHub repositories.

### Changed
- **UX Pivot**: Moved from a "self-serve playground" model to a professional "consultation" model.
- **CTA Updates**: Replaced "Live Demo" buttons with "Request Consultation" to capture high-intent leads.
- **Website Cleanup**: Refactored `index.html` to focus on the unified Legal AI Suite (LexiFlow, DepoLens, MeritScan).
- **Navigation**: Cleaned up the header to include a professional "Products" dropdown.

### Removed
- **Legacy Chat Widget**: Removed `widget.js` and `widget.css` as part of the shift to a lead-capture consultation model.
- **Public Demo Page**: Deleted `demo.html` to maintain the premium, high-touch sales process.

### Fixed
- **Mobile Responsiveness**: Improved navigation behavior on mobile devices.
- **Demo Request Endpoint**: Backend logic for demo requests now correctly triggers email notifications and lead database entries.

## [2026-05-25] - Core Platform Expansion

### Added
- **Multi-Channel Intake**: Beta support for Voice AI (Vapi) and Email Triage (Postmark).
- **CRM Integration Engine**: Production-ready mapping for Clio Grow and Filevine.
- **Dashboard v2**: Professional attorney dashboard with lead scoring and case summaries.

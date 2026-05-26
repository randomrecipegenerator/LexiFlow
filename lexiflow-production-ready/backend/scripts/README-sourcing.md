# Automated Nationwide Lead Sourcing Script

This script automates the lead sourcing process for LexiFlow, following the hybrid sourcing strategy.

## Features
- **Volume Sourcing:** Uses Apify's Google Maps Scraper to find law firms by practicing area and region.
- **Lead Enrichment:** Uses Apollo.io API to identify Managing Partners and their direct contact information (emails).
- **Format Support:** Outputs results to CSV or JSON.
- **Dry Run Mode:** Simulates data extraction for testing purposes without consuming API credits.

## Setup

### 1. Prerequisites
Ensure you have the required Python packages installed:
```bash
pip install apify-client requests
```

### 2. API Keys
The script requires the following environment variables to be set:
- `APIFY_API_TOKEN`: Your Apify API token.
- `APOLLO_API_KEY`: Your Apollo.io API key.

You can set them in your terminal or add them to the project's `.env` file:
```bash
export APIFY_API_TOKEN='your_token_here'
export APOLLO_API_KEY='your_key_here'
```

## Usage

### Run a Dry Run (Simulation)
```bash
python3 source_leads.py --dry-run --output simulation_results.csv
```

### Run a Real Scrape for Phase 1 Regions
```bash
python3 source_leads.py --limit 10 --output phase1_leads.csv
```

### Targeted Scrape
```bash
python3 source_leads.py --regions "Los Angeles, CA" "San Francisco, CA" --queries "Personal Injury Law Firm" --limit 20
```

## Strategy Rollout
This script is designed to support the Phase 1 rollout focusing on high-growth regions:
- Florida (Miami, Tampa, Orlando, Jacksonville, St. Petersburg)
- Texas (Houston, Dallas, Austin)
- California (Los Angeles, San Francisco)
- New York (New York City)
- Illinois (Chicago)

## Output
The script generates a CSV or JSON file containing:
- Firm Name
- Address, City, State
- Website
- Phone Number
- Category
- Rating & Reviews Count
- Managing Partner Name (Enriched)
- Direct Email (Enriched)

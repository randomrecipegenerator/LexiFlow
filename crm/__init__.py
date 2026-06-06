"""LexiFlow Enterprise CRM Integration Package.

Provides dedicated clients for Filevine, Clio Grow, and LeadDock
with OAuth support, webhooks, score-triggered sync engine,
and comprehensive error handling.
"""
from .filevine import FilevineClient, FilevineConfig, FilevineOAuthClient
from .score_sync_engine import ScoreTriggeredSyncEngine, evaluate_score, SCORE_THRESHOLDS
from .score_sync_engine import ScoreTriggeredAction
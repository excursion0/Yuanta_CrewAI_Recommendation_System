"""
LLM integration package for the financial product recommendation system.

This package contains LLM providers, response generation, and intent analysis
capabilities using Anthropic Claude (primary) and OpenAI (fallback).
"""

from .providers import LLMProvider, AnthropicProvider, OpenAIProvider, LLMResponse
from .response_generator import ResponseGenerator, RecommendationResponse
from .intent_analyzer import IntentAnalyzer, ExtractedIntent, IntentType, RiskLevel, InvestmentGoal
from .manager import LLMManager, LLMConfig, LLMHealthStatus

__all__ = [
    "LLMProvider",
    "AnthropicProvider", 
    "OpenAIProvider",
    "LLMResponse",
    "ResponseGenerator",
    "RecommendationResponse",
    "IntentAnalyzer",
    "ExtractedIntent",
    "IntentType",
    "RiskLevel",
    "InvestmentGoal",
    "LLMManager",
    "LLMConfig",
    "LLMHealthStatus"
] 
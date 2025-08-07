"""
Custom exception classes for the financial product recommendation system.

This module provides specific exception types for different error scenarios
to improve error handling and debugging.
"""


class FinancialRecommendationError(Exception):
    """Base exception for financial recommendation system"""
    pass


class LLMError(FinancialRecommendationError):
    """Exception for LLM-related errors"""
    pass


class SessionError(FinancialRecommendationError):
    """Exception for session management errors"""
    pass


class DataSourceError(FinancialRecommendationError):
    """Exception for data source errors"""
    pass


class EventBusError(FinancialRecommendationError):
    """Exception for event bus errors"""
    pass


class ChatbotError(FinancialRecommendationError):
    """Exception for chatbot-related errors"""
    pass


class ValidationError(FinancialRecommendationError):
    """Exception for data validation errors"""
    pass


class ConfigurationError(FinancialRecommendationError):
    """Exception for configuration errors"""
    pass


class NetworkError(FinancialRecommendationError):
    """Exception for network-related errors"""
    pass


class TimeoutError(FinancialRecommendationError):
    """Exception for timeout errors"""
    pass 
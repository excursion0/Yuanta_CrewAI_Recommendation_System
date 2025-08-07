"""
Custom exception classes for the financial recommendation system.

Provides specific exception types for different error scenarios
to enable better error handling and debugging.
"""

from typing import Optional, Dict, Any


class FinancialRecommendationError(Exception):
    """Base exception for financial recommendation system errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the exception.
        
        Args:
            message: Error message
            details: Optional additional error details
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class AgentInitializationError(FinancialRecommendationError):
    """Raised when an agent fails to initialize properly."""
    pass


class LLMConnectionError(FinancialRecommendationError):
    """Raised when LLM service connection fails."""
    pass


class DataValidationError(FinancialRecommendationError):
    """Raised when data validation fails."""
    pass


class ComplianceError(FinancialRecommendationError):
    """Raised when compliance checks fail."""
    pass


class SuitabilityError(FinancialRecommendationError):
    """Raised when suitability validation fails."""
    pass


class ProductNotFoundError(FinancialRecommendationError):
    """Raised when a requested product is not found."""
    pass


class SessionError(FinancialRecommendationError):
    """Raised when session management operations fail."""
    pass


class DiscordBotError(FinancialRecommendationError):
    """Raised when Discord bot operations fail."""
    pass


class TimeoutError(FinancialRecommendationError):
    """Raised when operations timeout."""
    pass


class ConfigurationError(FinancialRecommendationError):
    """Raised when configuration is invalid or missing."""
    pass


class ImportError(FinancialRecommendationError):
    """Raised when required modules cannot be imported."""
    pass


class DatabaseError(FinancialRecommendationError):
    """Raised when database operations fail."""
    pass


class APIError(FinancialRecommendationError):
    """Raised when external API calls fail."""
    pass


class ValidationError(FinancialRecommendationError):
    """Raised when input validation fails."""
    pass


class ProcessingError(FinancialRecommendationError):
    """Raised when data processing fails."""
    pass


class AuthenticationError(FinancialRecommendationError):
    """Raised when authentication fails."""
    pass


class PermissionError(FinancialRecommendationError):
    """Raised when permission checks fail."""
    pass


class ResourceNotFoundError(FinancialRecommendationError):
    """Raised when a requested resource is not found."""
    pass


class RateLimitError(FinancialRecommendationError):
    """Raised when rate limits are exceeded."""
    pass


class NetworkError(FinancialRecommendationError):
    """Raised when network operations fail."""
    pass


class SerializationError(FinancialRecommendationError):
    """Raised when data serialization/deserialization fails."""
    pass


class LoggingError(FinancialRecommendationError):
    """Raised when logging operations fail."""
    pass


class CacheError(FinancialRecommendationError):
    """Raised when caching operations fail."""
    pass


class EventBusError(FinancialRecommendationError):
    """Raised when event bus operations fail."""
    pass


class CrewAIError(FinancialRecommendationError):
    """Raised when CrewAI operations fail."""
    pass


class CrewAIExecutionError(CrewAIError):
    """Raised when CrewAI crew execution fails."""
    pass


class CrewAITaskError(CrewAIError):
    """Raised when CrewAI task creation or execution fails."""
    pass


class CrewAIAgentError(CrewAIError):
    """Raised when CrewAI agent operations fail."""
    pass


class CrewAITimeoutError(CrewAIError):
    """Raised when CrewAI operations timeout."""
    pass

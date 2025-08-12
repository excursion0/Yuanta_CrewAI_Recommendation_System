"""
Centralized configuration management for the financial recommendation system.

Provides constants and configuration values to replace magic numbers and strings
throughout the codebase.
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class LogLevel(Enum):
    """Logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class RiskLevel(Enum):
    """Risk tolerance levels"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class TimeHorizon(Enum):
    """Investment time horizons"""
    SHORT_TERM = "short_term"
    MEDIUM_TERM = "medium_term"
    LONG_TERM = "long_term"


@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    MAX_CONNECTIONS: int = 10
    CONNECTION_TIMEOUT: int = 30
    QUERY_TIMEOUT: int = 60
    RETRY_ATTEMPTS: int = 3
    POOL_SIZE: int = 5


@dataclass
class APIConfig:
    """API configuration settings"""
    MAX_REQUEST_SIZE: int = 1024 * 1024  # 1MB
    REQUEST_TIMEOUT: int = 30
    RATE_LIMIT_PER_MINUTE: int = 100
    MAX_CONCURRENT_REQUESTS: int = 10
    CORS_ORIGINS: List[str] = None
    
    def __post_init__(self):
        if self.CORS_ORIGINS is None:
            self.CORS_ORIGINS = ["http://localhost:3000", "https://localhost:3000"]


@dataclass
class CrewAIConfig:
    """CrewAI configuration settings"""
    MAX_RETRIES: int = 1
    MAX_ITERATIONS: int = 1
    TIMEOUT_SECONDS: int = 300
    VERBOSE: bool = False
    MEMORY_ENABLED: bool = False
    PROCESS_TYPE: str = "sequential"


@dataclass
class LLMConfig:
    """LLM configuration settings"""
    DEFAULT_MODEL: str = "claude-3-5-sonnet-20241022"
    MAX_TOKENS: int = 4000
    TEMPERATURE: float = 0.7
    TOP_P: float = 0.9
    REQUEST_TIMEOUT: int = 60
    RETRY_ATTEMPTS: int = 3


@dataclass
class DiscordConfig:
    """Discord bot configuration settings"""
    MAX_MESSAGE_LENGTH: int = 2000
    COMMAND_PREFIX: str = "/"
    RESPONSE_TIMEOUT: int = 30
    MAX_EMBED_FIELDS: int = 25
    MAX_EMBED_DESCRIPTION: int = 4096


@dataclass
class TelegramConfig:
    """Telegram bot configuration settings"""
    MAX_MESSAGE_LENGTH: int = 4096
    COMMAND_PREFIX: str = "/"
    RESPONSE_TIMEOUT: int = 30
    MAX_INLINE_KEYBOARD_ROWS: int = 8
    MAX_INLINE_KEYBOARD_COLS: int = 8


@dataclass
class ConversationConfig:
    """Conversation and memory configuration"""
    MAX_CONVERSATION_HISTORY: int = 3
    MAX_MESSAGE_LENGTH: int = 1000
    MEMORY_RETENTION_HOURS: int = 24
    CONTEXT_WINDOW_SIZE: int = 10
    MAX_USER_PROFILES: int = 1000


@dataclass
class ProductConfig:
    """Product recommendation configuration"""
    DEFAULT_RECOMMENDATION_LIMIT: int = 4
    MAX_PRODUCTS_PER_CATEGORY: int = 10
    MIN_RISK_SCORE: float = 0.0
    MAX_RISK_SCORE: float = 1.0
    DEFAULT_RISK_TOLERANCE: str = "moderate"
    DEFAULT_TIME_HORIZON: str = "medium_term"


@dataclass
class ValidationConfig:
    """Validation and compliance configuration"""
    MAX_INPUT_LENGTH: int = 5000
    MIN_INPUT_LENGTH: int = 1
    ALLOWED_FILE_TYPES: List[str] = None
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    REQUIRED_FIELDS: List[str] = None
    
    def __post_init__(self):
        if self.ALLOWED_FILE_TYPES is None:
            self.ALLOWED_FILE_TYPES = [".txt", ".pdf", ".doc", ".docx"]
        if self.REQUIRED_FIELDS is None:
            self.REQUIRED_FIELDS = ["user_query", "user_profile"]


@dataclass
class PerformanceConfig:
    """Performance and caching configuration"""
    CACHE_TTL_SECONDS: int = 3600  # 1 hour
    MAX_CACHE_SIZE: int = 1000
    ENABLE_COMPRESSION: bool = True
    ENABLE_CACHING: bool = True
    PERFORMANCE_MONITORING: bool = True


@dataclass
class SecurityConfig:
    """Security configuration settings"""
    API_KEY_HEADER: str = "X-API-Key"
    JWT_SECRET_KEY: str = "your-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    PASSWORD_MIN_LENGTH: int = 8
    SESSION_TIMEOUT_MINUTES: int = 30


class Config:
    """Main configuration class that aggregates all configuration sections"""
    
    def __init__(self):
        self.database = DatabaseConfig()
        self.api = APIConfig()
        self.crewai = CrewAIConfig()
        self.llm = LLMConfig()
        self.discord = DiscordConfig()
        self.telegram = TelegramConfig()
        self.conversation = ConversationConfig()
        self.product = ProductConfig()
        self.validation = ValidationConfig()
        self.performance = PerformanceConfig()
        self.security = SecurityConfig()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for serialization"""
        return {
            "database": self.database.__dict__,
            "api": self.api.__dict__,
            "crewai": self.crewai.__dict__,
            "llm": self.llm.__dict__,
            "discord": self.discord.__dict__,
            "telegram": self.telegram.__dict__,
            "conversation": self.conversation.__dict__,
            "product": self.product.__dict__,
            "validation": self.validation.__dict__,
            "performance": self.performance.__dict__,
            "security": self.security.__dict__
        }
    
    def update_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """Update configuration from dictionary"""
        for section_name, section_config in config_dict.items():
            if hasattr(self, section_name):
                section = getattr(self, section_name)
                for key, value in section_config.items():
                    if hasattr(section, key):
                        setattr(section, key, value)


# Global configuration instance
config = Config()

# Legacy constants for backward compatibility
MAX_CONVERSATION_HISTORY = config.conversation.MAX_CONVERSATION_HISTORY
MAX_RETRIES = config.crewai.MAX_RETRIES
DEFAULT_RECOMMENDATION_LIMIT = config.product.DEFAULT_RECOMMENDATION_LIMIT
TIMEOUT_SECONDS = config.crewai.TIMEOUT_SECONDS
MAX_MESSAGE_LENGTH = config.discord.MAX_MESSAGE_LENGTH

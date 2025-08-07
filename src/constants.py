"""
Constants and configuration values for the financial recommendation system.
"""

# Discord Configuration
DISCORD_MAX_MESSAGE_LENGTH = 1900
DISCORD_TIMEOUT_SECONDS = 25.0
DISCORD_COMMAND_PREFIX = "!"

# API Configuration
ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"
OPENAI_MODEL = "gpt-4"

# Product Database Configuration
DEFAULT_PRODUCT_LIMIT = 3
DEFAULT_RISK_LEVEL = "medium"
DEFAULT_INVESTMENT_AMOUNT = 100000

# Risk Analysis Configuration
DEFAULT_VOLATILITY = 0.15
DEFAULT_SHARPE_RATIO = 0.65
DEFAULT_MAX_DRAWDOWN = -0.20
DEFAULT_VAR_95 = -0.12

# Compliance Configuration
COMPLIANCE_THRESHOLD = 90.0
SUITABILITY_THRESHOLD = 70.0
DISCLOSURE_THRESHOLD = 80.0

# Session Configuration
DEFAULT_SESSION_TIMEOUT = 3600  # 1 hour
MAX_SESSION_MESSAGES = 100

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# File Paths
DATA_DIR = "data"
LOGS_DIR = "logs"
CONFIG_DIR = "config"

# Error Messages
ERROR_MESSAGES = {
    "import_failed": "Failed to import required module: {}",
    "api_key_missing": "API key not found in environment variables",
    "timeout_error": "Operation timed out after {} seconds",
    "validation_failed": "Data validation failed: {}",
    "connection_failed": "Failed to connect to {}: {}",
    "processing_error": "Error processing request: {}"
}

# Success Messages
SUCCESS_MESSAGES = {
    "bot_ready": "Discord bot is ready to use!",
    "api_configured": "API configured successfully",
    "test_passed": "Test passed successfully",
    "import_successful": "Import successful"
}

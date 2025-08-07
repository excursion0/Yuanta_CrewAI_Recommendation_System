"""
Enhanced base agent class for all financial recommendation agents.

This provides comprehensive common functionality and structure for all agents
in the CrewAI multi-agent system, including advanced logging, validation,
error handling, and performance monitoring.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
import logging
import os
import time
from datetime import datetime
from crewai import Agent, LLM
from crewai.tools import tool

from src.constants import ANTHROPIC_MODEL, LOG_LEVEL, LOG_FORMAT
from src.exceptions import AgentInitializationError, LLMConnectionError, ValidationError


class BaseAgent(ABC):
    """
    Enhanced abstract base class for all agents in the financial recommendation system.
    
    Provides comprehensive common functionality for agent initialization, LLM setup,
    tool management, logging, validation, error handling, and performance monitoring.
    """
    
    def __init__(self, llm_provider: Optional[str] = None, agent_name: Optional[str] = None):
        """
        Initialize the enhanced base agent.
        
        Args:
            llm_provider: Optional LLM provider override
            agent_name: Optional custom agent name for logging
        """
        self.llm_provider = llm_provider or "anthropic"
        self.agent_name = agent_name or self.__class__.__name__
        
        # Enhanced logging setup
        self._setup_logging()
        
        # Performance tracking
        self._performance_metrics = {
            'total_calls': 0,
            'total_processing_time': 0.0,
            'average_response_time': 0.0,
            'error_count': 0,
            'last_call_time': None
        }
        
        # Initialize agent with error handling
        try:
            self.agent = self._create_agent()
            self.log_info(f"Agent '{self.agent_name}' initialized successfully")
        except Exception as e:
            self.log_error(f"Failed to initialize agent '{self.agent_name}': {e}")
            raise AgentInitializationError(f"Agent initialization failed: {e}", {"agent_name": self.agent_name})
    
    def _setup_logging(self) -> None:
        """Set up enhanced logging for the agent."""
        self._logger = logging.getLogger(f"{self.__class__.__name__}")
        
        # Set log level from constants
        log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
        self._logger.setLevel(log_level)
        
        # Create formatter if not already set
        if not self._logger.handlers:
            formatter = logging.Formatter(LOG_FORMAT)
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
    
    def _create_llm(self) -> LLM:
        """
        Create the LLM instance for the agent with error handling.
        
        Returns:
            LLM: Configured LLM instance
            
        Raises:
            LLMConnectionError: If LLM creation fails
        """
        try:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise LLMConnectionError("ANTHROPIC_API_KEY not found in environment variables")
            
            llm = LLM(
                model=ANTHROPIC_MODEL,
                api_key=api_key
            )
            
            self.log_info(f"LLM created successfully with model: {ANTHROPIC_MODEL}")
            return llm
            
        except Exception as e:
            self.log_error(f"Failed to create LLM: {e}")
            raise LLMConnectionError(f"LLM creation failed: {e}")
    
    @abstractmethod
    def _create_agent(self) -> Agent:
        """
        Create the CrewAI agent instance.
        
        This method must be implemented by subclasses to define
        the specific agent configuration.
        
        Returns:
            Agent: Configured CrewAI agent
        """
        pass
    
    def get_agent(self) -> Agent:
        """
        Get the CrewAI agent instance.
        
        Returns:
            Agent: The configured agent
        """
        return self.agent
    
    def get_tools(self) -> List:
        """
        Get the tools available to this agent.
        
        Returns:
            List: List of tool functions
        """
        return self.agent.tools if hasattr(self.agent, 'tools') else []
    
    def get_role(self) -> str:
        """
        Get the agent's role description.
        
        Returns:
            str: Agent role
        """
        return self.agent.role if hasattr(self.agent, 'role') else "Unknown"
    
    def get_goal(self) -> str:
        """
        Get the agent's goal description.
        
        Returns:
            str: Agent goal
        """
        return self.agent.goal if hasattr(self.agent, 'goal') else "Unknown"
    
    def get_backstory(self) -> str:
        """
        Get the agent's backstory description.
        
        Returns:
            str: Agent backstory
        """
        return self.agent.backstory if hasattr(self.agent, 'backstory') else "Unknown"
    
    def log_info(self, message: str) -> None:
        """
        Log an info message with the agent's context.
        
        Args:
            message: Message to log
        """
        self._logger.info(f"[{self.agent_name}] {message}")
    
    def log_error(self, message: str, error: Optional[Exception] = None) -> None:
        """
        Log an error message with the agent's context.
        
        Args:
            message: Error message
            error: Optional exception object
        """
        if error:
            self._logger.error(f"[{self.agent_name}] {message}: {error}")
        else:
            self._logger.error(f"[{self.agent_name}] {message}")
    
    def log_warning(self, message: str) -> None:
        """
        Log a warning message with the agent's context.
        
        Args:
            message: Warning message
        """
        self._logger.warning(f"[{self.agent_name}] {message}")
    
    def log_debug(self, message: str) -> None:
        """
        Log a debug message with the agent's context.
        
        Args:
            message: Debug message
        """
        self._logger.debug(f"[{self.agent_name}] {message}")
    
    def validate_input(self, data: Dict[str, Any], required_fields: List[str]) -> bool:
        """
        Validate input data against required fields.
        
        Args:
            data: Input data to validate
            required_fields: List of required field names
            
        Returns:
            bool: True if validation passes, False otherwise
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                error_msg = f"Missing required fields: {missing_fields}"
                self.log_error(error_msg)
                raise ValidationError(error_msg, {"missing_fields": missing_fields})
            
            self.log_debug(f"Input validation passed for fields: {required_fields}")
            return True
            
        except Exception as e:
            if not isinstance(e, ValidationError):
                raise ValidationError(f"Validation failed: {e}")
            raise
    
    def safe_get(self, data: Dict[str, Any], key: str, default: Any = None) -> Any:
        """
        Safely get a value from a dictionary with logging.
        
        Args:
            data: Dictionary to search
            key: Key to look for
            default: Default value if key not found
            
        Returns:
            Any: Value or default
        """
        value = data.get(key, default)
        if key not in data:
            self.log_warning(f"Key '{key}' not found, using default: {default}")
        return value
    
    def track_performance(self, func_name: str, start_time: float) -> None:
        """
        Track performance metrics for agent operations.
        
        Args:
            func_name: Name of the function being tracked
            start_time: Start time of the operation
        """
        processing_time = time.time() - start_time
        
        self._performance_metrics['total_calls'] += 1
        self._performance_metrics['total_processing_time'] += processing_time
        self._performance_metrics['average_response_time'] = (
            self._performance_metrics['total_processing_time'] / 
            self._performance_metrics['total_calls']
        )
        self._performance_metrics['last_call_time'] = datetime.now()
        
        self.log_debug(f"Performance tracked: {func_name} took {processing_time:.3f}s")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for the agent.
        
        Returns:
            Dict[str, Any]: Performance metrics
        """
        return self._performance_metrics.copy()
    
    def reset_performance_metrics(self) -> None:
        """Reset performance metrics."""
        self._performance_metrics = {
            'total_calls': 0,
            'total_processing_time': 0.0,
            'average_response_time': 0.0,
            'error_count': 0,
            'last_call_time': None
        }
        self.log_info("Performance metrics reset")
    
    def validate_agent_configuration(self) -> bool:
        """
        Validate that the agent is properly configured.
        
        Returns:
            bool: True if configuration is valid
        """
        try:
            # Check if agent exists
            if not hasattr(self, 'agent') or self.agent is None:
                raise ValidationError("Agent not properly initialized")
            
            # Check if agent has required attributes
            required_attrs = ['role', 'goal']
            for attr in required_attrs:
                if not hasattr(self.agent, attr):
                    self.log_warning(f"Agent missing attribute: {attr}")
            
            # Check if tools are available
            tools = self.get_tools()
            if not tools:
                self.log_warning("Agent has no tools configured")
            
            self.log_info("Agent configuration validation passed")
            return True
            
        except Exception as e:
            self.log_error(f"Agent configuration validation failed: {e}")
            return False
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get comprehensive information about the agent.
        
        Returns:
            Dict[str, Any]: Agent information
        """
        return {
            'agent_name': self.agent_name,
            'class_name': self.__class__.__name__,
            'llm_provider': self.llm_provider,
            'role': self.get_role(),
            'goal': self.get_goal(),
            'backstory': self.get_backstory(),
            'tools_count': len(self.get_tools()),
            'performance_metrics': self.get_performance_metrics(),
            'is_configured': self.validate_agent_configuration()
        }
    
    def __str__(self) -> str:
        """String representation of the agent."""
        return f"{self.__class__.__name__}(name='{self.agent_name}', role='{self.get_role()}')"
    
    def __repr__(self) -> str:
        """Detailed string representation of the agent."""
        return f"{self.__class__.__name__}(name='{self.agent_name}', llm_provider='{self.llm_provider}')"

"""
Agent factory for creating and managing financial recommendation agents.

Provides a centralized way to create and configure agents
with proper error handling and validation.
"""

from typing import Dict, Any, Optional, Type
from enum import Enum

from src.agents.base_agent import BaseAgent
from src.agents.market_data_agent import MarketDataAgent
from src.agents.risk_analysis_agent import RiskAnalysisAgent
from src.agents.recommendation_agent import RecommendationAgent
from src.agents.compliance_agent import ComplianceAgent
from src.agents.report_writer_agent import ReportWriterAgent
from src.agents.memory_agent import MemoryAgent
from src.agents.supervisor_agent import SupervisorAgent
from src.exceptions import AgentInitializationError, ConfigurationError
import logging

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Enumeration of available agent types."""
    MARKET_DATA = "market_data"
    RISK_ANALYSIS = "risk_analysis"
    RECOMMENDATION = "recommendation"
    COMPLIANCE = "compliance"
    REPORT_WRITER = "report_writer"
    MEMORY = "memory"
    SUPERVISOR = "supervisor"


class AgentFactory:
    """
    Factory class for creating and managing financial recommendation agents.
    
    Provides centralized agent creation with proper error handling,
    configuration validation, and dependency management.
    """
    
    # Registry of available agents
    _agent_registry: Dict[AgentType, Type[BaseAgent]] = {
        AgentType.MARKET_DATA: MarketDataAgent,
        AgentType.RISK_ANALYSIS: RiskAnalysisAgent,
        AgentType.RECOMMENDATION: RecommendationAgent,
        AgentType.COMPLIANCE: ComplianceAgent,
        AgentType.REPORT_WRITER: ReportWriterAgent,
        AgentType.MEMORY: MemoryAgent,
        AgentType.SUPERVISOR: SupervisorAgent,
    }
    
    @classmethod
    def create_agent(cls, agent_type: AgentType, **kwargs) -> BaseAgent:
        """
        Create an agent of the specified type.
        
        Args:
            agent_type: Type of agent to create
            **kwargs: Additional configuration parameters
            
        Returns:
            BaseAgent: Configured agent instance
            
        Raises:
            AgentInitializationError: If agent creation fails
            ConfigurationError: If configuration is invalid
        """
        try:
            if agent_type not in cls._agent_registry:
                raise ConfigurationError(f"Unknown agent type: {agent_type}")
            
            agent_class = cls._agent_registry[agent_type]
            
            # Handle different constructor signatures
            if agent_type == AgentType.MARKET_DATA:
                # Enhanced MarketDataAgent requires llm_provider
                llm_provider = kwargs.get('llm_provider', 'anthropic')
                agent = agent_class(llm_provider=llm_provider)
                logger.info(f"Created enhanced {agent_type.value} agent with performance tracking")
            elif agent_type == AgentType.RISK_ANALYSIS:
                # RiskAnalysisAgent requires llm_provider
                llm_provider = kwargs.get('llm_provider', 'anthropic')
                agent = agent_class(llm_provider=llm_provider)
            elif agent_type == AgentType.RECOMMENDATION:
                # RecommendationAgent requires llm_provider
                llm_provider = kwargs.get('llm_provider', 'anthropic')
                agent = agent_class(llm_provider=llm_provider)
            elif agent_type == AgentType.COMPLIANCE:
                # ComplianceAgent requires llm_provider
                llm_provider = kwargs.get('llm_provider', 'anthropic')
                agent = agent_class(llm_provider=llm_provider)
            elif agent_type == AgentType.REPORT_WRITER:
                # ReportWriterAgent requires llm_provider
                llm_provider = kwargs.get('llm_provider', 'anthropic')
                agent = agent_class(llm_provider=llm_provider)
            elif agent_type == AgentType.MEMORY:
                # MemoryAgent requires llm_provider
                llm_provider = kwargs.get('llm_provider', 'anthropic')
                agent = agent_class(llm_provider=llm_provider)
            elif agent_type == AgentType.SUPERVISOR:
                # SupervisorAgent requires llm_provider
                llm_provider = kwargs.get('llm_provider', 'anthropic')
                agent = agent_class(llm_provider=llm_provider)
            else:
                # Default case
                agent = agent_class(**kwargs)
            
            return agent
            
        except Exception as e:
            raise AgentInitializationError(
                f"Failed to create agent {agent_type.value}: {str(e)}",
                details={"agent_type": agent_type.value, "error": str(e)}
            )
    
    @classmethod
    def create_all_agents(cls, **kwargs) -> Dict[AgentType, BaseAgent]:
        """
        Create all available agents.
        
        Args:
            **kwargs: Configuration parameters to pass to all agents
            
        Returns:
            Dict[AgentType, BaseAgent]: Dictionary of all created agents
            
        Raises:
            AgentInitializationError: If any agent creation fails
        """
        agents = {}
        failed_agents = []
        
        for agent_type in AgentType:
            try:
                agents[agent_type] = cls.create_agent(agent_type, **kwargs)
            except Exception as e:
                failed_agents.append((agent_type, str(e)))
        
        if failed_agents:
            error_details = {agent_type.value: error for agent_type, error in failed_agents}
            raise AgentInitializationError(
                f"Failed to create {len(failed_agents)} agents",
                details={"failed_agents": error_details}
            )
        
        return agents
    
    @classmethod
    def get_available_agent_types(cls) -> list:
        """
        Get list of available agent types.
        
        Returns:
            list: List of available agent types
        """
        return list(AgentType)
    
    @classmethod
    def register_agent(cls, agent_type: AgentType, agent_class: Type[BaseAgent]) -> None:
        """
        Register a new agent type.
        
        Args:
            agent_type: New agent type to register
            agent_class: Agent class to register
            
        Raises:
            ConfigurationError: If agent_type already exists
        """
        if agent_type in cls._agent_registry:
            raise ConfigurationError(f"Agent type {agent_type.value} already registered")
        
        cls._agent_registry[agent_type] = agent_class
    
    @classmethod
    def validate_agent_config(cls, agent_type: AgentType, config: Dict[str, Any]) -> bool:
        """
        Validate agent configuration.
        
        Args:
            agent_type: Type of agent to validate
            config: Configuration to validate
            
        Returns:
            bool: True if configuration is valid
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        if agent_type not in cls._agent_registry:
            raise ConfigurationError(f"Unknown agent type: {agent_type}")
        
        # Basic validation - can be extended per agent type
        required_fields = ["llm_provider"]  # Add more as needed
        
        missing_fields = [field for field in required_fields if field not in config]
        if missing_fields:
            raise ConfigurationError(f"Missing required fields: {missing_fields}")
        
        return True
    
    @classmethod
    def get_agent_info(cls, agent_type: AgentType) -> Dict[str, Any]:
        """
        Get information about an agent type.
        
        Args:
            agent_type: Type of agent to get info for
            
        Returns:
            Dict[str, Any]: Agent information
        """
        if agent_type not in cls._agent_registry:
            return {"error": f"Unknown agent type: {agent_type}"}
        
        agent_class = cls._agent_registry[agent_type]
        
        return {
            "name": agent_type.value,
            "class": agent_class.__name__,
            "module": agent_class.__module__,
            "description": getattr(agent_class, "__doc__", "No description available"),
            "available": True
        }
    
    @classmethod
    def get_all_agent_info(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all available agents.
        
        Returns:
            Dict[str, Dict[str, Any]]: Information about all agents
        """
        return {
            agent_type.value: cls.get_agent_info(agent_type)
            for agent_type in AgentType
        }

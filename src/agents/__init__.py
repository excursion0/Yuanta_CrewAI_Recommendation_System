"""
Financial recommendation agents using CrewAI.

This module contains specialized agents for different aspects of financial
recommendation and analysis, orchestrated by CrewAI.
"""

from .market_data_agent import MarketDataAgent
from .risk_analysis_agent import RiskAnalysisAgent
from .recommendation_agent import RecommendationAgent
from .compliance_agent import ComplianceAgent
from .report_writer_agent import ReportWriterAgent
from .memory_agent import MemoryAgent
from .supervisor_agent import SupervisorAgent

__all__ = [
    "MarketDataAgent",
    "RiskAnalysisAgent", 
    "RecommendationAgent",
    "ComplianceAgent",
    "ReportWriterAgent",
    "MemoryAgent",
    "SupervisorAgent"
]

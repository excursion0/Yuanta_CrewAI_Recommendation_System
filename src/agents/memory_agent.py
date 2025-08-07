"""
Memory Agent for financial product recommendation system.

This agent is responsible for storing and retrieving past user interactions
and scenarios for improved recommendations.
"""

from crewai import Agent, LLM
from crewai.tools import tool
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class MemoryAgent:
    """Agent responsible for conversation memory and history"""
    
    def __init__(self, llm_provider):
        self.llm_provider = llm_provider
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create the memory agent"""
        # Create CrewAI LLM instance
        crewai_llm = LLM(model="claude-3-5-sonnet-20241022")
        
        return Agent(
            role="Memory Agent",
            goal="Store and retrieve user interaction history",
            backstory="You are a memory agent who maintains user interaction records and preferences.",
            verbose=True,
            allow_delegation=False,
            llm=crewai_llm,
            tools=[
                self._store_interaction,
                self._retrieve_user_history,
                self._analyze_preferences,
                self._get_context_summary
            ]
        )
    
    @tool
    def _store_interaction(self, user_id: str, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store user interaction in memory"""
        try:
            # Mock interaction storage
            stored_data = {
                "user_id": user_id,
                "timestamp": "2025-08-05T20:00:00Z",
                "interaction_type": interaction_data.get("type", "query"),
                "query": interaction_data.get("query", ""),
                "response": interaction_data.get("response", ""),
                "recommendations": interaction_data.get("recommendations", []),
                "user_feedback": interaction_data.get("feedback", ""),
                "context": interaction_data.get("context", {})
            }
            
            logger.info(f"Stored interaction for user {user_id}")
            
            return {
                "success": True,
                "stored_data": stored_data,
                "user_id": user_id
            }
        except Exception as e:
            logger.error(f"Error storing interaction: {e}")
            return {
                "success": False,
                "error": str(e),
                "user_id": user_id,
                "interaction_data": interaction_data
            }
    
    @tool
    def _retrieve_user_history(self, user_id: str) -> Dict[str, Any]:
        """Retrieve user interaction history"""
        try:
            # Mock user history
            history = {
                "user_id": user_id,
                "total_interactions": 5,
                "last_interaction": "2025-08-05T19:45:00Z",
                "interactions": [
                    {
                        "timestamp": "2025-08-05T19:45:00Z",
                        "query": "I want to invest for retirement",
                        "recommendations": ["Yuanta Balanced Fund", "Yuanta Conservative Fund"],
                        "feedback": "positive"
                    },
                    {
                        "timestamp": "2025-08-05T19:30:00Z",
                        "query": "What are the best low-risk options?",
                        "recommendations": ["Yuanta Conservative Fund"],
                        "feedback": "positive"
                    }
                ],
                "preferences": {
                    "risk_level": "medium",
                    "investment_goals": ["retirement", "income"],
                    "preferred_products": ["mutual_funds", "bonds"]
                }
            }
            
            logger.info(f"Retrieved history for user {user_id}")
            
            return {
                "success": True,
                "history": history,
                "user_id": user_id
            }
        except Exception as e:
            logger.error(f"Error retrieving user history: {e}")
            return {
                "success": False,
                "error": str(e),
                "user_id": user_id
            }
    
    @tool
    def _analyze_preferences(self, user_history: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user preferences from history"""
        try:
            interactions = user_history.get("interactions", [])
            
            # Analyze preferences
            preferences = {
                "risk_tolerance": "medium",
                "investment_goals": [],
                "preferred_products": [],
                "interaction_patterns": [],
                "feedback_sentiment": "positive"
            }
            
            # Extract preferences from interactions
            for interaction in interactions:
                query = interaction.get("query", "").lower()
                recommendations = interaction.get("recommendations", [])
                feedback = interaction.get("feedback", "")
                
                # Analyze risk tolerance
                if "low risk" in query or "conservative" in query:
                    preferences["risk_tolerance"] = "low"
                elif "high risk" in query or "aggressive" in query:
                    preferences["risk_tolerance"] = "high"
                
                # Analyze investment goals
                if "retirement" in query:
                    preferences["investment_goals"].append("retirement")
                if "income" in query:
                    preferences["investment_goals"].append("income")
                if "growth" in query:
                    preferences["investment_goals"].append("growth")
                
                # Analyze preferred products
                for rec in recommendations:
                    if "fund" in rec.lower():
                        preferences["preferred_products"].append("mutual_funds")
                    elif "etf" in rec.lower():
                        preferences["preferred_products"].append("etfs")
                    elif "bond" in rec.lower():
                        preferences["preferred_products"].append("bonds")
            
            # Remove duplicates
            preferences["investment_goals"] = list(set(preferences["investment_goals"]))
            preferences["preferred_products"] = list(set(preferences["preferred_products"]))
            
            logger.info(f"Analyzed preferences for user")
            
            return {
                "success": True,
                "preferences": preferences,
                "user_history": user_history
            }
        except Exception as e:
            logger.error(f"Error analyzing preferences: {e}")
            return {
                "success": False,
                "error": str(e),
                "user_history": user_history
            }
    
    @tool
    def _get_context_summary(self, user_id: str) -> Dict[str, Any]:
        """Get context summary for user"""
        try:
            # Mock context summary
            context_summary = {
                "user_id": user_id,
                "session_count": 3,
                "total_interactions": 15,
                "average_session_length": 5,
                "last_session_date": "2025-08-05",
                "key_topics": [
                    "retirement planning",
                    "risk assessment",
                    "portfolio diversification"
                ],
                "recent_recommendations": [
                    "Yuanta Balanced Fund",
                    "Yuanta Conservative Fund",
                    "Yuanta ETF Index Fund"
                ],
                "user_satisfaction": "high",
                "preferred_communication_style": "detailed",
                "investment_knowledge_level": "intermediate"
            }
            
            logger.info(f"Generated context summary for user {user_id}")
            
            return {
                "success": True,
                "context_summary": context_summary,
                "user_id": user_id
            }
        except Exception as e:
            logger.error(f"Error getting context summary: {e}")
            return {
                "success": False,
                "error": str(e),
                "user_id": user_id
            }
    
    def get_agent(self) -> Agent:
        """Get the CrewAI agent"""
        return self.agent 
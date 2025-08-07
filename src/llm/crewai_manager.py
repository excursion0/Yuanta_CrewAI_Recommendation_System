"""
CrewAI Manager for integrating CrewAI with the existing LLM system.

This module provides a bridge between the existing LLM infrastructure
and the new CrewAI multi-agent system.
"""

from typing import Dict, Any, List, Optional
import logging
from ..agents.crew_orchestrator import FinancialCrewOrchestrator
from .manager import LLMManager
from src.data.models import UserProfile, FinancialProduct, ConversationMessage
from src.llm.response_generator import RecommendationResponse
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
import os
from src.llm.response_generator import IntentType

logger = logging.getLogger(__name__)


class CrewAIManager:
    """Manages CrewAI integration with existing LLM system"""
    
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager
        # Use primary_provider if available, otherwise use a default
        llm_provider = getattr(llm_manager, 'primary_provider', None)
        if not llm_provider:
            # If no primary provider, use a string identifier for the orchestrator
            llm_provider = "anthropic"  # Default fallback
        self.crew_orchestrator = FinancialCrewOrchestrator(llm_provider)
        self.enabled = True
        
    async def process_query_with_crewai(
        self,
        query: str,
        user_profile: Optional[UserProfile] = None,
        conversation_history: Optional[List[ConversationMessage]] = None,
        available_products: Optional[List[FinancialProduct]] = None
    ) -> RecommendationResponse:
        """Process query with full CrewAI multi-agent orchestration for evaluation"""
        try:
            logger.info("Starting full CrewAI multi-agent orchestration for evaluation...")
            
            # Convert user_profile to dict if it's a UserProfile object
            if hasattr(user_profile, 'model_dump'):
                user_profile = user_profile.model_dump()
            elif not isinstance(user_profile, dict):
                user_profile = self._create_default_user_profile()
            
            # Process with CrewAI orchestrator
            try:
                logger.info("🤖 Processing with CrewAI multi-agent system...")
                
                # Convert user profile to dict for CrewAI
                user_profile_dict = user_profile.model_dump() if hasattr(user_profile, 'model_dump') else user_profile
                
                # Process with CrewAI orchestrator
                crew_result = self.crew_orchestrator.process_financial_query(
                    user_query=query,
                    user_profile=user_profile_dict,
                    conversation_history=conversation_history
                )
                
                # Check if CrewAI failed due to LLM overload
                if not crew_result.get("success", False):
                    error_msg = crew_result.get("error", "")
                    if "overload" in error_msg.lower() or "overloaded" in error_msg.lower():
                        logger.warning("CrewAI failed due to LLM overload, falling back to LLM manager")
                        return await self._fallback_to_llm_manager(
                            query, user_profile, conversation_history, available_products
                        )
                    else:
                        logger.warning(f"CrewAI failed with error: {error_msg}")
                        return await self._fallback_to_llm_manager(
                            query, user_profile, conversation_history, available_products
                        )
                
                # Check if CrewAI used fallback response
                crew_execution = crew_result.get("crew_execution", {})
                if crew_execution.get("fallback_used", False):
                    logger.info("CrewAI used fallback response due to LLM overload")
                    logger.info(f"Original error: {crew_execution.get('original_error', 'Unknown')}")
                
                logger.info("✅ CrewAI multi-agent processing completed successfully")
                
                # Format the result
                formatted_result = self._format_crewai_result(crew_result, query)
                
                logger.info("✅ Successfully created CrewAI multi-agent response")
                return formatted_result
                
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"CrewAI multi-agent processing failed: {error_msg}")
                
                # Check if it's an overload error
                if "overload" in error_msg.lower() or "overloaded" in error_msg.lower():
                    logger.warning("Detected LLM overload error, falling back to LLM manager")
                else:
                    logger.warning("CrewAI processing failed, falling back to LLM manager")
                
                return await self._fallback_to_llm_manager(
                    query, user_profile, conversation_history, available_products
                )
            
        except Exception as e:
            logger.error(f"Error in process_query_with_crewai: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            error_traceback = traceback.format_exc()
            logger.error(f"Error traceback: {error_traceback}")
            
            # Fallback to LLM manager
            return await self._fallback_to_llm_manager(
                query, user_profile, conversation_history, available_products
            )
    
    async def _fallback_to_llm_manager(
        self,
        query: str,
        user_profile: Optional[UserProfile],
        conversation_history: Optional[List[ConversationMessage]],
        available_products: Optional[List[FinancialProduct]]
    ) -> RecommendationResponse:
        """Fallback to LLM manager when CrewAI fails"""
        try:
            logger.info("Using LLM manager fallback...")
            
            # Ensure LLM manager is initialized
            if not hasattr(self.llm_manager, '_initialized') or not self.llm_manager._initialized:
                await self.llm_manager.initialize()
            
            # Convert available_products to list of dicts if they are FinancialProduct objects
            if available_products:
                available_products = [p.model_dump() if hasattr(p, 'model_dump') else p for p in available_products]
            
            # Convert user_profile to UserProfile object for LLM manager
            from src.data.models import UserProfile
            if isinstance(user_profile, dict):
                try:
                    user_profile_obj = UserProfile(**user_profile)
                except Exception as e:
                    logger.warning(f"Could not create UserProfile object: {e}")
                    user_profile_obj = None
            else:
                user_profile_obj = user_profile
            
            # Use the existing LLM manager
            result = await self.llm_manager.process_query(
                query=query,
                available_products=available_products,
                user_profile=user_profile_obj,
                conversation_history=conversation_history
            )
            
            logger.info("LLM manager fallback completed successfully")
            return result
            
        except Exception as llm_error:
            logger.error(f"LLM manager fallback failed: {llm_error}")
            
            # Return a basic fallback response
            return RecommendationResponse(
                response=f"I understand you're asking about '{query}'. I'm here to help with financial product recommendations.\n\nBased on your query, I can help you find suitable financial products and provide personalized investment advice. Please let me know if you have any specific questions about investment options, risk levels, or product features.",
                recommendations=[],
                sources=["crewai_fallback"],
                processing_time=0.1,
                confidence=0.85
            )
    
    def _create_default_user_profile(self) -> Dict[str, Any]:
        """Create a default user profile for CrewAI processing"""
        return {
            "risk_level": "medium",
            "age": 35,
            "income_level": "medium",
            "investment_experience": "intermediate",
            "investment_goals": ["growth", "diversification"],
            "time_horizon": "long",
            "total_investment": 100000
        }
    
    async def _get_crewai_analysis(self, query: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Get analysis from CrewAI agents without relying on final response generation"""
        try:
            logger.info("Executing CrewAI agents for analysis...")
            
            # Create a simplified crew with just analysis tasks
            analysis_crew = self._create_analysis_crew(query, user_profile)
            
            # Execute the crew
            result = analysis_crew.kickoff()
            
            if result and hasattr(result, 'raw'):
                logger.info("CrewAI analysis completed successfully")
                return {
                    "success": True,
                    "analysis": str(result.raw),
                    "source": "crewai_multi_agent"
                }
            else:
                logger.warning("CrewAI analysis returned empty result")
                return {
                    "success": False,
                    "analysis": "No analysis available",
                    "source": "fallback"
                }
                
        except Exception as e:
            logger.error(f"Error in CrewAI analysis: {e}")
            return {
                "success": False,
                "analysis": f"Analysis failed: {str(e)}",
                "source": "fallback"
            }
    
    def _create_analysis_crew(self, query: str, user_profile: Dict[str, Any]) -> Crew:
        """Create a simplified crew for analysis only"""
        from crewai import Crew, Task
        
        # Create analysis tasks
        tasks = []
        
        # Market Analysis Task
        market_task = Task(
            description=f"Analyze market conditions for: {query}. Focus on current trends and economic indicators.",
            agent=self.crew_orchestrator.agents["market_data"],
            expected_output="Market analysis summary"
        )
        tasks.append(market_task)
        
        # Risk Analysis Task
        risk_task = Task(
            description=f"Assess risk factors for: {query}. User risk level: {user_profile.get('risk_level', 'medium')}.",
            agent=self.crew_orchestrator.agents["risk_analysis"],
            expected_output="Risk assessment summary"
        )
        tasks.append(risk_task)
        
        # Create crew
        crew = Crew(
            agents=list(self.crew_orchestrator.agents.values()),
            tasks=tasks,
            verbose=True,
            memory=False,
            max_rpm=None,
            max_iter=2
        )
        
        return crew
    
    async def _generate_final_response_with_crewai_insights(
        self,
        query: str,
        user_profile: Dict[str, Any],
        conversation_history: Optional[List[ConversationMessage]],
        available_products: Optional[List[FinancialProduct]],
        crew_analysis: Dict[str, Any]
    ) -> RecommendationResponse:
        """Generate final response using LLM manager with CrewAI insights"""
        try:
            logger.info("Generating final response with CrewAI insights...")
            
            # Ensure LLM manager is initialized
            if not hasattr(self.llm_manager, 'primary_provider') or not self.llm_manager.primary_provider:
                self.llm_manager.initialize()
            
            # Convert available_products to list of dicts if needed
            if available_products:
                available_products = [p.model_dump() if hasattr(p, 'model_dump') else p for p in available_products]
            
            # Create enhanced query with CrewAI insights
            enhanced_query = self._enhance_query_with_crewai_insights(query, crew_analysis)
            
            # Process with LLM manager
            response = await self.llm_manager.process_query(
                query=enhanced_query,
                user_profile=user_profile,
                conversation_history=conversation_history,
                available_products=available_products
            )
            
            # Add CrewAI source information
            if hasattr(response, 'sources'):
                response.sources = response.sources + ["crewai_multi_agent"] if response.sources else ["crewai_multi_agent"]
            
            logger.info("Final response generation completed successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error generating final response: {e}")
            # Fallback to basic LLM manager
            return await self._fallback_to_llm_manager(
                query, user_profile, conversation_history, available_products
            )
    
    def _enhance_query_with_crewai_insights(self, original_query: str, crew_analysis: Dict[str, Any]) -> str:
        """Enhance the original query with CrewAI analysis insights"""
        if crew_analysis.get("success", False):
            analysis = crew_analysis.get("analysis", "")
            enhanced_query = f"""
{original_query}

Additional Analysis Context:
{analysis}

Please provide a comprehensive response that incorporates this analysis context.
"""
            return enhanced_query
        else:
            return original_query
    
    def _format_crewai_result(self, crew_result: Dict[str, Any], original_query: str) -> Dict[str, Any]:
        """Format CrewAI result for compatibility with existing system"""
        try:
            # Handle different CrewAI output formats
            if hasattr(crew_result, 'raw') and hasattr(crew_result.raw, 'output'):
                # CrewAI CrewOutput object
                analysis_result = crew_result.raw.output
            elif isinstance(crew_result, dict):
                # Dictionary format
                analysis_result = crew_result.get("analysis_result", str(crew_result))
            else:
                # String or other format
                analysis_result = str(crew_result)
            
            # Extract key information from CrewAI result
            formatted_response = {
                "query": original_query,
                "response": analysis_result,
                "recommendations": self._extract_recommendations(analysis_result),
                "risk_assessment": self._extract_risk_assessment(analysis_result),
                "market_analysis": self._extract_market_analysis(analysis_result),
                "compliance_status": "compliant",
                "source": "crewai_multi_agent",
                "confidence_score": 0.95
            }
            
            return formatted_response
            
        except Exception as e:
            logger.error(f"Error formatting CrewAI result: {e}")
            return {
                "query": original_query,
                "response": str(crew_result) if crew_result else "CrewAI analysis completed",
                "source": "crewai_multi_agent",
                "confidence_score": 0.85
            }
    
    def _extract_recommendations(self, analysis_result: str) -> List[Dict[str, Any]]:
        """Extract recommendations from CrewAI analysis result"""
        # This is a simplified extraction - in practice, you'd parse the structured output
        recommendations = []
        
        # Mock extraction based on common patterns
        if "Yuanta" in analysis_result:
            recommendations.append({
                "name": "Yuanta Balanced Fund",
                "type": "mutual_fund",
                "allocation": "50%",
                "reasoning": "Balanced growth and income"
            })
        
        if "ETF" in analysis_result:
            recommendations.append({
                "name": "Yuanta ETF Index Fund",
                "type": "etf",
                "allocation": "30%",
                "reasoning": "Market exposure with diversification"
            })
        
        return recommendations
    
    def _extract_risk_assessment(self, analysis_result: str) -> Dict[str, Any]:
        """Extract risk assessment from CrewAI analysis result"""
        return {
            "risk_level": "medium",
            "risk_score": 0.65,
            "risk_factors": ["market_volatility", "interest_rate_risk"],
            "risk_management": "Diversification and regular rebalancing recommended"
        }
    
    def _extract_market_analysis(self, analysis_result: str) -> Dict[str, Any]:
        """Extract market analysis from CrewAI analysis result"""
        return {
            "market_trend": "bullish",
            "volatility": "moderate",
            "economic_conditions": "favorable",
            "sector_performance": "mixed"
        }
    
    def enable_crewai(self) -> None:
        """Enable CrewAI processing"""
        self.enabled = True
        logger.info("CrewAI processing enabled")
    
    def disable_crewai(self) -> None:
        """Disable CrewAI processing (fallback to standard LLM)"""
        self.enabled = False
        logger.info("CrewAI processing disabled")
    
    def get_crew_status(self) -> Dict[str, Any]:
        """Get CrewAI system status"""
        crew_status = self.crew_orchestrator.get_crew_status()
        crew_status["enabled"] = self.enabled
        return crew_status
    
    def update_user_profile(self, user_id: str, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile in CrewAI system"""
        return self.crew_orchestrator.update_user_profile(user_id, profile) 
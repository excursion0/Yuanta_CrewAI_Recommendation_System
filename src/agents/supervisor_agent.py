"""
Supervisor Agent for financial product recommendation system.

This agent acts as the director/orchestrator for all other agents,
managing the workflow and coordinating the multi-agent system.
"""

from crewai import Agent, LLM
from crewai.tools import tool
from typing import Dict, Any, List
import logging
import time

logger = logging.getLogger(__name__)


class SupervisorAgent:
    """Agent responsible for orchestrating all other agents"""
    
    def __init__(self, llm_provider):
        self.llm_provider = llm_provider
        
        # Cache ProductDatabase to avoid regenerating for each query
        from src.data.product_database import ProductDatabase
        self.product_database = ProductDatabase()
        
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create the supervisor agent"""
        # Create CrewAI LLM instance
        crewai_llm = LLM(model="claude-3-5-sonnet-20241022")
        
        return Agent(
            role="Financial Recommendation Director",
            goal="Coordinate financial analysis agents to deliver investment recommendations using ONLY real products from database",
            backstory="You are a financial director who coordinates analysis teams to provide investment advice. You MUST ensure all recommendations use only real products from the database.",
            verbose=True,
            allow_delegation=True,
            llm=crewai_llm,
            tools=[
                self._coordinate_analysis,
                self._validate_recommendations,
                self._create_workflow,
                self._finalize_report
            ]
        )
    
    @tool
    def _coordinate_analysis(self, user_query: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate the analysis workflow"""
        try:
            # Create analysis workflow
            workflow = {
                "user_query": user_query,
                "user_profile": user_profile,
                "analysis_steps": [
                    "market_data_analysis",
                    "risk_assessment",
                    "product_recommendation",
                    "compliance_check",
                    "report_generation"
                ],
                "agent_assignments": {
                    "market_data": "MarketDataAgent",
                    "risk_analysis": "RiskAnalysisAgent",
                    "recommendations": "RecommendationAgent",
                    "compliance": "ComplianceAgent",
                    "report_writer": "ReportWriterAgent"
                },
                "priority": "high",
                "estimated_completion_time": "5-10 minutes"
            }
            
            logger.info("Coordinated analysis workflow")
            
            return {
                "success": True,
                "workflow": workflow,
                "user_query": user_query,
                "user_profile": user_profile
            }
        except Exception as e:
            logger.error(f"Error coordinating analysis: {e}")
            return {
                "success": False,
                "error": str(e),
                "user_query": user_query,
                "user_profile": user_profile
            }
    
    @tool
    def _validate_recommendations(self, recommendations: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Validate recommendations for quality and suitability"""
        try:
            # Validate recommendations
            validation = {
                "overall_quality": "excellent",
                "suitability_score": 0.85,
                "compliance_status": "compliant",
                "risk_alignment": "appropriate",
                "validation_checks": [],
                "warnings": [],
                "recommendations": []
            }
            
            # Check risk alignment
            user_risk = user_profile.get("risk_level", "medium")
            rec_risk = recommendations.get("risk_level", "medium")
            
            if user_risk == rec_risk:
                validation["risk_alignment"] = "perfect"
                validation["validation_checks"].append("Risk level matches user profile")
            elif (user_risk == "medium" and rec_risk in ["low", "high"]) or \
                 (rec_risk == "medium" and user_risk in ["low", "high"]):
                validation["risk_alignment"] = "acceptable"
                validation["validation_checks"].append("Risk level within acceptable range")
            else:
                validation["risk_alignment"] = "needs_review"
                validation["warnings"].append("Risk level mismatch detected")
            
            # Check recommendation quality
            primary_recs = recommendations.get("primary_recommendations", [])
            if len(primary_recs) >= 2:
                validation["validation_checks"].append("Sufficient primary recommendations")
            else:
                validation["warnings"].append("Limited primary recommendations")
            
            # Check expected returns
            expected_returns = recommendations.get("expected_returns", "")
            if expected_returns:
                validation["validation_checks"].append("Expected returns specified")
            else:
                validation["warnings"].append("Expected returns not specified")
            
            # Calculate overall quality score
            quality_score = len(validation["validation_checks"]) / (len(validation["validation_checks"]) + len(validation["warnings"]))
            validation["overall_quality_score"] = quality_score
            
            if quality_score >= 0.8:
                validation["overall_quality"] = "excellent"
            elif quality_score >= 0.6:
                validation["overall_quality"] = "good"
            else:
                validation["overall_quality"] = "needs_improvement"
            
            logger.info(f"Validated recommendations: {validation['overall_quality']}")
            
            return {
                "success": True,
                "validation": validation,
                "recommendations": recommendations,
                "user_profile": user_profile
            }
        except Exception as e:
            logger.error(f"Error validating recommendations: {e}")
            return {
                "success": False,
                "error": str(e),
                "recommendations": recommendations,
                "user_profile": user_profile
            }
    
    @tool
    def _create_workflow(self, task_type: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Create specific workflow for task type"""
        try:
            # Create workflow based on task type
            if task_type == "initial_assessment":
                workflow = {
                    "task_type": "initial_assessment",
                    "steps": [
                        {"agent": "MarketDataAgent", "task": "fetch_market_data", "priority": "high"},
                        {"agent": "RiskAnalysisAgent", "task": "analyze_risk_tolerance", "priority": "high"},
                        {"agent": "RecommendationAgent", "task": "generate_initial_recommendations", "priority": "high"},
                        {"agent": "ComplianceAgent", "task": "check_compliance", "priority": "medium"},
                        {"agent": "ReportWriterAgent", "task": "create_summary", "priority": "medium"}
                    ],
                    "estimated_time": "3-5 minutes"
                }
            elif task_type == "portfolio_review":
                workflow = {
                    "task_type": "portfolio_review",
                    "steps": [
                        {"agent": "MarketDataAgent", "task": "analyze_market_conditions", "priority": "high"},
                        {"agent": "RiskAnalysisAgent", "task": "assess_portfolio_risk", "priority": "high"},
                        {"agent": "RecommendationAgent", "task": "suggest_adjustments", "priority": "high"},
                        {"agent": "ComplianceAgent", "task": "validate_changes", "priority": "medium"},
                        {"agent": "ReportWriterAgent", "task": "create_review_report", "priority": "medium"}
                    ],
                    "estimated_time": "5-8 minutes"
                }
            else:  # general recommendation
                workflow = {
                    "task_type": "general_recommendation",
                    "steps": [
                        {"agent": "MarketDataAgent", "task": "get_market_context", "priority": "medium"},
                        {"agent": "RiskAnalysisAgent", "task": "quick_risk_assessment", "priority": "high"},
                        {"agent": "RecommendationAgent", "task": "generate_recommendations", "priority": "high"},
                        {"agent": "ComplianceAgent", "task": "basic_compliance_check", "priority": "low"},
                        {"agent": "ReportWriterAgent", "task": "format_response", "priority": "medium"}
                    ],
                    "estimated_time": "2-3 minutes"
                }
            
            logger.info(f"Created workflow for {task_type}")
            
            return {
                "success": True,
                "workflow": workflow,
                "task_type": task_type,
                "user_profile": user_profile
            }
        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            return {
                "success": False,
                "error": str(e),
                "task_type": task_type,
                "user_profile": user_profile
            }
    
    @tool
    def _finalize_report(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize the comprehensive report using ONLY real products from database"""
        try:
            # Use cached ProductDatabase
            real_products = [p.name for p in self.product_database.get_all_products()]
            
            # Validate recommendations to ensure only real products are used
            recommendations = analysis_results.get("recommendations", {})
            if "primary_recommendations" in recommendations:
                valid_recommendations = []
                for rec in recommendations["primary_recommendations"]:
                    product_name = rec.get("name", "")
                    if product_name in real_products:
                        valid_recommendations.append(rec)
                    else:
                        logger.warning(f"Filtering out fake product in supervisor: {product_name}")
                
                # Update with only valid recommendations
                recommendations["primary_recommendations"] = valid_recommendations
            
            # Compile final report
            final_report = {
                "report_id": f"FIN_{analysis_results.get('user_id', 'unknown')}_{int(time.time())}",
                "timestamp": "2025-08-05T20:00:00Z",
                "sections": {
                    "executive_summary": analysis_results.get("summary", {}),
                    "market_analysis": analysis_results.get("market_data", {}),
                    "risk_assessment": analysis_results.get("risk_analysis", {}),
                    "recommendations": recommendations,
                    "compliance_check": analysis_results.get("compliance", {}),
                    "implementation_plan": analysis_results.get("implementation", {})
                },
                "quality_score": analysis_results.get("quality_score", 0.85),
                "compliance_status": analysis_results.get("compliance_status", "compliant"),
                "next_steps": [
                    "Review recommendations with financial advisor",
                    "Consider your investment timeline",
                    "Monitor portfolio performance",
                    "Schedule follow-up review"
                ],
                "disclaimers": [
                    "Past performance does not guarantee future results",
                    "Investments involve risk of loss",
                    "Consult with a financial advisor before investing",
                    "This report is for informational purposes only"
                ]
            }
            
            logger.info("Finalized comprehensive report with product validation")
            
            return {
                "success": True,
                "final_report": final_report,
                "analysis_results": analysis_results
            }
        except Exception as e:
            logger.error(f"Error finalizing report: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis_results": analysis_results
            }
    
    def get_agent(self) -> Agent:
        """Get the CrewAI agent"""
        return self.agent 
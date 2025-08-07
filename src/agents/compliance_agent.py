"""
Enhanced Compliance Agent for financial product recommendation system.

This agent is responsible for comprehensive regulatory compliance screening,
suitability validation, and disclosure management using advanced rule-based systems.
"""

from crewai import Agent, LLM
from crewai.tools import tool
from typing import Dict, Any, List, Optional
import logging
import os

# Import the new compliance systems
from src.compliance.compliance_rules_engine import ComplianceRulesEngine, ComplianceResult
from src.compliance.suitability_validation_engine import SuitabilityValidationEngine, SuitabilityAssessment
from src.compliance.disclosure_management_system import DisclosureManagementSystem, DisclosureAssessment

logger = logging.getLogger(__name__)


class ComplianceAgent:
    """Enhanced agent responsible for comprehensive regulatory compliance screening"""
    
    def __init__(self, llm_provider):
        self.llm_provider = llm_provider
        
        # Initialize the comprehensive compliance systems
        self.compliance_engine = ComplianceRulesEngine()
        self.suitability_engine = SuitabilityValidationEngine()
        self.disclosure_system = DisclosureManagementSystem()
        
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create the enhanced compliance agent"""
        # Create CrewAI LLM instance with direct Anthropic configuration
        crewai_llm = LLM(
            model="claude-3-5-sonnet-20241022",
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        
        # Create properly decorated tool functions
        @tool
        def check_regulatory_compliance(recommendation: Dict[str, Any]) -> Dict[str, Any]:
            """Perform comprehensive regulatory compliance check using rule-based engine"""
            return self._check_regulatory_compliance(recommendation)
        
        @tool
        def validate_suitability(recommendation: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
            """Validate suitability using advanced suitability validation engine"""
            return self._validate_suitability(recommendation, user_profile)
        
        @tool
        def review_disclosures(content: str, product_type: str = "general") -> Dict[str, Any]:
            """Review required disclosures using automated disclosure management system"""
            return self._review_disclosures(content, product_type)
        
        return Agent(
            role="Financial Compliance Specialist",
            goal="Ensure comprehensive regulatory compliance and suitability validation",
            backstory="You are an expert compliance specialist who ensures financial recommendations meet all regulatory standards including SEC, FINRA, and suitability requirements.",
            verbose=True,
            allow_delegation=False,
            llm=crewai_llm,
            tools=[
                check_regulatory_compliance,
                validate_suitability,
                review_disclosures
            ]
        )
    
    def _check_regulatory_compliance(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive regulatory compliance check using rule-based engine"""
        try:
            # Use the compliance rules engine for comprehensive checking
            compliance_result = self.compliance_engine.check_compliance(recommendation)
            
            # Get compliance summary
            summary = self.compliance_engine.get_compliance_summary(compliance_result)
            
            logger.info(f"Compliance check completed: {compliance_result.overall_compliance.value} ({compliance_result.compliance_score:.1f}%)")
            
            return {
                "success": True,
                "compliance_status": {
                    "overall_compliance": compliance_result.overall_compliance.value,
                    "compliance_score": compliance_result.compliance_score,
                    "checks_passed": len(compliance_result.checks_passed),
                    "checks_failed": len(compliance_result.checks_failed),
                    "warnings": compliance_result.warnings,
                    "violations": compliance_result.violations,
                    "recommendations": compliance_result.recommendations
                },
                "audit_trail": compliance_result.audit_trail,
                "recommendation": recommendation
            }
            
        except Exception as e:
            logger.error(f"Error in regulatory compliance check: {e}")
            return {
                "success": False,
                "error": str(e),
                "compliance_status": {
                    "overall_compliance": "non_compliant",
                    "compliance_score": 0.0,
                    "checks_passed": 0,
                    "checks_failed": 0,
                    "warnings": [f"Compliance check error: {str(e)}"],
                    "violations": ["Compliance check failed"],
                    "recommendations": ["Review compliance system"]
                },
                "recommendation": recommendation
            }
    
    def _validate_suitability(self, recommendation: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Validate suitability using advanced suitability validation engine"""
        try:
            # Use the suitability validation engine for comprehensive assessment
            suitability_result = self.suitability_engine.validate_suitability(recommendation, user_profile)
            
            # Get suitability summary
            summary = self.suitability_engine.get_suitability_summary(suitability_result)
            
            logger.info(f"Suitability validation completed: {suitability_result.overall_suitability.value} ({suitability_result.suitability_score:.1f}%)")
            
            return {
                "success": True,
                "suitability_status": {
                    "overall_suitability": suitability_result.overall_suitability.value,
                    "suitability_score": suitability_result.suitability_score,
                    "risk_alignment": suitability_result.risk_alignment,
                    "goal_alignment": suitability_result.goal_alignment,
                    "horizon_alignment": suitability_result.horizon_alignment,
                    "amount_suitability": suitability_result.amount_suitability,
                    "warnings": suitability_result.warnings,
                    "recommendations": suitability_result.recommendations
                },
                "audit_trail": suitability_result.audit_trail,
                "user_profile": user_profile,
                "recommendation": recommendation
            }
            
        except Exception as e:
            logger.error(f"Error in suitability validation: {e}")
            return {
                "success": False,
                "error": str(e),
                "suitability_status": {
                    "overall_suitability": "unsuitable",
                    "suitability_score": 0.0,
                    "risk_alignment": 0.0,
                    "goal_alignment": 0.0,
                    "horizon_alignment": 0.0,
                    "amount_suitability": 0.0,
                    "warnings": [f"Suitability validation error: {str(e)}"],
                    "recommendations": ["Review suitability assessment"]
                },
                "user_profile": user_profile,
                "recommendation": recommendation
            }
    
    def _review_disclosures(self, content: str, product_type: str = "general") -> Dict[str, Any]:
        """Review required disclosures using automated disclosure management system"""
        try:
            # Use the disclosure management system for comprehensive disclosure checking
            disclosure_result = self.disclosure_system.check_disclosures(content, product_type)
            
            # Get disclosure summary
            summary = self.disclosure_system.get_disclosure_summary(disclosure_result)
            
            logger.info(f"Disclosure review completed: {disclosure_result.overall_status.value} ({disclosure_result.compliance_score:.1f}%)")
            
            return {
                "success": True,
                "disclosure_status": {
                    "overall_status": disclosure_result.overall_status.value,
                    "compliance_score": disclosure_result.compliance_score,
                    "found_disclosures": disclosure_result.found_disclosures,
                    "missing_disclosures": disclosure_result.missing_disclosures,
                    "warnings": disclosure_result.warnings,
                    "recommendations": disclosure_result.recommendations
                },
                "audit_trail": disclosure_result.audit_trail,
                "content": content,
                "product_type": product_type
            }
            
        except Exception as e:
            logger.error(f"Error in disclosure review: {e}")
            return {
                "success": False,
                "error": str(e),
                "disclosure_status": {
                    "overall_status": "non_compliant",
                    "compliance_score": 0.0,
                    "found_disclosures": [],
                    "missing_disclosures": ["All disclosures"],
                    "warnings": [f"Disclosure review error: {str(e)}"],
                    "recommendations": ["Review disclosure system"]
                },
                "content": content,
                "product_type": product_type
            }
    
    def perform_comprehensive_compliance_check(self, recommendation: Dict[str, Any], user_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform comprehensive compliance check including regulatory, suitability, and disclosure validation"""
        try:
            results = {}
            
            # 1. Regulatory Compliance Check
            regulatory_result = self._check_regulatory_compliance(recommendation)
            results["regulatory_compliance"] = regulatory_result
            
            # 2. Suitability Validation (if user profile provided)
            if user_profile:
                suitability_result = self._validate_suitability(recommendation, user_profile)
                results["suitability_validation"] = suitability_result
            else:
                results["suitability_validation"] = {
                    "success": False,
                    "error": "No user profile provided for suitability validation"
                }
            
            # 3. Disclosure Review
            content = recommendation.get("content", "")
            disclosure_result = self._review_disclosures(content, recommendation.get("product_type", "general"))
            results["disclosure_review"] = disclosure_result
            
            # 4. Overall Assessment
            overall_success = all(result.get("success", False) for result in results.values())
            
            # Calculate overall compliance score
            regulatory_score = regulatory_result.get("compliance_status", {}).get("compliance_score", 0.0)
            suitability_score = suitability_result.get("suitability_status", {}).get("suitability_score", 0.0) if user_profile else 100.0
            disclosure_score = disclosure_result.get("disclosure_status", {}).get("compliance_score", 0.0)
            
            overall_score = (regulatory_score + suitability_score + disclosure_score) / 3
            
            # Determine overall compliance level
            if overall_score >= 90.0:
                overall_compliance = "compliant"
            elif overall_score >= 70.0:
                overall_compliance = "needs_review"
            else:
                overall_compliance = "non_compliant"
            
            logger.info(f"Comprehensive compliance check completed: {overall_compliance} ({overall_score:.1f}%)")
            
            return {
                "success": overall_success,
                "overall_compliance": overall_compliance,
                "overall_score": overall_score,
                "detailed_results": results,
                "summary": {
                    "regulatory_compliance": regulatory_score,
                    "suitability_validation": suitability_score if user_profile else "N/A",
                    "disclosure_review": disclosure_score,
                    "overall_compliance": overall_compliance
                }
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive compliance check: {e}")
            return {
                "success": False,
                "error": str(e),
                "overall_compliance": "non_compliant",
                "overall_score": 0.0,
                "detailed_results": {},
                "summary": {
                    "error": str(e)
                }
            }
    
    def get_agent(self) -> Agent:
        """Get the CrewAI agent instance"""
        return self.agent 
#!/usr/bin/env python3
"""
Disclosure Management System for Financial Product Recommendations

This module provides automated disclosure requirement checking, template generation,
and compliance tracking for financial product recommendations.
"""

import logging
import re
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class DisclosureType(Enum):
    """Types of required disclosures"""
    RISK_DISCLOSURE = "risk_disclosure"
    PAST_PERFORMANCE = "past_performance"
    FEE_DISCLOSURE = "fee_disclosure"
    INVESTMENT_OBJECTIVES = "investment_objectives"
    REGULATORY_DISCLAIMER = "regulatory_disclaimer"
    CONFLICT_OF_INTEREST = "conflict_of_interest"
    LIQUIDITY_RISK = "liquidity_risk"
    VOLATILITY_DISCLOSURE = "volatility_disclosure"
    TAX_IMPLICATIONS = "tax_implications"
    REDEMPTION_TERMS = "redemption_terms"


class DisclosureStatus(Enum):
    """Disclosure compliance status"""
    COMPLIANT = "compliant"
    PARTIAL = "partial"
    NON_COMPLIANT = "non_compliant"
    MISSING = "missing"


@dataclass
class DisclosureRequirement:
    """Individual disclosure requirement"""
    disclosure_id: str
    disclosure_type: DisclosureType
    name: str
    description: str
    required: bool
    severity: str  # "low", "medium", "high", "critical"
    keywords: List[str]
    template: str
    regulatory_basis: str


@dataclass
class DisclosureCheck:
    """Result of a disclosure check"""
    disclosure_id: str
    disclosure_name: str
    status: DisclosureStatus
    found_keywords: List[str]
    missing_keywords: List[str]
    coverage_score: float  # 0.0 to 1.0
    reasoning: str
    template_suggestion: str


@dataclass
class DisclosureAssessment:
    """Comprehensive disclosure assessment result"""
    overall_status: DisclosureStatus
    compliance_score: float  # 0.0 to 100.0
    disclosure_checks: List[DisclosureCheck]
    found_disclosures: List[str]
    missing_disclosures: List[str]
    warnings: List[str]
    recommendations: List[str]
    audit_trail: Dict[str, Any]


class DisclosureManagementSystem:
    """Automated disclosure management system"""
    
    def __init__(self):
        self.disclosure_requirements = self._initialize_disclosure_requirements()
        self.disclosure_templates = self._initialize_disclosure_templates()
        self.regulatory_framework = self._initialize_regulatory_framework()
        logger.info(f"Initialized disclosure management system with {len(self.disclosure_requirements)} requirements")
    
    def _initialize_disclosure_requirements(self) -> Dict[str, DisclosureRequirement]:
        """Initialize disclosure requirements"""
        requirements = {}
        
        # Risk Disclosure
        requirements["risk_disclosure"] = DisclosureRequirement(
            disclosure_id="risk_disclosure",
            disclosure_type=DisclosureType.RISK_DISCLOSURE,
            name="Risk Disclosure",
            description="Comprehensive disclosure of investment risks",
            required=True,
            severity="high",
            keywords=["risk", "disclosure", "warning", "volatility", "potential loss", "market risk", "investment risk"],
            template="Investment involves risk, including the potential loss of principal. Past performance does not guarantee future results.",
            regulatory_basis="SEC Rule 10b-5, FINRA Rule 2111"
        )
        
        # Past Performance
        requirements["past_performance"] = DisclosureRequirement(
            disclosure_id="past_performance",
            disclosure_type=DisclosureType.PAST_PERFORMANCE,
            name="Past Performance Disclaimer",
            description="Disclaimer about past performance not guaranteeing future results",
            required=True,
            severity="medium",
            keywords=["past performance", "historical returns", "previous results", "disclaimer", "future results"],
            template="Past performance does not guarantee future results. Investment returns and principal value will fluctuate.",
            regulatory_basis="SEC Rule 156, FINRA Rule 2210"
        )
        
        # Fee Disclosure
        requirements["fee_disclosure"] = DisclosureRequirement(
            disclosure_id="fee_disclosure",
            disclosure_type=DisclosureType.FEE_DISCLOSURE,
            name="Fee and Expense Disclosure",
            description="Clear disclosure of all fees and expenses",
            required=True,
            severity="high",
            keywords=["fees", "expenses", "expense ratio", "management fee", "transaction cost", "sales charge", "load"],
            template="This investment involves fees and expenses that will reduce returns. Please review the prospectus for complete fee information.",
            regulatory_basis="SEC Rule 498, FINRA Rule 2210"
        )
        
        # Investment Objectives
        requirements["investment_objectives"] = DisclosureRequirement(
            disclosure_id="investment_objectives",
            disclosure_type=DisclosureType.INVESTMENT_OBJECTIVES,
            name="Investment Objectives",
            description="Clear statement of investment objectives and strategy",
            required=True,
            severity="medium",
            keywords=["investment objectives", "investment goals", "investment strategy", "investment purpose", "fund objective"],
            template="This fund seeks to achieve its investment objective through [specific strategy]. Investment objectives may not be met.",
            regulatory_basis="SEC Rule 498, FINRA Rule 2210"
        )
        
        # Regulatory Disclaimer
        requirements["regulatory_disclaimer"] = DisclosureRequirement(
            disclosure_id="regulatory_disclaimer",
            disclosure_type=DisclosureType.REGULATORY_DISCLAIMER,
            name="Regulatory Disclaimer",
            description="Standard regulatory disclaimers and notices",
            required=True,
            severity="medium",
            keywords=["regulatory", "disclaimer", "compliance", "legal", "regulatory notice", "securities"],
            template="This material is for informational purposes only and does not constitute investment advice or a recommendation.",
            regulatory_basis="SEC Rule 10b-5, FINRA Rule 2210"
        )
        
        # Conflict of Interest
        requirements["conflict_of_interest"] = DisclosureRequirement(
            disclosure_id="conflict_of_interest",
            disclosure_type=DisclosureType.CONFLICT_OF_INTEREST,
            name="Conflict of Interest Disclosure",
            description="Disclosure of potential conflicts of interest",
            required=False,
            severity="medium",
            keywords=["conflict of interest", "compensation", "commission", "affiliate", "related party"],
            template="We may receive compensation in connection with this recommendation. Please review our conflicts of interest disclosure.",
            regulatory_basis="FINRA Rule 2111, SEC Rule 10b-5"
        )
        
        # Liquidity Risk
        requirements["liquidity_risk"] = DisclosureRequirement(
            disclosure_id="liquidity_risk",
            disclosure_type=DisclosureType.LIQUIDITY_RISK,
            name="Liquidity Risk Disclosure",
            description="Disclosure of liquidity risks for illiquid investments",
            required=False,
            severity="medium",
            keywords=["liquidity", "illiquid", "redemption", "trading volume", "market risk", "liquidity risk"],
            template="This investment may be illiquid and difficult to sell. Liquidity may be limited during market stress.",
            regulatory_basis="SEC Rule 498, FINRA Rule 2111"
        )
        
        # Volatility Disclosure
        requirements["volatility_disclosure"] = DisclosureRequirement(
            disclosure_id="volatility_disclosure",
            disclosure_type=DisclosureType.VOLATILITY_DISCLOSURE,
            name="Volatility Disclosure",
            description="Disclosure of investment volatility and price fluctuations",
            required=False,
            severity="low",
            keywords=["volatility", "standard deviation", "risk measure", "price fluctuation", "volatile"],
            template="This investment may experience significant price volatility. Values may fluctuate substantially.",
            regulatory_basis="SEC Rule 498, FINRA Rule 2210"
        )
        
        # Tax Implications
        requirements["tax_implications"] = DisclosureRequirement(
            disclosure_id="tax_implications",
            disclosure_type=DisclosureType.TAX_IMPLICATIONS,
            name="Tax Implications Disclosure",
            description="Disclosure of potential tax implications",
            required=False,
            severity="low",
            keywords=["tax", "taxation", "tax implications", "tax consequences", "tax treatment"],
            template="Investment returns may have tax implications. Consult a tax advisor regarding your specific situation.",
            regulatory_basis="SEC Rule 498"
        )
        
        # Redemption Terms
        requirements["redemption_terms"] = DisclosureRequirement(
            disclosure_id="redemption_terms",
            disclosure_type=DisclosureType.REDEMPTION_TERMS,
            name="Redemption Terms Disclosure",
            description="Disclosure of redemption terms and restrictions",
            required=False,
            severity="medium",
            keywords=["redemption", "redemption terms", "redemption restrictions", "withdrawal", "exit"],
            template="Redemption may be subject to restrictions and fees. Please review the prospectus for complete terms.",
            regulatory_basis="SEC Rule 498, FINRA Rule 2111"
        )
        
        return requirements
    
    def _initialize_disclosure_templates(self) -> Dict[str, str]:
        """Initialize disclosure templates"""
        return {
            "comprehensive_risk": """
INVESTMENT RISK DISCLOSURE

This investment involves risk, including the potential loss of principal. Investment returns and principal value will fluctuate. Past performance does not guarantee future results. This material is for informational purposes only and does not constitute investment advice or a recommendation.

Key Risks:
• Market Risk: Investment value may decline due to market conditions
• Volatility Risk: Investment may experience significant price fluctuations
• Liquidity Risk: Investment may be difficult to sell in certain market conditions
• Credit Risk: Issuer may default on obligations
• Interest Rate Risk: Bond values may decline when interest rates rise

Please review the prospectus for complete risk information before investing.
            """,
            
            "fee_disclosure": """
FEE AND EXPENSE DISCLOSURE

This investment involves fees and expenses that will reduce returns. Please review the prospectus for complete fee information.

Typical Fees:
• Management Fee: Annual fee for portfolio management
• Expense Ratio: Ongoing fund operating expenses
• Transaction Costs: Costs associated with buying/selling securities
• Sales Charges: One-time fees for fund purchases (if applicable)

All fees reduce investment returns. Higher fees do not guarantee better performance.
            """,
            
            "regulatory_notice": """
REGULATORY NOTICE

This material is for informational purposes only and does not constitute investment advice or a recommendation to buy, sell, or hold any security. Investment decisions should be based on your individual circumstances and objectives.

Regulatory Compliance:
• SEC Registered Investment Advisor
• FINRA Member Firm
• Compliance with applicable securities laws
• Conflicts of interest disclosure available upon request

For complete information, please review the prospectus and consult with your financial advisor.
            """,
            
            "suitability_notice": """
SUITABILITY NOTICE

This recommendation is based on your individual profile and circumstances. Investment suitability depends on:
• Risk tolerance and investment objectives
• Time horizon and liquidity needs
• Financial situation and tax considerations
• Investment experience and knowledge

Please ensure this investment aligns with your goals and risk tolerance before proceeding.
            """
        }
    
    def _initialize_regulatory_framework(self) -> Dict[str, Any]:
        """Initialize regulatory framework for disclosures"""
        return {
            "sec_requirements": {
                "mandatory_disclosures": [
                    "risk_disclosure",
                    "past_performance",
                    "fee_disclosure",
                    "investment_objectives"
                ],
                "conditional_disclosures": [
                    "conflict_of_interest",
                    "liquidity_risk",
                    "redemption_terms"
                ]
            },
            "finra_requirements": {
                "mandatory_disclosures": [
                    "risk_disclosure",
                    "regulatory_disclaimer"
                ],
                "suitability_disclosures": [
                    "investment_objectives",
                    "conflict_of_interest"
                ]
            },
            "compliance_thresholds": {
                "mandatory_compliance": 100.0,  # All mandatory disclosures required
                "overall_compliance": 80.0,     # 80% overall compliance required
                "critical_missing": 0,          # No critical disclosures can be missing
                "high_missing": 1              # Max 1 high severity disclosure missing
            }
        }
    
    def check_disclosures(self, content: str, product_type: str = "general") -> DisclosureAssessment:
        """Perform comprehensive disclosure check"""
        try:
            disclosure_checks = []
            found_disclosures = []
            missing_disclosures = []
            warnings = []
            recommendations = []
            
            # Check each disclosure requirement
            for req_id, requirement in self.disclosure_requirements.items():
                check_result = self._check_disclosure_requirement(requirement, content, product_type)
                disclosure_checks.append(check_result)
                
                if check_result.status == DisclosureStatus.COMPLIANT:
                    found_disclosures.append(requirement.name)
                elif check_result.status == DisclosureStatus.PARTIAL:
                    found_disclosures.append(f"{requirement.name} (Partial)")
                    warnings.append(f"Partial disclosure: {requirement.name}")
                else:
                    missing_disclosures.append(requirement.name)
                    if requirement.required:
                        warnings.append(f"Missing required disclosure: {requirement.name}")
                    else:
                        warnings.append(f"Missing recommended disclosure: {requirement.name}")
                
                # Generate recommendations for missing or partial disclosures
                if check_result.status != DisclosureStatus.COMPLIANT:
                    recommendations.append(f"Add {requirement.name}: {check_result.template_suggestion}")
            
            # Calculate compliance score
            mandatory_requirements = [req for req in self.disclosure_requirements.values() if req.required]
            mandatory_checks = [check for check in disclosure_checks if any(req.disclosure_id == check.disclosure_id for req in mandatory_requirements)]
            
            if mandatory_checks:
                mandatory_score = sum(check.coverage_score for check in mandatory_checks) / len(mandatory_checks) * 100
            else:
                mandatory_score = 100.0
            
            overall_score = sum(check.coverage_score for check in disclosure_checks) / len(disclosure_checks) * 100 if disclosure_checks else 0
            
            # Determine overall status
            overall_status = self._determine_disclosure_status(disclosure_checks, overall_score, mandatory_score)
            
            # Create audit trail
            audit_trail = {
                "timestamp": datetime.now().isoformat(),
                "content_length": len(content),
                "product_type": product_type,
                "total_requirements": len(self.disclosure_requirements),
                "mandatory_requirements": len(mandatory_requirements),
                "found_disclosures": len(found_disclosures),
                "missing_disclosures": len(missing_disclosures),
                "overall_score": overall_score,
                "mandatory_score": mandatory_score,
                "overall_status": overall_status.value
            }
            
            logger.info(f"Disclosure check completed: {overall_status.value} ({overall_score:.1f}%)")
            
            return DisclosureAssessment(
                overall_status=overall_status,
                compliance_score=overall_score,
                disclosure_checks=disclosure_checks,
                found_disclosures=found_disclosures,
                missing_disclosures=missing_disclosures,
                warnings=warnings,
                recommendations=recommendations,
                audit_trail=audit_trail
            )
            
        except Exception as e:
            logger.error(f"Error in disclosure check: {e}")
            return DisclosureAssessment(
                overall_status=DisclosureStatus.NON_COMPLIANT,
                compliance_score=0.0,
                disclosure_checks=[],
                found_disclosures=[],
                missing_disclosures=list(self.disclosure_requirements.keys()),
                warnings=[f"Disclosure check error: {str(e)}"],
                recommendations=["Review disclosure system"],
                audit_trail={"error": str(e)}
            )
    
    def _check_disclosure_requirement(self, requirement: DisclosureRequirement, content: str, product_type: str) -> DisclosureCheck:
        """Check individual disclosure requirement"""
        try:
            content_lower = content.lower()
            found_keywords = []
            missing_keywords = []
            
            # Check for required keywords
            for keyword in requirement.keywords:
                if keyword.lower() in content_lower:
                    found_keywords.append(keyword)
                else:
                    missing_keywords.append(keyword)
            
            # Calculate coverage score
            total_keywords = len(requirement.keywords)
            found_count = len(found_keywords)
            
            if total_keywords == 0:
                coverage_score = 1.0
            else:
                coverage_score = found_count / total_keywords
            
            # Determine status
            if coverage_score >= 0.8:
                status = DisclosureStatus.COMPLIANT
                reasoning = f"Comprehensive disclosure found ({found_count}/{total_keywords} keywords)"
            elif coverage_score >= 0.5:
                status = DisclosureStatus.PARTIAL
                reasoning = f"Partial disclosure found ({found_count}/{total_keywords} keywords)"
            else:
                status = DisclosureStatus.MISSING
                reasoning = f"Insufficient disclosure ({found_count}/{total_keywords} keywords)"
            
            # Generate template suggestion
            template_suggestion = self._generate_template_suggestion(requirement, found_keywords, missing_keywords)
            
            return DisclosureCheck(
                disclosure_id=requirement.disclosure_id,
                disclosure_name=requirement.name,
                status=status,
                found_keywords=found_keywords,
                missing_keywords=missing_keywords,
                coverage_score=coverage_score,
                reasoning=reasoning,
                template_suggestion=template_suggestion
            )
            
        except Exception as e:
            logger.error(f"Error checking disclosure {requirement.disclosure_id}: {e}")
            return DisclosureCheck(
                disclosure_id=requirement.disclosure_id,
                disclosure_name=requirement.name,
                status=DisclosureStatus.MISSING,
                found_keywords=[],
                missing_keywords=requirement.keywords,
                coverage_score=0.0,
                reasoning=f"Disclosure check error: {str(e)}",
                template_suggestion=requirement.template
            )
    
    def _generate_template_suggestion(self, requirement: DisclosureRequirement, found_keywords: List[str], missing_keywords: List[str]) -> str:
        """Generate template suggestion for missing disclosure"""
        if not missing_keywords:
            return "Disclosure appears complete"
        
        # Use the requirement's template as base
        template = requirement.template
        
        # Add specific suggestions for missing keywords
        if missing_keywords:
            template += f"\n\nConsider adding: {', '.join(missing_keywords)}"
        
        return template
    
    def _determine_disclosure_status(self, checks: List[DisclosureCheck], overall_score: float, mandatory_score: float) -> DisclosureStatus:
        """Determine overall disclosure status"""
        thresholds = self.regulatory_framework["compliance_thresholds"]
        
        # Check mandatory compliance
        if mandatory_score < thresholds["mandatory_compliance"]:
            return DisclosureStatus.NON_COMPLIANT
        
        # Check critical missing disclosures
        critical_missing = len([c for c in checks if c.status == DisclosureStatus.MISSING and 
                              any(req.disclosure_id == c.disclosure_id and req.severity == "critical" 
                                  for req in self.disclosure_requirements.values())])
        
        if critical_missing > thresholds["critical_missing"]:
            return DisclosureStatus.NON_COMPLIANT
        
        # Check high severity missing disclosures
        high_missing = len([c for c in checks if c.status == DisclosureStatus.MISSING and 
                           any(req.disclosure_id == c.disclosure_id and req.severity == "high" 
                               for req in self.disclosure_requirements.values())])
        
        if high_missing > thresholds["high_missing"]:
            return DisclosureStatus.NON_COMPLIANT
        
        # Check overall compliance score
        if overall_score >= thresholds["overall_compliance"]:
            return DisclosureStatus.COMPLIANT
        else:
            return DisclosureStatus.PARTIAL
    
    def generate_disclosure_template(self, disclosure_type: str, product_type: str = "general") -> str:
        """Generate disclosure template for specific type"""
        try:
            if disclosure_type in self.disclosure_templates:
                return self.disclosure_templates[disclosure_type]
            
            # Generate custom template based on disclosure requirements
            requirement = self.disclosure_requirements.get(disclosure_type)
            if requirement:
                return requirement.template
            
            return f"Standard {disclosure_type} disclosure template"
            
        except Exception as e:
            logger.error(f"Error generating disclosure template: {e}")
            return "Disclosure template generation error"
    
    def get_disclosure_summary(self, assessment: DisclosureAssessment) -> Dict[str, Any]:
        """Get a summary of disclosure assessment results"""
        return {
            "overall_status": assessment.overall_status.value,
            "compliance_score": assessment.compliance_score,
            "total_checks": len(assessment.disclosure_checks),
            "found_disclosures": len(assessment.found_disclosures),
            "missing_disclosures": len(assessment.missing_disclosures),
            "warnings": len(assessment.warnings),
            "recommendations": len(assessment.recommendations),
            "audit_trail": assessment.audit_trail
        }

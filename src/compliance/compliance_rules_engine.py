#!/usr/bin/env python3
"""
Compliance Rules Engine for Financial Product Recommendations

This module provides a comprehensive rule-based compliance checking system
for financial product recommendations, ensuring regulatory compliance with
SEC, FINRA, and other financial industry standards.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ComplianceLevel(Enum):
    """Compliance levels for recommendations"""
    COMPLIANT = "compliant"
    NEEDS_REVIEW = "needs_review"
    NON_COMPLIANT = "non_compliant"
    CRITICAL = "critical"


class RuleType(Enum):
    """Types of compliance rules"""
    DISCLOSURE = "disclosure"
    SUITABILITY = "suitability"
    REGULATORY = "regulatory"
    RISK = "risk"
    FEE = "fee"


@dataclass
class ComplianceRule:
    """Individual compliance rule definition"""
    rule_id: str
    rule_type: RuleType
    name: str
    description: str
    severity: str  # "low", "medium", "high", "critical"
    enabled: bool = True
    weight: float = 1.0  # Weight for scoring (0.0 to 1.0)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ComplianceCheck:
    """Result of a compliance check"""
    rule_id: str
    rule_name: str
    passed: bool
    score: float  # 0.0 to 1.0
    details: str
    severity: str
    weight: float


@dataclass
class ComplianceResult:
    """Overall compliance result"""
    overall_compliance: ComplianceLevel
    compliance_score: float  # 0.0 to 100.0
    checks_passed: List[ComplianceCheck]
    checks_failed: List[ComplianceCheck]
    warnings: List[str]
    violations: List[str]
    recommendations: List[str]
    audit_trail: Dict[str, Any]


class ComplianceRulesEngine:
    """Comprehensive compliance rules engine"""
    
    def __init__(self):
        self.rules = self._initialize_rules()
        self.regulatory_framework = self._initialize_regulatory_framework()
        logger.info(f"Initialized compliance engine with {len(self.rules)} rules")
    
    def _initialize_rules(self) -> Dict[str, ComplianceRule]:
        """Initialize compliance rules"""
        rules = {}
        
        # Disclosure Rules
        rules["disclosure_001"] = ComplianceRule(
            rule_id="disclosure_001",
            rule_type=RuleType.DISCLOSURE,
            name="Risk Disclosure Required",
            description="All investment recommendations must include clear risk disclosures",
            severity="high",
            weight=1.0
        )
        
        rules["disclosure_002"] = ComplianceRule(
            rule_id="disclosure_002",
            rule_type=RuleType.DISCLOSURE,
            name="Past Performance Disclaimer",
            description="Past performance disclaimers must be included",
            severity="medium",
            weight=0.8
        )
        
        rules["disclosure_003"] = ComplianceRule(
            rule_id="disclosure_003",
            rule_type=RuleType.DISCLOSURE,
            name="Fee and Expense Disclosure",
            description="All fees and expenses must be clearly disclosed",
            severity="high",
            weight=1.0
        )
        
        rules["disclosure_004"] = ComplianceRule(
            rule_id="disclosure_004",
            rule_type=RuleType.DISCLOSURE,
            name="Investment Objectives Disclosure",
            description="Investment objectives must be clearly stated",
            severity="medium",
            weight=0.7
        )
        
        rules["disclosure_005"] = ComplianceRule(
            rule_id="disclosure_005",
            rule_type=RuleType.DISCLOSURE,
            name="Regulatory Disclaimer",
            description="Regulatory disclaimers must be included",
            severity="medium",
            weight=0.6
        )
        
        # Suitability Rules
        rules["suitability_001"] = ComplianceRule(
            rule_id="suitability_001",
            rule_type=RuleType.SUITABILITY,
            name="Risk Level Alignment",
            description="Product risk level must align with user risk tolerance",
            severity="high",
            weight=1.0
        )
        
        rules["suitability_002"] = ComplianceRule(
            rule_id="suitability_002",
            rule_type=RuleType.SUITABILITY,
            name="Investment Horizon Alignment",
            description="Product time horizon must align with user investment horizon",
            severity="medium",
            weight=0.8
        )
        
        rules["suitability_003"] = ComplianceRule(
            rule_id="suitability_003",
            rule_type=RuleType.SUITABILITY,
            name="Investment Goal Alignment",
            description="Product must align with user investment goals",
            severity="high",
            weight=1.0
        )
        
        rules["suitability_004"] = ComplianceRule(
            rule_id="suitability_004",
            rule_type=RuleType.SUITABILITY,
            name="Investment Amount Suitability",
            description="Product minimum investment must be suitable for user amount",
            severity="medium",
            weight=0.7
        )
        
        # Regulatory Rules
        rules["regulatory_001"] = ComplianceRule(
            rule_id="regulatory_001",
            rule_type=RuleType.REGULATORY,
            name="SEC Compliance",
            description="Recommendations must comply with SEC regulations",
            severity="critical",
            weight=1.0
        )
        
        rules["regulatory_002"] = ComplianceRule(
            rule_id="regulatory_002",
            rule_type=RuleType.REGULATORY,
            name="FINRA Compliance",
            description="Recommendations must comply with FINRA rules",
            severity="critical",
            weight=1.0
        )
        
        rules["regulatory_003"] = ComplianceRule(
            rule_id="regulatory_003",
            rule_type=RuleType.REGULATORY,
            name="Anti-Money Laundering",
            description="Recommendations must not violate AML regulations",
            severity="critical",
            weight=1.0
        )
        
        # Risk Rules
        rules["risk_001"] = ComplianceRule(
            rule_id="risk_001",
            rule_type=RuleType.RISK,
            name="Volatility Disclosure",
            description="Product volatility must be clearly disclosed",
            severity="medium",
            weight=0.8
        )
        
        rules["risk_002"] = ComplianceRule(
            rule_id="risk_002",
            rule_type=RuleType.RISK,
            name="Liquidity Risk Disclosure",
            description="Liquidity risks must be disclosed for illiquid products",
            severity="medium",
            weight=0.7
        )
        
        # Fee Rules
        rules["fee_001"] = ComplianceRule(
            rule_id="fee_001",
            rule_type=RuleType.FEE,
            name="Expense Ratio Disclosure",
            description="Fund expense ratios must be clearly disclosed",
            severity="high",
            weight=0.9
        )
        
        rules["fee_002"] = ComplianceRule(
            rule_id="fee_002",
            rule_type=RuleType.FEE,
            name="Transaction Fee Disclosure",
            description="All transaction fees must be disclosed",
            severity="medium",
            weight=0.7
        )
        
        return rules
    
    def _initialize_regulatory_framework(self) -> Dict[str, Any]:
        """Initialize regulatory framework"""
        return {
            "sec_regulations": {
                "disclosure_requirements": [
                    "risk_disclosure",
                    "fee_disclosure", 
                    "performance_disclaimer",
                    "investment_objectives"
                ],
                "suitability_requirements": [
                    "risk_tolerance_assessment",
                    "investment_goal_alignment",
                    "time_horizon_consideration"
                ]
            },
            "finra_rules": {
                "suitability_rule": "Rule 2111",
                "disclosure_requirements": [
                    "material_information",
                    "conflicts_of_interest",
                    "compensation_disclosure"
                ]
            },
            "compliance_thresholds": {
                "critical_violations": 0,  # No critical violations allowed
                "high_violations": 1,      # Max 1 high severity violation
                "medium_violations": 3,    # Max 3 medium severity violations
                "low_violations": 5        # Max 5 low severity violations
            }
        }
    
    def check_compliance(self, recommendation: Dict[str, Any], user_profile: Optional[Dict[str, Any]] = None) -> ComplianceResult:
        """Perform comprehensive compliance check"""
        try:
            checks_passed = []
            checks_failed = []
            warnings = []
            violations = []
            recommendations = []
            
            # Perform all compliance checks
            for rule_id, rule in self.rules.items():
                if not rule.enabled:
                    continue
                
                check_result = self._perform_rule_check(rule, recommendation, user_profile)
                
                if check_result.passed:
                    checks_passed.append(check_result)
                else:
                    checks_failed.append(check_result)
                    
                    # Generate warnings and violations based on severity
                    if rule.severity == "critical":
                        violations.append(f"Critical: {rule.name} - {check_result.details}")
                    elif rule.severity == "high":
                        violations.append(f"High: {rule.name} - {check_result.details}")
                    elif rule.severity == "medium":
                        warnings.append(f"Medium: {rule.name} - {check_result.details}")
                    else:  # low
                        warnings.append(f"Low: {rule.name} - {check_result.details}")
            
            # Calculate compliance score
            total_weight = sum(rule.weight for rule in self.rules.values() if rule.enabled)
            passed_weight = sum(check.weight for check in checks_passed)
            compliance_score = (passed_weight / total_weight) * 100 if total_weight > 0 else 0
            
            # Determine overall compliance level
            overall_compliance = self._determine_compliance_level(checks_failed, compliance_score)
            
            # Generate recommendations for failed checks
            for check in checks_failed:
                recommendations.append(f"Address {check.rule_name}: {check.details}")
            
            # Create audit trail
            audit_trail = {
                "timestamp": datetime.now().isoformat(),
                "total_rules": len([r for r in self.rules.values() if r.enabled]),
                "rules_passed": len(checks_passed),
                "rules_failed": len(checks_failed),
                "compliance_score": compliance_score,
                "overall_compliance": overall_compliance.value,
                "severity_breakdown": self._get_severity_breakdown(checks_failed)
            }
            
            logger.info(f"Compliance check completed: {overall_compliance.value} ({compliance_score:.1f}%)")
            
            return ComplianceResult(
                overall_compliance=overall_compliance,
                compliance_score=compliance_score,
                checks_passed=checks_passed,
                checks_failed=checks_failed,
                warnings=warnings,
                violations=violations,
                recommendations=recommendations,
                audit_trail=audit_trail
            )
            
        except Exception as e:
            logger.error(f"Error in compliance check: {e}")
            return ComplianceResult(
                overall_compliance=ComplianceLevel.NON_COMPLIANT,
                compliance_score=0.0,
                checks_passed=[],
                checks_failed=[],
                warnings=[f"Compliance check error: {str(e)}"],
                violations=["Compliance check failed"],
                recommendations=["Review compliance system"],
                audit_trail={"error": str(e)}
            )
    
    def _perform_rule_check(self, rule: ComplianceRule, recommendation: Dict[str, Any], user_profile: Optional[Dict[str, Any]] = None) -> ComplianceCheck:
        """Perform individual rule check"""
        try:
            content = recommendation.get("content", "").lower()
            rule_type = rule.rule_type
            
            if rule_type == RuleType.DISCLOSURE:
                return self._check_disclosure_rule(rule, content)
            elif rule_type == RuleType.SUITABILITY:
                return self._check_suitability_rule(rule, recommendation, user_profile)
            elif rule_type == RuleType.REGULATORY:
                return self._check_regulatory_rule(rule, content)
            elif rule_type == RuleType.RISK:
                return self._check_risk_rule(rule, content)
            elif rule_type == RuleType.FEE:
                return self._check_fee_rule(rule, content)
            else:
                return ComplianceCheck(
                    rule_id=rule.rule_id,
                    rule_name=rule.name,
                    passed=False,
                    score=0.0,
                    details=f"Unknown rule type: {rule_type}",
                    severity=rule.severity,
                    weight=rule.weight
                )
                
        except Exception as e:
            logger.error(f"Error checking rule {rule.rule_id}: {e}")
            return ComplianceCheck(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                passed=False,
                score=0.0,
                details=f"Rule check error: {str(e)}",
                severity=rule.severity,
                weight=rule.weight
            )
    
    def _check_disclosure_rule(self, rule: ComplianceRule, content: str) -> ComplianceCheck:
        """Check disclosure-related rules"""
        if rule.rule_id == "disclosure_001":  # Risk Disclosure
            keywords = ["risk", "disclosure", "warning", "volatility", "potential loss"]
            found = any(keyword in content for keyword in keywords)
            return ComplianceCheck(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                passed=found,
                score=1.0 if found else 0.0,
                details="Risk disclosure found" if found else "Risk disclosure missing",
                severity=rule.severity,
                weight=rule.weight
            )
        
        elif rule.rule_id == "disclosure_002":  # Past Performance
            keywords = ["past performance", "historical returns", "previous results", "disclaimer"]
            found = any(keyword in content for keyword in keywords)
            return ComplianceCheck(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                passed=found,
                score=1.0 if found else 0.0,
                details="Past performance disclaimer found" if found else "Past performance disclaimer missing",
                severity=rule.severity,
                weight=rule.weight
            )
        
        elif rule.rule_id == "disclosure_003":  # Fees and Expenses
            keywords = ["fees", "expenses", "expense ratio", "management fee", "transaction cost"]
            found = any(keyword in content for keyword in keywords)
            return ComplianceCheck(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                passed=found,
                score=1.0 if found else 0.0,
                details="Fee disclosure found" if found else "Fee disclosure missing",
                severity=rule.severity,
                weight=rule.weight
            )
        
        elif rule.rule_id == "disclosure_004":  # Investment Objectives
            keywords = ["investment objectives", "investment goals", "investment strategy", "investment purpose"]
            found = any(keyword in content for keyword in keywords)
            return ComplianceCheck(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                passed=found,
                score=1.0 if found else 0.0,
                details="Investment objectives found" if found else "Investment objectives missing",
                severity=rule.severity,
                weight=rule.weight
            )
        
        elif rule.rule_id == "disclosure_005":  # Regulatory Disclaimer
            keywords = ["regulatory", "disclaimer", "compliance", "legal", "regulatory notice"]
            found = any(keyword in content for keyword in keywords)
            return ComplianceCheck(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                passed=found,
                score=1.0 if found else 0.0,
                details="Regulatory disclaimer found" if found else "Regulatory disclaimer missing",
                severity=rule.severity,
                weight=rule.weight
            )
        
        else:
            return ComplianceCheck(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                passed=False,
                score=0.0,
                details=f"Unknown disclosure rule: {rule.rule_id}",
                severity=rule.severity,
                weight=rule.weight
            )
    
    def _check_suitability_rule(self, rule: ComplianceRule, recommendation: Dict[str, Any], user_profile: Optional[Dict[str, Any]] = None) -> ComplianceCheck:
        """Check suitability-related rules"""
        if not user_profile:
            return ComplianceCheck(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                passed=False,
                score=0.0,
                details="No user profile provided for suitability check",
                severity=rule.severity,
                weight=rule.weight
            )
        
        if rule.rule_id == "suitability_001":  # Risk Level Alignment
            user_risk = user_profile.get("risk_level", "medium")
            product_risk = recommendation.get("risk_level", "medium")
            
            # Risk level compatibility matrix
            risk_compatible = {
                "low": ["low", "medium"],
                "medium": ["low", "medium", "high"],
                "high": ["medium", "high"]
            }
            
            compatible = product_risk in risk_compatible.get(user_risk, [])
            return ComplianceCheck(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                passed=compatible,
                score=1.0 if compatible else 0.0,
                details=f"Risk alignment: User {user_risk} vs Product {product_risk}" + (" ✓" if compatible else " ✗"),
                severity=rule.severity,
                weight=rule.weight
            )
        
        elif rule.rule_id == "suitability_002":  # Investment Horizon
            user_horizon = user_profile.get("time_horizon", "medium")
            product_horizon = recommendation.get("time_horizon", "medium")
            
            # Horizon compatibility matrix
            horizon_compatible = {
                "short": ["short", "medium"],
                "medium": ["short", "medium", "long"],
                "long": ["medium", "long"]
            }
            
            compatible = product_horizon in horizon_compatible.get(user_horizon, [])
            return ComplianceCheck(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                passed=compatible,
                score=1.0 if compatible else 0.0,
                details=f"Horizon alignment: User {user_horizon} vs Product {product_horizon}" + (" ✓" if compatible else " ✗"),
                severity=rule.severity,
                weight=rule.weight
            )
        
        elif rule.rule_id == "suitability_003":  # Investment Goals
            user_goals = user_profile.get("investment_goals", [])
            product_goals = recommendation.get("investment_goals", [])
            
            if not user_goals or not product_goals:
                return ComplianceCheck(
                    rule_id=rule.rule_id,
                    rule_name=rule.name,
                    passed=False,
                    score=0.0,
                    details="Missing investment goals information",
                    severity=rule.severity,
                    weight=rule.weight
                )
            
            # Check for goal alignment
            aligned_goals = set(user_goals) & set(product_goals)
            alignment_score = len(aligned_goals) / len(user_goals) if user_goals else 0.0
            
            return ComplianceCheck(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                passed=alignment_score > 0.5,
                score=alignment_score,
                details=f"Goal alignment: {len(aligned_goals)}/{len(user_goals)} goals aligned",
                severity=rule.severity,
                weight=rule.weight
            )
        
        elif rule.rule_id == "suitability_004":  # Investment Amount
            user_amount = user_profile.get("total_investment", 0)
            min_investment = recommendation.get("minimum_investment", 0)
            
            if min_investment == 0:
                return ComplianceCheck(
                    rule_id=rule.rule_id,
                    rule_name=rule.name,
                    passed=True,
                    score=1.0,
                    details="No minimum investment requirement",
                    severity=rule.severity,
                    weight=rule.weight
                )
            
            suitable = user_amount >= min_investment
            return ComplianceCheck(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                passed=suitable,
                score=1.0 if suitable else 0.0,
                details=f"Investment amount: ${user_amount:,} vs ${min_investment:,} minimum" + (" ✓" if suitable else " ✗"),
                severity=rule.severity,
                weight=rule.weight
            )
        
        else:
            return ComplianceCheck(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                passed=False,
                score=0.0,
                details=f"Unknown suitability rule: {rule.rule_id}",
                severity=rule.severity,
                weight=rule.weight
            )
    
    def _check_regulatory_rule(self, rule: ComplianceRule, content: str) -> ComplianceCheck:
        """Check regulatory-related rules"""
        # For now, assume compliance if basic disclosures are present
        has_disclosures = any(keyword in content for keyword in ["disclosure", "disclaimer", "regulatory", "compliance"])
        
        return ComplianceCheck(
            rule_id=rule.rule_id,
            rule_name=rule.name,
            passed=has_disclosures,
            score=1.0 if has_disclosures else 0.0,
            details="Regulatory compliance check" + (" ✓" if has_disclosures else " ✗"),
            severity=rule.severity,
            weight=rule.weight
        )
    
    def _check_risk_rule(self, rule: ComplianceRule, content: str) -> ComplianceCheck:
        """Check risk-related rules"""
        if rule.rule_id == "risk_001":  # Volatility Disclosure
            keywords = ["volatility", "standard deviation", "risk measure", "price fluctuation"]
            found = any(keyword in content for keyword in keywords)
            return ComplianceCheck(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                passed=found,
                score=1.0 if found else 0.0,
                details="Volatility disclosure found" if found else "Volatility disclosure missing",
                severity=rule.severity,
                weight=rule.weight
            )
        
        elif rule.rule_id == "risk_002":  # Liquidity Risk
            keywords = ["liquidity", "illiquid", "redemption", "trading volume", "market risk"]
            found = any(keyword in content for keyword in keywords)
            return ComplianceCheck(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                passed=found,
                score=1.0 if found else 0.0,
                details="Liquidity risk disclosure found" if found else "Liquidity risk disclosure missing",
                severity=rule.severity,
                weight=rule.weight
            )
        
        else:
            return ComplianceCheck(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                passed=False,
                score=0.0,
                details=f"Unknown risk rule: {rule.rule_id}",
                severity=rule.severity,
                weight=rule.weight
            )
    
    def _check_fee_rule(self, rule: ComplianceRule, content: str) -> ComplianceCheck:
        """Check fee-related rules"""
        if rule.rule_id == "fee_001":  # Expense Ratio
            keywords = ["expense ratio", "management fee", "operating expenses", "fund expenses"]
            found = any(keyword in content for keyword in keywords)
            return ComplianceCheck(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                passed=found,
                score=1.0 if found else 0.0,
                details="Expense ratio disclosure found" if found else "Expense ratio disclosure missing",
                severity=rule.severity,
                weight=rule.weight
            )
        
        elif rule.rule_id == "fee_002":  # Transaction Fees
            keywords = ["transaction fee", "commission", "trading cost", "brokerage fee", "sales charge"]
            found = any(keyword in content for keyword in keywords)
            return ComplianceCheck(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                passed=found,
                score=1.0 if found else 0.0,
                details="Transaction fee disclosure found" if found else "Transaction fee disclosure missing",
                severity=rule.severity,
                weight=rule.weight
            )
        
        else:
            return ComplianceCheck(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                passed=False,
                score=0.0,
                details=f"Unknown fee rule: {rule.rule_id}",
                severity=rule.severity,
                weight=rule.weight
            )
    
    def _determine_compliance_level(self, failed_checks: List[ComplianceCheck], compliance_score: float) -> ComplianceLevel:
        """Determine overall compliance level"""
        critical_violations = len([c for c in failed_checks if c.severity == "critical"])
        high_violations = len([c for c in failed_checks if c.severity == "high"])
        medium_violations = len([c for c in failed_checks if c.severity == "medium"])
        
        thresholds = self.regulatory_framework["compliance_thresholds"]
        
        if critical_violations > thresholds["critical_violations"]:
            return ComplianceLevel.CRITICAL
        elif high_violations > thresholds["high_violations"]:
            return ComplianceLevel.NON_COMPLIANT
        elif medium_violations > thresholds["medium_violations"]:
            return ComplianceLevel.NEEDS_REVIEW
        elif compliance_score >= 90.0:
            return ComplianceLevel.COMPLIANT
        elif compliance_score >= 70.0:
            return ComplianceLevel.NEEDS_REVIEW
        else:
            return ComplianceLevel.NON_COMPLIANT
    
    def _get_severity_breakdown(self, failed_checks: List[ComplianceCheck]) -> Dict[str, int]:
        """Get breakdown of failed checks by severity"""
        breakdown = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for check in failed_checks:
            breakdown[check.severity] += 1
        return breakdown
    
    def get_compliance_summary(self, result: ComplianceResult) -> Dict[str, Any]:
        """Get a summary of compliance results"""
        return {
            "overall_compliance": result.overall_compliance.value,
            "compliance_score": result.compliance_score,
            "total_checks": len(result.checks_passed) + len(result.checks_failed),
            "checks_passed": len(result.checks_passed),
            "checks_failed": len(result.checks_failed),
            "warnings": len(result.warnings),
            "violations": len(result.violations),
            "recommendations": len(result.recommendations),
            "audit_trail": result.audit_trail
        }

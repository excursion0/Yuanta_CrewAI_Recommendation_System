#!/usr/bin/env python3
"""
Suitability Validation Engine for Financial Product Recommendations

This module provides advanced suitability matching algorithms for validating
financial product recommendations against user profiles, ensuring appropriate
risk tolerance and investment goal alignment.
"""

import logging
import math
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class SuitabilityLevel(Enum):
    """Suitability levels for recommendations"""
    EXCELLENT = "excellent"
    GOOD = "good"
    MODERATE = "moderate"
    POOR = "poor"
    UNSUITABLE = "unsuitable"


class RiskTolerance(Enum):
    """Risk tolerance levels"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class InvestmentHorizon(Enum):
    """Investment time horizons"""
    SHORT_TERM = "short_term"  # < 3 years
    MEDIUM_TERM = "medium_term"  # 3-10 years
    LONG_TERM = "long_term"  # > 10 years


@dataclass
class SuitabilityFactor:
    """Individual suitability factor"""
    factor_id: str
    name: str
    description: str
    weight: float  # 0.0 to 1.0
    score: float  # 0.0 to 1.0
    reasoning: str
    critical: bool = False


@dataclass
class SuitabilityAssessment:
    """Comprehensive suitability assessment result"""
    overall_suitability: SuitabilityLevel
    suitability_score: float  # 0.0 to 100.0
    factors: List[SuitabilityFactor]
    risk_alignment: float  # 0.0 to 1.0
    goal_alignment: float  # 0.0 to 1.0
    horizon_alignment: float  # 0.0 to 1.0
    amount_suitability: float  # 0.0 to 1.0
    warnings: List[str]
    recommendations: List[str]
    audit_trail: Dict[str, Any]


class SuitabilityValidationEngine:
    """Advanced suitability validation engine"""
    
    def __init__(self):
        self.risk_mapping = self._initialize_risk_mapping()
        self.goal_mapping = self._initialize_goal_mapping()
        self.horizon_mapping = self._initialize_horizon_mapping()
        self.suitability_thresholds = self._initialize_suitability_thresholds()
        logger.info("Initialized suitability validation engine")
    
    def _initialize_risk_mapping(self) -> Dict[str, Dict[str, Any]]:
        """Initialize risk tolerance mapping"""
        return {
            "conservative": {
                "risk_score": 1.0,
                "volatility_tolerance": 0.1,
                "max_drawdown_tolerance": 0.05,
                "suitable_products": ["conservative", "bond", "income"],
                "unsuitable_products": ["growth", "technology", "international"]
            },
            "moderate": {
                "risk_score": 2.0,
                "volatility_tolerance": 0.15,
                "max_drawdown_tolerance": 0.10,
                "suitable_products": ["conservative", "balanced", "income", "international"],
                "unsuitable_products": ["technology"]
            },
            "aggressive": {
                "risk_score": 3.0,
                "volatility_tolerance": 0.25,
                "max_drawdown_tolerance": 0.20,
                "suitable_products": ["balanced", "growth", "international", "technology"],
                "unsuitable_products": []
            }
        }
    
    def _initialize_goal_mapping(self) -> Dict[str, Dict[str, Any]]:
        """Initialize investment goal mapping"""
        return {
            "income": {
                "priority": 1.0,
                "suitable_products": ["income", "bond", "conservative"],
                "unsuitable_products": ["growth", "technology"],
                "expected_return_range": (0.04, 0.08)
            },
            "growth": {
                "priority": 1.0,
                "suitable_products": ["growth", "balanced", "international"],
                "unsuitable_products": ["income"],
                "expected_return_range": (0.08, 0.15)
            },
            "retirement": {
                "priority": 0.9,
                "suitable_products": ["conservative", "balanced", "income"],
                "unsuitable_products": ["technology"],
                "expected_return_range": (0.06, 0.12)
            },
            "diversification": {
                "priority": 0.8,
                "suitable_products": ["international", "balanced", "etf_index"],
                "unsuitable_products": [],
                "expected_return_range": (0.07, 0.12)
            },
            "capital_preservation": {
                "priority": 0.9,
                "suitable_products": ["conservative", "bond", "income"],
                "unsuitable_products": ["growth", "technology", "international"],
                "expected_return_range": (0.04, 0.07)
            },
            "tax_efficiency": {
                "priority": 0.7,
                "suitable_products": ["etf_index", "bond"],
                "unsuitable_products": [],
                "expected_return_range": (0.06, 0.10)
            }
        }
    
    def _initialize_horizon_mapping(self) -> Dict[str, Dict[str, Any]]:
        """Initialize investment horizon mapping"""
        return {
            "short_term": {
                "years": 3,
                "suitable_products": ["conservative", "bond", "income"],
                "unsuitable_products": ["growth", "technology", "international"],
                "liquidity_requirement": "high"
            },
            "medium_term": {
                "years": 7,
                "suitable_products": ["conservative", "balanced", "income", "international"],
                "unsuitable_products": ["technology"],
                "liquidity_requirement": "medium"
            },
            "long_term": {
                "years": 15,
                "suitable_products": ["balanced", "growth", "international", "technology"],
                "unsuitable_products": [],
                "liquidity_requirement": "low"
            }
        }
    
    def _initialize_suitability_thresholds(self) -> Dict[str, float]:
        """Initialize suitability scoring thresholds"""
        return {
            "excellent": 85.0,
            "good": 70.0,
            "moderate": 50.0,
            "poor": 30.0,
            "unsuitable": 0.0
        }
    
    def validate_suitability(self, recommendation: Dict[str, Any], user_profile: Dict[str, Any]) -> SuitabilityAssessment:
        """Perform comprehensive suitability validation"""
        try:
            factors = []
            warnings = []
            recommendations = []
            
            # Assess risk alignment
            risk_factor = self._assess_risk_alignment(recommendation, user_profile)
            factors.append(risk_factor)
            
            # Assess goal alignment
            goal_factor = self._assess_goal_alignment(recommendation, user_profile)
            factors.append(goal_factor)
            
            # Assess horizon alignment
            horizon_factor = self._assess_horizon_alignment(recommendation, user_profile)
            factors.append(horizon_factor)
            
            # Assess amount suitability
            amount_factor = self._assess_amount_suitability(recommendation, user_profile)
            factors.append(amount_factor)
            
            # Calculate overall suitability score
            total_weight = sum(factor.weight for factor in factors)
            weighted_score = sum(factor.score * factor.weight for factor in factors)
            overall_score = (weighted_score / total_weight) * 100 if total_weight > 0 else 0
            
            # Determine suitability level
            suitability_level = self._determine_suitability_level(overall_score)
            
            # Generate warnings and recommendations
            for factor in factors:
                if factor.score < 0.5 and factor.critical:
                    warnings.append(f"Critical: {factor.name} - {factor.reasoning}")
                elif factor.score < 0.7:
                    warnings.append(f"Warning: {factor.name} - {factor.reasoning}")
                
                if factor.score < 0.8:
                    recommendations.append(f"Improve {factor.name}: {factor.reasoning}")
            
            # Create audit trail
            audit_trail = {
                "timestamp": datetime.now().isoformat(),
                "user_profile": user_profile,
                "recommendation": recommendation,
                "factors_assessed": len(factors),
                "overall_score": overall_score,
                "suitability_level": suitability_level.value,
                "risk_alignment": risk_factor.score,
                "goal_alignment": goal_factor.score,
                "horizon_alignment": horizon_factor.score,
                "amount_suitability": amount_factor.score
            }
            
            logger.info(f"Suitability validation completed: {suitability_level.value} ({overall_score:.1f}%)")
            
            return SuitabilityAssessment(
                overall_suitability=suitability_level,
                suitability_score=overall_score,
                factors=factors,
                risk_alignment=risk_factor.score,
                goal_alignment=goal_factor.score,
                horizon_alignment=horizon_factor.score,
                amount_suitability=amount_factor.score,
                warnings=warnings,
                recommendations=recommendations,
                audit_trail=audit_trail
            )
            
        except Exception as e:
            logger.error(f"Error in suitability validation: {e}")
            return SuitabilityAssessment(
                overall_suitability=SuitabilityLevel.UNSUITABLE,
                suitability_score=0.0,
                factors=[],
                risk_alignment=0.0,
                goal_alignment=0.0,
                horizon_alignment=0.0,
                amount_suitability=0.0,
                warnings=[f"Suitability validation error: {str(e)}"],
                recommendations=["Review suitability assessment"],
                audit_trail={"error": str(e)}
            )
    
    def _assess_risk_alignment(self, recommendation: Dict[str, Any], user_profile: Dict[str, Any]) -> SuitabilityFactor:
        """Assess risk tolerance alignment"""
        try:
            user_risk = user_profile.get("risk_level", "moderate").lower()
            product_risk = recommendation.get("risk_level", "moderate").lower()
            
            # Get risk mapping
            user_risk_mapping = self.risk_mapping.get(user_risk, self.risk_mapping["moderate"])
            user_risk_score = user_risk_mapping["risk_score"]
            
            # Map product risk to numeric score
            product_risk_scores = {"conservative": 1.0, "moderate": 2.0, "aggressive": 3.0}
            product_risk_score = product_risk_scores.get(product_risk, 2.0)
            
            # Calculate risk alignment score
            risk_difference = abs(user_risk_score - product_risk_score)
            max_difference = 2.0  # Conservative to Aggressive
            
            if risk_difference == 0:
                score = 1.0
                reasoning = "Perfect risk alignment"
            elif risk_difference == 1:
                score = 0.7
                reasoning = "Good risk alignment with minor deviation"
            elif risk_difference == 2:
                score = 0.3
                reasoning = "Poor risk alignment - significant deviation"
            else:
                score = 0.0
                reasoning = "Unacceptable risk alignment"
            
            # Check if product is in suitable/unsuitable lists
            suitable_products = user_risk_mapping["suitable_products"]
            unsuitable_products = user_risk_mapping["unsuitable_products"]
            
            product_type = recommendation.get("product_type", "").lower()
            
            if product_type in unsuitable_products:
                score *= 0.5
                reasoning += " - Product type not suitable for risk level"
            elif product_type in suitable_products:
                score = min(score * 1.2, 1.0)
                reasoning += " - Product type well-suited for risk level"
            
            return SuitabilityFactor(
                factor_id="risk_alignment",
                name="Risk Tolerance Alignment",
                description="Assesses alignment between user risk tolerance and product risk level",
                weight=1.0,
                score=score,
                reasoning=reasoning,
                critical=True
            )
            
        except Exception as e:
            logger.error(f"Error assessing risk alignment: {e}")
            return SuitabilityFactor(
                factor_id="risk_alignment",
                name="Risk Tolerance Alignment",
                description="Assesses alignment between user risk tolerance and product risk level",
                weight=1.0,
                score=0.0,
                reasoning=f"Risk alignment assessment error: {str(e)}",
                critical=True
            )
    
    def _assess_goal_alignment(self, recommendation: Dict[str, Any], user_profile: Dict[str, Any]) -> SuitabilityFactor:
        """Assess investment goal alignment"""
        try:
            user_goals = user_profile.get("investment_goals", [])
            product_goals = recommendation.get("investment_goals", [])
            
            if not user_goals:
                return SuitabilityFactor(
                    factor_id="goal_alignment",
                    name="Investment Goal Alignment",
                    description="Assesses alignment between user investment goals and product objectives",
                    weight=0.9,
                    score=0.0,
                    reasoning="No user investment goals provided",
                    critical=True
                )
            
            if not product_goals:
                return SuitabilityFactor(
                    factor_id="goal_alignment",
                    name="Investment Goal Alignment",
                    description="Assesses alignment between user investment goals and product objectives",
                    weight=0.9,
                    score=0.0,
                    reasoning="No product investment goals provided",
                    critical=True
                )
            
            # Calculate goal alignment
            aligned_goals = set(user_goals) & set(product_goals)
            total_user_goals = len(user_goals)
            
            if total_user_goals == 0:
                score = 0.0
                reasoning = "No user goals to align"
            else:
                alignment_ratio = len(aligned_goals) / total_user_goals
                
                if alignment_ratio >= 0.8:
                    score = 1.0
                    reasoning = f"Excellent goal alignment: {len(aligned_goals)}/{total_user_goals} goals matched"
                elif alignment_ratio >= 0.6:
                    score = 0.8
                    reasoning = f"Good goal alignment: {len(aligned_goals)}/{total_user_goals} goals matched"
                elif alignment_ratio >= 0.4:
                    score = 0.6
                    reasoning = f"Moderate goal alignment: {len(aligned_goals)}/{total_user_goals} goals matched"
                elif alignment_ratio >= 0.2:
                    score = 0.3
                    reasoning = f"Poor goal alignment: {len(aligned_goals)}/{total_user_goals} goals matched"
                else:
                    score = 0.0
                    reasoning = f"No goal alignment: {len(aligned_goals)}/{total_user_goals} goals matched"
            
            # Check for goal-specific suitability
            for goal in user_goals:
                goal_mapping = self.goal_mapping.get(goal, {})
                suitable_products = goal_mapping.get("suitable_products", [])
                unsuitable_products = goal_mapping.get("unsuitable_products", [])
                
                product_type = recommendation.get("product_type", "").lower()
                
                if product_type in unsuitable_products:
                    score *= 0.7
                    reasoning += f" - Product not suitable for {goal} goal"
                elif product_type in suitable_products:
                    score = min(score * 1.1, 1.0)
                    reasoning += f" - Product well-suited for {goal} goal"
            
            return SuitabilityFactor(
                factor_id="goal_alignment",
                name="Investment Goal Alignment",
                description="Assesses alignment between user investment goals and product objectives",
                weight=0.9,
                score=score,
                reasoning=reasoning,
                critical=True
            )
            
        except Exception as e:
            logger.error(f"Error assessing goal alignment: {e}")
            return SuitabilityFactor(
                factor_id="goal_alignment",
                name="Investment Goal Alignment",
                description="Assesses alignment between user investment goals and product objectives",
                weight=0.9,
                score=0.0,
                reasoning=f"Goal alignment assessment error: {str(e)}",
                critical=True
            )
    
    def _assess_horizon_alignment(self, recommendation: Dict[str, Any], user_profile: Dict[str, Any]) -> SuitabilityFactor:
        """Assess investment horizon alignment"""
        try:
            user_horizon = user_profile.get("time_horizon", "medium_term").lower()
            product_horizon = recommendation.get("time_horizon", "medium_term").lower()
            
            # Get horizon mapping
            user_horizon_mapping = self.horizon_mapping.get(user_horizon, self.horizon_mapping["medium_term"])
            product_horizon_mapping = self.horizon_mapping.get(product_horizon, self.horizon_mapping["medium_term"])
            
            user_years = user_horizon_mapping["years"]
            product_years = product_horizon_mapping["years"]
            
            # Calculate horizon alignment
            horizon_difference = abs(user_years - product_years)
            max_difference = 12  # Short-term to long-term
            
            if horizon_difference == 0:
                score = 1.0
                reasoning = "Perfect horizon alignment"
            elif horizon_difference <= 3:
                score = 0.8
                reasoning = "Good horizon alignment with minor deviation"
            elif horizon_difference <= 7:
                score = 0.6
                reasoning = "Moderate horizon alignment"
            elif horizon_difference <= 10:
                score = 0.3
                reasoning = "Poor horizon alignment"
            else:
                score = 0.0
                reasoning = "Unacceptable horizon alignment"
            
            # Check product suitability for user horizon
            suitable_products = user_horizon_mapping["suitable_products"]
            unsuitable_products = user_horizon_mapping["unsuitable_products"]
            
            product_type = recommendation.get("product_type", "").lower()
            
            if product_type in unsuitable_products:
                score *= 0.6
                reasoning += " - Product type not suitable for investment horizon"
            elif product_type in suitable_products:
                score = min(score * 1.1, 1.0)
                reasoning += " - Product type well-suited for investment horizon"
            
            return SuitabilityFactor(
                factor_id="horizon_alignment",
                name="Investment Horizon Alignment",
                description="Assesses alignment between user investment horizon and product time horizon",
                weight=0.8,
                score=score,
                reasoning=reasoning,
                critical=False
            )
            
        except Exception as e:
            logger.error(f"Error assessing horizon alignment: {e}")
            return SuitabilityFactor(
                factor_id="horizon_alignment",
                name="Investment Horizon Alignment",
                description="Assesses alignment between user investment horizon and product time horizon",
                weight=0.8,
                score=0.0,
                reasoning=f"Horizon alignment assessment error: {str(e)}",
                critical=False
            )
    
    def _assess_amount_suitability(self, recommendation: Dict[str, Any], user_profile: Dict[str, Any]) -> SuitabilityFactor:
        """Assess investment amount suitability"""
        try:
            user_amount = user_profile.get("total_investment", 0)
            min_investment = recommendation.get("minimum_investment", 0)
            max_investment = recommendation.get("maximum_investment", float('inf'))
            
            if min_investment == 0:
                return SuitabilityFactor(
                    factor_id="amount_suitability",
                    name="Investment Amount Suitability",
                    description="Assesses suitability of investment amount for product requirements",
                    weight=0.7,
                    score=1.0,
                    reasoning="No minimum investment requirement",
                    critical=False
                )
            
            # Check minimum investment
            if user_amount < min_investment:
                score = 0.0
                reasoning = f"Insufficient investment amount: ${user_amount:,} < ${min_investment:,} minimum"
            else:
                # Calculate amount suitability score
                if max_investment == float('inf'):
                    # No maximum limit
                    if user_amount >= min_investment * 10:
                        score = 1.0
                        reasoning = f"Excellent amount suitability: ${user_amount:,} (10x minimum)"
                    elif user_amount >= min_investment * 5:
                        score = 0.9
                        reasoning = f"Good amount suitability: ${user_amount:,} (5x minimum)"
                    elif user_amount >= min_investment * 2:
                        score = 0.7
                        reasoning = f"Moderate amount suitability: ${user_amount:,} (2x minimum)"
                    else:
                        score = 0.5
                        reasoning = f"Minimum amount suitability: ${user_amount:,} (1x minimum)"
                else:
                    # Has maximum limit
                    if user_amount > max_investment:
                        score = 0.0
                        reasoning = f"Exceeds maximum investment: ${user_amount:,} > ${max_investment:,}"
                    elif user_amount >= max_investment * 0.8:
                        score = 0.9
                        reasoning = f"Good amount suitability: ${user_amount:,} (80% of maximum)"
                    elif user_amount >= max_investment * 0.5:
                        score = 0.7
                        reasoning = f"Moderate amount suitability: ${user_amount:,} (50% of maximum)"
                    else:
                        score = 0.5
                        reasoning = f"Low amount suitability: ${user_amount:,} (25% of maximum)"
            
            return SuitabilityFactor(
                factor_id="amount_suitability",
                name="Investment Amount Suitability",
                description="Assesses suitability of investment amount for product requirements",
                weight=0.7,
                score=score,
                reasoning=reasoning,
                critical=False
            )
            
        except Exception as e:
            logger.error(f"Error assessing amount suitability: {e}")
            return SuitabilityFactor(
                factor_id="amount_suitability",
                name="Investment Amount Suitability",
                description="Assesses suitability of investment amount for product requirements",
                weight=0.7,
                score=0.0,
                reasoning=f"Amount suitability assessment error: {str(e)}",
                critical=False
            )
    
    def _determine_suitability_level(self, score: float) -> SuitabilityLevel:
        """Determine overall suitability level based on score"""
        thresholds = self.suitability_thresholds
        
        if score >= thresholds["excellent"]:
            return SuitabilityLevel.EXCELLENT
        elif score >= thresholds["good"]:
            return SuitabilityLevel.GOOD
        elif score >= thresholds["moderate"]:
            return SuitabilityLevel.MODERATE
        elif score >= thresholds["poor"]:
            return SuitabilityLevel.POOR
        else:
            return SuitabilityLevel.UNSUITABLE
    
    def get_suitability_summary(self, assessment: SuitabilityAssessment) -> Dict[str, Any]:
        """Get a summary of suitability assessment results"""
        return {
            "overall_suitability": assessment.overall_suitability.value,
            "suitability_score": assessment.suitability_score,
            "risk_alignment": assessment.risk_alignment,
            "goal_alignment": assessment.goal_alignment,
            "horizon_alignment": assessment.horizon_alignment,
            "amount_suitability": assessment.amount_suitability,
            "total_factors": len(assessment.factors),
            "warnings": len(assessment.warnings),
            "recommendations": len(assessment.recommendations),
            "audit_trail": assessment.audit_trail
        }

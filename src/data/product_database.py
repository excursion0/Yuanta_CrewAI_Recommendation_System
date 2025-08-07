"""
Product Database for Financial Recommendation System

This module contains a comprehensive database of financial products
with detailed information for intelligent recommendation matching.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import random
import math

@dataclass
class Product:
    """Financial product with comprehensive details"""
    id: str
    name: str
    type: str
    category: str
    risk_level: str
    expected_return_min: float
    expected_return_max: float
    volatility: float
    sharpe_ratio: float
    expense_ratio: float
    minimum_investment: int
    liquidity: str
    description: str
    investment_goals: List[str]
    time_horizon: List[str]
    sectors: List[str]
    regions: List[str]
    asset_classes: List[str]
    performance_rating: int  # 1-5 stars
    suitability_score: float  # 0-100
    last_updated: datetime

class ProductDatabase:
    """Comprehensive product database with intelligent matching"""
    
    def __init__(self):
        self.products = self._initialize_products()
        self.categories = self._get_categories()
        self.risk_profiles = self._get_risk_profiles()
    
    def _initialize_products(self) -> Dict[str, Product]:
        """Initialize comprehensive product database"""
        products = {}
        
        # Conservative Funds (Low Risk)
        products["yuanta_conservative"] = Product(
            id="yuanta_conservative",
            name="Yuanta Conservative Fund",
            type="mutual_fund",
            category="conservative",
            risk_level="low",
            expected_return_min=0.04,
            expected_return_max=0.06,
            volatility=0.08,
            sharpe_ratio=0.75,
            expense_ratio=0.008,
            minimum_investment=1000,
            liquidity="high",
            description="Conservative fund focusing on capital preservation with steady income generation",
            investment_goals=["income", "capital_preservation", "retirement"],
            time_horizon=["short_term", "medium_term"],
            sectors=["financials", "utilities", "consumer_staples"],
            regions=["domestic"],
            asset_classes=["bonds", "large_cap_stocks"],
            performance_rating=4,
            suitability_score=85,
            last_updated=datetime.now()
        )
        
        products["yuanta_bond"] = Product(
            id="yuanta_bond",
            name="Yuanta Bond Fund",
            type="bond_fund",
            category="fixed_income",
            risk_level="low",
            expected_return_min=0.03,
            expected_return_max=0.05,
            volatility=0.05,
            sharpe_ratio=0.85,
            expense_ratio=0.006,
            minimum_investment=500,
            liquidity="high",
            description="Government and corporate bond fund for income generation",
            investment_goals=["income", "capital_preservation", "retirement"],
            time_horizon=["short_term", "medium_term"],
            sectors=["government", "corporate"],
            regions=["domestic"],
            asset_classes=["bonds"],
            performance_rating=4,
            suitability_score=90,
            last_updated=datetime.now()
        )
        
        # Balanced Funds (Medium Risk)
        products["yuanta_balanced"] = Product(
            id="yuanta_balanced",
            name="Yuanta Balanced Fund",
            type="mutual_fund",
            category="balanced",
            risk_level="medium",
            expected_return_min=0.08,
            expected_return_max=0.12,
            volatility=0.12,
            sharpe_ratio=0.70,
            expense_ratio=0.010,
            minimum_investment=1000,
            liquidity="high",
            description="Balanced fund with 60% stocks and 40% bonds for growth and income",
            investment_goals=["growth", "income", "diversification", "retirement"],
            time_horizon=["medium_term", "long_term"],
            sectors=["technology", "healthcare", "financials", "consumer_discretionary"],
            regions=["domestic", "international"],
            asset_classes=["stocks", "bonds"],
            performance_rating=4,
            suitability_score=80,
            last_updated=datetime.now()
        )
        
        products["yuanta_etf_index"] = Product(
            id="yuanta_etf_index",
            name="Yuanta ETF Index Fund",
            type="etf",
            category="index",
            risk_level="medium",
            expected_return_min=0.08,
            expected_return_max=0.12,
            volatility=0.15,
            sharpe_ratio=0.65,
            expense_ratio=0.005,
            minimum_investment=100,
            liquidity="very_high",
            description="Low-cost ETF tracking major market indices for broad diversification",
            investment_goals=["growth", "diversification", "retirement", "tax_efficiency"],
            time_horizon=["medium_term", "long_term"],
            sectors=["all_sectors"],
            regions=["domestic", "international"],
            asset_classes=["stocks"],
            performance_rating=5,
            suitability_score=85,
            last_updated=datetime.now()
        )
        
        # Growth Funds (High Risk)
        products["yuanta_growth"] = Product(
            id="yuanta_growth",
            name="Yuanta Growth Fund",
            type="mutual_fund",
            category="growth",
            risk_level="high",
            expected_return_min=0.12,
            expected_return_max=0.18,
            volatility=0.20,
            sharpe_ratio=0.60,
            expense_ratio=0.012,
            minimum_investment=1000,
            liquidity="high",
            description="Aggressive growth fund focusing on high-growth companies",
            investment_goals=["growth", "capital_appreciation", "long_term_wealth"],
            time_horizon=["long_term"],
            sectors=["technology", "healthcare", "consumer_discretionary"],
            regions=["domestic", "international", "emerging_markets"],
            asset_classes=["stocks"],
            performance_rating=4,
            suitability_score=75,
            last_updated=datetime.now()
        )
        
        products["yuanta_technology"] = Product(
            id="yuanta_technology",
            name="Yuanta Technology Fund",
            type="sector_fund",
            category="technology",
            risk_level="high",
            expected_return_min=0.15,
            expected_return_max=0.25,
            volatility=0.25,
            sharpe_ratio=0.55,
            expense_ratio=0.015,
            minimum_investment=1000,
            liquidity="high",
            description="Technology sector fund for aggressive growth investors",
            investment_goals=["growth", "capital_appreciation", "sector_focus"],
            time_horizon=["long_term"],
            sectors=["technology"],
            regions=["domestic", "international"],
            asset_classes=["stocks"],
            performance_rating=4,
            suitability_score=70,
            last_updated=datetime.now()
        )
        
        # International Funds
        products["yuanta_international"] = Product(
            id="yuanta_international",
            name="Yuanta International Fund",
            type="mutual_fund",
            category="international",
            risk_level="medium",
            expected_return_min=0.09,
            expected_return_max=0.14,
            volatility=0.16,
            sharpe_ratio=0.62,
            expense_ratio=0.011,
            minimum_investment=1000,
            liquidity="medium",
            description="International equity fund for geographic diversification",
            investment_goals=["growth", "diversification", "international_exposure"],
            time_horizon=["medium_term", "long_term"],
            sectors=["all_sectors"],
            regions=["developed_markets", "emerging_markets"],
            asset_classes=["stocks"],
            performance_rating=4,
            suitability_score=78,
            last_updated=datetime.now()
        )
        
        # Income Funds
        products["yuanta_income"] = Product(
            id="yuanta_income",
            name="Yuanta Income Fund",
            type="mutual_fund",
            category="income",
            risk_level="low",
            expected_return_min=0.05,
            expected_return_max=0.08,
            volatility=0.09,
            sharpe_ratio=0.72,
            expense_ratio=0.009,
            minimum_investment=1000,
            liquidity="high",
            description="Income-focused fund with dividend-paying stocks and bonds",
            investment_goals=["income", "capital_preservation", "retirement"],
            time_horizon=["short_term", "medium_term", "long_term"],
            sectors=["utilities", "financials", "consumer_staples"],
            regions=["domestic"],
            asset_classes=["stocks", "bonds"],
            performance_rating=4,
            suitability_score=88,
            last_updated=datetime.now()
        )
        
        # Real Estate Funds
        products["yuanta_real_estate"] = Product(
            id="yuanta_real_estate",
            name="Yuanta Real Estate Fund",
            type="reit_fund",
            category="real_estate",
            risk_level="medium",
            expected_return_min=0.08,
            expected_return_max=0.12,
            volatility=0.14,
            sharpe_ratio=0.58,
            expense_ratio=0.013,
            minimum_investment=1000,
            liquidity="medium",
            description="Real estate investment trust fund for diversification",
            investment_goals=["growth", "diversification", "income", "inflation_protection"],
            time_horizon=["medium_term", "long_term"],
            sectors=["real_estate"],
            regions=["domestic"],
            asset_classes=["real_estate"],
            performance_rating=3,
            suitability_score=65,
            last_updated=datetime.now()
        )
        
        return products
    
    def _get_categories(self) -> Dict[str, Dict[str, Any]]:
        """Get product categories with characteristics"""
        return {
            "conservative": {
                "risk_level": "low",
                "expected_return": "4-6%",
                "volatility": "low",
                "suitable_for": ["retirement", "income", "capital_preservation"]
            },
            "balanced": {
                "risk_level": "medium",
                "expected_return": "8-12%",
                "volatility": "medium",
                "suitable_for": ["growth", "income", "diversification"]
            },
            "growth": {
                "risk_level": "high",
                "expected_return": "12-18%",
                "volatility": "high",
                "suitable_for": ["growth", "capital_appreciation", "long_term_wealth"]
            },
            "income": {
                "risk_level": "low",
                "expected_return": "5-8%",
                "volatility": "low",
                "suitable_for": ["income", "retirement", "capital_preservation"]
            },
            "international": {
                "risk_level": "medium",
                "expected_return": "9-14%",
                "volatility": "medium",
                "suitable_for": ["growth", "diversification", "international_exposure"]
            },
            "real_estate": {
                "risk_level": "medium",
                "expected_return": "8-12%",
                "volatility": "medium",
                "suitable_for": ["diversification", "income", "inflation_protection"]
            }
        }
    
    def _get_risk_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Get risk profiles with characteristics"""
        return {
            "low": {
                "volatility_range": (0.05, 0.10),
                "expected_return_range": (0.03, 0.08),
                "suitable_products": ["conservative", "income", "bond"],
                "allocation_strategy": "60% bonds, 30% conservative stocks, 10% alternatives"
            },
            "medium": {
                "volatility_range": (0.10, 0.18),
                "expected_return_range": (0.08, 0.14),
                "suitable_products": ["balanced", "international", "real_estate"],
                "allocation_strategy": "50% stocks, 40% bonds, 10% alternatives"
            },
            "high": {
                "volatility_range": (0.18, 0.30),
                "expected_return_range": (0.12, 0.25),
                "suitable_products": ["growth", "technology", "emerging_markets"],
                "allocation_strategy": "70% stocks, 20% bonds, 10% alternatives"
            }
        }
    
    def get_all_products(self) -> List[Product]:
        """Get all products in the database"""
        return list(self.products.values())
    
    def get_products_by_risk_level(self, risk_level: str) -> List[Product]:
        """Get products matching a specific risk level"""
        return [product for product in self.products.values() if product.risk_level == risk_level]
    
    def get_products_by_category(self, category: str) -> List[Product]:
        """Get products in a specific category"""
        return [product for product in self.products.values() if product.category == category]
    
    def get_products_by_goal(self, goal: str) -> List[Product]:
        """Get products suitable for a specific investment goal"""
        return [product for product in self.products.values() if goal in product.investment_goals]
    
    def get_products_by_time_horizon(self, horizon: str) -> List[Product]:
        """Get products suitable for a specific time horizon"""
        return [product for product in self.products.values() if horizon in product.time_horizon]
    
    def search_products(self, criteria: Dict[str, Any]) -> List[Product]:
        """Search products based on multiple criteria"""
        matching_products = []
        
        for product in self.products.values():
            match_score = 0
            total_criteria = 0
            
            # Risk level matching
            if "risk_level" in criteria:
                total_criteria += 1
                if product.risk_level == criteria["risk_level"]:
                    match_score += 1
            
            # Investment goals matching
            if "investment_goals" in criteria:
                total_criteria += 1
                user_goals = criteria["investment_goals"]
                if isinstance(user_goals, list):
                    for goal in user_goals:
                        if goal in product.investment_goals:
                            match_score += 1
                            break
                else:
                    if user_goals in product.investment_goals:
                        match_score += 1
            
            # Time horizon matching
            if "time_horizon" in criteria:
                total_criteria += 1
                if criteria["time_horizon"] in product.time_horizon:
                    match_score += 1
            
            # Minimum investment matching
            if "minimum_investment" in criteria:
                total_criteria += 1
                if product.minimum_investment <= criteria["minimum_investment"]:
                    match_score += 1
            
            # Calculate match percentage
            if total_criteria > 0:
                match_percentage = match_score / total_criteria
                if match_percentage >= 0.5:  # At least 50% match
                    matching_products.append((product, match_percentage))
        
        # Sort by match percentage (highest first)
        matching_products.sort(key=lambda x: x[1], reverse=True)
        return [product for product, _ in matching_products]
    
    def calculate_product_suitability(self, product: Product, user_profile: Dict[str, Any]) -> float:
        """Calculate suitability score for a product based on user profile"""
        score = 0
        max_score = 100
        
        # Risk level alignment (30 points)
        user_risk = user_profile.get("risk_level", "medium")
        if product.risk_level == user_risk:
            score += 30
        elif (product.risk_level == "medium" and user_risk in ["low", "high"]) or \
             (user_risk == "medium" and product.risk_level in ["low", "high"]):
            score += 20
        else:
            score += 10
        
        # Investment goals alignment (25 points)
        user_goals = user_profile.get("investment_goals", [])
        if isinstance(user_goals, list):
            for goal in user_goals:
                if goal in product.investment_goals:
                    score += 25
                    break
        else:
            if user_goals in product.investment_goals:
                score += 25
        
        # Time horizon alignment (20 points)
        user_horizon = user_profile.get("time_horizon", "medium")
        if user_horizon in product.time_horizon:
            score += 20
        
        # Investment amount suitability (15 points)
        user_investment = user_profile.get("total_investment", 100000)
        if user_investment >= product.minimum_investment * 10:  # Can invest 10x minimum
            score += 15
        elif user_investment >= product.minimum_investment:
            score += 10
        else:
            score += 5
        
        # Performance rating bonus (10 points)
        score += (product.performance_rating - 1) * 2.5  # 0-10 points based on 1-5 rating
        
        return min(score, max_score)
    
    def get_recommended_products(self, user_profile: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """Get recommended products based on user profile"""
        recommendations = []
        
        # Get all products and calculate suitability scores
        all_products = self.get_all_products()
        scored_products = []
        
        for product in all_products:
            suitability_score = self.calculate_product_suitability(product, user_profile)
            scored_products.append((product, suitability_score))
        
        # Sort by suitability score (highest first)
        scored_products.sort(key=lambda x: x[1], reverse=True)
        
        # Return top recommendations
        for product, score in scored_products[:limit]:
            recommendations.append({
                "product": product,
                "suitability_score": score,
                "suitability_level": self._get_suitability_level(score),
                "reasoning": self._get_recommendation_reasoning(product, user_profile, score)
            })
        
        return recommendations
    
    def _get_suitability_level(self, score: float) -> str:
        """Get suitability level based on score"""
        if score >= 80:
            return "excellent"
        elif score >= 60:
            return "good"
        elif score >= 40:
            return "moderate"
        else:
            return "poor"
    
    def _get_recommendation_reasoning(self, product: Product, user_profile: Dict[str, Any], score: float) -> str:
        """Generate reasoning for product recommendation"""
        reasoning_parts = []
        
        # Risk level reasoning
        user_risk = user_profile.get("risk_level", "medium")
        if product.risk_level == user_risk:
            reasoning_parts.append(f"Risk level matches your {user_risk} risk tolerance")
        elif product.risk_level == "medium":
            reasoning_parts.append("Moderate risk level suitable for most investors")
        else:
            reasoning_parts.append(f"Consider {product.risk_level} risk level carefully")
        
        # Investment goals reasoning
        user_goals = user_profile.get("investment_goals", [])
        if isinstance(user_goals, list):
            for goal in user_goals:
                if goal in product.investment_goals:
                    reasoning_parts.append(f"Aligns with your {goal} investment goal")
                    break
        
        # Time horizon reasoning
        user_horizon = user_profile.get("time_horizon", "medium")
        if user_horizon in product.time_horizon:
            reasoning_parts.append(f"Suitable for your {user_horizon} time horizon")
        
        # Performance reasoning
        if product.performance_rating >= 4:
            reasoning_parts.append("Strong historical performance")
        elif product.performance_rating >= 3:
            reasoning_parts.append("Solid historical performance")
        
        # Cost reasoning
        if product.expense_ratio <= 0.008:
            reasoning_parts.append("Low expense ratio")
        elif product.expense_ratio <= 0.012:
            reasoning_parts.append("Reasonable expense ratio")
        
        return "; ".join(reasoning_parts)
    
    def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """Get a specific product by ID"""
        return self.products.get(product_id)
    
    def get_product_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        total_products = len(self.products)
        risk_levels = {}
        categories = {}
        
        for product in self.products.values():
            risk_levels[product.risk_level] = risk_levels.get(product.risk_level, 0) + 1
            categories[product.category] = categories.get(product.category, 0) + 1
        
        return {
            "total_products": total_products,
            "risk_level_distribution": risk_levels,
            "category_distribution": categories,
            "average_expense_ratio": sum(p.expense_ratio for p in self.products.values()) / total_products,
            "average_performance_rating": sum(p.performance_rating for p in self.products.values()) / total_products
        }

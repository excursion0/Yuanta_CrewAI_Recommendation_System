"""
Recommendation Agent for financial product recommendation system.

This agent is responsible for suggesting financial products, allocations,
and investment strategies based on user needs and market conditions.
"""

from crewai import Agent, LLM
from crewai.tools import tool
from typing import Dict, Any, List
import logging
import os
import math
from datetime import datetime

# Import the product database
from src.data.product_database import ProductDatabase

logger = logging.getLogger(__name__)


class RecommendationAgent:
    """Agent responsible for financial product recommendations"""
    
    def __init__(self, llm_provider):
        self.llm_provider = llm_provider
        self.product_db = ProductDatabase()
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create the recommendation agent"""
        # Create CrewAI LLM instance with direct Anthropic configuration
        crewai_llm = LLM(
            model="claude-3-5-sonnet-20241022",
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        
        # Create properly decorated tool functions (reduced to 2 tools to prevent loops)
        @tool
        def generate_product_recommendations(user_profile: Dict[str, Any], market_data: Dict[str, Any]) -> str:
            """Generate personalized product recommendations"""
            return self._generate_product_recommendations(user_profile, market_data)
        
        @tool
        def suggest_investment_strategy(user_profile: Dict[str, Any], market_data: Dict[str, Any]) -> str:
            """Suggest investment strategy based on profile and market data"""
            return self._suggest_investment_strategy(user_profile, market_data)
        
        return Agent(
            role="Financial Product Recommendation Specialist",
            goal="Generate investment recommendations based on user needs and market conditions",
            backstory="You are a financial advisor who creates personalized investment recommendations.",
            verbose=False,  # Reduce verbose output
            allow_delegation=False,
            llm=crewai_llm,
            tools=[
                generate_product_recommendations,
                suggest_investment_strategy
            ]
        )
    
    def _generate_product_recommendations(self, user_profile: Dict[str, Any], market_data: Dict[str, Any]) -> str:
        """Generate personalized product recommendations"""
        try:
            # Get recommended products from database
            recommendations = self.product_db.get_recommended_products(user_profile, limit=5)
            
            if not recommendations:
                return "No suitable products found for your profile. Please consult with a financial advisor."
            
            # Format comprehensive recommendations
            result = f"""PERSONALIZED PRODUCT RECOMMENDATIONS - {datetime.now().strftime('%Y-%m-%d %H:%M')}

USER PROFILE ANALYSIS:
• Risk Level: {user_profile.get('risk_level', 'medium').upper()}
• Investment Goals: {', '.join(user_profile.get('investment_goals', ['general']))}
• Time Horizon: {user_profile.get('time_horizon', 'medium').upper()}
• Investment Amount: ${user_profile.get('total_investment', 100000):,}

TOP RECOMMENDATIONS:"""

            for i, rec in enumerate(recommendations[:3], 1):
                product = rec["product"]
                result += f"""

{i}. {product.name} ({rec['suitability_level'].upper()} MATCH - {rec['suitability_score']:.0f}/100)
   • Type: {product.type.replace('_', ' ').title()}
   • Category: {product.category.replace('_', ' ').title()}
   • Risk Level: {product.risk_level.upper()}
   • Expected Return: {product.expected_return_min:.1%} - {product.expected_return_max:.1%}
   • Volatility: {product.volatility:.1%}
   • Sharpe Ratio: {product.sharpe_ratio:.2f}
   • Expense Ratio: {product.expense_ratio:.1%}
   • Minimum Investment: ${product.minimum_investment:,}
   • Liquidity: {product.liquidity.replace('_', ' ').title()}
   • Performance Rating: {'★' * product.performance_rating}{'☆' * (5 - product.performance_rating)}
   
   REASONING: {rec['reasoning']}
   
   DESCRIPTION: {product.description}"""

            # Add secondary recommendations
            if len(recommendations) > 3:
                result += f"""

SECONDARY OPTIONS:"""
                for i, rec in enumerate(recommendations[3:], 4):
                    product = rec["product"]
                    result += f"""

{i}. {product.name} ({rec['suitability_level'].upper()} MATCH - {rec['suitability_score']:.0f}/100)
   • Type: {product.type.replace('_', ' ').title()}
   • Risk Level: {product.risk_level.upper()}
   • Expected Return: {product.expected_return_min:.1%} - {product.expected_return_max:.1%}
   • Minimum Investment: ${product.minimum_investment:,}
   • Performance Rating: {'★' * product.performance_rating}{'☆' * (5 - product.performance_rating)}"""

            # Add portfolio allocation suggestion
            allocation = self._create_portfolio_allocation(user_profile, recommendations)
            result += f"""

PORTFOLIO ALLOCATION SUGGESTION:
• Total Investment: ${user_profile.get('total_investment', 100000):,}
• Risk Level: {user_profile.get('risk_level', 'medium').upper()}
• Expected Portfolio Return: {allocation['expected_return']}
• Diversification Score: {allocation['diversification_score']:.1f}/10
• Rebalancing Frequency: {allocation['rebalancing_frequency']}

RECOMMENDED ALLOCATIONS:"""
            
            for fund_type, percentage in allocation['allocations'].items():
                result += f"""
• {fund_type.replace('_', ' ').title()}: {percentage:.0%}"""

            result += f"""

IMPORTANT CONSIDERATIONS:
• All recommendations are based on your risk profile and investment goals
• Past performance does not guarantee future results
• Consider consulting with a financial advisor before investing
• Review fund prospectuses for complete information
• Diversification helps reduce risk but does not eliminate it"""

            logger.info(f"Generated {len(recommendations)} product recommendations for {user_profile.get('risk_level', 'medium')} risk level")
            return result
            
        except Exception as e:
            logger.error(f"Error generating product recommendations: {e}")
            return f"Error generating recommendations: {str(e)}"
    
    def _create_portfolio_allocation(self, user_profile: Dict[str, Any], recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create optimal portfolio allocation based on recommendations"""
        try:
            risk_level = user_profile.get("risk_level", "medium")
            total_investment = user_profile.get("total_investment", 100000)
            
            # Create allocation strategy based on risk level
            if risk_level == "low":
                allocations = {
                    "conservative_funds": 0.60,
                    "bond_funds": 0.30,
                    "index_funds": 0.10
                }
                expected_return = "4-6%"
                diversification_score = 8.5
                rebalancing_frequency = "Semi-annually"
                
            elif risk_level == "medium":
                allocations = {
                    "balanced_funds": 0.50,
                    "index_funds": 0.30,
                    "growth_funds": 0.20
                }
                expected_return = "8-12%"
                diversification_score = 9.0
                rebalancing_frequency = "Quarterly"
                
            else:  # High risk
                allocations = {
                    "growth_funds": 0.60,
                    "index_funds": 0.25,
                    "balanced_funds": 0.15
                }
                expected_return = "12-18%"
                diversification_score = 7.5
                rebalancing_frequency = "Quarterly"
            
            # Adjust allocations based on available products
            available_categories = [rec["product"].category for rec in recommendations]
            
            # Map categories to allocation types
            category_mapping = {
                "conservative": "conservative_funds",
                "income": "conservative_funds",
                "balanced": "balanced_funds",
                "index": "index_funds",
                "growth": "growth_funds",
                "technology": "growth_funds",
                "international": "index_funds",
                "real_estate": "balanced_funds"
            }
            
            # Adjust allocations based on available products
            adjusted_allocations = {}
            for category in available_categories:
                allocation_type = category_mapping.get(category, "balanced_funds")
                if allocation_type in allocations:
                    adjusted_allocations[allocation_type] = allocations[allocation_type]
            
            # Normalize allocations to sum to 100%
            total_allocation = sum(adjusted_allocations.values())
            if total_allocation > 0:
                for key in adjusted_allocations:
                    adjusted_allocations[key] /= total_allocation
            
            logger.info(f"Created portfolio allocation for {risk_level} risk level")
            
            return {
                "success": True,
                "total_investment": total_investment,
                "risk_level": risk_level,
                "allocations": adjusted_allocations,
                "expected_return": expected_return,
                "diversification_score": diversification_score,
                "rebalancing_frequency": rebalancing_frequency
            }
            
        except Exception as e:
            logger.error(f"Error creating portfolio allocation: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_investment": user_profile.get("total_investment", 100000),
                "risk_level": user_profile.get("risk_level", "medium"),
                "allocations": {"balanced_funds": 1.0},
                "expected_return": "8-12%",
                "diversification_score": 7.0,
                "rebalancing_frequency": "Quarterly"
            }
    
    def _analyze_product_suitability(self, product, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze suitability of a specific product for the user"""
        try:
            # Use the product database's suitability calculation
            suitability_score = self.product_db.calculate_product_suitability(product, user_profile)
            
            # Determine suitability level
            if suitability_score >= 80:
                suitability_level = "excellent"
                recommendation = "Highly recommended"
            elif suitability_score >= 60:
                suitability_level = "good"
                recommendation = "Recommended"
            elif suitability_score >= 40:
                suitability_level = "moderate"
                recommendation = "Consider with caution"
            else:
                suitability_level = "poor"
                recommendation = "Not recommended"
            
            # Generate reasoning
            reasoning = self.product_db._get_recommendation_reasoning(product, user_profile, suitability_score)
            
            logger.info(f"Analyzed product suitability: {suitability_level} ({suitability_score:.0f}/100)")
            
            return {
                "success": True,
                "product": product,
                "suitability_score": suitability_score,
                "suitability_level": suitability_level,
                "recommendation": recommendation,
                "reasoning": reasoning
            }
        except Exception as e:
            logger.error(f"Error analyzing product suitability: {e}")
            return {
                "success": False,
                "error": str(e),
                "product": product,
                "user_profile": user_profile
            }
    
    def _suggest_investment_strategy(self, user_profile: Dict[str, Any], market_data: Dict[str, Any]) -> str:
        """Suggest overall investment strategy using real market data"""
        try:
            risk_level = user_profile.get("risk_level", "medium")
            investment_horizon = user_profile.get("time_horizon", "medium")
            goals = user_profile.get("investment_goals", [])
            total_investment = user_profile.get("total_investment", 100000)
            
            # Get market conditions from market data
            market_volatility = market_data.get("volatility_level", "MODERATE")
            market_sentiment = market_data.get("sentiment_level", "NEUTRAL")
            economic_cycle = market_data.get("economic_cycle", "Expansion")
            
            # Create investment strategy
            strategy = {
                "approach": "",
                "key_principles": [],
                "allocation_strategy": "",
                "rebalancing_frequency": "",
                "monitoring_frequency": "",
                "risk_management": [],
                "market_considerations": []
            }
            
            if risk_level == "low":
                strategy["approach"] = "Conservative - Capital Preservation"
                strategy["key_principles"] = [
                    "Prioritize capital preservation",
                    "Focus on income generation",
                    "Maintain liquidity",
                    "Diversify across stable assets"
                ]
                strategy["allocation_strategy"] = "60% conservative funds, 30% bonds, 10% index funds"
                strategy["rebalancing_frequency"] = "Semi-annually"
                strategy["monitoring_frequency"] = "Monthly"
                strategy["risk_management"] = [
                    "Maintain emergency fund (3-6 months expenses)",
                    "Regular income reviews",
                    "Conservative withdrawal rates (3-4%)",
                    "Focus on dividend-paying investments"
                ]
                
            elif risk_level == "medium":
                strategy["approach"] = "Balanced - Growth and Income"
                strategy["key_principles"] = [
                    "Balance growth and income",
                    "Diversify across asset classes",
                    "Regular rebalancing",
                    "Long-term perspective"
                ]
                strategy["allocation_strategy"] = "50% balanced funds, 30% index funds, 20% growth funds"
                strategy["rebalancing_frequency"] = "Quarterly"
                strategy["monitoring_frequency"] = "Bi-weekly"
                strategy["risk_management"] = [
                    "Maintain target allocations",
                    "Monitor market conditions",
                    "Adjust for life changes",
                    "Consider tax-efficient investing"
                ]
                
            else:  # High risk
                strategy["approach"] = "Aggressive - Growth Focus"
                strategy["key_principles"] = [
                    "Maximize growth potential",
                    "Accept higher volatility",
                    "Long-term investment horizon",
                    "Active management"
                ]
                strategy["allocation_strategy"] = "60% growth funds, 25% index funds, 15% balanced funds"
                strategy["rebalancing_frequency"] = "Quarterly"
                strategy["monitoring_frequency"] = "Weekly"
                strategy["risk_management"] = [
                    "Regular portfolio reviews",
                    "Market timing considerations",
                    "Emergency fund maintenance",
                    "Consider sector rotation"
                ]
            
            # Add market-specific considerations
            if market_volatility == "HIGH":
                strategy["market_considerations"].append("Consider defensive positioning due to high market volatility")
            elif market_volatility == "LOW":
                strategy["market_considerations"].append("Favorable conditions for growth investments")
            
            if market_sentiment == "FEAR":
                strategy["market_considerations"].append("Market fear may present buying opportunities")
            elif market_sentiment == "GREED":
                strategy["market_considerations"].append("Exercise caution due to market exuberance")
            
            if economic_cycle == "Contraction":
                strategy["market_considerations"].append("Economic contraction suggests defensive positioning")
            elif economic_cycle == "Expansion":
                strategy["market_considerations"].append("Economic expansion supports growth investments")
            
            # Format strategy response
            result = f"""INVESTMENT STRATEGY RECOMMENDATION - {datetime.now().strftime('%Y-%m-%d %H:%M')}

USER PROFILE:
• Risk Level: {risk_level.upper()}
• Time Horizon: {investment_horizon.upper()}
• Investment Goals: {', '.join(goals) if goals else 'General'}
• Investment Amount: ${total_investment:,}

MARKET CONDITIONS:
• Volatility: {market_volatility}
• Sentiment: {market_sentiment}
• Economic Cycle: {economic_cycle}

RECOMMENDED STRATEGY: {strategy['approach']}

KEY PRINCIPLES:"""
            
            for principle in strategy["key_principles"]:
                result += f"\n• {principle}"
            
            result += f"""

ALLOCATION STRATEGY:
{strategy['allocation_strategy']}

PORTFOLIO MANAGEMENT:
• Rebalancing Frequency: {strategy['rebalancing_frequency']}
• Monitoring Frequency: {strategy['monitoring_frequency']}

RISK MANAGEMENT:"""
            
            for risk_item in strategy["risk_management"]:
                result += f"\n• {risk_item}"
            
            if strategy["market_considerations"]:
                result += "\n\nMARKET CONSIDERATIONS:"
                for consideration in strategy["market_considerations"]:
                    result += f"\n• {consideration}"
            
            result += f"""

IMPLEMENTATION STEPS:
1. Review your current portfolio allocation
2. Identify gaps in your investment strategy
3. Consider the recommended products from our database
4. Implement changes gradually over 3-6 months
5. Set up regular monitoring and rebalancing schedule
6. Review strategy annually or when life circumstances change

IMPORTANT DISCLAIMERS:
• This strategy is based on your risk profile and current market conditions
• Past performance does not guarantee future results
• Consider consulting with a financial advisor before implementing
• Investment strategies should be reviewed regularly
• Market conditions can change rapidly, requiring strategy adjustments"""

            logger.info(f"Suggested investment strategy for {risk_level} risk level")
            return result
            
        except Exception as e:
            logger.error(f"Error suggesting investment strategy: {e}")
            return f"Error suggesting investment strategy: {str(e)}"
    
    def get_agent(self) -> Agent:
        """Get the CrewAI agent"""
        return self.agent 
"""
Executive Summary Templates

This module provides template-based generation for executive summaries
based on user profiles, risk levels, and analysis results.
"""

from typing import Dict, Any, List
import json
import os
from datetime import datetime

class ExecutiveSummaryTemplates:
    """Template system for generating executive summaries"""
    
    def __init__(self):
        self.templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        self._load_templates()
    
    def _load_templates(self):
        """Load template files"""
        self.templates = {
            "conservative": self._get_conservative_template(),
            "moderate": self._get_moderate_template(),
            "aggressive": self._get_aggressive_template(),
            "retirement": self._get_retirement_template(),
            "income": self._get_income_template(),
            "growth": self._get_growth_template()
        }
    
    def _get_conservative_template(self) -> Dict[str, Any]:
        """Conservative investor template"""
        return {
            "title": "Conservative Investment Summary",
            "intro": "Based on your conservative risk profile, we've identified investment opportunities focused on capital preservation and steady income generation.",
            "key_points": [
                "Capital preservation is the primary objective",
                "Focus on low-volatility investments",
                "Steady income generation",
                "Diversification across stable sectors"
            ],
            "risk_emphasis": "Your conservative approach prioritizes stability over high returns, which is appropriate for your risk tolerance.",
            "next_steps": [
                "Review bond and fixed-income options",
                "Consider dividend-paying stocks",
                "Evaluate government securities",
                "Plan for regular portfolio rebalancing"
            ],
            "disclaimer": "Conservative investments may provide lower returns but typically offer greater stability and reduced volatility."
        }
    
    def _get_moderate_template(self) -> Dict[str, Any]:
        """Moderate investor template"""
        return {
            "title": "Balanced Investment Summary",
            "intro": "Your moderate risk profile allows for a balanced approach that seeks both growth and income while managing risk appropriately.",
            "key_points": [
                "Balanced growth and income objectives",
                "Moderate risk exposure",
                "Diversified portfolio allocation",
                "Regular rebalancing strategy"
            ],
            "risk_emphasis": "Your moderate risk tolerance allows for a mix of growth and income investments with appropriate risk management.",
            "next_steps": [
                "Review balanced fund options",
                "Consider sector diversification",
                "Evaluate growth and income funds",
                "Plan for quarterly portfolio reviews"
            ],
            "disclaimer": "Moderate investments offer a balance between growth potential and risk management, suitable for medium-term goals."
        }
    
    def _get_aggressive_template(self) -> Dict[str, Any]:
        """Aggressive investor template"""
        return {
            "title": "Growth Investment Summary",
            "intro": "Your aggressive risk profile enables us to focus on high-growth opportunities with the potential for significant returns over time.",
            "key_points": [
                "Maximum growth potential",
                "Higher risk tolerance",
                "Focus on growth sectors",
                "Long-term investment horizon"
            ],
            "risk_emphasis": "Your aggressive approach accepts higher volatility in pursuit of maximum growth potential.",
            "next_steps": [
                "Review growth fund options",
                "Consider technology and innovation sectors",
                "Evaluate international opportunities",
                "Plan for regular performance monitoring"
            ],
            "disclaimer": "Aggressive investments carry higher risk and volatility but offer potential for significant long-term returns."
        }
    
    def _get_retirement_template(self) -> Dict[str, Any]:
        """Retirement-focused template"""
        return {
            "title": "Retirement Planning Summary",
            "intro": "Your retirement-focused investment strategy prioritizes long-term growth and income generation for your future financial security.",
            "key_points": [
                "Long-term growth objectives",
                "Income generation for retirement",
                "Tax-efficient investment strategies",
                "Regular portfolio rebalancing"
            ],
            "risk_emphasis": "Retirement planning balances growth needs with the importance of preserving capital for future income needs.",
            "next_steps": [
                "Review retirement account options",
                "Consider target-date funds",
                "Evaluate income-generating investments",
                "Plan for regular retirement goal reviews"
            ],
            "disclaimer": "Retirement investments should be reviewed regularly and adjusted based on changing life circumstances and market conditions."
        }
    
    def _get_income_template(self) -> Dict[str, Any]:
        """Income-focused template"""
        return {
            "title": "Income Investment Summary",
            "intro": "Your income-focused strategy prioritizes regular cash flow and dividend generation to meet current income needs.",
            "key_points": [
                "Regular income generation",
                "Dividend-paying investments",
                "Stable cash flow",
                "Income-focused diversification"
            ],
            "risk_emphasis": "Income investments focus on generating regular cash flow while maintaining appropriate risk levels.",
            "next_steps": [
                "Review dividend-paying stocks",
                "Consider bond ladder strategies",
                "Evaluate REITs and income funds",
                "Plan for monthly income monitoring"
            ],
            "disclaimer": "Income investments provide regular cash flow but may have limited growth potential compared to growth-focused strategies."
        }
    
    def _get_growth_template(self) -> Dict[str, Any]:
        """Growth-focused template"""
        return {
            "title": "Growth Investment Summary",
            "intro": "Your growth-focused strategy prioritizes capital appreciation and long-term wealth building through strategic investments.",
            "key_points": [
                "Maximum capital appreciation",
                "Long-term growth focus",
                "Innovation and technology emphasis",
                "Strategic sector allocation"
            ],
            "risk_emphasis": "Growth investments accept higher volatility in pursuit of maximum long-term returns.",
            "next_steps": [
                "Review growth fund options",
                "Consider emerging market opportunities",
                "Evaluate technology and innovation sectors",
                "Plan for regular growth monitoring"
            ],
            "disclaimer": "Growth investments offer potential for significant returns but carry higher risk and volatility."
        }
    
    def get_template(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Get appropriate template based on user profile"""
        risk_level = user_profile.get("risk_level", "medium").lower()
        investment_goals = [goal.lower() for goal in user_profile.get("investment_goals", [])]
        
        # Determine template based on goals and risk
        if "retirement" in investment_goals:
            return self.templates["retirement"]
        elif "income" in investment_goals:
            return self.templates["income"]
        elif "growth" in investment_goals:
            return self.templates["growth"]
        elif risk_level == "low":
            return self.templates["conservative"]
        elif risk_level == "high":
            return self.templates["aggressive"]
        else:
            return self.templates["moderate"]
    
    def format_recommendations(self, recommendations: List[Dict[str, Any]]) -> str:
        """Format recommendations for summary"""
        if not recommendations:
            return "No specific recommendations available at this time."
        
        formatted = []
        
        for i, rec in enumerate(recommendations[:3], 1):
            product_name = rec.get("name", "Unknown Product")
            allocation = rec.get("allocation", "N/A")
            reasoning = rec.get("reasoning", "No specific reasoning provided")
            
            formatted.append(f"{i}. **{product_name}** ({allocation})\n   {reasoning}")
        
        return "\n\n".join(formatted)
    
    def format_risk_analysis(self, risk_analysis: Dict[str, Any]) -> str:
        """Format risk analysis for summary"""
        risk_level = risk_analysis.get("risk_level", "medium")
        risk_score = risk_analysis.get("risk_score", "N/A")
        volatility = risk_analysis.get("volatility", "N/A")
        
        return f"Risk Level: {risk_level.title()}\nRisk Score: {risk_score}\nVolatility: {volatility}"
    
    def format_expected_returns(self, recommendations: Dict[str, Any]) -> str:
        """Format expected returns for summary"""
        expected_returns = recommendations.get("expected_returns", "8-12% annually")
        return f"Expected Returns: {expected_returns}"
    
    def generate_summary(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary using templates"""
        user_profile = analysis_data.get("user_profile", {})
        recommendations = analysis_data.get("recommendations", {})
        risk_analysis = analysis_data.get("risk_analysis", {})
        
        # Get appropriate template
        template = self.get_template(user_profile)
        
        # Format data
        formatted_recommendations = self.format_recommendations(
            recommendations.get("primary_recommendations", [])
        )
        formatted_risk = self.format_risk_analysis(risk_analysis)
        formatted_returns = self.format_expected_returns(recommendations)
        
        # Generate summary
        summary = {
            "title": template["title"],
            "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "intro": template["intro"],
            "key_points": template["key_points"],
            "recommendations": formatted_recommendations,
            "risk_analysis": formatted_risk,
            "expected_returns": formatted_returns,
            "risk_emphasis": template["risk_emphasis"],
            "next_steps": template["next_steps"],
            "disclaimer": template["disclaimer"]
        }
        
        return summary

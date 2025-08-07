"""
Report Writer Agent for financial product recommendation system.

This agent is responsible for generating human-readable summaries
and comprehensive reports from financial analysis.
"""

from crewai import Agent, LLM
from crewai.tools import tool
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class ReportWriterAgent:
    """Agent responsible for generating comprehensive reports"""
    
    def __init__(self, llm_provider):
        self.llm_provider = llm_provider
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create the report writer agent"""
        # Create CrewAI LLM instance
        crewai_llm = LLM(model="claude-3-5-sonnet-20241022")
        
        # Create tools as simple inline functions (like the working agents)
        @tool
        def generate_executive_summary(analysis_data: Dict[str, Any]) -> str:
            """Generate executive summary of financial analysis"""
            try:
                from src.templates.executive_summary_templates import ExecutiveSummaryTemplates
                
                # Initialize template system
                template_system = ExecutiveSummaryTemplates()
                
                # Generate summary using templates
                summary = template_system.generate_summary(analysis_data)
                
                # Format as string for CrewAI
                formatted_summary = f"""
EXECUTIVE SUMMARY: {summary['title']}

{summary['intro']}

KEY POINTS:
{chr(10).join(f"• {point}" for point in summary['key_points'])}

RECOMMENDATIONS:
{summary['recommendations']}

RISK ANALYSIS:
{summary['risk_analysis']}

EXPECTED RETURNS:
{summary['expected_returns']}

NEXT STEPS:
{chr(10).join(f"• {step}" for step in summary['next_steps'])}

DISCLAIMER: {summary['disclaimer']}
"""
                
                return formatted_summary
            except Exception as e:
                return f"EXECUTIVE SUMMARY: Error generating summary - {str(e)}"
        
        @tool
        def create_detailed_report(analysis_data: Dict[str, Any]) -> str:
            """Create detailed financial report"""
            try:
                from src.templates.executive_summary_templates import ExecutiveSummaryTemplates
                
                # Initialize template system
                template_system = ExecutiveSummaryTemplates()
                
                # Generate summary using templates
                summary = template_system.generate_summary(analysis_data)
                
                # Create detailed report
                detailed_report = f"""
DETAILED FINANCIAL REPORT

{summary['title']}
Generated: {summary['generated_date']}

EXECUTIVE SUMMARY:
{summary['intro']}

KEY INVESTMENT POINTS:
{chr(10).join(f"• {point}" for point in summary['key_points'])}

DETAILED RECOMMENDATIONS:
{summary['recommendations']}

COMPREHENSIVE RISK ANALYSIS:
{summary['risk_analysis']}

EXPECTED RETURNS:
{summary['expected_returns']}

RISK CONSIDERATIONS:
{summary['risk_emphasis']}

IMPLEMENTATION STRATEGY:
{chr(10).join(f"• {step}" for step in summary['next_steps'])}

MONITORING GUIDELINES:
• Regular portfolio review (quarterly)
• Performance tracking against benchmarks
• Risk assessment updates
• Rebalancing as needed

DISCLAIMER: {summary['disclaimer']}
"""
                
                return detailed_report
            except Exception as e:
                return f"DETAILED FINANCIAL REPORT: Error generating report - {str(e)}"
        
        return Agent(
            role="Financial Report Writer",
            goal="Create financial reports and summaries",
            backstory="You are a financial writer who creates clear and professional financial reports.",
            verbose=True,
            allow_delegation=False,
            llm=crewai_llm,
            tools=[
                generate_executive_summary,
                create_detailed_report
            ]
        )
    
    @tool
    def _generate_executive_summary(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary of financial analysis using template system"""
        try:
            from src.templates.executive_summary_templates import ExecutiveSummaryTemplates
            
            # Initialize template system
            template_system = ExecutiveSummaryTemplates()
            
            # Generate summary using templates
            summary = template_system.generate_summary(analysis_data)
            
            logger.info("Generated executive summary using template system")
            
            return {
                "success": True,
                "summary": summary,
                "analysis_data": analysis_data,
                "template_used": True
            }
        except Exception as e:
            logger.error(f"Error generating executive summary: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis_data": analysis_data
            }
    
    @tool
    def _create_detailed_report(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed financial report"""
        try:
            user_profile = analysis_data.get("user_profile", {})
            recommendations = analysis_data.get("recommendations", {})
            market_data = analysis_data.get("market_data", {})
            risk_analysis = analysis_data.get("risk_analysis", {})
            
            # Create detailed report structure
            report = {
                "report_title": "Comprehensive Financial Analysis Report",
                "sections": {
                    "executive_summary": {
                        "title": "Executive Summary",
                        "content": "This report provides a comprehensive analysis of your financial profile and personalized investment recommendations."
                    },
                    "user_profile_analysis": {
                        "title": "Profile Analysis",
                        "content": f"Risk Level: {user_profile.get('risk_level', 'medium')}\nInvestment Goals: {', '.join(user_profile.get('investment_goals', []))}\nTime Horizon: {user_profile.get('time_horizon', 'medium')}"
                    },
                    "market_analysis": {
                        "title": "Market Analysis",
                        "content": f"Market Trend: {market_data.get('market_trend', 'stable')}\nVolatility: {market_data.get('volatility_index', 0.15)}\nEconomic Conditions: Favorable for investment"
                    },
                    "recommendations": {
                        "title": "Investment Recommendations",
                        "content": self._format_recommendations_content(recommendations)
                    },
                    "risk_analysis": {
                        "title": "Risk Analysis",
                        "content": self._format_risk_analysis_content(risk_analysis)
                    },
                    "implementation_plan": {
                        "title": "Implementation Plan",
                        "content": "1. Review recommendations\n2. Consult with advisor\n3. Begin implementation\n4. Regular monitoring"
                    }
                },
                "disclaimers": [
                    "Past performance does not guarantee future results",
                    "Investments involve risk of loss",
                    "Consult with a financial advisor before investing"
                ]
            }
            
            logger.info("Created detailed financial report")
            
            return {
                "success": True,
                "report": report,
                "analysis_data": analysis_data
            }
        except Exception as e:
            logger.error(f"Error creating detailed report: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis_data": analysis_data
            }
    
    @tool
    def _format_recommendations(self, recommendations: Dict[str, Any]) -> Dict[str, Any]:
        """Format recommendations for clear presentation"""
        try:
            formatted = {
                "primary_recommendations": [],
                "secondary_recommendations": [],
                "allocation_summary": "",
                "expected_returns": "",
                "risk_considerations": []
            }
            
            # Format primary recommendations
            for rec in recommendations.get("primary_recommendations", []):
                formatted["primary_recommendations"].append({
                    "product_name": rec.get("name", ""),
                    "product_type": rec.get("type", ""),
                    "allocation": rec.get("allocation", ""),
                    "reasoning": rec.get("reasoning", ""),
                    "key_features": [
                        "Professional management",
                        "Diversified portfolio",
                        "Risk-appropriate allocation"
                    ]
                })
            
            # Format secondary recommendations
            for rec in recommendations.get("secondary_recommendations", []):
                formatted["secondary_recommendations"].append({
                    "product_name": rec.get("name", ""),
                    "product_type": rec.get("type", ""),
                    "allocation": rec.get("allocation", ""),
                    "reasoning": rec.get("reasoning", "")
                })
            
            # Create allocation summary
            total_primary = sum(float(rec.get("allocation", "0%").rstrip("%")) for rec in recommendations.get("primary_recommendations", []))
            total_secondary = sum(float(rec.get("allocation", "0%").rstrip("%")) for rec in recommendations.get("secondary_recommendations", []))
            
            formatted["allocation_summary"] = f"Primary: {total_primary}%, Secondary: {total_secondary}%"
            formatted["expected_returns"] = recommendations.get("expected_returns", "8-12% annually")
            formatted["risk_considerations"] = recommendations.get("risk_considerations", [])
            
            logger.info("Formatted recommendations for presentation")
            
            return {
                "success": True,
                "formatted_recommendations": formatted,
                "original_recommendations": recommendations
            }
        except Exception as e:
            logger.error(f"Error formatting recommendations: {e}")
            return {
                "success": False,
                "error": str(e),
                "recommendations": recommendations
            }
    
    @tool
    def _write_risk_analysis(self, risk_data: Dict[str, Any]) -> Dict[str, Any]:
        """Write comprehensive risk analysis"""
        try:
            risk_level = risk_data.get("risk_level", "medium")
            risk_metrics = risk_data.get("risk_metrics", {})
            portfolio_risk = risk_data.get("portfolio_risk", {})
            
            # Create risk analysis report
            risk_analysis = {
                "risk_profile": {
                    "level": risk_level,
                    "description": f"Your risk tolerance is {risk_level}",
                    "implications": self._get_risk_implications(risk_level)
                },
                "risk_metrics": {
                    "volatility": f"{risk_metrics.get('volatility', 0.15):.1%}",
                    "sharpe_ratio": f"{risk_metrics.get('sharpe_ratio', 0.65):.2f}",
                    "max_drawdown": f"{risk_metrics.get('max_drawdown', -0.20):.1%}",
                    "var_95": f"{risk_metrics.get('var_95', -0.12):.1%}"
                },
                "portfolio_analysis": {
                    "total_risk": f"{portfolio_risk.get('total_risk', 0.12):.1%}",
                    "diversification_score": f"{portfolio_risk.get('diversification_score', 0.75):.0%}",
                    "concentration_risk": portfolio_risk.get("concentration_risk", "low")
                },
                "risk_management": {
                    "strategies": [
                        "Regular portfolio rebalancing",
                        "Diversification across asset classes",
                        "Risk monitoring and adjustment",
                        "Emergency fund maintenance"
                    ],
                    "monitoring_frequency": "Quarterly reviews recommended"
                }
            }
            
            logger.info("Wrote comprehensive risk analysis")
            
            return {
                "success": True,
                "risk_analysis": risk_analysis,
                "risk_data": risk_data
            }
        except Exception as e:
            logger.error(f"Error writing risk analysis: {e}")
            return {
                "success": False,
                "error": str(e),
                "risk_data": risk_data
            }
    
    def _format_recommendations_content(self, recommendations: Dict[str, Any]) -> str:
        """Format recommendations content for report"""
        content = "Based on your profile and market conditions, we recommend:\n\n"
        
        # Primary recommendations
        content += "Primary Recommendations:\n"
        for rec in recommendations.get("primary_recommendations", []):
            content += f"• {rec.get('name', '')} ({rec.get('allocation', '')}) - {rec.get('reasoning', '')}\n"
        
        # Secondary recommendations
        content += "\nSecondary Recommendations:\n"
        for rec in recommendations.get("secondary_recommendations", []):
            content += f"• {rec.get('name', '')} ({rec.get('allocation', '')}) - {rec.get('reasoning', '')}\n"
        
        content += f"\nExpected Returns: {recommendations.get('expected_returns', '8-12% annually')}"
        
        return content
    
    def _format_risk_analysis_content(self, risk_analysis: Dict[str, Any]) -> str:
        """Format risk analysis content for report"""
        content = "Risk Analysis Summary:\n\n"
        
        risk_level = risk_analysis.get("risk_level", "medium")
        content += f"Risk Profile: {risk_level} risk tolerance\n"
        content += f"Risk Score: {risk_analysis.get('risk_score', 0)}/10\n"
        content += f"Risk Description: {risk_analysis.get('risk_description', '')}\n\n"
        
        content += "Risk Factors Considered:\n"
        factors = risk_analysis.get("factors", {})
        for factor, value in factors.items():
            content += f"• {factor.replace('_', ' ').title()}: {value}\n"
        
        return content
    
    def _get_risk_implications(self, risk_level: str) -> List[str]:
        """Get implications for different risk levels"""
        if risk_level == "low":
            return [
                "Conservative investment approach",
                "Focus on capital preservation",
                "Lower expected returns",
                "Stable, predictable performance"
            ]
        elif risk_level == "medium":
            return [
                "Balanced growth and income",
                "Moderate volatility expected",
                "Diversified portfolio approach",
                "Long-term investment focus"
            ]
        else:  # high risk
            return [
                "Aggressive growth strategy",
                "Higher volatility expected",
                "Potential for significant returns",
                "Requires active monitoring"
            ]
    
    def get_agent(self) -> Agent:
        """Get the CrewAI agent"""
        return self.agent 
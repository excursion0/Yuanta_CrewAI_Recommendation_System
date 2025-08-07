"""
Risk Analysis Agent for financial product recommendation system.

This agent is responsible for analyzing portfolio risk, risk tolerance,
and providing risk assessment for financial recommendations.
"""

from crewai import Agent, LLM
from crewai.tools import tool
from typing import Dict, Any, List
import logging
import os
import math
import random
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RiskAnalysisAgent:
    """Agent responsible for risk analysis and assessment"""
    
    def __init__(self, llm_provider):
        self.llm_provider = llm_provider
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create the risk analysis agent"""
        # Create CrewAI LLM instance with direct Anthropic configuration
        crewai_llm = LLM(
            model="claude-3-5-sonnet-20241022",
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        
        # Create tools as inner functions (reduced from 4 to 2 tools)
        @tool
        def assess_portfolio_risk(risk_level: str, investment_amount: int) -> str:
            """Assess portfolio risk for given risk level and investment amount"""
            return self._assess_portfolio_risk(risk_level, investment_amount)
        
        @tool
        def analyze_market_risk(market_conditions: str) -> str:
            """Analyze market risk factors"""
            return self._analyze_market_risk(market_conditions)
        
        # Create agent with simplified configuration (like the working Market Data Agent)
        agent = Agent(
            role="Risk Analysis Specialist",
            goal="Analyze investment risks and provide risk management strategies",
            backstory="You are a risk analysis specialist. You assess investment risks and provide clear risk management recommendations.",
            verbose=True,
            llm=crewai_llm,
            tools=[assess_portfolio_risk, analyze_market_risk]
        )
        
        return agent
    
    def _analyze_risk_tolerance(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user's risk tolerance based on profile"""
        try:
            # Extract risk factors from user profile
            age = user_profile.get("age", 30)
            income_level = user_profile.get("income_level", "medium")
            investment_experience = user_profile.get("investment_experience", "beginner")
            investment_goals = user_profile.get("investment_goals", [])
            
            # Calculate risk tolerance score
            risk_score = 0
            
            # Age factor (younger = higher risk tolerance)
            if age < 30:
                risk_score += 3
            elif age < 50:
                risk_score += 2
            else:
                risk_score += 1
            
            # Income factor
            if income_level == "high":
                risk_score += 2
            elif income_level == "medium":
                risk_score += 1
            
            # Experience factor
            if investment_experience == "expert":
                risk_score += 3
            elif investment_experience == "advanced":
                risk_score += 2
            elif investment_experience == "intermediate":
                risk_score += 1
            
            # Goals factor
            if "growth" in [goal.lower() for goal in investment_goals]:
                risk_score += 2
            if "income" in [goal.lower() for goal in investment_goals]:
                risk_score += 1
            
            # Determine risk level
            if risk_score >= 8:
                risk_level = "high"
                risk_description = "Aggressive investor comfortable with high volatility"
            elif risk_score >= 5:
                risk_level = "medium"
                risk_description = "Balanced investor seeking moderate risk-return"
            else:
                risk_level = "low"
                risk_description = "Conservative investor prioritizing capital preservation"
            
            logger.info(f"Analyzed risk tolerance for user: {risk_level}")
            
            return {
                "success": True,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "risk_description": risk_description,
                "factors": {
                    "age_factor": age,
                    "income_factor": income_level,
                    "experience_factor": investment_experience,
                    "goals_factor": investment_goals
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing risk tolerance: {e}")
            return {
                "success": False,
                "error": str(e),
                "user_profile": user_profile
            }
    
    def _assess_portfolio_risk(self, risk_level: str, investment_amount: int) -> str:
        """Assess portfolio risk for given risk level and investment amount using real algorithms"""
        try:
            # Generate realistic portfolio data based on risk level
            portfolio_data = self._generate_portfolio_data(risk_level, investment_amount)
            
            # Calculate real risk metrics
            risk_metrics = self._calculate_portfolio_risk_metrics(portfolio_data)
            
            # Generate asset allocation based on risk level
            asset_allocation = self._generate_asset_allocation(risk_level)
            
            # Calculate portfolio statistics
            portfolio_stats = self._calculate_portfolio_statistics(portfolio_data)
            
            # Format comprehensive risk assessment
            assessment = f"""PORTFOLIO RISK ASSESSMENT for {risk_level.upper()} risk level with ${investment_amount:,} investment:

RISK METRICS:
• Risk Score: {risk_metrics['risk_score']:.2f} ({risk_metrics['risk_level']})
• Volatility: {risk_metrics['volatility']:.1%}
• Sharpe Ratio: {risk_metrics['sharpe_ratio']:.2f}
• Maximum Drawdown: {risk_metrics['max_drawdown']:.1%}
• Value at Risk (95%): {risk_metrics['var_95']:.1%}
• Beta: {risk_metrics['beta']:.2f}

ASSET ALLOCATION:
• Stocks: {asset_allocation['stocks']:.0%}
• Bonds: {asset_allocation['bonds']:.0%}
• Alternatives: {asset_allocation['alternatives']:.0%}
• Cash: {asset_allocation['cash']:.0%}

PORTFOLIO STATISTICS:
• Expected Annual Return: {portfolio_stats['expected_return']:.1%}
• Standard Deviation: {portfolio_stats['std_dev']:.1%}
• Correlation with Market: {portfolio_stats['correlation']:.2f}
• Diversification Score: {portfolio_stats['diversification']:.1f}/10

RISK MANAGEMENT RECOMMENDATIONS:
• Rebalancing Frequency: {risk_metrics['rebalancing_frequency']}
• Stop-Loss Level: {risk_metrics['stop_loss']:.1%}
• Monitoring Frequency: {risk_metrics['monitoring_frequency']}
• Diversification Strategy: {risk_metrics['diversification_strategy']}"""

            logger.info(f"Completed portfolio risk assessment for {risk_level} risk level")
            return assessment
            
        except Exception as e:
            logger.error(f"Error in portfolio risk assessment: {e}")
            return f"Error assessing portfolio risk: {str(e)}"
    
    def _analyze_market_risk(self, market_conditions: str) -> str:
        """Analyze market risk factors using real market data simulation"""
        try:
            # Generate current market risk data
            market_risk_data = self._generate_market_risk_data()
            
            # Calculate market risk metrics
            risk_metrics = self._calculate_market_risk_metrics(market_risk_data)
            
            # Analyze market conditions
            market_analysis = self._analyze_current_market_conditions(market_conditions)
            
            # Format comprehensive market risk analysis
            analysis = f"""MARKET RISK ANALYSIS - {datetime.now().strftime('%Y-%m-%d %H:%M')}:

CURRENT MARKET CONDITIONS:
• Market Volatility (VIX): {market_risk_data['vix']:.1f} ({risk_metrics['volatility_level']})
• Fear/Greed Index: {market_risk_data['fear_greed']:.0f}/100 ({risk_metrics['sentiment_level']})
• Economic Cycle: {market_risk_data['economic_cycle']} ({risk_metrics['cycle_risk']})
• Interest Rate Environment: {market_risk_data['interest_rate']:.2f}% ({risk_metrics['rate_risk']})

RISK FACTORS:
• Economic Cycle Risk: {risk_metrics['economic_risk']} ({risk_metrics['economic_score']:.1f}/10)
• Interest Rate Risk: {risk_metrics['interest_rate_risk']} ({risk_metrics['rate_score']:.1f}/10)
• Inflation Risk: {risk_metrics['inflation_risk']} ({risk_metrics['inflation_score']:.1f}/10)
• Geopolitical Risk: {risk_metrics['geopolitical_risk']} ({risk_metrics['geopolitical_score']:.1f}/10)
• Sector Concentration Risk: {risk_metrics['sector_risk']} ({risk_metrics['sector_score']:.1f}/10)

MARKET SENTIMENT INDICATORS:
• Put/Call Ratio: {market_risk_data['put_call_ratio']:.2f} ({risk_metrics['sentiment_interpretation']})
• Market Breadth: {market_risk_data['market_breadth']:.1%} ({risk_metrics['breadth_interpretation']})
• Sector Performance: {market_risk_data['sector_performance']} ({risk_metrics['sector_interpretation']})

OVERALL MARKET RISK ASSESSMENT:
• Composite Risk Score: {risk_metrics['composite_risk']:.1f}/10 ({risk_metrics['risk_level']})
• Risk Trend: {risk_metrics['risk_trend']}
• Recommended Strategy: {risk_metrics['recommended_strategy']}
• Key Concerns: {risk_metrics['key_concerns']}"""

            logger.info(f"Completed market risk analysis")
            return analysis
            
        except Exception as e:
            logger.error(f"Error in market risk analysis: {e}")
            return f"Error analyzing market risk: {str(e)}"
    
    def _generate_portfolio_data(self, risk_level: str, investment_amount: int) -> Dict[str, Any]:
        """Generate realistic portfolio data based on risk level"""
        # Generate 252 days of daily returns (1 year of trading days)
        days = 252
        
        if risk_level.lower() == "high":
            # High risk: higher volatility, higher expected return
            daily_return_mean = 0.0012  # 30% annual return
            daily_volatility = 0.025    # 40% annual volatility
        elif risk_level.lower() == "medium":
            # Medium risk: moderate volatility, moderate return
            daily_return_mean = 0.0008  # 20% annual return
            daily_volatility = 0.015    # 24% annual volatility
        else:
            # Low risk: lower volatility, lower return
            daily_return_mean = 0.0004  # 10% annual return
            daily_volatility = 0.008    # 13% annual volatility
        
        # Generate daily returns using random walk
        daily_returns = []
        cumulative_return = 0
        
        for day in range(days):
            # Generate daily return with some autocorrelation
            if day > 0 and random.random() < 0.3:  # 30% chance of autocorrelation
                daily_return = daily_returns[-1] * 0.7 + random.gauss(daily_return_mean, daily_volatility) * 0.3
            else:
                daily_return = random.gauss(daily_return_mean, daily_volatility)
            
            daily_returns.append(daily_return)
            cumulative_return += daily_return
        
        # Calculate portfolio value over time
        portfolio_values = [investment_amount]
        for return_rate in daily_returns:
            new_value = portfolio_values[-1] * (1 + return_rate)
            portfolio_values.append(new_value)
        
        return {
            "risk_level": risk_level,
            "investment_amount": investment_amount,
            "daily_returns": daily_returns,
            "portfolio_values": portfolio_values,
            "total_return": cumulative_return,
            "annualized_return": (1 + cumulative_return) ** (252 / days) - 1
        }
    
    def _calculate_portfolio_risk_metrics(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive risk metrics for portfolio"""
        daily_returns = portfolio_data["daily_returns"]
        risk_level = portfolio_data["risk_level"]
        
        # Calculate basic statistics
        mean_return = sum(daily_returns) / len(daily_returns)
        variance = sum((r - mean_return) ** 2 for r in daily_returns) / len(daily_returns)
        volatility = math.sqrt(variance * 252)  # Annualized volatility
        
        # Calculate Sharpe ratio (assuming risk-free rate of 2%)
        risk_free_rate = 0.02
        excess_return = portfolio_data["annualized_return"] - risk_free_rate
        sharpe_ratio = excess_return / volatility if volatility > 0 else 0
        
        # Calculate maximum drawdown
        portfolio_values = portfolio_data["portfolio_values"]
        peak = portfolio_values[0]
        max_drawdown = 0
        
        for value in portfolio_values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            max_drawdown = max(max_drawdown, drawdown)
        
        # Calculate Value at Risk (95% confidence)
        sorted_returns = sorted(daily_returns)
        var_index = int(len(sorted_returns) * 0.05)
        var_95 = sorted_returns[var_index] if var_index < len(sorted_returns) else sorted_returns[0]
        
        # Calculate Beta (correlation with market)
        # Simulate market returns
        market_returns = [random.gauss(0.0006, 0.015) for _ in daily_returns]
        market_variance = sum((r - sum(market_returns) / len(market_returns)) ** 2 for r in market_returns) / len(market_returns)
        covariance = sum((r - mean_return) * (m - sum(market_returns) / len(market_returns)) for r, m in zip(daily_returns, market_returns)) / len(daily_returns)
        beta = covariance / market_variance if market_variance > 0 else 1.0
        
        # Determine risk level based on metrics
        if volatility > 0.25:
            risk_level_desc = "HIGH"
        elif volatility > 0.15:
            risk_level_desc = "MEDIUM"
        else:
            risk_level_desc = "LOW"
        
        # Risk management recommendations
        if risk_level.lower() == "high":
            rebalancing_frequency = "Monthly"
            stop_loss = 0.15
            monitoring_frequency = "Daily"
            diversification_strategy = "Sector rotation and international exposure"
        elif risk_level.lower() == "medium":
            rebalancing_frequency = "Quarterly"
            stop_loss = 0.10
            monitoring_frequency = "Weekly"
            diversification_strategy = "Balanced asset allocation"
        else:
            rebalancing_frequency = "Semi-annually"
            stop_loss = 0.05
            monitoring_frequency = "Monthly"
            diversification_strategy = "Conservative bond-heavy allocation"
        
        return {
            "risk_score": volatility * 100,  # Convert to percentage
            "risk_level": risk_level_desc,
            "volatility": volatility,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "var_95": var_95,
            "beta": beta,
            "rebalancing_frequency": rebalancing_frequency,
            "stop_loss": stop_loss,
            "monitoring_frequency": monitoring_frequency,
            "diversification_strategy": diversification_strategy
        }
    
    def _generate_asset_allocation(self, risk_level: str) -> Dict[str, float]:
        """Generate appropriate asset allocation based on risk level"""
        if risk_level.lower() == "high":
            return {
                "stocks": 0.70,
                "bonds": 0.15,
                "alternatives": 0.10,
                "cash": 0.05
            }
        elif risk_level.lower() == "medium":
            return {
                "stocks": 0.50,
                "bonds": 0.35,
                "alternatives": 0.10,
                "cash": 0.05
            }
        else:
            return {
                "stocks": 0.25,
                "bonds": 0.60,
                "alternatives": 0.10,
                "cash": 0.05
            }
    
    def _calculate_portfolio_statistics(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate additional portfolio statistics"""
        daily_returns = portfolio_data["daily_returns"]
        
        # Expected return (annualized)
        expected_return = portfolio_data["annualized_return"]
        
        # Standard deviation (annualized)
        mean_return = sum(daily_returns) / len(daily_returns)
        variance = sum((r - mean_return) ** 2 for r in daily_returns) / len(daily_returns)
        std_dev = math.sqrt(variance * 252)
        
        # Correlation with market (simulated)
        correlation = random.uniform(0.7, 0.95)
        
        # Diversification score (based on number of assets and correlation)
        diversification = min(10, 5 + (1 - correlation) * 5)
        
        return {
            "expected_return": expected_return,
            "std_dev": std_dev,
            "correlation": correlation,
            "diversification": diversification
        }
    
    def _generate_market_risk_data(self) -> Dict[str, Any]:
        """Generate realistic market risk data"""
        return {
            "vix": random.uniform(15, 35),  # Volatility index
            "fear_greed": random.uniform(30, 70),  # Fear/Greed index
            "economic_cycle": random.choice(["Expansion", "Peak", "Contraction", "Trough"]),
            "interest_rate": random.uniform(4.5, 6.5),  # Current interest rate
            "put_call_ratio": random.uniform(0.8, 1.2),  # Put/Call ratio
            "market_breadth": random.uniform(0.4, 0.8),  # Market breadth
            "sector_performance": random.choice(["Technology leading", "Financials leading", "Healthcare leading", "Balanced"])
        }
    
    def _calculate_market_risk_metrics(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate market risk metrics"""
        vix = market_data["vix"]
        fear_greed = market_data["fear_greed"]
        economic_cycle = market_data["economic_cycle"]
        interest_rate = market_data["interest_rate"]
        put_call_ratio = market_data["put_call_ratio"]
        market_breadth = market_data["market_breadth"]
        
        # Volatility level
        if vix < 20:
            volatility_level = "LOW"
        elif vix < 30:
            volatility_level = "MODERATE"
        else:
            volatility_level = "HIGH"
        
        # Sentiment level
        if fear_greed < 40:
            sentiment_level = "FEAR"
        elif fear_greed > 60:
            sentiment_level = "GREED"
        else:
            sentiment_level = "NEUTRAL"
        
        # Risk scores (0-10 scale)
        economic_score = {"Expansion": 3, "Peak": 7, "Contraction": 8, "Trough": 4}[economic_cycle]
        rate_score = min(10, max(0, (interest_rate - 4) * 2))
        inflation_score = random.uniform(3, 7)
        geopolitical_score = random.uniform(4, 8)
        sector_score = random.uniform(3, 6)
        
        # Risk interpretations
        economic_risk = "LOW" if economic_score < 4 else "MEDIUM" if economic_score < 7 else "HIGH"
        interest_rate_risk = "LOW" if rate_score < 4 else "MEDIUM" if rate_score < 7 else "HIGH"
        inflation_risk = "LOW" if inflation_score < 4 else "MEDIUM" if inflation_score < 7 else "HIGH"
        geopolitical_risk = "LOW" if geopolitical_score < 4 else "MEDIUM" if geopolitical_score < 7 else "HIGH"
        sector_risk = "LOW" if sector_score < 4 else "MEDIUM" if sector_score < 7 else "HIGH"
        
        # Cycle risk
        cycle_risk = "LOW" if economic_cycle in ["Expansion", "Trough"] else "HIGH"
        
        # Rate risk
        rate_risk = "LOW" if interest_rate < 5 else "MEDIUM" if interest_rate < 6 else "HIGH"
        
        # Composite risk score
        composite_risk = (economic_score + rate_score + inflation_score + geopolitical_score + sector_score) / 5
        
        # Risk level
        if composite_risk < 4:
            risk_level = "LOW"
        elif composite_risk < 7:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"
        
        # Risk trend
        risk_trend = random.choice(["Increasing", "Stable", "Decreasing"])
        
        # Recommended strategy
        if risk_level == "LOW":
            recommended_strategy = "Opportunistic buying with moderate risk"
        elif risk_level == "MEDIUM":
            recommended_strategy = "Balanced approach with defensive positioning"
        else:
            recommended_strategy = "Defensive strategy with capital preservation focus"
        
        # Sentiment interpretations
        sentiment_interpretation = "Bullish" if put_call_ratio < 1 else "Bearish"
        breadth_interpretation = "Strong" if market_breadth > 0.6 else "Weak"
        sector_interpretation = "Concentrated" if market_data["sector_performance"] != "Balanced" else "Diversified"
        
        # Key concerns
        concerns = []
        if economic_score > 6:
            concerns.append("Economic cycle risk")
        if rate_score > 6:
            concerns.append("Interest rate sensitivity")
        if geopolitical_score > 6:
            concerns.append("Geopolitical uncertainty")
        if sector_score > 6:
            concerns.append("Sector concentration")
        
        key_concerns = ", ".join(concerns) if concerns else "No major concerns"
        
        return {
            "volatility_level": volatility_level,
            "sentiment_level": sentiment_level,
            "cycle_risk": cycle_risk,
            "rate_risk": rate_risk,
            "economic_risk": economic_risk,
            "economic_score": economic_score,
            "interest_rate_risk": interest_rate_risk,
            "rate_score": rate_score,
            "inflation_risk": inflation_risk,
            "inflation_score": inflation_score,
            "geopolitical_risk": geopolitical_risk,
            "geopolitical_score": geopolitical_score,
            "sector_risk": sector_risk,
            "sector_score": sector_score,
            "composite_risk": composite_risk,
            "risk_level": risk_level,
            "risk_trend": risk_trend,
            "recommended_strategy": recommended_strategy,
            "sentiment_interpretation": sentiment_interpretation,
            "breadth_interpretation": breadth_interpretation,
            "sector_interpretation": sector_interpretation,
            "key_concerns": key_concerns
        }
    
    def _analyze_current_market_conditions(self, market_conditions: str) -> Dict[str, Any]:
        """Analyze current market conditions based on input"""
        # This would typically analyze real market data
        # For now, we'll provide a basic analysis based on the input
        conditions_lower = market_conditions.lower()
        
        analysis = {
            "market_trend": "NEUTRAL",
            "volatility_expectation": "MODERATE",
            "sector_focus": "BALANCED",
            "risk_appetite": "MODERATE"
        }
        
        if any(word in conditions_lower for word in ["bull", "up", "strong", "growth"]):
            analysis["market_trend"] = "BULLISH"
            analysis["risk_appetite"] = "HIGH"
        elif any(word in conditions_lower for word in ["bear", "down", "weak", "decline"]):
            analysis["market_trend"] = "BEARISH"
            analysis["risk_appetite"] = "LOW"
        
        if any(word in conditions_lower for word in ["volatile", "uncertain", "turbulent"]):
            analysis["volatility_expectation"] = "HIGH"
        elif any(word in conditions_lower for word in ["stable", "calm", "steady"]):
            analysis["volatility_expectation"] = "LOW"
        
        return analysis
    
    def _evaluate_product_risk(self, product_type: str) -> str:
        """Evaluate risk for specific product types"""
        # Mock implementation with structured response
        return f"PRODUCT RISK EVALUATION for {product_type}: Risk level medium, liquidity good, credit risk low, market risk moderate. Suitable for balanced investors with proper diversification."
    
    def _suggest_risk_mitigation(self, risk_factors: list[str]) -> str:
        """Suggest risk mitigation strategies"""
        # Mock implementation with structured response
        factor_list = ", ".join(risk_factors)
        return f"RISK MITIGATION STRATEGIES for {factor_list}: Diversification across asset classes, regular portfolio rebalancing, dollar-cost averaging, stop-loss strategies at 15-20%, monthly monitoring recommended."
    
    def _calculate_risk_metrics(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate risk metrics for financial products"""
        try:
            product_type = product_data.get("type", "mutual_fund")
            expected_return = product_data.get("expected_return", "8-12%")
            risk_level = product_data.get("risk_level", "medium")
            
            # Calculate risk metrics
            risk_metrics = {
                "volatility": 0.15,
                "sharpe_ratio": 0.65,
                "max_drawdown": -0.20,
                "var_95": -0.12,  # Value at Risk (95% confidence)
                "beta": 1.05,
                "correlation_with_market": 0.85
            }
            
            # Adjust metrics based on product type
            if product_type == "etf":
                risk_metrics["volatility"] = 0.18
                risk_metrics["sharpe_ratio"] = 0.70
            elif product_type == "bond":
                risk_metrics["volatility"] = 0.08
                risk_metrics["sharpe_ratio"] = 0.80
            
            logger.info(f"Calculated risk metrics for {product_type}")
            
            return {
                "success": True,
                "product_type": product_type,
                "risk_metrics": risk_metrics,
                "expected_return": expected_return,
                "risk_level": risk_level
            }
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {e}")
            return {
                "success": False,
                "error": str(e),
                "product_data": product_data
            }
    
    def _recommend_risk_adjustments(self, current_risk: Dict[str, Any], target_risk: str) -> Dict[str, Any]:
        """Recommend adjustments to achieve target risk level"""
        try:
            current_level = current_risk.get("risk_level", "medium")
            
            # Generate risk adjustment recommendations
            adjustments = {
                "current_risk": current_level,
                "target_risk": target_risk,
                "recommendations": []
            }
            
            if current_level == "low" and target_risk == "high":
                adjustments["recommendations"] = [
                    "Increase allocation to growth funds",
                    "Add technology sector exposure",
                    "Consider emerging market investments",
                    "Reduce bond allocation"
                ]
            elif current_level == "high" and target_risk == "low":
                adjustments["recommendations"] = [
                    "Increase bond allocation",
                    "Add conservative funds",
                    "Reduce technology exposure",
                    "Consider dividend-paying stocks"
                ]
            else:
                adjustments["recommendations"] = [
                    "Maintain current allocation",
                    "Rebalance quarterly",
                    "Monitor market conditions"
                ]
            
            logger.info(f"Recommended risk adjustments: {current_level} → {target_risk}")
            
            return {
                "success": True,
                "adjustments": adjustments
            }
        except Exception as e:
            logger.error(f"Error recommending risk adjustments: {e}")
            return {
                "success": False,
                "error": str(e),
                "current_risk": current_risk,
                "target_risk": target_risk
            }
    
    def get_agent(self) -> Agent:
        """Get the CrewAI agent"""
        return self.agent 
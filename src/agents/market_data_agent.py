"""
Enhanced Market Data Agent for CrewAI financial analysis.

This agent inherits from BaseAgent and is responsible for fetching and analyzing 
market data, economic indicators, and market conditions with enhanced logging,
validation, and performance tracking.
"""

import os
import logging
from crewai import Agent, LLM
from crewai.tools import tool
from dotenv import load_dotenv
from typing import Dict, Any, Optional

from src.agents.base_agent import BaseAgent

load_dotenv()


class MarketDataAgent(BaseAgent):
    """
    Enhanced Market Data Agent for financial analysis.
    
    Inherits from BaseAgent to get common functionality including:
    - Enhanced logging with context
    - Performance tracking
    - Input validation
    - Error handling
    - Configuration validation
    """
    
    def __init__(self, llm_provider: Optional[str] = None):
        """
        Initialize the enhanced market data agent.
        
        Args:
            llm_provider: Optional LLM provider override
        """
        # Call parent constructor with custom agent name
        super().__init__(llm_provider=llm_provider, agent_name="MarketDataAgent")
        
        # Validate configuration after initialization
        if not self.validate_agent_configuration():
            self.log_error("Market data agent configuration validation failed")
    
    def _create_agent(self) -> Agent:
        """
        Create the enhanced market data agent with improved error handling.
        
        Returns:
            Agent: Configured CrewAI agent
        """
        try:
            # Use parent's LLM creation with error handling
            crewai_llm = self._create_llm()
            
            # Create tools with enhanced error handling
            @tool
            def fetch_market_data(query: str) -> str:
                """Fetch realistic market data based on query with enhanced logging"""
                start_time = self._performance_metrics.get('last_call_time')
                
                try:
                    from src.data.market_data_simulator import MarketDataSimulator
                    
                    # Initialize simulator
                    simulator = MarketDataSimulator()
                    
                    # Get comprehensive market data
                    market_data = simulator.get_market_data()
                    global_data = simulator.get_global_market_data()
                    commodity_data = simulator.get_commodity_data()
                    currency_data = simulator.get_currency_data()
                    
                    # Format response based on query
                    response = self._format_market_response(query, market_data, global_data, commodity_data, currency_data)
                    
                    # Track performance
                    if start_time:
                        self.track_performance("fetch_market_data", start_time.timestamp())
                    
                    self.log_info(f"Market data fetched successfully for query: {query[:50]}...")
                    return response
                    
                except Exception as e:
                    self.log_error(f"Error fetching market data: {e}")
                    return f"Error fetching market data: {str(e)}"
            
            @tool
            def analyze_economic_indicators(indicators: str) -> str:
                """Analyze economic indicators with enhanced logging"""
                start_time = self._performance_metrics.get('last_call_time')
                
                try:
                    from src.data.market_data_simulator import MarketDataSimulator
                    
                    # Initialize simulator
                    simulator = MarketDataSimulator()
                    
                    # Get economic indicators
                    economic_data = simulator.get_economic_indicators()
                    
                    # Format response
                    response = self._format_economic_analysis(indicators, economic_data)
                    
                    # Track performance
                    if start_time:
                        self.track_performance("analyze_economic_indicators", start_time.timestamp())
                    
                    self.log_info(f"Economic indicators analyzed successfully for: {indicators[:50]}...")
                    return response
                    
                except Exception as e:
                    self.log_error(f"Error analyzing economic indicators: {e}")
                    return f"Error analyzing economic indicators: {str(e)}"
            
            # Create agent with enhanced configuration
            agent = Agent(
                role="Market Data Specialist",
                goal="Provide comprehensive market data analysis and economic insights",
                backstory="""You are an expert market data specialist with deep knowledge of 
                financial markets, economic indicators, and market analysis. You provide 
                accurate, timely, and comprehensive market data to support investment decisions.""",
                verbose=True,
                llm=crewai_llm,
                tools=[fetch_market_data, analyze_economic_indicators]
            )
            
            self.log_info("Market data agent created successfully")
            return agent
            
        except Exception as e:
            self.log_error(f"Failed to create market data agent: {e}")
            raise
    
    def _format_market_response(self, query: str, market_data: Dict, global_data: Dict, 
                               commodity_data: Dict, currency_data: Dict) -> str:
        """
        Format market response based on query type.
        
        Args:
            query: User query
            market_data: Market data dictionary
            global_data: Global market data
            commodity_data: Commodity data
            currency_data: Currency data
            
        Returns:
            str: Formatted response
        """
        query_lower = query.lower()
        
        if "stock" in query_lower or "equity" in query_lower:
            return self._format_stock_data(query, market_data)
        elif "global" in query_lower or "international" in query_lower:
            return self._format_global_data(query, global_data)
        elif "commodity" in query_lower:
            return self._format_commodity_data(query, commodity_data)
        elif "currency" in query_lower or "forex" in query_lower:
            return self._format_currency_data(query, currency_data)
        else:
            return self._format_general_market_data(query, market_data)
    
    def _format_stock_data(self, query: str, market_data: Dict) -> str:
        """Format stock market data response."""
        symbols_data = market_data["symbols"]
        top_gainers = sorted(symbols_data.items(), key=lambda x: x[1]["change_percent"], reverse=True)[:3]
        top_losers = sorted(symbols_data.items(), key=lambda x: x[1]["change_percent"])[:3]
        
        response = f"MARKET DATA ANALYSIS for '{query}':\n"
        response += f"Overall Trend: {market_data['market_summary']['overall_trend'].upper()}\n"
        response += f"Average Change: {market_data['market_summary']['average_change']}%\n"
        response += f"Advancing: {market_data['market_summary']['advancing']}, Declining: {market_data['market_summary']['declining']}\n\n"
        
        response += "TOP GAINERS:\n"
        for symbol, data in top_gainers:
            response += f"• {symbol}: ${data['price']} (+{data['change_percent']}%)\n"
        
        response += "\nTOP LOSERS:\n"
        for symbol, data in top_losers:
            response += f"• {symbol}: ${data['price']} ({data['change_percent']}%)\n"
        
        response += f"\nSECTOR PERFORMANCE:\n"
        for sector, data in market_data["sector_performance"].items():
            response += f"• {sector.title()}: {data['return']}% (Vol: {data['volatility']}%)\n"
        
        return response
    
    def _format_global_data(self, query: str, global_data: Dict) -> str:
        """Format global market data response."""
        response = f"GLOBAL MARKET DATA for '{query}':\n"
        response += "MAJOR INDICES:\n"
        for index, data in global_data["indices"].items():
            response += f"• {index}: {data['price']} ({data['change_percent']:+}%)\n"
        
        response += f"\nREGIONAL PERFORMANCE:\n"
        for region, data in global_data["regional_performance"].items():
            if "average_return" in data:
                response += f"• {region.replace('_', ' ').title()}: {data['average_return']}%\n"
        
        return response
    
    def _format_commodity_data(self, query: str, commodity_data: Dict) -> str:
        """Format commodity data response."""
        response = f"COMMODITY MARKET DATA for '{query}':\n"
        for commodity, data in commodity_data["commodities"].items():
            response += f"• {commodity}: ${data['price']} ({data['change_percent']:+}%) {data['unit']}\n"
        response += f"\nCommodity Index: {commodity_data['commodity_index']}%"
        
        return response
    
    def _format_currency_data(self, query: str, currency_data: Dict) -> str:
        """Format currency data response."""
        response = f"CURRENCY MARKET DATA for '{query}':\n"
        for pair, data in currency_data["exchange_rates"].items():
            response += f"• {pair}: {data['rate']} ({data['change_percent']:+}%)\n"
        response += f"\nDollar Index: {currency_data['dollar_index']}%"
        
        return response
    
    def _format_general_market_data(self, query: str, market_data: Dict) -> str:
        """Format general market data response."""
        response = f"COMPREHENSIVE MARKET DATA for '{query}':\n"
        response += f"Market Trend: {market_data['market_summary']['overall_trend'].upper()}\n"
        response += f"Average Change: {market_data['market_summary']['average_change']}%\n"
        response += f"Total Volume: {market_data['market_summary']['total_volume']:,}\n\n"
        
        response += "KEY SECTORS:\n"
        for sector, data in market_data["sector_performance"].items():
            response += f"• {sector.title()}: {data['return']}% (Vol: {data['volatility']}%)\n"
        
        return response
    
    def _format_economic_analysis(self, indicators: str, economic_data: Dict) -> str:
        """
        Format economic indicators analysis.
        
        Args:
            indicators: Requested indicators
            economic_data: Economic data dictionary
            
        Returns:
            str: Formatted economic analysis
        """
        response = f"ECONOMIC INDICATORS ANALYSIS for '{indicators}':\n\n"
        
        response += "KEY INDICATORS:\n"
        for indicator, data in economic_data["indicators"].items():
            response += f"• {indicator}: {data['value']} ({data['change']:+}%)\n"
        
        response += f"\nECONOMIC OUTLOOK:\n"
        response += f"• GDP Growth: {economic_data['outlook']['gdp_growth']}%\n"
        response += f"• Inflation Rate: {economic_data['outlook']['inflation_rate']}%\n"
        response += f"• Unemployment Rate: {economic_data['outlook']['unemployment_rate']}%\n"
        response += f"• Interest Rate: {economic_data['outlook']['interest_rate']}%\n"
        
        return response
    
    def get_market_data_summary(self) -> Dict[str, Any]:
        """
        Get a summary of market data agent capabilities.
        
        Returns:
            Dict[str, Any]: Agent summary
        """
        return {
            **self.get_agent_info(),
            'capabilities': [
                'Stock market data analysis',
                'Global market insights',
                'Commodity price tracking',
                'Currency exchange rates',
                'Economic indicators analysis'
            ],
            'data_sources': [
                'Market data simulator',
                'Economic indicators',
                'Real-time market feeds'
            ]
        }

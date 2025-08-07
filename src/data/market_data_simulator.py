"""
Market Data Simulator

This module provides realistic market data simulation without requiring API keys.
It generates data that mimics real market conditions and economic indicators.
"""

import random
import math
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json
import os

class MarketDataSimulator:
    """Simulates realistic market data for financial analysis"""
    
    def __init__(self):
        self.base_prices = {
            "SPY": 450.0,  # S&P 500 ETF
            "QQQ": 380.0,  # NASDAQ ETF
            "IWM": 180.0,  # Russell 2000 ETF
            "GLD": 190.0,  # Gold ETF
            "TLT": 90.0,   # 20+ Year Treasury ETF
            "VTI": 220.0,  # Total Stock Market ETF
            "VEA": 45.0,   # Developed Markets ETF
            "VWO": 40.0,   # Emerging Markets ETF
            "BND": 80.0,   # Total Bond Market ETF
            "VNQ": 85.0,   # Real Estate ETF
        }
        
        self.economic_indicators = {
            "gdp_growth": 2.1,
            "inflation_rate": 3.2,
            "unemployment_rate": 3.8,
            "federal_funds_rate": 5.25,
            "consumer_confidence": 108.0,
            "manufacturing_pmi": 50.2,
            "housing_starts": 1.45,
            "retail_sales_growth": 2.8,
            "industrial_production": 101.2,
            "capacity_utilization": 78.5
        }
        
        self.sector_performance = {
            "technology": {"weight": 0.25, "volatility": 0.22},
            "healthcare": {"weight": 0.15, "volatility": 0.18},
            "financials": {"weight": 0.12, "volatility": 0.16},
            "consumer_discretionary": {"weight": 0.11, "volatility": 0.19},
            "industrials": {"weight": 0.10, "volatility": 0.17},
            "consumer_staples": {"weight": 0.08, "volatility": 0.14},
            "energy": {"weight": 0.05, "volatility": 0.25},
            "materials": {"weight": 0.04, "volatility": 0.20},
            "utilities": {"weight": 0.03, "volatility": 0.15},
            "real_estate": {"weight": 0.07, "volatility": 0.18}
        }
        
        self.market_sentiment = {
            "fear_greed_index": 65,
            "vix": 18.5,
            "put_call_ratio": 0.85,
            "advance_decline_ratio": 1.2,
            "market_breadth": 0.68
        }
    
    def _generate_price_movement(self, base_price: float, volatility: float, days: int = 1) -> float:
        """Generate realistic price movement using random walk with volatility"""
        movement = 0
        for _ in range(days):
            # Daily return with normal distribution
            daily_return = random.gauss(0.0005, volatility / math.sqrt(252))
            movement += daily_return
        
        return base_price * (1 + movement)
    
    def _update_economic_indicators(self) -> Dict[str, float]:
        """Update economic indicators with realistic changes"""
        updated = {}
        for indicator, current_value in self.economic_indicators.items():
            # Small random change based on indicator type
            if "rate" in indicator or "ratio" in indicator:
                change = random.gauss(0, 0.1)
            elif "growth" in indicator:
                change = random.gauss(0, 0.2)
            else:
                change = random.gauss(0, 0.5)
            
            updated[indicator] = max(0, current_value + change)
        
        return updated
    
    def _update_market_sentiment(self) -> Dict[str, float]:
        """Update market sentiment indicators"""
        updated = {}
        for indicator, current_value in self.market_sentiment.items():
            if indicator == "fear_greed_index":
                change = random.gauss(0, 3)
                updated[indicator] = max(0, min(100, current_value + change))
            elif indicator == "vix":
                change = random.gauss(0, 1.5)
                updated[indicator] = max(10, current_value + change)
            elif indicator == "put_call_ratio":
                change = random.gauss(0, 0.05)
                updated[indicator] = max(0.5, min(2.0, current_value + change))
            elif indicator == "advance_decline_ratio":
                change = random.gauss(0, 0.1)
                updated[indicator] = max(0.3, min(3.0, current_value + change))
            else:
                change = random.gauss(0, 0.05)
                updated[indicator] = max(0, min(1, current_value + change))
        
        return updated
    
    def get_market_data(self, symbols: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get comprehensive market data for specified symbols"""
        if symbols is None:
            symbols = list(self.base_prices.keys())
        
        market_data = {
            "timestamp": datetime.now().isoformat(),
            "symbols": {},
            "market_summary": {},
            "sector_performance": {},
            "economic_indicators": self._update_economic_indicators(),
            "market_sentiment": self._update_market_sentiment()
        }
        
        # Generate data for each symbol
        for symbol in symbols:
            if symbol in self.base_prices:
                base_price = self.base_prices[symbol]
                volatility = 0.15 + random.uniform(0, 0.1)  # 15-25% volatility
                
                current_price = self._generate_price_movement(base_price, volatility)
                previous_price = self._generate_price_movement(base_price, volatility, 1)
                
                change = current_price - previous_price
                change_percent = (change / previous_price) * 100
                
                market_data["symbols"][symbol] = {
                    "price": round(current_price, 2),
                    "change": round(change, 2),
                    "change_percent": round(change_percent, 2),
                    "volume": random.randint(1000000, 50000000),
                    "market_cap": round(current_price * random.randint(1000000, 100000000), 0),
                    "pe_ratio": round(random.uniform(10, 30), 2),
                    "dividend_yield": round(random.uniform(0, 4), 2),
                    "beta": round(random.uniform(0.5, 1.5), 2)
                }
        
        # Market summary
        total_change = sum(data["change_percent"] for data in market_data["symbols"].values())
        avg_change = total_change / len(market_data["symbols"])
        
        market_data["market_summary"] = {
            "overall_trend": "bullish" if avg_change > 0.5 else "bearish" if avg_change < -0.5 else "neutral",
            "average_change": round(avg_change, 2),
            "advancing": len([s for s in market_data["symbols"].values() if s["change"] > 0]),
            "declining": len([s for s in market_data["symbols"].values() if s["change"] < 0]),
            "unchanged": len([s for s in market_data["symbols"].values() if s["change"] == 0]),
            "total_volume": sum(s["volume"] for s in market_data["symbols"].values())
        }
        
        # Sector performance
        for sector, info in self.sector_performance.items():
            sector_return = random.gauss(0.0005, info["volatility"] / math.sqrt(252))
            market_data["sector_performance"][sector] = {
                "return": round(sector_return * 100, 2),
                "weight": info["weight"],
                "volatility": round(info["volatility"] * 100, 1)
            }
        
        return market_data
    
    def get_economic_indicators(self) -> Dict[str, Any]:
        """Get comprehensive economic indicators"""
        indicators = self._update_economic_indicators()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "indicators": indicators,
            "analysis": {
                "gdp_outlook": "moderate_growth" if indicators["gdp_growth"] > 2.0 else "slow_growth",
                "inflation_trend": "elevated" if indicators["inflation_rate"] > 3.0 else "stable",
                "employment_health": "strong" if indicators["unemployment_rate"] < 4.0 else "moderate",
                "monetary_policy": "restrictive" if indicators["federal_funds_rate"] > 5.0 else "accommodative",
                "consumer_sentiment": "positive" if indicators["consumer_confidence"] > 100 else "neutral"
            },
            "forecasts": {
                "gdp_growth_forecast": round(indicators["gdp_growth"] + random.gauss(0, 0.3), 1),
                "inflation_forecast": round(indicators["inflation_rate"] + random.gauss(0, 0.2), 1),
                "fed_rate_forecast": round(indicators["federal_funds_rate"] + random.gauss(0, 0.25), 2)
            }
        }
    
    def get_global_market_data(self) -> Dict[str, Any]:
        """Get global market data for major indices"""
        global_indices = {
            "S&P_500": {"base": 4500, "volatility": 0.15},
            "NASDAQ": {"base": 14000, "volatility": 0.20},
            "DOW_JONES": {"base": 35000, "volatility": 0.12},
            "FTSE_100": {"base": 7500, "volatility": 0.14},
            "NIKKEI_225": {"base": 32000, "volatility": 0.16},
            "DAX": {"base": 16000, "volatility": 0.15},
            "SHANGHAI_COMPOSITE": {"base": 3200, "volatility": 0.18},
            "HANG_SENG": {"base": 18000, "volatility": 0.17}
        }
        
        global_data = {
            "timestamp": datetime.now().isoformat(),
            "indices": {},
            "regional_performance": {
                "north_america": {"return": 0, "count": 0},
                "europe": {"return": 0, "count": 0},
                "asia_pacific": {"return": 0, "count": 0}
            }
        }
        
        for index, info in global_indices.items():
            current_price = self._generate_price_movement(info["base"], info["volatility"])
            previous_price = self._generate_price_movement(info["base"], info["volatility"], 1)
            
            change = current_price - previous_price
            change_percent = (change / previous_price) * 100
            
            global_data["indices"][index] = {
                "price": round(current_price, 2),
                "change": round(change, 2),
                "change_percent": round(change_percent, 2)
            }
            
            # Categorize by region
            if index in ["S&P_500", "NASDAQ", "DOW_JONES"]:
                global_data["regional_performance"]["north_america"]["return"] += change_percent
                global_data["regional_performance"]["north_america"]["count"] += 1
            elif index in ["FTSE_100", "DAX"]:
                global_data["regional_performance"]["europe"]["return"] += change_percent
                global_data["regional_performance"]["europe"]["count"] += 1
            elif index in ["NIKKEI_225", "SHANGHAI_COMPOSITE", "HANG_SENG"]:
                global_data["regional_performance"]["asia_pacific"]["return"] += change_percent
                global_data["regional_performance"]["asia_pacific"]["count"] += 1
        
        # Calculate average returns by region
        for region in global_data["regional_performance"]:
            if global_data["regional_performance"][region]["count"] > 0:
                avg_return = global_data["regional_performance"][region]["return"] / global_data["regional_performance"][region]["count"]
                global_data["regional_performance"][region]["average_return"] = round(avg_return, 2)
        
        return global_data
    
    def get_commodity_data(self) -> Dict[str, Any]:
        """Get commodity market data"""
        commodities = {
            "GOLD": {"base": 1900, "volatility": 0.12},
            "SILVER": {"base": 24, "volatility": 0.18},
            "OIL_WTI": {"base": 75, "volatility": 0.25},
            "NATURAL_GAS": {"base": 3.5, "volatility": 0.30},
            "COPPER": {"base": 4.2, "volatility": 0.20},
            "CORN": {"base": 5.8, "volatility": 0.15},
            "WHEAT": {"base": 6.2, "volatility": 0.16},
            "SOYBEANS": {"base": 13.5, "volatility": 0.14}
        }
        
        commodity_data = {
            "timestamp": datetime.now().isoformat(),
            "commodities": {},
            "commodity_index": 0
        }
        
        total_change = 0
        for commodity, info in commodities.items():
            current_price = self._generate_price_movement(info["base"], info["volatility"])
            previous_price = self._generate_price_movement(info["base"], info["volatility"], 1)
            
            change = current_price - previous_price
            change_percent = (change / previous_price) * 100
            total_change += change_percent
            
            commodity_data["commodities"][commodity] = {
                "price": round(current_price, 2),
                "change": round(change, 2),
                "change_percent": round(change_percent, 2),
                "unit": "USD/oz" if commodity in ["GOLD", "SILVER"] else "USD/bbl" if commodity in ["OIL_WTI", "NATURAL_GAS"] else "USD/lb" if commodity == "COPPER" else "USD/bu"
            }
        
        commodity_data["commodity_index"] = round(total_change / len(commodities), 2)
        
        return commodity_data
    
    def get_currency_data(self) -> Dict[str, Any]:
        """Get currency exchange rate data"""
        currencies = {
            "EUR_USD": {"base": 1.08, "volatility": 0.008},
            "GBP_USD": {"base": 1.26, "volatility": 0.010},
            "USD_JPY": {"base": 150, "volatility": 0.012},
            "USD_CNY": {"base": 7.25, "volatility": 0.005},
            "USD_CAD": {"base": 1.35, "volatility": 0.008},
            "AUD_USD": {"base": 0.66, "volatility": 0.012},
            "USD_CHF": {"base": 0.88, "volatility": 0.009},
            "USD_MXN": {"base": 17.5, "volatility": 0.015}
        }
        
        currency_data = {
            "timestamp": datetime.now().isoformat(),
            "exchange_rates": {},
            "dollar_index": 0
        }
        
        dollar_strength = 0
        for pair, info in currencies.items():
            current_rate = self._generate_price_movement(info["base"], info["volatility"])
            previous_rate = self._generate_price_movement(info["base"], info["volatility"], 1)
            
            change = current_rate - previous_rate
            change_percent = (change / previous_rate) * 100
            
            currency_data["exchange_rates"][pair] = {
                "rate": round(current_rate, 4),
                "change": round(change, 4),
                "change_percent": round(change_percent, 2)
            }
            
            # Calculate dollar strength (simplified)
            if "USD" in pair:
                if pair.startswith("USD"):
                    dollar_strength += change_percent
                else:
                    dollar_strength -= change_percent
        
        currency_data["dollar_index"] = round(dollar_strength / len(currencies), 2)
        
        return currency_data

"""
Intent classification system for investment queries.
"""

import logging
from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class InvestmentIntent(Enum):
    """Investment intent types"""
    RETIREMENT_PLANNING = "retirement_planning"
    GROWTH_INVESTMENT = "growth_investment"
    INCOME_GENERATION = "income_generation"
    CAPITAL_PRESERVATION = "capital_preservation"
    DIVERSIFICATION = "diversification"
    TAX_EFFICIENCY = "tax_efficiency"
    RISK_MANAGEMENT = "risk_management"
    PORTFOLIO_REVIEW = "portfolio_review"
    FUND_SPECIFIC = "fund_specific"
    GENERAL_ADVICE = "general_advice"

@dataclass
class IntentResult:
    """Result of intent classification"""
    intent: InvestmentIntent
    confidence: float
    extracted_info: Dict[str, Any]
    reasoning: str

class IntentClassifier:
    """Classifies user investment intent using LLM"""
    
    def __init__(self, llm_manager):
        self.llm_manager = llm_manager
        self.logger = logging.getLogger(__name__)
    
    async def classify_intent(self, query: str, user_context: Optional[Dict] = None) -> IntentResult:
        """
        Classify the user's investment intent from their query.
        
        Args:
            query: User's investment query
            user_context: Optional user context (profile, history, etc.)
            
        Returns:
            IntentResult with classified intent and confidence
        """
        try:
            self.logger.info(f"🔍 Classifying intent for query: {query[:100]}...")
            
            # Create intent classification prompt
            intent_prompt = self._create_intent_prompt(query, user_context)
            
            self.logger.info(f"📝 Intent prompt created, calling LLM...")
            
            # Get LLM response directly from the primary provider
            if self.llm_manager.primary_provider:
                response = await self.llm_manager.primary_provider.generate_response(intent_prompt)
                
                if not response or not response.content:
                    self.logger.warning("❌ No response from LLM for intent classification")
                    return self._fallback_intent(query)
                
                self.logger.info(f"📄 LLM response received: {response.content[:200]}...")
                
                # Add more detailed logging
                self.logger.info(f"📄 Full LLM response: {response.content}")
                self.logger.info(f"📄 Response type: {type(response.content)}")
                self.logger.info(f"📄 Response length: {len(response.content) if response.content else 0}")
                
                # Parse the LLM response
                intent_result = self._parse_intent_response(response.content, query)
                
                self.logger.info(f"✅ Intent classified: {intent_result.intent.value} (confidence: {intent_result.confidence:.2f})")
                self.logger.info(f"💡 Reasoning: {intent_result.reasoning}")
                
                return intent_result
            else:
                self.logger.warning("❌ No primary LLM provider available")
                return self._fallback_intent(query)
            
        except Exception as e:
            self.logger.error(f"❌ Error classifying intent: {e}")
            self.logger.error(f"❌ Exception type: {type(e).__name__}")
            import traceback
            self.logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return self._fallback_intent(query)
    
    def _create_intent_prompt(self, query: str, user_context: Optional[Dict] = None) -> str:
        """Create the prompt for intent classification"""
        
        context_info = ""
        if user_context:
            context_info = f"""
User Context:
- Risk Tolerance: {user_context.get('risk_tolerance', 'unknown')}
- Investment Goals: {user_context.get('goals', [])}
- Time Horizon: {user_context.get('time_horizon', 'unknown')}
"""
        
        prompt = f"""You are an investment intent classifier. Analyze the user's query and classify their investment intent.

{context_info}
User Query: "{query}"

Available intents:
1. RETIREMENT_PLANNING - User is planning for retirement, seeking long-term stability
2. GROWTH_INVESTMENT - User wants high returns, willing to take risks
3. INCOME_GENERATION - User wants regular income from investments
4. CAPITAL_PRESERVATION - User wants to protect their capital, low risk
5. DIVERSIFICATION - User wants to spread risk across different investments
6. TAX_EFFICIENCY - User is concerned about tax implications
7. RISK_MANAGEMENT - User wants to understand or manage investment risks
8. PORTFOLIO_REVIEW - User wants to review or rebalance their portfolio
9. FUND_SPECIFIC - User is asking about a specific fund or product
10. GENERAL_ADVICE - User wants general investment advice

Respond in this exact JSON format:
{{
    "intent": "intent_name",
    "confidence": 0.95,
    "extracted_info": {{
        "risk_tolerance": "low/medium/high",
        "time_horizon": "short/medium/long",
        "investment_amount": "mentioned_amount_or_null",
        "specific_fund": "fund_name_or_null"
    }},
    "reasoning": "Brief explanation of why this intent was chosen"
}}

Only respond with the JSON, no additional text."""
        
        return prompt
    
    def _parse_intent_response(self, response: str, original_query: str) -> IntentResult:
        """Parse the LLM response to extract intent information"""
        
        try:
            # Clean the response (remove markdown if present)
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            
            import json
            parsed = json.loads(clean_response)
            
            # Extract intent
            intent_name = parsed.get("intent", "GENERAL_ADVICE")
            intent = InvestmentIntent(intent_name.lower())
            
            # Extract confidence
            confidence = parsed.get("confidence", 0.8)
            
            # Extract additional info
            extracted_info = parsed.get("extracted_info", {})
            
            # Extract reasoning
            reasoning = parsed.get("reasoning", "No reasoning provided")
            
            return IntentResult(
                intent=intent,
                confidence=confidence,
                extracted_info=extracted_info,
                reasoning=reasoning
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error parsing intent response: {e}")
            return self._fallback_intent(original_query)
    
    def _fallback_intent(self, query: str) -> IntentResult:
        """Fallback intent classification when LLM fails"""
        
        query_lower = query.lower()
        
        # Simple fallback logic with better keyword matching
        if any(word in query_lower for word in ["retirement", "retire", "pension"]):
            intent = InvestmentIntent.RETIREMENT_PLANNING
        elif any(word in query_lower for word in ["growth", "high return", "aggressive", "significant returns"]):
            intent = InvestmentIntent.GROWTH_INVESTMENT
        elif any(word in query_lower for word in ["income", "dividend", "regular"]):
            intent = InvestmentIntent.INCOME_GENERATION
        elif any(word in query_lower for word in ["conservative", "safe", "preserve"]):
            intent = InvestmentIntent.CAPITAL_PRESERVATION
        elif any(word in query_lower for word in ["diversify", "diversification", "spread", "etf", "index"]):
            intent = InvestmentIntent.DIVERSIFICATION
        elif any(word in query_lower for word in ["tax", "tax-efficient", "tax efficiency"]):
            intent = InvestmentIntent.TAX_EFFICIENCY
        elif any(word in query_lower for word in ["risk", "volatility", "manage risk"]):
            intent = InvestmentIntent.RISK_MANAGEMENT
        elif any(word in query_lower for word in ["portfolio", "review", "rebalance"]):
            intent = InvestmentIntent.PORTFOLIO_REVIEW
        elif any(word in query_lower for word in ["fund", "yuanta", "specific", "specifically"]):
            intent = InvestmentIntent.FUND_SPECIFIC
        else:
            intent = InvestmentIntent.GENERAL_ADVICE
        
        return IntentResult(
            intent=intent,
            confidence=0.6,  # Lower confidence for fallback
            extracted_info={},
            reasoning="Fallback classification using keyword matching"
        )
    
    def get_product_recommendations(self, intent_result: IntentResult) -> Dict[str, Any]:
        """
        Get product recommendations based on classified intent.
        
        Args:
            intent_result: The classified intent result
            
        Returns:
            Dictionary with product recommendations
        """
        
        # Map intents to product types
        intent_to_products = {
            InvestmentIntent.RETIREMENT_PLANNING: {
                "primary": "Conservative Fund",
                "secondary": "Balanced Fund",
                "reasoning": "Retirement planning requires stability and consistent returns"
            },
            InvestmentIntent.GROWTH_INVESTMENT: {
                "primary": "Growth Fund",
                "secondary": "ETF Index Fund",
                "reasoning": "Growth investment seeks higher returns with higher risk tolerance"
            },
            InvestmentIntent.INCOME_GENERATION: {
                "primary": "Conservative Fund",
                "secondary": "Balanced Fund",
                "reasoning": "Income generation requires stable, dividend-paying investments"
            },
            InvestmentIntent.CAPITAL_PRESERVATION: {
                "primary": "Conservative Fund",
                "secondary": "Conservative Fund",
                "reasoning": "Capital preservation requires low-risk, stable investments"
            },
            InvestmentIntent.DIVERSIFICATION: {
                "primary": "ETF Index Fund",
                "secondary": "Balanced Fund",
                "reasoning": "Diversification benefits from broad market exposure"
            },
            InvestmentIntent.TAX_EFFICIENCY: {
                "primary": "ETF Index Fund",
                "secondary": "Conservative Fund",
                "reasoning": "ETFs typically have better tax efficiency than mutual funds"
            },
            InvestmentIntent.RISK_MANAGEMENT: {
                "primary": "Conservative Fund",
                "secondary": "Balanced Fund",
                "reasoning": "Risk management requires understanding of different risk levels"
            },
            InvestmentIntent.PORTFOLIO_REVIEW: {
                "primary": "Balanced Fund",
                "secondary": "ETF Index Fund",
                "reasoning": "Portfolio review considers balanced, diversified approaches"
            },
            InvestmentIntent.FUND_SPECIFIC: {
                "primary": "Growth Fund",  # Changed from Conservative to Growth for fund-specific
                "secondary": "Conservative Fund",
                "reasoning": "Fund-specific queries may need multiple fund options"
            },
            InvestmentIntent.GENERAL_ADVICE: {
                "primary": "Balanced Fund",
                "secondary": "Conservative Fund",
                "reasoning": "General advice benefits from balanced, moderate approaches"
            }
        }
        
        return intent_to_products.get(intent_result.intent, {
            "primary": "Conservative Fund",
            "secondary": "Balanced Fund",
            "reasoning": "Default recommendation for unknown intent"
        }) 
"""
Response generation for financial product recommendation system.

This module generates personalized responses and recommendations using LLM
integration with context from data sources and user profiles.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from .providers import LLMProvider, LLMResponse
from .intent_analyzer import ExtractedIntent, IntentType
from src.data.models import FinancialProduct, UserProfile, ChatMessage

logger = logging.getLogger(__name__)


class RecommendationResponse(BaseModel):
    """Structured recommendation response"""
    content: str = Field(..., description="Generated response content")
    recommendations: List[FinancialProduct] = Field(default_factory=list, description="Recommended products")
    reasoning: str = Field(..., description="Reasoning for recommendations")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in recommendations")
    intent_type: IntentType = Field(..., description="Detected intent type")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ResponseGenerator:
    """Generates personalized financial product recommendations"""
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
    
    async def generate_recommendation(
        self,
        query: str,
        intent: ExtractedIntent,
        available_products: List[FinancialProduct],
        user_profile: Optional[UserProfile] = None,
        conversation_history: Optional[List[ChatMessage]] = None,
        **kwargs
    ) -> RecommendationResponse:
        """Generate personalized financial product recommendations"""
        try:
            # Create context for LLM
            context = self._create_context(
                intent, available_products, user_profile, conversation_history
            )
            
            # Generate recommendation prompt
            prompt = self._create_recommendation_prompt(query, intent, context)
            
            # Generate response using LLM
            llm_response = await self.llm_provider.generate_response(
                prompt=prompt,
                context=context,
                temperature=0.7,
                max_tokens=1500,
                **kwargs
            )
            
            # Parse and structure the response
            recommendation_response = self._parse_recommendation_response(
                llm_response, intent, available_products
            )
            
            return recommendation_response
            
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return self._create_fallback_response(query, intent, available_products)
    
    def _create_context(
        self,
        intent: ExtractedIntent,
        available_products: List[FinancialProduct],
        user_profile: Optional[UserProfile] = None,
        conversation_history: Optional[List[ChatMessage]] = None
    ) -> Dict[str, Any]:
        """Create context for LLM generation"""
        context = {
            "products": available_products,
            "intent": intent.model_dump()
        }
        
        if user_profile:
            context["user_profile"] = user_profile
        
        if conversation_history:
            context["conversation_history"] = conversation_history
        
        return context
    
    def _create_recommendation_prompt(
        self, 
        query: str, 
        intent: ExtractedIntent, 
        context: Dict[str, Any]
    ) -> str:
        """Create prompt for recommendation generation"""
        
        # Base prompt based on intent type
        if intent.intent_type == IntentType.PRODUCT_RECOMMENDATION:
            base_prompt = """You are a financial advisor providing personalized product recommendations. 
            Based on the user's query and profile, recommend the most suitable financial products."""
        elif intent.intent_type == IntentType.PRODUCT_COMPARISON:
            base_prompt = """You are a financial advisor comparing financial products. 
            Provide a detailed comparison of the relevant products based on the user's needs."""
        elif intent.intent_type == IntentType.RISK_ASSESSMENT:
            base_prompt = """You are a financial advisor assessing risk tolerance and recommending 
            appropriate products based on the user's risk profile."""
        else:
            base_prompt = """You are a financial advisor providing helpful information about 
            financial products and investment strategies."""
        
        # Add intent-specific instructions
        intent_instructions = self._get_intent_instructions(intent)
        
        # Add user context if available
        user_context = ""
        if "user_profile" in context:
            user_context = f"""
User Profile:
- Risk Tolerance: {context['user_profile'].risk_tolerance}
- Investment Goals: {', '.join(context['user_profile'].investment_goals)}
- Time Horizon: {context['user_profile'].time_horizon}
- Preferred Products: {', '.join(context['user_profile'].preferred_product_types)}
"""
        
        # Add product information
        products_info = self._format_products_for_recommendation(context["products"])
        
        # Enhanced formatting instructions
        formatting_instructions = """
**RESPONSE FORMATTING REQUIREMENTS:**

Please format your response in a clear, professional structure:

1. **Executive Summary** (2-3 sentences)
   - Brief overview of your recommendation
   - Key points for the user

2. **Analysis Section**
   - Market context and conditions
   - Risk assessment and considerations
   - Product suitability analysis

3. **Recommendations**
   - Specific product recommendations with clear reasoning
   - Allocation percentages and strategy
   - Implementation timeline

4. **Next Steps**
   - Clear action items for the user
   - Follow-up recommendations
   - Important considerations

**FORMATTING GUIDELINES:**
- Use clear headings with **bold** formatting
- Use bullet points (•) for lists
- Keep paragraphs concise (2-3 sentences max)
- Use professional, conversational tone
- Include specific numbers and percentages
- Add disclaimers where appropriate

**EXAMPLE STRUCTURE:**
**Executive Summary**
Brief overview here...

**Market Analysis**
• Current market conditions
• Key factors affecting recommendations

**Risk Assessment**
• Risk level: [Low/Medium/High]
• Key risk factors to consider

**Product Recommendations**
• **Product Name** (XX% allocation)
  - Expected return: X-X%
  - Risk level: [Low/Medium/High]
  - Reasoning: [Clear explanation]

**Implementation Strategy**
• Immediate actions
• Timeline for implementation
• Monitoring recommendations

**Important Disclaimers**
• Risk warnings
• Professional advice notice
"""
        
        prompt = f"""
{base_prompt}

{intent_instructions}

{formatting_instructions}

User Query: "{query}"

{user_context}

Available Products:
{products_info}

Please provide a comprehensive response that includes:
1. A personalized recommendation based on the user's needs
2. Clear reasoning for your recommendations
3. Key considerations and risks
4. Next steps or additional questions if needed

Format your response using the structure above with clear headings, bullet points, and professional formatting.
"""
        
        return prompt
    
    def _get_intent_instructions(self, intent: ExtractedIntent) -> str:
        """Get intent-specific instructions"""
        if intent.intent_type == IntentType.PRODUCT_RECOMMENDATION:
            return """
Focus on:
- Matching products to user's risk tolerance and goals
- Explaining why each recommendation is suitable
- Providing clear next steps for the user
"""
        elif intent.intent_type == IntentType.PRODUCT_COMPARISON:
            return """
Focus on:
- Comparing key features of relevant products
- Highlighting differences in risk, return, and costs
- Helping user understand trade-offs
"""
        elif intent.intent_type == IntentType.RISK_ASSESSMENT:
            return """
Focus on:
- Understanding the user's risk tolerance
- Explaining risk-return relationships
- Recommending products appropriate for their risk level
"""
        else:
            return """
Focus on:
- Providing helpful, accurate information
- Addressing the user's specific question
- Suggesting relevant products when appropriate
"""
    
    def _format_products_for_recommendation(self, products: List[Any]) -> str:
        """Format products for recommendation context"""
        if not products:
            return "No products available for recommendation."
        
        formatted = []
        for product in products:
            # Handle both FinancialProduct objects and dictionaries
            if isinstance(product, dict):
                name = product.get('name', 'Unknown Product')
                product_type = product.get('type', 'unknown')
                risk_level = product.get('risk_level', 'unknown')
                expected_return = product.get('expected_return', 'unknown')
                minimum_investment = product.get('minimum_investment', 0)
                expense_ratio = product.get('expense_ratio', 0)
                description = product.get('description', 'No description available')
            else:
                # Handle FinancialProduct objects
                name = product.name
                product_type = product.type
                risk_level = product.risk_level
                expected_return = product.expected_return
                minimum_investment = product.minimum_investment
                expense_ratio = product.expense_ratio or 0
                description = product.description
            
            formatted.append(
                f"• {name} ({product_type})\n"
                f"  - Risk Level: {risk_level}\n"
                f"  - Expected Return: {expected_return}\n"
                f"  - Minimum Investment: ${minimum_investment:,.0f}\n"
                f"  - Expense Ratio: {expense_ratio:.2%}\n"
                f"  - Description: {description}"
            )
        
        return "\n\n".join(formatted)
    
    def _parse_recommendation_response(
        self, 
        llm_response: LLMResponse, 
        intent: ExtractedIntent,
        available_products: List[Any]
    ) -> RecommendationResponse:
        """Parse LLM response into structured recommendation"""
        
        # Extract recommended products based on content
        recommended_products = self._extract_recommended_products(
            llm_response.content, available_products
        )
        
        # Extract reasoning from response
        reasoning = self._extract_reasoning(llm_response.content)
        
        # Calculate confidence based on intent and response quality
        confidence = self._calculate_confidence(intent, llm_response, recommended_products)
        
        return RecommendationResponse(
            content=llm_response.content,
            recommendations=recommended_products,
            reasoning=reasoning,
            confidence=confidence,
            intent_type=intent.intent_type,
            metadata={
                "provider": llm_response.provider,
                "model": llm_response.model,
                "tokens_used": llm_response.tokens_used,
                "latency_ms": llm_response.latency_ms
            }
        )
    
    def _extract_recommended_products(
        self, 
        response_content: str, 
        available_products: List[Any]
    ) -> List[Any]:
        """Extract recommended products from response content"""
        recommended = []
        response_lower = response_content.lower()
        
        for product in available_products:
            # Handle both FinancialProduct objects and dictionaries
            if isinstance(product, dict):
                name = product.get('name', 'Unknown Product')
                product_type = product.get('type', 'unknown')
            else:
                # Handle FinancialProduct objects
                name = product.name
                product_type = product.type
            
            # Check if product name is mentioned in response
            if name.lower() in response_lower:
                recommended.append(product)
            # Check if product type is mentioned
            elif product_type.lower() in response_lower:
                recommended.append(product)
        
        # If no specific products found, return top products based on risk level
        if not recommended and available_products:
            # Simple fallback: return first 3 products
            recommended = available_products[:3]
        
        return recommended
    
    def _extract_reasoning(self, response_content: str) -> str:
        """Extract reasoning from response content"""
        # Simple extraction - could be enhanced with more sophisticated parsing
        lines = response_content.split('\n')
        reasoning_lines = []
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['because', 'since', 'due to', 'reason', 'consider']):
                reasoning_lines.append(line)
        
        if reasoning_lines:
            return ' '.join(reasoning_lines)
        else:
            # Fallback: use first few sentences
            sentences = response_content.split('.')
            return '. '.join(sentences[:3]) + '.'
    
    def _calculate_confidence(
        self, 
        intent: ExtractedIntent, 
        llm_response: LLMResponse,
        recommended_products: List[Any]
    ) -> float:
        """Calculate confidence in recommendations"""
        # Base confidence from intent
        base_confidence = intent.confidence
        
        # Adjust based on response quality
        response_length = len(llm_response.content)
        if response_length > 200:
            base_confidence += 0.1
        elif response_length < 50:
            base_confidence -= 0.2
        
        # Adjust based on number of recommendations
        if recommended_products:
            base_confidence += 0.1
        else:
            base_confidence -= 0.2
        
        # Adjust based on latency (faster is better)
        if llm_response.latency_ms and llm_response.latency_ms < 2000:
            base_confidence += 0.05
        
        return min(max(base_confidence, 0.0), 1.0)
    
    def _create_fallback_response(
        self, 
        query: str, 
        intent: ExtractedIntent,
        available_products: List[Any]
    ) -> RecommendationResponse:
        """Create fallback response when LLM generation fails"""
        fallback_content = f"""
I understand you're asking about "{query}". I'm here to help with financial product recommendations.

Based on your query, I can help you find suitable financial products. Here are some general considerations:

• Risk tolerance is important when choosing investments
• Consider your investment timeline and goals
• Diversification can help manage risk
• Always review fees and expenses

Would you like me to provide specific product recommendations based on your needs? Please let me know your risk tolerance and investment goals.
"""
        
        return RecommendationResponse(
            content=fallback_content,
            recommendations=available_products[:2] if available_products else [],
            reasoning="Fallback response due to generation error",
            confidence=0.3,
            intent_type=intent.intent_type,
            metadata={"fallback": True}
        ) 
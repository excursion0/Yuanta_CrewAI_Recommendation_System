"""
LLM manager for the financial product recommendation system.

This module coordinates all LLM components including providers, intent analysis,
and response generation with fallback mechanisms.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from .providers import LLMProvider, AnthropicProvider, OpenAIProvider, LLMResponse
from .intent_analyzer import IntentAnalyzer, ExtractedIntent
from .response_generator import ResponseGenerator, RecommendationResponse
from src.data.models import FinancialProduct, UserProfile, ChatMessage
from src.core.exceptions import LLMError, NetworkError, ConfigurationError

logger = logging.getLogger(__name__)


class LLMConfig(BaseModel):
    """Configuration for LLM providers"""
    anthropic_api_key: Optional[str] = Field(None, description="Anthropic API key")
    anthropic_model: str = Field(default="claude-3-5-sonnet-20241022", description="Anthropic model")
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key")
    openai_model: str = Field(default="gpt-4", description="OpenAI model")
    fallback_enabled: bool = Field(default=True, description="Enable fallback to OpenAI")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    timeout_seconds: int = Field(default=30, description="Request timeout in seconds")


class LLMHealthStatus(BaseModel):
    """Health status of LLM components"""
    anthropic_healthy: bool = Field(..., description="Anthropic provider health")
    openai_healthy: bool = Field(..., description="OpenAI provider health")
    primary_provider: str = Field(..., description="Current primary provider")
    fallback_available: bool = Field(..., description="Fallback provider available")
    last_check: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LLMManager:
    """Manages LLM providers, intent analysis, and response generation"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.primary_provider: Optional[LLMProvider] = None
        self.fallback_provider: Optional[LLMProvider] = None
        self.intent_analyzer: Optional[IntentAnalyzer] = None
        self.response_generator: Optional[ResponseGenerator] = None
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize LLM components"""
        try:
            # Initialize primary provider (Anthropic)
            if self.config.anthropic_api_key and self.config.anthropic_api_key != "your_actual_anthropic_key_here":
                self.primary_provider = AnthropicProvider(
                    api_key=self.config.anthropic_api_key,
                    model=self.config.anthropic_model
                )
                logger.info("Anthropic provider initialized")
            else:
                logger.warning("Anthropic API key not configured or using placeholder")
            
            # Initialize fallback provider (OpenAI) only if enabled and configured
            if (self.config.fallback_enabled and 
                self.config.openai_api_key and 
                self.config.openai_api_key != "your_openai_api_key_here"):
                self.fallback_provider = OpenAIProvider(
                    api_key=self.config.openai_api_key,
                    model=self.config.openai_model
                )
                logger.info("OpenAI fallback provider initialized")
            else:
                logger.info("OpenAI fallback disabled (not configured)")
            
            # Check provider health
            primary_healthy = await self._check_provider_health(self.primary_provider)
            fallback_healthy = await self._check_provider_health(self.fallback_provider)
            
            if not primary_healthy and not fallback_healthy:
                logger.error("No LLM providers are healthy - will use mock responses")
                return False
            
            # Initialize intent analyzer with healthy provider
            active_provider = self.primary_provider if primary_healthy else self.fallback_provider
            self.intent_analyzer = IntentAnalyzer(active_provider)
            
            # Initialize response generator with active provider
            self.response_generator = ResponseGenerator(active_provider)
            
            self._initialized = True
            logger.info("LLM manager initialized successfully")
            return True
            
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"Network error during LLM manager initialization: {e}")
            return False
        except ValueError as e:
            logger.error(f"Configuration error in LLM manager: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during LLM manager initialization: {e}")
            return False
    
    async def process_query(
        self,
        query: str,
        available_products: List[FinancialProduct],
        user_profile: Optional[UserProfile] = None,
        conversation_history: Optional[List[ChatMessage]] = None,
        **kwargs
    ) -> RecommendationResponse:
        """Process user query and generate recommendation"""
        if not self._initialized:
            raise RuntimeError("LLM manager not initialized")
        
        try:
            # Step 1: Analyze intent
            intent = await self._analyze_intent_with_fallback(
                query, user_profile, conversation_history
            )
            
            # Step 2: Generate recommendation
            recommendation = await self._generate_recommendation_with_fallback(
                query, intent, available_products, user_profile, conversation_history, **kwargs
            )
            
            return recommendation
            
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"Network error during query processing: {e}")
            return self._create_error_response(query, available_products)
        except ValueError as e:
            logger.error(f"Invalid input during query processing: {e}")
            return self._create_error_response(query, available_products)
        except Exception as e:
            logger.error(f"Unexpected error during query processing: {e}")
            return self._create_error_response(query, available_products)
    
    async def _analyze_intent_with_fallback(
        self,
        query: str,
        user_profile: Optional[UserProfile] = None,
        conversation_history: Optional[List[ChatMessage]] = None
    ) -> ExtractedIntent:
        """Analyze intent with fallback to alternative provider"""
        context = {}
        if user_profile:
            context["user_profile"] = user_profile
        if conversation_history:
            context["conversation_history"] = conversation_history
        
        # Try primary provider first
        if self.intent_analyzer and self.primary_provider:
            try:
                return await self.intent_analyzer.analyze_intent(query, context)
            except Exception as e:
                logger.warning(f"Primary intent analysis failed: {e}")
        
        # Try fallback provider
        if self.fallback_provider:
            try:
                fallback_analyzer = IntentAnalyzer(self.fallback_provider)
                return await fallback_analyzer.analyze_intent(query, context)
            except Exception as e:
                logger.error(f"Fallback intent analysis failed: {e}")
        
        # Return default intent
        return ExtractedIntent(
            intent_type="unknown",
            confidence=0.0,
            keywords=self._extract_basic_keywords(query)
        )
    
    async def _generate_recommendation_with_fallback(
        self,
        query: str,
        intent: ExtractedIntent,
        available_products: List[FinancialProduct],
        user_profile: Optional[UserProfile] = None,
        conversation_history: Optional[List[ChatMessage]] = None,
        **kwargs
    ) -> RecommendationResponse:
        """Generate recommendation with fallback to alternative provider"""
        
        # Try primary provider first
        if self.response_generator and self.primary_provider:
            try:
                return await self.response_generator.generate_recommendation(
                    query, intent, available_products, user_profile, conversation_history, **kwargs
                )
            except Exception as e:
                logger.warning(f"Primary recommendation generation failed: {e}")
        
        # Try fallback provider
        if self.fallback_provider:
            try:
                fallback_generator = ResponseGenerator(self.fallback_provider)
                return await fallback_generator.generate_recommendation(
                    query, intent, available_products, user_profile, conversation_history, **kwargs
                )
            except Exception as e:
                logger.error(f"Fallback recommendation generation failed: {e}")
        
        # Return fallback response
        return self._create_error_response(query, available_products)
    
    async def _check_provider_health(self, provider: Optional[LLMProvider]) -> bool:
        """Check if provider is healthy"""
        if not provider:
            return False
        
        try:
            return await provider.health_check()
        except Exception as e:
            logger.error(f"Provider health check failed: {e}")
            return False
    
    def _extract_basic_keywords(self, query: str) -> List[str]:
        """Extract basic keywords from query"""
        keywords = []
        query_lower = query.lower()
        
        # Financial keywords
        financial_keywords = ['fund', 'etf', 'bond', 'stock', 'investment', 'portfolio', 'risk', 'return']
        for keyword in financial_keywords:
            if keyword in query_lower:
                keywords.append(keyword)
        
        return keywords
    
    def _create_error_response(self, query: str, available_products: List[FinancialProduct]) -> RecommendationResponse:
        """Create error response when all providers fail"""
        error_content = f"""
I apologize, but I'm experiencing technical difficulties processing your query: "{query}".

I'm here to help with financial product recommendations. Please try again in a moment, or you can:

• Ask about specific types of investments (mutual funds, ETFs, bonds)
• Inquire about risk tolerance and investment goals
• Request product comparisons
• Ask about investment strategies

I'll be happy to assist once the system is back online.
"""
        
        return RecommendationResponse(
            content=error_content,
            recommendations=available_products[:2] if available_products else [],
            reasoning="Error response due to system issues",
            confidence=0.0,
            intent_type="unknown",
            metadata={"error": True}
        )
    
    async def health_check(self) -> LLMHealthStatus:
        """Check health of all LLM components"""
        anthropic_healthy = await self._check_provider_health(self.primary_provider)
        openai_healthy = await self._check_provider_health(self.fallback_provider)
        
        primary_provider = "anthropic" if anthropic_healthy else "openai" if openai_healthy else "none"
        # Fallback is available if the other provider is healthy when primary fails
        fallback_available = (openai_healthy and not anthropic_healthy) or (anthropic_healthy and not openai_healthy)
        
        return LLMHealthStatus(
            anthropic_healthy=anthropic_healthy,
            openai_healthy=openai_healthy,
            primary_provider=primary_provider,
            fallback_available=fallback_available
        )
    
    async def get_available_models(self) -> Dict[str, List[str]]:
        """Get available models for each provider"""
        models = {}
        
        if self.primary_provider:
            try:
                models["anthropic"] = await self.primary_provider.get_models()
            except Exception as e:
                logger.error(f"Failed to get Anthropic models: {e}")
                models["anthropic"] = []
        
        if self.fallback_provider:
            try:
                models["openai"] = await self.fallback_provider.get_models()
            except Exception as e:
                logger.error(f"Failed to get OpenAI models: {e}")
                models["openai"] = []
        
        return models
    
    async def test_generation(self, test_prompt: str = "Hello, how can you help me with investments?") -> Dict[str, Any]:
        """Test LLM generation capabilities"""
        try:
            if not self._initialized:
                return {"error": "LLM manager not initialized"}
            
            # Test intent analysis
            intent = await self._analyze_intent_with_fallback(test_prompt)
            
            # Test response generation with mock products
            mock_products = [
                FinancialProduct(
                    product_id="TEST_001",
                    name="Test Mutual Fund",
                    type="mutual_fund",
                    risk_level="medium",
                    description="A test mutual fund for demonstration",
                    issuer="Test Financial Corp",
                    inception_date=datetime.now(timezone.utc),
                    expected_return="5-8%",
                    volatility=0.15,
                    sharpe_ratio=0.85,
                    minimum_investment=1000.0,
                    expense_ratio=0.0125,
                    dividend_yield=0.025,
                    regulatory_status="approved",
                    compliance_requirements=["SEC"],
                    tags=["test", "fund"],
                    categories=["equity"],
                    embedding_id="test_emb_001",
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
            ]
            
            recommendation = await self._generate_recommendation_with_fallback(
                test_prompt, intent, mock_products
            )
            
            return {
                "success": True,
                "intent": intent.model_dump(),
                "recommendation": recommendation.model_dump(),
                "health": (await self.health_check()).model_dump()
            }
            
        except Exception as e:
            logger.error(f"LLM test generation failed: {e}")
            return {"error": str(e)} 
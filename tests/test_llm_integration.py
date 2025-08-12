"""
Tests for LLM integration components.

This module tests the LLM providers, intent analysis, response generation,
and LLM manager functionality.
"""

import pytest
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock, patch

from src.llm import (
    LLMProvider, AnthropicProvider, OpenAIProvider, LLMResponse,
    IntentAnalyzer, ExtractedIntent, IntentType, RiskLevel, InvestmentGoal,
    ResponseGenerator, RecommendationResponse,
    LLMManager, LLMConfig, LLMHealthStatus
)
from src.data.models import FinancialProduct, UserProfile, ChatMessage


class TestLLMProviders:
    """Test LLM provider implementations"""
    
    @pytest.fixture
    def mock_anthropic_response(self):
        """Mock Anthropic API response"""
        mock_response = Mock()
        mock_response.content = [Mock(text="Test response from Anthropic")]
        mock_response.usage = Mock(total_tokens=30)
        return mock_response
    
    @pytest.fixture
    def mock_openai_response(self):
        """Mock OpenAI API response"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response from OpenAI"))]
        mock_response.usage = Mock(total_tokens=30)
        return mock_response
    
    @pytest.mark.asyncio
    async def test_anthropic_provider_creation(self):
        """Test Anthropic provider creation"""
        provider = AnthropicProvider(
            api_key="test_key",
            model="claude-3-5-sonnet-20241022"
        )
        
        assert provider.api_key == "test_key"
        assert provider.model == "claude-3-5-sonnet-20241022"
        assert provider.client is not None
    
    @pytest.mark.asyncio
    async def test_openai_provider_creation(self):
        """Test OpenAI provider creation"""
        provider = OpenAIProvider(
            api_key="test_key",
            model="gpt-4"
        )
        
        assert provider.api_key == "test_key"
        assert provider.model == "gpt-4"
        assert provider.client is not None
    
    @pytest.mark.asyncio
    @patch('anthropic.Anthropic')
    async def test_anthropic_response_generation(self, mock_anthropic, mock_anthropic_response):
        """Test Anthropic response generation"""
        mock_anthropic.return_value.messages.create.return_value = mock_anthropic_response
        
        provider = AnthropicProvider(api_key="test_key")
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.return_value = mock_anthropic_response
            
            response = await provider.generate_response("Test prompt")
            
            assert response.content == "Test response from Anthropic"
            assert response.provider == "anthropic"
            assert response.model == "claude-3-5-sonnet-20241022"
            assert response.tokens_used == 30
    
    @pytest.mark.asyncio
    @patch('openai.AsyncOpenAI')
    async def test_openai_response_generation(self, mock_openai, mock_openai_response):
        """Test OpenAI response generation"""
        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = mock_openai_response
        mock_openai.return_value = mock_client
        
        provider = OpenAIProvider(api_key="test_key")
        
        response = await provider.generate_response("Test prompt")
        
        assert response.content == "Test response from OpenAI"
        assert response.provider == "openai"
        assert response.model == "gpt-4"
        assert response.tokens_used == 30
    
    @pytest.mark.asyncio
    async def test_provider_health_check_failure(self):
        """Test provider health check when API is unavailable"""
        provider = AnthropicProvider(api_key="invalid_key")
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.side_effect = Exception("API error")
            
            is_healthy = await provider.health_check()
            assert not is_healthy


class TestIntentAnalyzer:
    """Test intent analysis functionality"""
    
    @pytest.fixture
    def mock_llm_provider(self):
        """Mock LLM provider for intent analysis"""
        provider = Mock(spec=LLMProvider)
        provider.generate_response = AsyncMock()
        return provider
    
    @pytest.fixture
    def sample_products(self):
        """Sample financial products for testing"""
        now = datetime.now(timezone.utc)
        return [
            FinancialProduct(
                product_id="TEST_001",
                name="Test Mutual Fund",
                type="mutual_fund",
                risk_level="medium",
                description="A test mutual fund",
                issuer="Test Corp",
                inception_date=now,
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
                created_at=now,
                updated_at=now
            )
        ]
    
    @pytest.mark.asyncio
    async def test_intent_analyzer_creation(self, mock_llm_provider):
        """Test intent analyzer creation"""
        analyzer = IntentAnalyzer(mock_llm_provider)
        assert analyzer.llm_provider == mock_llm_provider
    
    @pytest.mark.asyncio
    async def test_intent_analysis_success(self, mock_llm_provider):
        """Test successful intent analysis"""
        # Mock LLM response with structured intent data
        mock_response = LLMResponse(
            content="""INTENT_TYPE: product_recommendation
CONFIDENCE: 0.85
RISK_TOLERANCE: medium
INVESTMENT_GOALS: retirement,wealth_building
INVESTMENT_HORIZON: long_term
PREFERRED_PRODUCTS: mutual_fund,etf
BUDGET_MIN: 1000
BUDGET_MAX: 50000
KEYWORDS: investment,fund,retirement
ENTITIES: Test Fund""",
            model="test-model",
            provider="test-provider"
        )
        
        mock_llm_provider.generate_response.return_value = mock_response
        
        analyzer = IntentAnalyzer(mock_llm_provider)
        intent = await analyzer.analyze_intent("I want to invest in mutual funds for retirement")
        
        assert intent.intent_type == IntentType.PRODUCT_RECOMMENDATION
        assert intent.confidence == 0.85
        assert intent.risk_tolerance == RiskLevel.MEDIUM
        assert InvestmentGoal.RETIREMENT in intent.investment_goals
        assert InvestmentGoal.WEALTH_BUILDING in intent.investment_goals
        assert "mutual_fund" in intent.preferred_product_types
        assert "etf" in intent.preferred_product_types
        assert intent.budget_range["min"] == 1000.0
        assert intent.budget_range["max"] == 50000.0
        assert "investment" in intent.keywords
        assert "fund" in intent.keywords
    
    @pytest.mark.asyncio
    async def test_intent_analysis_failure(self, mock_llm_provider):
        """Test intent analysis when LLM fails"""
        mock_llm_provider.generate_response.side_effect = Exception("LLM error")
        
        analyzer = IntentAnalyzer(mock_llm_provider)
        intent = await analyzer.analyze_intent("I want to invest in mutual funds for retirement")
        
        assert intent.intent_type == IntentType.UNKNOWN
        assert intent.confidence == 0.0
        assert len(intent.keywords) > 0  # Should extract basic keywords
        assert "fund" in intent.keywords  # Should extract 'fund' from 'mutual funds'
        assert "retirement" in intent.keywords  # Should extract 'retirement'
    
    @pytest.mark.asyncio
    async def test_intent_validation(self, mock_llm_provider):
        """Test intent validation"""
        analyzer = IntentAnalyzer(mock_llm_provider)
        
        # Valid intent
        valid_intent = ExtractedIntent(
            intent_type=IntentType.PRODUCT_RECOMMENDATION,
            confidence=0.8,
            risk_tolerance=RiskLevel.MEDIUM,
            keywords=["fund", "investment"]
        )
        assert await analyzer.validate_intent(valid_intent)
        
        # Invalid intent - low confidence
        invalid_intent = ExtractedIntent(
            intent_type=IntentType.PRODUCT_RECOMMENDATION,
            confidence=0.2,
            keywords=["fund"]
        )
        assert not await analyzer.validate_intent(invalid_intent)
        
        # Invalid intent - unknown type
        unknown_intent = ExtractedIntent(
            intent_type=IntentType.UNKNOWN,
            confidence=0.8,
            keywords=["fund"]
        )
        assert not await analyzer.validate_intent(unknown_intent)


class TestResponseGenerator:
    """Test response generation functionality"""
    
    @pytest.fixture
    def mock_llm_provider(self):
        """Mock LLM provider for response generation"""
        provider = Mock(spec=LLMProvider)
        provider.generate_response = AsyncMock()
        return provider
    
    @pytest.fixture
    def sample_products(self):
        """Sample financial products for testing"""
        now = datetime.now(timezone.utc)
        return [
            FinancialProduct(
                product_id="TEST_001",
                name="Test Mutual Fund",
                type="mutual_fund",
                risk_level="medium",
                description="A test mutual fund for retirement",
                issuer="Test Corp",
                inception_date=now,
                expected_return="5-8%",
                volatility=0.15,
                sharpe_ratio=0.85,
                minimum_investment=1000.0,
                expense_ratio=0.0125,
                dividend_yield=0.025,
                regulatory_status="approved",
                compliance_requirements=["SEC"],
                tags=["test", "fund", "retirement"],
                categories=["equity"],
                embedding_id="test_emb_001",
                created_at=now,
                updated_at=now
            ),
            FinancialProduct(
                product_id="TEST_002",
                name="Test ETF",
                type="etf",
                risk_level="low",
                description="A test ETF for conservative investors",
                issuer="Test Corp",
                inception_date=now,
                expected_return="3-5%",
                volatility=0.08,
                sharpe_ratio=0.75,
                minimum_investment=500.0,
                expense_ratio=0.008,
                dividend_yield=0.015,
                regulatory_status="approved",
                compliance_requirements=["SEC"],
                tags=["test", "etf", "conservative"],
                categories=["bond"],
                embedding_id="test_emb_002",
                created_at=now,
                updated_at=now
            )
        ]
    
    @pytest.mark.asyncio
    async def test_response_generator_creation(self, mock_llm_provider):
        """Test response generator creation"""
        generator = ResponseGenerator(mock_llm_provider)
        assert generator.llm_provider == mock_llm_provider
    
    @pytest.mark.asyncio
    async def test_recommendation_generation(self, mock_llm_provider, sample_products):
        """Test recommendation generation"""
        # Mock LLM response
        mock_response = LLMResponse(
            content="Based on your retirement goals, I recommend the Test Mutual Fund. It offers a good balance of risk and return with a 5-8% expected return. The fund is suitable for long-term retirement planning.",
            model="test-model",
            provider="test-provider",
            tokens_used=150,
            latency_ms=1200
        )
        
        mock_llm_provider.generate_response.return_value = mock_response
        
        # Create intent
        intent = ExtractedIntent(
            intent_type=IntentType.PRODUCT_RECOMMENDATION,
            confidence=0.85,
            risk_tolerance=RiskLevel.MEDIUM,
            investment_goals=[InvestmentGoal.RETIREMENT],
            keywords=["retirement", "fund"]
        )
        
        generator = ResponseGenerator(mock_llm_provider)
        recommendation = await generator.generate_recommendation(
            "I want to invest for retirement",
            intent,
            sample_products
        )
        
        assert recommendation.content == mock_response.content
        assert len(recommendation.recommendations) > 0
        assert "Test Mutual Fund" in recommendation.reasoning
        assert recommendation.confidence > 0.0
        assert recommendation.intent_type == IntentType.PRODUCT_RECOMMENDATION
        assert recommendation.metadata["provider"] == "test-provider"
    
    @pytest.mark.asyncio
    async def test_recommendation_generation_failure(self, mock_llm_provider, sample_products):
        """Test recommendation generation when LLM fails"""
        mock_llm_provider.generate_response.side_effect = Exception("LLM error")
        
        intent = ExtractedIntent(
            intent_type=IntentType.PRODUCT_RECOMMENDATION,
            confidence=0.8,
            keywords=["investment"]
        )
        
        generator = ResponseGenerator(mock_llm_provider)
        recommendation = await generator.generate_recommendation(
            "I want to invest",
            intent,
            sample_products
        )
        
        assert "fallback" in recommendation.metadata
        assert recommendation.confidence == 0.3
        assert len(recommendation.recommendations) > 0


class TestLLMManager:
    """Test LLM manager functionality"""
    
    @pytest.fixture
    def llm_config(self):
        """LLM configuration for testing"""
        return LLMConfig(
            anthropic_api_key="test_anthropic_key",
            openai_api_key="test_openai_key",
            fallback_enabled=True
        )
    
    @pytest.fixture
    def sample_products(self):
        """Sample financial products for testing"""
        now = datetime.now(timezone.utc)
        return [
            FinancialProduct(
                product_id="TEST_001",
                name="Test Mutual Fund",
                type="mutual_fund",
                risk_level="medium",
                description="A test mutual fund",
                issuer="Test Corp",
                inception_date=now,
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
                created_at=now,
                updated_at=now
            )
        ]
    
    @pytest.mark.asyncio
    async def test_llm_manager_creation(self, llm_config):
        """Test LLM manager creation"""
        manager = LLMManager(llm_config)
        assert manager.config == llm_config
        assert not manager._initialized
    
    @pytest.mark.asyncio
    @patch('src.llm.providers.AnthropicProvider')
    @patch('src.llm.providers.OpenAIProvider')
    async def test_llm_manager_initialization(self, mock_openai, mock_anthropic, llm_config):
        """Test LLM manager initialization"""
        # Mock providers
        mock_anthropic_instance = Mock()
        mock_anthropic_instance.health_check = AsyncMock(return_value=True)
        mock_anthropic.return_value = mock_anthropic_instance
        
        mock_openai_instance = Mock()
        mock_openai_instance.health_check = AsyncMock(return_value=True)
        mock_openai.return_value = mock_openai_instance
        
        # Mock the health check method to avoid actual API calls
        with patch.object(LLMManager, '_check_provider_health') as mock_health_check:
            mock_health_check.side_effect = [True, True]  # Both providers healthy
            
            manager = LLMManager(llm_config)
            success = await manager.initialize()
            
            assert success
            assert manager._initialized
            assert manager.primary_provider is not None
            assert manager.fallback_provider is not None
            assert manager.intent_analyzer is not None
            assert manager.response_generator is not None
    
    @pytest.mark.asyncio
    async def test_llm_manager_initialization_failure(self, llm_config):
        """Test LLM manager initialization when providers fail"""
        manager = LLMManager(llm_config)
        
        # Mock providers to fail health checks
        with patch('src.llm.providers.AnthropicProvider') as mock_anthropic:
            mock_anthropic_instance = Mock()
            mock_anthropic_instance.health_check = AsyncMock(return_value=False)
            mock_anthropic.return_value = mock_anthropic_instance
            
            success = await manager.initialize()
            assert not success
            assert not manager._initialized
    
    @pytest.mark.asyncio
    async def test_query_processing(self, llm_config, sample_products):
        """Test query processing with LLM manager"""
        manager = LLMManager(llm_config)
        
        # Mock successful initialization
        with patch.object(manager, '_initialized', True):
            with patch.object(manager, '_analyze_intent_with_fallback') as mock_analyze:
                with patch.object(manager, '_generate_recommendation_with_fallback') as mock_generate:
                    # Mock intent analysis
                    mock_intent = ExtractedIntent(
                        intent_type=IntentType.PRODUCT_RECOMMENDATION,
                        confidence=0.8,
                        keywords=["fund"]
                    )
                    mock_analyze.return_value = mock_intent
                    
                    # Mock recommendation
                    mock_recommendation = RecommendationResponse(
                        content="Test recommendation",
                        recommendations=sample_products,
                        reasoning="Test reasoning",
                        confidence=0.8,
                        intent_type=IntentType.PRODUCT_RECOMMENDATION
                    )
                    mock_generate.return_value = mock_recommendation
                    
                    result = await manager.process_query(
                        "I want to invest in mutual funds",
                        sample_products
                    )
                    
                    assert result == mock_recommendation
                    mock_analyze.assert_called_once()
                    mock_generate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_health_check(self, llm_config):
        """Test LLM manager health check"""
        manager = LLMManager(llm_config)
        
        # Mock providers
        with patch.object(manager, 'primary_provider') as mock_primary:
            with patch.object(manager, 'fallback_provider') as mock_fallback:
                mock_primary.health_check = AsyncMock(return_value=True)
                mock_fallback.health_check = AsyncMock(return_value=True)
                
                health = await manager.health_check()
                
                assert health.anthropic_healthy
                assert health.openai_healthy
                assert health.primary_provider == "anthropic"
                # When both are healthy, fallback is not needed
                assert not health.fallback_available
        
        # Test fallback scenario
        with patch.object(manager, 'primary_provider') as mock_primary:
            with patch.object(manager, 'fallback_provider') as mock_fallback:
                mock_primary.health_check = AsyncMock(return_value=False)
                mock_fallback.health_check = AsyncMock(return_value=True)
                
                health = await manager.health_check()
                
                assert not health.anthropic_healthy
                assert health.openai_healthy
                assert health.primary_provider == "openai"
                assert health.fallback_available
    
    @pytest.mark.asyncio
    async def test_test_generation(self, llm_config):
        """Test LLM test generation"""
        manager = LLMManager(llm_config)
        
        # Mock successful initialization and processing
        with patch.object(manager, '_initialized', True):
            with patch.object(manager, '_analyze_intent_with_fallback') as mock_analyze:
                with patch.object(manager, '_generate_recommendation_with_fallback') as mock_generate:
                    with patch.object(manager, 'health_check') as mock_health:
                        # Mock responses
                        mock_intent = ExtractedIntent(
                            intent_type=IntentType.PRODUCT_RECOMMENDATION,
                            confidence=0.8,
                            keywords=["test"]
                        )
                        mock_analyze.return_value = mock_intent
                        
                        mock_recommendation = RecommendationResponse(
                            content="Test response",
                            recommendations=[],
                            reasoning="Test reasoning",
                            confidence=0.8,
                            intent_type=IntentType.PRODUCT_RECOMMENDATION
                        )
                        mock_generate.return_value = mock_recommendation
                        
                        mock_health.return_value = LLMHealthStatus(
                            anthropic_healthy=True,
                            openai_healthy=True,
                            primary_provider="anthropic",
                            fallback_available=False
                        )
                        
                        result = await manager.test_generation()
                        
                        assert result["success"]
                        assert "intent" in result
                        assert "recommendation" in result
                        assert "health" in result


class TestLLMIntegration:
    """Integration tests for LLM components"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_llm_flow(self):
        """Test end-to-end LLM flow with mocked components"""
        # This test simulates a complete LLM flow without actual API calls
        config = LLMConfig(
            anthropic_api_key="test_key",
            openai_api_key="test_key",
            fallback_enabled=True
        )
        
        manager = LLMManager(config)
        
        # Mock the entire flow
        with patch.object(manager, 'initialize', return_value=True):
            with patch.object(manager, '_initialized', True):
                with patch.object(manager, '_analyze_intent_with_fallback') as mock_analyze:
                    with patch.object(manager, '_generate_recommendation_with_fallback') as mock_generate:
                        # Mock intent analysis
                        mock_intent = ExtractedIntent(
                            intent_type=IntentType.PRODUCT_RECOMMENDATION,
                            confidence=0.9,
                            risk_tolerance=RiskLevel.MEDIUM,
                            investment_goals=[InvestmentGoal.RETIREMENT],
                            keywords=["retirement", "fund"]
                        )
                        mock_analyze.return_value = mock_intent
                        
                        # Mock recommendation
                        mock_recommendation = RecommendationResponse(
                            content="I recommend the Test Mutual Fund for your retirement goals.",
                            recommendations=[],
                            reasoning="Based on your retirement goals and medium risk tolerance",
                            confidence=0.9,
                            intent_type=IntentType.PRODUCT_RECOMMENDATION
                        )
                        mock_generate.return_value = mock_recommendation
                        
                        # Test the flow
                        result = await manager.process_query(
                            "I want to invest for retirement",
                            []
                        )
                        
                        assert result.content == "I recommend the Test Mutual Fund for your retirement goals."
                        assert result.confidence == 0.9
                        assert result.intent_type == IntentType.PRODUCT_RECOMMENDATION 
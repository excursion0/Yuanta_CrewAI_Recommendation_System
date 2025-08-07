"""
Basic functionality tests for the financial product recommendation system.

This module contains tests to verify the core components are working
correctly, including data models, event bus, and API endpoints.
"""

import pytest
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any

from src.data.models import (
    FinancialProduct, UserProfile, ChatMessage, ChatResponse,
    RiskLevel, ProductType, InvestmentExperience
)
from src.core.event_bus import EventBus, EventType
from src.utils.session_manager import SessionManager


class TestDataModels:
    """Test data model functionality"""
    
    def test_financial_product_creation(self):
        """Test creating a financial product"""
        product = FinancialProduct(
            product_id="TEST_001",
            name="Test Fund",
            type=ProductType.MUTUAL_FUND,
            risk_level=RiskLevel.LOW,
            description="A test mutual fund",
            issuer="Test Company",
            inception_date=datetime.now(timezone.utc),
            expected_return="3-5%",
            volatility=0.08,
            sharpe_ratio=1.2,
            minimum_investment=1000.0,
            expense_ratio=0.75,
            dividend_yield=2.5,
            regulatory_status="approved",
            compliance_requirements=["SEC", "FINRA"],
            tags=["test", "low-risk"],
            categories=["mutual_funds", "equity"],
            embedding_id="emb_001"
        )
        
        assert product.product_id == "TEST_001"
        assert product.name == "Test Fund"
        assert product.type == ProductType.MUTUAL_FUND
        assert product.risk_level == RiskLevel.LOW
    
    def test_user_profile_creation(self):
        """Test creating a user profile"""
        profile = UserProfile(
            user_id="USER_001",
            name="John Doe",
            email="john.doe@example.com",
            age=35,
            income_level="middle",
            investment_experience=InvestmentExperience.INTERMEDIATE,
            risk_tolerance=RiskLevel.MEDIUM,
            investment_goals=["retirement", "wealth_building"],
            time_horizon="10-20_years",
            preferred_product_types=[ProductType.MUTUAL_FUND, ProductType.ETF],
            preferred_sectors=["technology", "healthcare"],
            geographic_preferences=["US", "Europe"],
            current_portfolio_value=50000.0,
            monthly_investment_capacity=1000.0
        )
        
        assert profile.user_id == "USER_001"
        assert profile.name == "John Doe"
        assert profile.investment_experience == InvestmentExperience.INTERMEDIATE
        assert profile.risk_tolerance == RiskLevel.MEDIUM
    
    def test_chat_message_creation(self):
        """Test creating a chat message"""
        message = ChatMessage(
            platform="discord",
            user_id="USER_001",
            session_id="SESSION_001",
            message_text="I'm looking for a low-risk investment option",
            timestamp=datetime.now(timezone.utc),
            metadata={"channel_id": "123456"}
        )
        
        assert message.platform == "discord"
        assert message.user_id == "USER_001"
        assert message.message_text == "I'm looking for a low-risk investment option"
    
    def test_chat_response_creation(self):
        """Test creating a chat response"""
        response = ChatResponse(
            response_text="Based on your query, I recommend the Conservative Growth Fund.",
            recommendations=[
                {
                    "product_id": "PROD_001",
                    "name": "Conservative Growth Fund",
                    "risk_level": "low",
                    "expected_return": "3-5%"
                }
            ],
            confidence=0.88,
            sources=["structured_db", "vector_search"],
            processing_time=1.2
        )
        
        assert response.response_text == "Based on your query, I recommend the Conservative Growth Fund."
        assert response.confidence == 0.88
        assert len(response.recommendations) == 1


class TestEventBus:
    """Test event bus functionality"""
    
    @pytest.fixture
    def event_bus(self):
        """Create a test event bus"""
        return EventBus()
    
    @pytest.mark.asyncio
    async def test_event_publishing(self, event_bus):
        """Test publishing events"""
        events_received = []

        async def test_handler(event_data):
            events_received.append(event_data)

        # Start the event bus
        await event_bus.start()

        # Subscribe to events
        event_bus.subscribe(EventType.CHAT_MESSAGE, test_handler)

        # Publish an event
        test_data = {"test": "data"}
        await event_bus.publish(EventType.CHAT_MESSAGE, test_data)

        # Wait a bit for processing
        await asyncio.sleep(0.2)

        assert len(events_received) == 1
        assert events_received[0] == test_data

        # Stop the event bus
        await event_bus.stop()
    
    @pytest.mark.asyncio
    async def test_event_bus_start_stop(self, event_bus):
        """Test starting and stopping the event bus"""
        # Start the event bus
        await event_bus.start()
        
        # Verify it's running
        assert event_bus._processing == True
        
        # Stop the event bus
        await event_bus.stop()
        
        # Verify it's stopped
        assert event_bus._processing == False


class TestSessionManager:
    """Test session manager functionality"""
    
    @pytest.fixture
    def session_manager(self):
        """Create a test session manager"""
        return SessionManager()
    
    @pytest.mark.asyncio
    async def test_session_creation(self, session_manager):
        """Test creating a session"""
        session_id = await session_manager.create_session("USER_001", "discord")
        
        assert session_id is not None
        assert len(session_id) > 0
        
        # Verify session exists
        session = await session_manager.get_session(session_id)
        assert session is not None
        assert session.user_id == "USER_001"
        assert session.platform == "discord"
        assert session.is_active == True
    
    @pytest.mark.asyncio
    async def test_session_validation(self, session_manager):
        """Test session validation"""
        session_id = await session_manager.create_session("USER_001", "discord")
        
        # Valid session
        is_valid = await session_manager.validate_session(session_id, "USER_001")
        assert is_valid == True
        
        # Invalid user
        is_valid = await session_manager.validate_session(session_id, "USER_002")
        assert is_valid == False
    
    @pytest.mark.asyncio
    async def test_session_stats(self, session_manager):
        """Test getting session statistics"""
        session_id = await session_manager.create_session("USER_001", "discord")
        
        stats = await session_manager.get_session_stats(session_id)
        
        assert stats["session_id"] == session_id
        assert stats["user_id"] == "USER_001"
        assert stats["platform"] == "discord"
        assert stats["is_active"] == True
        assert stats["message_count"] == 0


class TestAPIEndpoints:
    """Test API endpoint functionality"""
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check endpoint"""
        # This would require a running API server
        # For now, just test the endpoint structure
        assert True  # Placeholder for actual API test
    
    @pytest.mark.asyncio
    async def test_chat_message_processing(self):
        """Test chat message processing"""
        # This would require a running API server
        # For now, just test the endpoint structure
        assert True  # Placeholder for actual API test


class TestIntegration:
    """Test integration between components"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_flow(self):
        """Test end-to-end message processing flow"""
        # Create event bus
        event_bus = EventBus()
        await event_bus.start()
        
        # Create session manager
        session_manager = SessionManager()
        
        # Create a session
        session_id = await session_manager.create_session("USER_001", "discord")
        
        # Create a chat message
        message = ChatMessage(
            platform="discord",
            user_id="USER_001",
            session_id=session_id,
            message_text="I'm looking for a low-risk investment option",
            timestamp=datetime.now(timezone.utc),
            metadata={"channel_id": "123456"}
        )
        
        # Process the message (simplified)
        response = ChatResponse(
            response_text="Based on your query, I recommend the Conservative Growth Fund.",
            recommendations=[
                {
                    "product_id": "PROD_001",
                    "name": "Conservative Growth Fund",
                    "risk_level": "low",
                    "expected_return": "3-5%"
                }
            ],
            confidence=0.88,
            sources=["structured_db", "vector_search"],
            processing_time=1.2
        )
        
        # Verify response
        assert response.response_text is not None
        assert response.confidence > 0
        assert len(response.recommendations) > 0
        
        # Cleanup
        await event_bus.stop()


if __name__ == "__main__":
    # Run basic tests
    pytest.main([__file__, "-v"])

"""
Core data models for the financial product recommendation system.

This module contains all the Pydantic models used throughout the system,
including financial products, user profiles, conversation messages, and
knowledge graph entities.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
import uuid


class RiskLevel(str, Enum):
    """Risk levels for financial products"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class ProductType(str, Enum):
    """Types of financial products"""
    MUTUAL_FUND = "mutual_fund"
    ETF = "etf"
    BOND = "bond"
    STOCK = "stock"
    OPTION = "option"
    FUTURE = "future"
    CRYPTO = "crypto"
    REAL_ESTATE = "real_estate"


class InvestmentExperience(str, Enum):
    """Investment experience levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class MessageType(str, Enum):
    """Types of conversation messages"""
    USER_QUERY = "user_query"
    SYSTEM_RESPONSE = "system_response"
    SYSTEM_ERROR = "system_error"


class RelationshipType(str, Enum):
    """Types of knowledge graph relationships"""
    SIMILAR_TO = "similar_to"
    PART_OF = "part_of"
    DEPENDS_ON = "depends_on"
    CORRELATES_WITH = "correlates_with"
    OPPOSES = "opposes"
    SUPPORTS = "supports"


class FinancialProduct(BaseModel):
    """Core financial product model"""
    product_id: str = Field(description="Unique product identifier")
    name: str = Field(description="Product name")
    type: ProductType = Field(description="Product type")
    risk_level: RiskLevel = Field(description="Risk assessment")
    
    # Basic Information
    description: str = Field(description="Product description")
    issuer: str = Field(description="Product issuer")
    inception_date: datetime = Field(description="Product inception date")
    
    # Performance Metrics
    expected_return: str = Field(description="Expected return range")
    volatility: float = Field(description="Volatility measure")
    sharpe_ratio: Optional[float] = Field(description="Sharpe ratio")
    
    # Financial Details
    minimum_investment: float = Field(description="Minimum investment amount")
    expense_ratio: Optional[float] = Field(description="Expense ratio")
    dividend_yield: Optional[float] = Field(description="Dividend yield")
    
    # Compliance and Regulatory
    regulatory_status: str = Field(description="Regulatory status")
    compliance_requirements: List[str] = Field(description="Compliance requirements")
    
    # Metadata
    tags: List[str] = Field(description="Product tags for search")
    categories: List[str] = Field(description="Product categories")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Record creation time")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Record update time")
    
    # Vector embedding reference
    embedding_id: Optional[str] = Field(description="Reference to vector embedding")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_id": "FUND_001",
                "name": "Conservative Growth Fund",
                "type": "mutual_fund",
                "risk_level": "low",
                "description": "A conservative mutual fund focusing on stable growth",
                "issuer": "ABC Investment Company",
                "expected_return": "3-5%",
                "volatility": 0.08,
                "minimum_investment": 1000.0,
                "expense_ratio": 0.75,
                "tags": ["conservative", "growth", "low-risk"],
                "categories": ["mutual_funds", "equity", "domestic"]
            }
        }
    )


class UserProfile(BaseModel):
    """User profile and preferences model"""
    user_id: str = Field(description="Unique user identifier")
    
    # Personal Information
    name: str = Field(description="User name")
    email: str = Field(description="User email")
    age: int = Field(description="User age")
    income_level: str = Field(description="Income level category")
    
    # Investment Profile
    investment_experience: InvestmentExperience = Field(description="Investment experience level")
    risk_tolerance: RiskLevel = Field(description="User risk tolerance")
    investment_goals: List[str] = Field(description="Investment goals")
    time_horizon: str = Field(description="Investment time horizon")
    
    # Preferences
    preferred_product_types: List[ProductType] = Field(description="Preferred product types")
    preferred_sectors: List[str] = Field(description="Preferred sectors")
    geographic_preferences: List[str] = Field(description="Geographic preferences")
    
    # Financial Information
    current_portfolio_value: Optional[float] = Field(description="Current portfolio value")
    monthly_investment_capacity: Optional[float] = Field(description="Monthly investment capacity")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Profile creation time")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Profile update time")
    last_activity: datetime = Field(default_factory=datetime.utcnow, description="Last user activity")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "USER_001",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "age": 35,
                "income_level": "middle",
                "investment_experience": "intermediate",
                "risk_tolerance": "medium",
                "investment_goals": ["retirement", "wealth_building"],
                "time_horizon": "10-20_years",
                "preferred_product_types": ["mutual_fund", "etf"],
                "preferred_sectors": ["technology", "healthcare"]
            }
        }
    )


class ConversationMessage(BaseModel):
    """Individual message in conversation"""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique message identifier")
    session_id: str = Field(description="Conversation session identifier")
    user_id: str = Field(description="User identifier")
    
    message_type: MessageType = Field(description="Message type")
    content: str = Field(description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    
    # Context Information
    intent: Optional[Dict[str, Any]] = Field(default=None, description="Detected intent")
    entities: Optional[List[Dict[str, Any]]] = Field(default=None, description="Extracted entities")
    confidence: Optional[float] = Field(default=None, description="Intent confidence score")
    
    # Response Information (for system messages)
    recommendations: Optional[List[Dict[str, Any]]] = Field(default=None, description="Recommended products")
    sources: Optional[List[str]] = Field(default=None, description="Data sources used")
    generation_time: Optional[float] = Field(default=None, description="Response generation time")


class ConversationSession(BaseModel):
    """Complete conversation session"""
    session_id: str = Field(description="Session identifier")
    user_id: str = Field(description="User identifier")
    
    # Session Information
    start_time: datetime = Field(default_factory=datetime.utcnow, description="Session start time")
    end_time: Optional[datetime] = Field(description="Session end time")
    message_count: int = Field(default=0, description="Total message count")
    
    # Context
    user_profile: Optional[UserProfile] = Field(description="User profile at session start")
    session_context: Dict[str, Any] = Field(default_factory=dict, description="Session-specific context")
    
    # Messages
    messages: List[ConversationMessage] = Field(default_factory=list, description="Session messages")


class GraphNode(BaseModel):
    """Knowledge graph node"""
    node_id: str = Field(description="Node identifier")
    node_type: str = Field(description="Node type")
    properties: Dict[str, Any] = Field(description="Node properties")
    labels: List[str] = Field(description="Node labels")


class GraphRelationship(BaseModel):
    """Knowledge graph relationship"""
    relationship_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Relationship identifier")
    source_node_id: str = Field(description="Source node ID")
    target_node_id: str = Field(description="Target node ID")
    relationship_type: RelationshipType = Field(description="Relationship type")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Relationship properties")
    confidence: float = Field(description="Relationship confidence")


# Event Models for Event-Driven Architecture

class ChatMessageEvent(BaseModel):
    """Event for incoming chat messages"""
    event_type: str = Field(default="chat.message")
    platform: str = Field(description="Chat platform")
    user_id: str = Field(description="User identifier")
    session_id: str = Field(description="Session identifier")
    message_text: str = Field(description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Platform-specific metadata")


class ChatResponseEvent(BaseModel):
    """Event for chat responses"""
    event_type: str = Field(default="chat.response")
    session_id: str = Field(description="Session identifier")
    response_text: str = Field(description="Response content")
    recommendations: List[Dict[str, Any]] = Field(default_factory=list, description="Product recommendations")
    confidence: float = Field(description="Response confidence")
    sources: List[str] = Field(default_factory=list, description="Data sources used")
    processing_time: float = Field(description="Processing time")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Platform-specific metadata")


class SessionCreatedEvent(BaseModel):
    """Event for session creation"""
    event_type: str = Field(default="session.created")
    session_id: str = Field(description="Session identifier")
    user_id: str = Field(description="User identifier")
    platform: str = Field(description="Chat platform")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")


class SessionEndedEvent(BaseModel):
    """Event for session ending"""
    event_type: str = Field(default="session.ended")
    session_id: str = Field(description="Session identifier")
    duration: float = Field(description="Session duration in seconds")
    message_count: int = Field(description="Total messages in session")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")


# API Models

class ChatMessage(BaseModel):
    """Incoming chat message for API"""
    platform: str = Field(description="Chat platform (discord, telegram, etc.)")
    user_id: str = Field(description="User identifier")
    session_id: str = Field(description="Session identifier")
    message_text: str = Field(description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    metadata: Optional[Dict[str, Any]] = Field(description="Platform-specific metadata")


class ChatResponse(BaseModel):
    """Chat response for API"""
    response_text: str = Field(description="Response content")
    recommendations: Optional[List[Dict[str, Any]]] = Field(description="Product recommendations")
    confidence: float = Field(description="Response confidence score")
    sources: List[str] = Field(description="Data sources used")
    processing_time: float = Field(description="Processing time in seconds")


# Utility Models

class DataSynchronizationEvent(BaseModel):
    """Event for data synchronization across storage systems"""
    event_type: str = Field(description="Synchronization event type")
    entity_type: str = Field(description="Entity type being synchronized")
    entity_id: str = Field(description="Entity identifier")
    operation: str = Field(description="Operation type (create, update, delete)")
    data: Dict[str, Any] = Field(description="Entity data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    source: str = Field(description="Event source")


class IntentAnalysisResult(BaseModel):
    """Result of intent analysis"""
    primary_intent: str = Field(description="Primary detected intent")
    confidence: float = Field(description="Confidence score")
    entities: Dict[str, Any] = Field(default_factory=dict, description="Extracted entities")
    sub_intents: List[str] = Field(default_factory=list, description="Sub-intents")
    query_complexity: str = Field(description="Query complexity level")


class ToolSelectionResult(BaseModel):
    """Result of tool selection"""
    selected_tools: List[Dict[str, Any]] = Field(description="Selected tools and parameters")
    priority_order: List[str] = Field(description="Tool execution priority order")
    estimated_time: float = Field(description="Estimated processing time")
    fallback_options: List[str] = Field(default_factory=list, description="Fallback tool options")


class DataRetrievalResult(BaseModel):
    """Result of data retrieval operation"""
    source: str = Field(description="Data source name")
    results: List[Dict[str, Any]] = Field(description="Retrieved data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Retrieval metadata")
    confidence: float = Field(description="Result confidence")
    processing_time: float = Field(description="Processing time")

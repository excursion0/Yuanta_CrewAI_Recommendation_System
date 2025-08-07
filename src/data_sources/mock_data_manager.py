"""
Mock data manager for the financial product recommendation system.

This module provides mock financial products for testing and development
without requiring real database connections.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from enum import Enum

from src.data.models import FinancialProduct, UserProfile, GraphNode, GraphRelationship, ProductType, RiskLevel, InvestmentExperience, RelationshipType


class FusionStrategy(str, Enum):
    """Data fusion strategies"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"
    CONCATENATION = "concatenation"
    INTERSECTION = "intersection"


class MockDataManager:
    """
    Mock data manager for testing and development.
    
    Provides sample financial products without requiring real database connections.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the mock data manager.
        
        Args:
            config: Optional configuration dictionary (not used in mock)
        """
        self.config = config or {}
        self._logger = logging.getLogger(__name__)
        self._running = False
        
        # Initialize mock data
        self._mock_products = self._create_mock_products()
        self._mock_user_profiles = self._create_mock_user_profiles()
        self._mock_graph_nodes = self._create_mock_graph_nodes()
        self._mock_graph_relationships = self._create_mock_graph_relationships()
    
    def _create_mock_products(self) -> List[FinancialProduct]:
        """Create mock financial products"""
        now = datetime.now(timezone.utc)
        
        return [
            # Mutual Funds
            FinancialProduct(
                product_id="MF_001",
                name="Yuanta Growth Fund",
                type=ProductType.MUTUAL_FUND,
                risk_level=RiskLevel.HIGH,
                description="A growth-oriented mutual fund focusing on technology and innovation companies",
                issuer="Yuanta Securities",
                inception_date=datetime(2020, 1, 15, tzinfo=timezone.utc),
                expected_return="12-18%",
                volatility=0.25,
                sharpe_ratio=1.2,
                minimum_investment=5000.0,
                expense_ratio=0.015,
                dividend_yield=0.02,
                regulatory_status="approved",
                compliance_requirements=["SEC", "FINRA"],
                tags=["growth", "technology", "innovation"],
                categories=["equity", "growth"],
                embedding_id="emb_mf_001"
            ),
            FinancialProduct(
                product_id="MF_002",
                name="Yuanta Balanced Fund",
                type=ProductType.MUTUAL_FUND,
                risk_level=RiskLevel.MEDIUM,
                description="A balanced fund with 60% equities and 40% fixed income",
                issuer="Yuanta Securities",
                inception_date=datetime(2019, 6, 10, tzinfo=timezone.utc),
                expected_return="8-12%",
                volatility=0.15,
                sharpe_ratio=0.95,
                minimum_investment=3000.0,
                expense_ratio=0.012,
                dividend_yield=0.035,
                regulatory_status="approved",
                compliance_requirements=["SEC", "FINRA"],
                tags=["balanced", "diversified", "income"],
                categories=["mixed", "balanced"],
                embedding_id="emb_mf_002"
            ),
            FinancialProduct(
                product_id="MF_003",
                name="Yuanta Conservative Fund",
                type=ProductType.MUTUAL_FUND,
                risk_level=RiskLevel.LOW,
                description="A conservative fund focused on capital preservation and income",
                issuer="Yuanta Securities",
                inception_date=datetime(2018, 3, 20, tzinfo=timezone.utc),
                expected_return="4-6%",
                volatility=0.08,
                sharpe_ratio=0.75,
                minimum_investment=2000.0,
                expense_ratio=0.008,
                dividend_yield=0.045,
                regulatory_status="approved",
                compliance_requirements=["SEC", "FINRA"],
                tags=["conservative", "income", "preservation"],
                categories=["fixed_income", "conservative"],
                embedding_id="emb_mf_003"
            ),
            
            # ETFs
            FinancialProduct(
                product_id="ETF_001",
                name="Yuanta S&P 500 ETF",
                type=ProductType.ETF,
                risk_level=RiskLevel.MEDIUM,
                description="An ETF tracking the S&P 500 index for broad market exposure",
                issuer="Yuanta Securities",
                inception_date=datetime(2021, 2, 15, tzinfo=timezone.utc),
                expected_return="10-12%",
                volatility=0.18,
                sharpe_ratio=0.85,
                minimum_investment=100.0,
                expense_ratio=0.005,
                dividend_yield=0.018,
                regulatory_status="approved",
                compliance_requirements=["SEC", "FINRA"],
                tags=["index", "large_cap", "diversified"],
                categories=["equity", "index"],
                embedding_id="emb_etf_001"
            ),
            FinancialProduct(
                product_id="ETF_002",
                name="Yuanta Bond ETF",
                type=ProductType.ETF,
                risk_level=RiskLevel.LOW,
                description="An ETF focused on investment-grade corporate bonds",
                issuer="Yuanta Securities",
                inception_date=datetime(2020, 9, 8, tzinfo=timezone.utc),
                expected_return="3-5%",
                volatility=0.06,
                sharpe_ratio=0.65,
                minimum_investment=100.0,
                expense_ratio=0.003,
                dividend_yield=0.032,
                regulatory_status="approved",
                compliance_requirements=["SEC", "FINRA"],
                tags=["bonds", "income", "conservative"],
                categories=["fixed_income", "bonds"],
                embedding_id="emb_etf_002"
            ),
            
            # Bonds
            FinancialProduct(
                product_id="BOND_001",
                name="Yuanta Corporate Bond Fund",
                type=ProductType.BOND,
                risk_level=RiskLevel.LOW,
                description="A fund investing in high-quality corporate bonds",
                issuer="Yuanta Securities",
                inception_date=datetime(2017, 11, 12, tzinfo=timezone.utc),
                expected_return="4-6%",
                volatility=0.05,
                sharpe_ratio=0.70,
                minimum_investment=1000.0,
                expense_ratio=0.007,
                dividend_yield=0.040,
                regulatory_status="approved",
                compliance_requirements=["SEC", "FINRA"],
                tags=["corporate_bonds", "income", "stable"],
                categories=["fixed_income", "bonds"],
                embedding_id="emb_bond_001"
            ),
            
            # International
            FinancialProduct(
                product_id="INT_001",
                name="Yuanta International Growth Fund",
                type=ProductType.MUTUAL_FUND,
                risk_level=RiskLevel.HIGH,
                description="A fund investing in international growth companies",
                issuer="Yuanta Securities",
                inception_date=datetime(2021, 5, 20, tzinfo=timezone.utc),
                expected_return="15-20%",
                volatility=0.28,
                sharpe_ratio=1.1,
                minimum_investment=5000.0,
                expense_ratio=0.018,
                dividend_yield=0.015,
                regulatory_status="approved",
                compliance_requirements=["SEC", "FINRA"],
                tags=["international", "growth", "emerging_markets"],
                categories=["equity", "international"],
                embedding_id="emb_int_001"
            ),
            
            # Retirement
            FinancialProduct(
                product_id="RET_001",
                name="Yuanta Target Retirement 2040",
                type=ProductType.MUTUAL_FUND,
                risk_level=RiskLevel.MEDIUM,
                description="A target-date fund for investors planning to retire around 2040",
                issuer="Yuanta Securities",
                inception_date=datetime(2019, 8, 15, tzinfo=timezone.utc),
                expected_return="7-10%",
                volatility=0.14,
                sharpe_ratio=0.80,
                minimum_investment=1000.0,
                expense_ratio=0.010,
                dividend_yield=0.025,
                regulatory_status="approved",
                compliance_requirements=["SEC", "FINRA"],
                tags=["retirement", "target_date", "diversified"],
                categories=["mixed", "retirement"],
                embedding_id="emb_ret_001"
            )
        ]
    
    def _create_mock_user_profiles(self) -> Dict[str, UserProfile]:
        """Create mock user profiles"""
        now = datetime.now(timezone.utc)
        
        return {
            "user_001": UserProfile(
                user_id="user_001",
                name="John Doe",
                email="john.doe@example.com",
                age=35,
                income_level="high",
                investment_experience=InvestmentExperience.INTERMEDIATE,
                risk_tolerance=RiskLevel.HIGH,
                investment_goals=["wealth_building", "growth"],
                time_horizon="long_term",
                preferred_product_types=[ProductType.MUTUAL_FUND, ProductType.ETF],
                preferred_sectors=["technology", "healthcare"],
                geographic_preferences=["US", "international"],
                budget_range={"min": 10000.0, "max": 100000.0},
                current_portfolio_value=50000.0,
                monthly_investment_capacity=2000.0
            ),
            "user_002": UserProfile(
                user_id="user_002",
                name="Jane Smith",
                email="jane.smith@example.com",
                age=55,
                income_level="medium",
                investment_experience=InvestmentExperience.BEGINNER,
                risk_tolerance=RiskLevel.LOW,
                investment_goals=["income", "preservation"],
                time_horizon="medium_term",
                preferred_product_types=[ProductType.BOND, ProductType.ETF],
                preferred_sectors=["utilities", "consumer_staples"],
                geographic_preferences=["US"],
                budget_range={"min": 5000.0, "max": 50000.0},
                current_portfolio_value=25000.0,
                monthly_investment_capacity=1000.0
            ),
            "user_003": UserProfile(
                user_id="user_003",
                name="Mike Johnson",
                email="mike.johnson@example.com",
                age=45,
                income_level="medium",
                investment_experience=InvestmentExperience.INTERMEDIATE,
                risk_tolerance=RiskLevel.MEDIUM,
                investment_goals=["retirement", "balanced"],
                time_horizon="long_term",
                preferred_product_types=[ProductType.MUTUAL_FUND, ProductType.ETF],
                preferred_sectors=["diversified"],
                geographic_preferences=["US", "developed_markets"],
                budget_range={"min": 2000.0, "max": 25000.0},
                current_portfolio_value=15000.0,
                monthly_investment_capacity=800.0
            )
        }
    
    def _create_mock_graph_nodes(self) -> List[GraphNode]:
        """Create mock graph nodes"""
        now = datetime.now(timezone.utc)
        
        return [
            GraphNode(
                node_id="node_001",
                node_type="product",
                properties={
                    "name": "Yuanta Growth Fund",
                    "type": "mutual_fund",
                    "risk_level": "high"
                },
                labels=["product", "fund"]
            ),
            GraphNode(
                node_id="node_002",
                node_type="sector",
                properties={
                    "name": "Technology",
                    "description": "Technology sector investments"
                },
                labels=["sector", "technology"]
            ),
            GraphNode(
                node_id="node_003",
                node_type="risk_profile",
                properties={
                    "name": "High Risk",
                    "description": "High risk tolerance profile"
                },
                labels=["risk_profile", "high_risk"]
            )
        ]
    
    def _create_mock_graph_relationships(self) -> List[GraphRelationship]:
        """Create mock graph relationships"""
        now = datetime.now(timezone.utc)
        
        return [
            GraphRelationship(
                relationship_id="rel_001",
                source_node_id="node_001",
                target_node_id="node_002",
                relationship_type=RelationshipType.PART_OF,
                properties={
                    "weight": 0.8,
                    "confidence": 0.9
                },
                confidence=0.9
            ),
            GraphRelationship(
                relationship_id="rel_002",
                source_node_id="node_001",
                target_node_id="node_003",
                relationship_type=RelationshipType.SUPPORTS,
                properties={
                    "weight": 0.9,
                    "confidence": 0.95
                },
                confidence=0.95
            )
        ]
    
    async def start(self):
        """Start the mock data manager"""
        self._logger.info("Starting mock data manager...")
        self._running = True
        self._logger.info("Mock data manager started successfully")
    
    async def stop(self):
        """Stop the mock data manager"""
        self._logger.info("Stopping mock data manager...")
        self._running = False
        self._logger.info("Mock data manager stopped successfully")
    
    async def search_products(
        self,
        query: str = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[FinancialProduct]:
        """Search for financial products"""
        results = self._mock_products.copy()
        
        # Apply filters if provided
        if filters:
            if "risk_level" in filters:
                results = [p for p in results if p.risk_level == filters["risk_level"]]
            
            if "type" in filters:
                results = [p for p in results if p.type == filters["type"]]
            
            if "min_investment" in filters:
                results = [p for p in results if p.minimum_investment >= filters["min_investment"]]
            
            if "max_investment" in filters:
                results = [p for p in results if p.minimum_investment <= filters["max_investment"]]
        
        # Apply text search if query provided
        if query:
            query_lower = query.lower()
            results = [
                p for p in results
                if (query_lower in p.name.lower() or
                    query_lower in p.description.lower() or
                    any(query_lower in tag.lower() for tag in p.tags))
            ]
        
        # Apply pagination
        results = results[offset:offset + limit]
        
        return results
    
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by ID"""
        return self._mock_user_profiles.get(user_id)
    
    async def save_user_profile(self, profile: UserProfile) -> bool:
        """Save user profile"""
        self._mock_user_profiles[profile.user_id] = profile
        return True
    
    async def get_graph_nodes(
        self,
        node_type: str = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100
    ) -> List[GraphNode]:
        """Get graph nodes"""
        results = self._mock_graph_nodes.copy()
        
        if node_type:
            results = [n for n in results if n.node_type == node_type]
        
        return results[:limit]
    
    async def get_graph_relationships(
        self,
        source_node_id: str = None,
        target_node_id: str = None,
        relationship_type: str = None,
        limit: int = 100
    ) -> List[GraphRelationship]:
        """Get graph relationships"""
        results = self._mock_graph_relationships.copy()
        
        if source_node_id:
            results = [r for r in results if r.source_node_id == source_node_id]
        
        if target_node_id:
            results = [r for r in results if r.target_node_id == target_node_id]
        
        if relationship_type:
            results = [r for r in results if r.relationship_type == relationship_type]
        
        return results[:limit]
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of mock data manager"""
        return {
            "status": "healthy",
            "running": self._running,
            "products_count": len(self._mock_products),
            "users_count": len(self._mock_user_profiles),
            "nodes_count": len(self._mock_graph_nodes),
            "relationships_count": len(self._mock_graph_relationships),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def get_available_sources(self) -> List[str]:
        """Get available data sources"""
        return ["mock_data"]
    
    @property
    def is_running(self) -> bool:
        """Check if data manager is running"""
        return self._running
    
    async def add_product_to_all_sources(self, product: FinancialProduct):
        """Add a product to mock data"""
        self._mock_products.append(product)
        self._logger.info(f"Added product {product.product_id} to mock data") 
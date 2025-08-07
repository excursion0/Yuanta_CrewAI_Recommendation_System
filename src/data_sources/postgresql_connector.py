"""
PostgreSQL connector for the financial product recommendation system.

This module provides integration with PostgreSQL database for structured
data storage and retrieval of financial products and user profiles.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

import asyncpg
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from .base_connector import BaseDataConnector, DataSourceType
from src.data.models import FinancialProduct, UserProfile, GraphNode, GraphRelationship


class PostgreSQLConnector(BaseDataConnector):
    """
    PostgreSQL connector implementation.
    
    Handles connection to PostgreSQL database and provides
    structured query capabilities for financial products and user profiles.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the PostgreSQL connector.
        
        Args:
            config: Configuration dictionary with PostgreSQL connection details
        """
        super().__init__(DataSourceType.POSTGRESQL, config)
        self._engine = None
        self._session_factory = None
        
    @property
    def source_name(self) -> str:
        """Return the source name"""
        return "postgresql"
    
    async def connect(self):
        """Connect to PostgreSQL database"""
        try:
            # Extract connection parameters
            host = self.get_config("host", "localhost")
            port = self.get_config("port", 5432)
            database = self.get_config("database", "financial_products")
            username = self.get_config("username", "postgres")
            password = self.get_config("password", "")
            
            # Create async engine
            connection_string = f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}"
            self._engine = create_async_engine(
                connection_string,
                echo=self.get_config("echo", False),
                pool_size=self.get_config("pool_size", 10),
                max_overflow=self.get_config("max_overflow", 20)
            )
            
            # Create session factory
            self._session_factory = sessionmaker(
                self._engine, class_=AsyncSession, expire_on_commit=False
            )
            
            # Test connection
            async with self._engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            
            self._connected = True
            self._logger.info(f"Connected to PostgreSQL database: {database}")
            
        except Exception as e:
            self._logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from PostgreSQL database"""
        try:
            if self._engine:
                await self._engine.dispose()
                self._engine = None
                self._session_factory = None
            
            self._connected = False
            self._logger.info("Disconnected from PostgreSQL database")
            
        except Exception as e:
            self._logger.error(f"Error disconnecting from PostgreSQL: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the PostgreSQL connector.
        
        Returns:
            Dict[str, Any]: Health check results
        """
        try:
            if not self._connected:
                return {
                    "status": "disconnected",
                    "source": self.source_name,
                    "error": "Not connected to database"
                }
            
            # Test connection with a simple query
            async with self._engine.begin() as conn:
                result = await conn.execute(text("SELECT 1 as test"))
                row = result.fetchone()
                
                if row and row[0] == 1:
                    return {
                        "status": "healthy",
                        "source": self.source_name,
                        "connected": True,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "source": self.source_name,
                        "error": "Health check query failed"
                    }
                    
        except Exception as e:
            return {
                "status": "unhealthy",
                "source": self.source_name,
                "error": str(e)
            }
    
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a query on PostgreSQL.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List[Dict[str, Any]]: Query results
        """
        try:
            await self.ensure_connected()
            
            async with self._session_factory() as session:
                result = await session.execute(text(query), params or {})
                rows = result.fetchall()
                
                # Convert to list of dictionaries
                results = []
                for row in rows:
                    results.append(dict(row._mapping))
                
                return results
                
        except Exception as e:
            self._logger.error(f"Error executing query: {e}")
            return []
    
    async def _search_products_structured(self, query: str, filters: Dict[str, Any], 
                                        limit: int, offset: int) -> List[Dict[str, Any]]:
        """
        Search products using structured SQL queries.
        
        Args:
            query: Search query
            filters: Search filters
            limit: Maximum number of results
            offset: Result offset
            
        Returns:
            List[Dict[str, Any]]: Product results
        """
        try:
            # Build SQL query
            sql = """
                SELECT 
                    product_id, name, type, risk_level, description, issuer,
                    inception_date, expected_return, volatility, sharpe_ratio,
                    minimum_investment, expense_ratio, dividend_yield,
                    regulatory_status, compliance_requirements, tags, categories,
                    embedding_id, created_at, updated_at
                FROM financial_products
                WHERE 1=1
            """
            
            params = {}
            
            # Add search conditions
            if query:
                sql += " AND (name ILIKE :query OR description ILIKE :query)"
                params["query"] = f"%{query}%"
            
            # Add filters
            if filters:
                if "risk_level" in filters:
                    sql += " AND risk_level = :risk_level"
                    params["risk_level"] = filters["risk_level"]
                
                if "product_type" in filters:
                    sql += " AND type = :product_type"
                    params["product_type"] = filters["product_type"]
                
                if "min_investment" in filters:
                    sql += " AND minimum_investment >= :min_investment"
                    params["min_investment"] = filters["min_investment"]
                
                if "max_investment" in filters:
                    sql += " AND minimum_investment <= :max_investment"
                    params["max_investment"] = filters["max_investment"]
            
            # Add ordering and pagination
            sql += " ORDER BY name LIMIT :limit OFFSET :offset"
            params["limit"] = limit
            params["offset"] = offset
            
            return await self.execute_query(sql, params)
            
        except Exception as e:
            self._logger.error(f"Error in structured product search: {e}")
            return []
    
    async def _search_products_vector(self, query: str, filters: Dict[str, Any], 
                                    limit: int, offset: int) -> List[Dict[str, Any]]:
        """
        Search products using vector similarity (placeholder for PostgreSQL vector extension).
        
        Args:
            query: Search query
            filters: Search filters
            limit: Maximum number of results
            offset: Result offset
            
        Returns:
            List[Dict[str, Any]]: Product results
        """
        # Note: Using structured search as primary method
        # For advanced vector search, implement pgvector extension:
        # - Install pgvector extension
        # - Implement vector similarity search
        # - Use embeddings for semantic search
        self._logger.info("Vector search not implemented, falling back to structured search")
        return await self._search_products_structured(query, filters, limit, offset)
    
    async def _search_products_graph(self, query: str, filters: Dict[str, Any], 
                                   limit: int, offset: int) -> List[Dict[str, Any]]:
        """
        Search products using graph queries (not applicable for PostgreSQL).
        
        Args:
            query: Search query
            filters: Search filters
            limit: Maximum number of results
            offset: Result offset
            
        Returns:
            List[Dict[str, Any]]: Product results
        """
        self._logger.warning("Graph search not supported for PostgreSQL")
        return []
    
    async def _get_user_profile_structured(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile using structured queries.
        
        Args:
            user_id: User identifier
            
        Returns:
            Optional[Dict[str, Any]]: User profile data
        """
        try:
            sql = """
                SELECT 
                    user_id, name, email, age, income_level, investment_experience,
                    risk_tolerance, investment_goals, time_horizon, preferred_product_types,
                    preferred_sectors, geographic_preferences, current_portfolio_value,
                    monthly_investment_capacity, created_at, updated_at
                FROM user_profiles
                WHERE user_id = :user_id
            """
            
            results = await self.execute_query(sql, {"user_id": user_id})
            
            if results:
                return results[0]
            return None
            
        except Exception as e:
            self._logger.error(f"Error getting user profile: {e}")
            return None
    
    async def _save_user_profile_structured(self, profile: UserProfile) -> bool:
        """
        Save user profile using structured queries.
        
        Args:
            profile: User profile to save
            
        Returns:
            bool: True if successful
        """
        try:
            # Convert profile to dict for insertion
            profile_data = profile.model_dump()
            
            # Handle list fields
            profile_data["investment_goals"] = list(profile_data.get("investment_goals", []))
            profile_data["preferred_product_types"] = list(profile_data.get("preferred_product_types", []))
            profile_data["preferred_sectors"] = list(profile_data.get("preferred_sectors", []))
            profile_data["geographic_preferences"] = list(profile_data.get("geographic_preferences", []))
            
            sql = """
                INSERT INTO user_profiles (
                    user_id, name, email, age, income_level, investment_experience,
                    risk_tolerance, investment_goals, time_horizon, preferred_product_types,
                    preferred_sectors, geographic_preferences, current_portfolio_value,
                    monthly_investment_capacity, created_at, updated_at
                ) VALUES (
                    :user_id, :name, :email, :age, :income_level, :investment_experience,
                    :risk_tolerance, :investment_goals, :time_horizon, :preferred_product_types,
                    :preferred_sectors, :geographic_preferences, :current_portfolio_value,
                    :monthly_investment_capacity, :created_at, :updated_at
                )
                ON CONFLICT (user_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    email = EXCLUDED.email,
                    age = EXCLUDED.age,
                    income_level = EXCLUDED.income_level,
                    investment_experience = EXCLUDED.investment_experience,
                    risk_tolerance = EXCLUDED.risk_tolerance,
                    investment_goals = EXCLUDED.investment_goals,
                    time_horizon = EXCLUDED.time_horizon,
                    preferred_product_types = EXCLUDED.preferred_product_types,
                    preferred_sectors = EXCLUDED.preferred_sectors,
                    geographic_preferences = EXCLUDED.geographic_preferences,
                    current_portfolio_value = EXCLUDED.current_portfolio_value,
                    monthly_investment_capacity = EXCLUDED.monthly_investment_capacity,
                    updated_at = EXCLUDED.updated_at
            """
            
            await self.execute_query(sql, profile_data)
            return True
            
        except Exception as e:
            self._logger.error(f"Error saving user profile: {e}")
            return False
    
    async def _get_graph_nodes_neo4j(self, node_type: str, filters: Dict[str, Any], 
                                    limit: int) -> List[Dict[str, Any]]:
        """Get graph nodes from Neo4j (not applicable for PostgreSQL)"""
        self._logger.warning("Graph node retrieval not supported for PostgreSQL")
        return []
    
    async def _get_graph_relationships_neo4j(self, source_node_id: str, target_node_id: str,
                                           relationship_type: str, limit: int) -> List[Dict[str, Any]]:
        """Get graph relationships from Neo4j (not applicable for PostgreSQL)"""
        self._logger.warning("Graph relationship retrieval not supported for PostgreSQL")
        return []
    
    async def create_tables(self):
        """Create database tables if they don't exist"""
        try:
            # Create financial_products table
            products_sql = """
                CREATE TABLE IF NOT EXISTS financial_products (
                    product_id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    type VARCHAR(50) NOT NULL,
                    risk_level VARCHAR(20) NOT NULL,
                    description TEXT,
                    issuer VARCHAR(255),
                    inception_date TIMESTAMP,
                    expected_return VARCHAR(50),
                    volatility DECIMAL(5,4),
                    sharpe_ratio DECIMAL(5,4),
                    minimum_investment DECIMAL(15,2),
                    expense_ratio DECIMAL(5,4),
                    dividend_yield DECIMAL(5,4),
                    regulatory_status VARCHAR(50),
                    compliance_requirements TEXT[],
                    tags TEXT[],
                    categories TEXT[],
                    embedding_id VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            
            # Create user_profiles table
            profiles_sql = """
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255),
                    age INTEGER,
                    income_level VARCHAR(50),
                    investment_experience VARCHAR(50),
                    risk_tolerance VARCHAR(20),
                    investment_goals TEXT[],
                    time_horizon VARCHAR(50),
                    preferred_product_types TEXT[],
                    preferred_sectors TEXT[],
                    geographic_preferences TEXT[],
                    current_portfolio_value DECIMAL(15,2),
                    monthly_investment_capacity DECIMAL(15,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            
            await self.execute_query(products_sql)
            await self.execute_query(profiles_sql)
            
            self._logger.info("Database tables created successfully")
            
        except Exception as e:
            self._logger.error(f"Error creating tables: {e}")
            raise 
"""
Base data connector for the financial product recommendation system.

This module provides the base interface that all data source connectors
must implement, ensuring consistent behavior across different data sources.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum

from src.data.models import FinancialProduct, UserProfile, GraphNode, GraphRelationship


class DataSourceType(str, Enum):
    """Data source types"""
    POSTGRESQL = "postgresql"
    CHROMADB = "chromadb"
    NEO4J = "neo4j"


class QueryType(str, Enum):
    """Query types for different data sources"""
    STRUCTURED = "structured"
    VECTOR = "vector"
    GRAPH = "graph"
    HYBRID = "hybrid"


class BaseDataConnector(ABC):
    """
    Base class for data source connectors.
    
    Provides a common interface for different data sources
    and handles connection management, query execution, and data retrieval.
    """
    
    def __init__(self, source_type: DataSourceType, config: Dict[str, Any]):
        """
        Initialize the data connector.
        
        Args:
            source_type: Type of data source
            config: Configuration dictionary for the connector
        """
        self.source_type = source_type
        self.config = config
        self._logger = logging.getLogger(self.__class__.__name__)
        self._connected = False
        self._connection = None
        
    @property
    @abstractmethod
    def source_name(self) -> str:
        """Return the source name"""
        pass
    
    @abstractmethod
    async def connect(self):
        """Connect to the data source"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Disconnect from the data source"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the connector"""
        pass
    
    @abstractmethod
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a query on the data source.
        
        Args:
            query: Query string or query object
            params: Query parameters
            
        Returns:
            List[Dict[str, Any]]: Query results
        """
        pass
    
    async def search_products(self, 
                            query: str = None,
                            filters: Optional[Dict[str, Any]] = None,
                            limit: int = 10,
                            offset: int = 0) -> List[FinancialProduct]:
        """
        Search for financial products.
        
        Args:
            query: Search query
            filters: Search filters
            limit: Maximum number of results
            offset: Result offset
            
        Returns:
            List[FinancialProduct]: List of financial products
        """
        try:
            # Build query based on source type
            if self.source_type == DataSourceType.POSTGRESQL:
                results = await self._search_products_structured(query, filters, limit, offset)
            elif self.source_type == DataSourceType.CHROMADB:
                results = await self._search_products_vector(query, filters, limit, offset)
            elif self.source_type == DataSourceType.NEO4J:
                results = await self._search_products_graph(query, filters, limit, offset)
            else:
                raise ValueError(f"Unsupported source type: {self.source_type}")
            
            # Convert results to FinancialProduct objects
            products = []
            for result in results:
                try:
                    product = FinancialProduct(**result)
                    products.append(product)
                except Exception as e:
                    self._logger.warning(f"Failed to parse product result: {e}")
                    continue
            
            return products
            
        except Exception as e:
            self._logger.error(f"Error searching products: {e}")
            return []
    
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """
        Get user profile from the data source.
        
        Args:
            user_id: User identifier
            
        Returns:
            Optional[UserProfile]: User profile if found
        """
        try:
            if self.source_type == DataSourceType.POSTGRESQL:
                result = await self._get_user_profile_structured(user_id)
            else:
                self._logger.warning(f"User profile retrieval not supported for {self.source_type}")
                return None
            
            if result:
                return UserProfile(**result)
            return None
            
        except Exception as e:
            self._logger.error(f"Error getting user profile: {e}")
            return None
    
    async def save_user_profile(self, profile: UserProfile) -> bool:
        """
        Save user profile to the data source.
        
        Args:
            profile: User profile to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.source_type == DataSourceType.POSTGRESQL:
                return await self._save_user_profile_structured(profile)
            else:
                self._logger.warning(f"User profile saving not supported for {self.source_type}")
                return False
                
        except Exception as e:
            self._logger.error(f"Error saving user profile: {e}")
            return False
    
    async def get_graph_nodes(self, 
                             node_type: str = None,
                             filters: Optional[Dict[str, Any]] = None,
                             limit: int = 100) -> List[GraphNode]:
        """
        Get graph nodes from the data source.
        
        Args:
            node_type: Type of nodes to retrieve
            filters: Node filters
            limit: Maximum number of results
            
        Returns:
            List[GraphNode]: List of graph nodes
        """
        try:
            if self.source_type == DataSourceType.NEO4J:
                results = await self._get_graph_nodes_neo4j(node_type, filters, limit)
            else:
                self._logger.warning(f"Graph node retrieval not supported for {self.source_type}")
                return []
            
            nodes = []
            for result in results:
                try:
                    node = GraphNode(**result)
                    nodes.append(node)
                except Exception as e:
                    self._logger.warning(f"Failed to parse graph node: {e}")
                    continue
            
            return nodes
            
        except Exception as e:
            self._logger.error(f"Error getting graph nodes: {e}")
            return []
    
    async def get_graph_relationships(self,
                                    source_node_id: str = None,
                                    target_node_id: str = None,
                                    relationship_type: str = None,
                                    limit: int = 100) -> List[GraphRelationship]:
        """
        Get graph relationships from the data source.
        
        Args:
            source_node_id: Source node ID
            target_node_id: Target node ID
            relationship_type: Type of relationship
            limit: Maximum number of results
            
        Returns:
            List[GraphRelationship]: List of graph relationships
        """
        try:
            if self.source_type == DataSourceType.NEO4J:
                results = await self._get_graph_relationships_neo4j(
                    source_node_id, target_node_id, relationship_type, limit
                )
            else:
                self._logger.warning(f"Graph relationship retrieval not supported for {self.source_type}")
                return []
            
            relationships = []
            for result in results:
                try:
                    rel = GraphRelationship(**result)
                    relationships.append(rel)
                except Exception as e:
                    self._logger.warning(f"Failed to parse graph relationship: {e}")
                    continue
            
            return relationships
            
        except Exception as e:
            self._logger.error(f"Error getting graph relationships: {e}")
            return []
    
    # Abstract methods for specific implementations
    @abstractmethod
    async def _search_products_structured(self, query: str, filters: Dict[str, Any], 
                                        limit: int, offset: int) -> List[Dict[str, Any]]:
        """Search products using structured queries"""
        pass
    
    @abstractmethod
    async def _search_products_vector(self, query: str, filters: Dict[str, Any], 
                                    limit: int, offset: int) -> List[Dict[str, Any]]:
        """Search products using vector similarity"""
        pass
    
    @abstractmethod
    async def _search_products_graph(self, query: str, filters: Dict[str, Any], 
                                   limit: int, offset: int) -> List[Dict[str, Any]]:
        """Search products using graph queries"""
        pass
    
    @abstractmethod
    async def _get_user_profile_structured(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile using structured queries"""
        pass
    
    @abstractmethod
    async def _save_user_profile_structured(self, profile: UserProfile) -> bool:
        """Save user profile using structured queries"""
        pass
    
    @abstractmethod
    async def _get_graph_nodes_neo4j(self, node_type: str, filters: Dict[str, Any], 
                                    limit: int) -> List[Dict[str, Any]]:
        """Get graph nodes from Neo4j"""
        pass
    
    @abstractmethod
    async def _get_graph_relationships_neo4j(self, source_node_id: str, target_node_id: str,
                                           relationship_type: str, limit: int) -> List[Dict[str, Any]]:
        """Get graph relationships from Neo4j"""
        pass
    
    @property
    def is_connected(self) -> bool:
        """Check if the connector is connected"""
        return self._connected
    
    async def ensure_connected(self):
        """Ensure the connector is connected"""
        if not self._connected:
            await self.connect()
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Any: Configuration value
        """
        return self.config.get(key, default)
    
    async def test_connection(self) -> bool:
        """
        Test the connection to the data source.
        
        Returns:
            bool: True if connection is successful
        """
        try:
            await self.ensure_connected()
            health = await self.health_check()
            return health.get("status") == "healthy"
        except Exception as e:
            self._logger.error(f"Connection test failed: {e}")
            return False 
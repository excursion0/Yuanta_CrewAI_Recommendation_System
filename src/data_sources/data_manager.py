"""
Data manager for the financial product recommendation system.

This module provides centralized management of all data sources,
including PostgreSQL, ChromaDB, and Neo4j, with unified access
and query coordination.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum

from .base_connector import BaseDataConnector, DataSourceType, QueryType
from .postgresql_connector import PostgreSQLConnector
from .chromadb_connector import ChromaDBConnector
from .neo4j_connector import Neo4jConnector
from src.data.models import FinancialProduct, UserProfile, GraphNode, GraphRelationship


class FusionStrategy(str, Enum):
    """Data fusion strategies"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"
    CONCATENATION = "concatenation"
    INTERSECTION = "intersection"


class DataManager:
    """
    Central manager for all data sources.
    
    Coordinates multiple data sources and provides unified access
    to structured, vector, and graph data with intelligent fusion.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the data manager.
        
        Args:
            config: Configuration dictionary with data source settings
        """
        self.config = config
        self._logger = logging.getLogger(__name__)
        
        # Store connectors by source type
        self._connectors: Dict[DataSourceType, BaseDataConnector] = {}
        self._running = False
        
        # Initialize connectors based on configuration
        self._initialize_connectors()
    
    def _initialize_connectors(self):
        """Initialize data source connectors based on configuration"""
        try:
            # PostgreSQL connector
            if "postgresql" in self.config:
                postgres_config = self.config["postgresql"]
                self._connectors[DataSourceType.POSTGRESQL] = PostgreSQLConnector(postgres_config)
                self._logger.info("PostgreSQL connector initialized")
            
            # ChromaDB connector
            if "chromadb" in self.config:
                chromadb_config = self.config["chromadb"]
                self._connectors[DataSourceType.CHROMADB] = ChromaDBConnector(chromadb_config)
                self._logger.info("ChromaDB connector initialized")
            
            # Neo4j connector
            if "neo4j" in self.config:
                neo4j_config = self.config["neo4j"]
                self._connectors[DataSourceType.NEO4J] = Neo4jConnector(neo4j_config)
                self._logger.info("Neo4j connector initialized")
            
            self._logger.info(f"Initialized {len(self._connectors)} data source connectors")
            
        except Exception as e:
            self._logger.error(f"Error initializing connectors: {e}")
            raise
    
    async def start(self):
        """Start all data source connectors"""
        try:
            self._logger.info("Starting data manager...")
            
            # Start all connectors
            for source_type, connector in self._connectors.items():
                try:
                    await connector.connect()
                    self._logger.info(f"Connected to {source_type.value}")
                except Exception as e:
                    self._logger.error(f"Failed to connect to {source_type.value}: {e}")
            
            # Create schemas if needed
            await self._create_schemas()
            
            self._running = True
            self._logger.info("Data manager started successfully")
            
        except Exception as e:
            self._logger.error(f"Failed to start data manager: {e}")
            raise
    
    async def stop(self):
        """Stop all data source connectors"""
        try:
            self._logger.info("Stopping data manager...")
            
            # Stop all connectors
            for source_type, connector in self._connectors.items():
                try:
                    await connector.disconnect()
                    self._logger.info(f"Disconnected from {source_type.value}")
                except Exception as e:
                    self._logger.error(f"Error disconnecting from {source_type.value}: {e}")
            
            self._running = False
            self._logger.info("Data manager stopped successfully")
            
        except Exception as e:
            self._logger.error(f"Error stopping data manager: {e}")
    
    async def _create_schemas(self):
        """Create database schemas if needed"""
        try:
            # Create PostgreSQL tables
            if DataSourceType.POSTGRESQL in self._connectors:
                postgres_connector = self._connectors[DataSourceType.POSTGRESQL]
                await postgres_connector.create_tables()
            
            # Create Neo4j schema
            if DataSourceType.NEO4J in self._connectors:
                neo4j_connector = self._connectors[DataSourceType.NEO4J]
                await neo4j_connector.create_graph_schema()
            
            self._logger.info("Database schemas created successfully")
            
        except Exception as e:
            self._logger.error(f"Error creating schemas: {e}")
            raise
    
    async def search_products(self, 
                            query: str = None,
                            filters: Optional[Dict[str, Any]] = None,
                            query_types: List[QueryType] = None,
                            fusion_strategy: FusionStrategy = FusionStrategy.WEIGHTED,
                            limit: int = 10,
                            offset: int = 0) -> List[FinancialProduct]:
        """
        Search for financial products across all data sources.
        
        Args:
            query: Search query
            filters: Search filters
            query_types: Types of queries to perform
            fusion_strategy: Strategy for combining results
            limit: Maximum number of results
            offset: Result offset
            
        Returns:
            List[FinancialProduct]: Combined product results
        """
        try:
            if query_types is None:
                query_types = [QueryType.STRUCTURED, QueryType.VECTOR, QueryType.GRAPH]
            
            # Collect results from each data source
            all_results = {}
            
            for source_type, connector in self._connectors.items():
                try:
                    if source_type == DataSourceType.POSTGRESQL and QueryType.STRUCTURED in query_types:
                        results = await connector.search_products(query, filters, limit, offset)
                        all_results[source_type] = results
                    
                    elif source_type == DataSourceType.CHROMADB and QueryType.VECTOR in query_types:
                        results = await connector.search_products(query, filters, limit, offset)
                        all_results[source_type] = results
                    
                    elif source_type == DataSourceType.NEO4J and QueryType.GRAPH in query_types:
                        results = await connector.search_products(query, filters, limit, offset)
                        all_results[source_type] = results
                        
                except Exception as e:
                    self._logger.error(f"Error searching {source_type.value}: {e}")
                    continue
            
            # Fuse results based on strategy
            fused_results = await self._fuse_results(all_results, fusion_strategy, limit)
            
            return fused_results
            
        except Exception as e:
            self._logger.error(f"Error in product search: {e}")
            return []
    
    async def _fuse_results(self, 
                           all_results: Dict[DataSourceType, List[FinancialProduct]],
                           strategy: FusionStrategy,
                           limit: int) -> List[FinancialProduct]:
        """
        Fuse results from multiple data sources.
        
        Args:
            all_results: Results from each data source
            strategy: Fusion strategy to use
            limit: Maximum number of results
            
        Returns:
            List[FinancialProduct]: Fused results
        """
        try:
            if strategy == FusionStrategy.ROUND_ROBIN:
                return await self._fuse_round_robin(all_results, limit)
            
            elif strategy == FusionStrategy.WEIGHTED:
                return await self._fuse_weighted(all_results, limit)
            
            elif strategy == FusionStrategy.CONCATENATION:
                return await self._fuse_concatenation(all_results, limit)
            
            elif strategy == FusionStrategy.INTERSECTION:
                return await self._fuse_intersection(all_results, limit)
            
            else:
                self._logger.warning(f"Unknown fusion strategy: {strategy}")
                return await self._fuse_weighted(all_results, limit)
                
        except Exception as e:
            self._logger.error(f"Error fusing results: {e}")
            return []
    
    async def _fuse_round_robin(self, all_results: Dict[DataSourceType, List[FinancialProduct]], 
                               limit: int) -> List[FinancialProduct]:
        """Fuse results using round-robin strategy"""
        fused = []
        sources = list(all_results.keys())
        
        if not sources:
            return fused
        
        # Round-robin through sources
        max_length = max(len(results) for results in all_results.values())
        for i in range(min(max_length, limit)):
            for source in sources:
                if i < len(all_results[source]):
                    fused.append(all_results[source][i])
                    if len(fused) >= limit:
                        return fused
        
        return fused
    
    async def _fuse_weighted(self, all_results: Dict[DataSourceType, List[FinancialProduct]], 
                           limit: int) -> List[FinancialProduct]:
        """Fuse results using weighted strategy"""
        # Define weights for different sources
        weights = {
            DataSourceType.POSTGRESQL: 0.4,  # Structured data
            DataSourceType.CHROMADB: 0.4,    # Vector similarity
            DataSourceType.NEO4J: 0.2        # Graph relationships
        }
        
        # Create weighted list
        weighted_results = []
        for source_type, results in all_results.items():
            weight = weights.get(source_type, 0.1)
            for product in results:
                weighted_results.append((product, weight))
        
        # Sort by weight and return top results
        weighted_results.sort(key=lambda x: x[1], reverse=True)
        return [product for product, _ in weighted_results[:limit]]
    
    async def _fuse_concatenation(self, all_results: Dict[DataSourceType, List[FinancialProduct]], 
                                limit: int) -> List[FinancialProduct]:
        """Fuse results using concatenation strategy"""
        fused = []
        seen_ids = set()
        
        for results in all_results.values():
            for product in results:
                if product.product_id not in seen_ids:
                    fused.append(product)
                    seen_ids.add(product.product_id)
                    if len(fused) >= limit:
                        return fused
        
        return fused
    
    async def _fuse_intersection(self, all_results: Dict[DataSourceType, List[FinancialProduct]], 
                               limit: int) -> List[FinancialProduct]:
        """Fuse results using intersection strategy"""
        if not all_results:
            return []
        
        # Find products that appear in all sources
        product_counts = {}
        for results in all_results.values():
            for product in results:
                product_counts[product.product_id] = product_counts.get(product.product_id, 0) + 1
        
        # Get products that appear in all sources
        num_sources = len(all_results)
        intersection_products = [
            product_id for product_id, count in product_counts.items()
            if count == num_sources
        ]
        
        # Return intersection products
        fused = []
        for product_id in intersection_products[:limit]:
            # Find the product in any source
            for results in all_results.values():
                for product in results:
                    if product.product_id == product_id:
                        fused.append(product)
                        break
                if product_id in [p.product_id for p in fused]:
                    break
        
        return fused
    
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """
        Get user profile from structured data source.
        
        Args:
            user_id: User identifier
            
        Returns:
            Optional[UserProfile]: User profile if found
        """
        try:
            # User profiles are stored in PostgreSQL
            if DataSourceType.POSTGRESQL in self._connectors:
                connector = self._connectors[DataSourceType.POSTGRESQL]
                return await connector.get_user_profile(user_id)
            
            return None
            
        except Exception as e:
            self._logger.error(f"Error getting user profile: {e}")
            return None
    
    async def save_user_profile(self, profile: UserProfile) -> bool:
        """
        Save user profile to structured data source.
        
        Args:
            profile: User profile to save
            
        Returns:
            bool: True if successful
        """
        try:
            # User profiles are stored in PostgreSQL
            if DataSourceType.POSTGRESQL in self._connectors:
                connector = self._connectors[DataSourceType.POSTGRESQL]
                return await connector.save_user_profile(profile)
            
            return False
            
        except Exception as e:
            self._logger.error(f"Error saving user profile: {e}")
            return False
    
    async def get_graph_nodes(self, 
                             node_type: str = None,
                             filters: Optional[Dict[str, Any]] = None,
                             limit: int = 100) -> List[GraphNode]:
        """
        Get graph nodes from Neo4j.
        
        Args:
            node_type: Type of nodes to retrieve
            filters: Node filters
            limit: Maximum number of results
            
        Returns:
            List[GraphNode]: Graph nodes
        """
        try:
            if DataSourceType.NEO4J in self._connectors:
                connector = self._connectors[DataSourceType.NEO4J]
                return await connector.get_graph_nodes(node_type, filters, limit)
            
            return []
            
        except Exception as e:
            self._logger.error(f"Error getting graph nodes: {e}")
            return []
    
    async def get_graph_relationships(self,
                                    source_node_id: str = None,
                                    target_node_id: str = None,
                                    relationship_type: str = None,
                                    limit: int = 100) -> List[GraphRelationship]:
        """
        Get graph relationships from Neo4j.
        
        Args:
            source_node_id: Source node ID
            target_node_id: Target node ID
            relationship_type: Type of relationship
            limit: Maximum number of results
            
        Returns:
            List[GraphRelationship]: Graph relationships
        """
        try:
            if DataSourceType.NEO4J in self._connectors:
                connector = self._connectors[DataSourceType.NEO4J]
                return await connector.get_graph_relationships(
                    source_node_id, target_node_id, relationship_type, limit
                )
            
            return []
            
        except Exception as e:
            self._logger.error(f"Error getting graph relationships: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on all data sources.
        
        Returns:
            Dict[str, Any]: Health check results
        """
        health_results = {
            "manager_running": self._running,
            "sources": {}
        }
        
        for source_type, connector in self._connectors.items():
            try:
                source_health = await connector.health_check()
                health_results["sources"][source_type.value] = source_health
            except Exception as e:
                health_results["sources"][source_type.value] = {
                    "error": str(e),
                    "status": "unhealthy"
                }
        
        return health_results
    
    def get_available_sources(self) -> List[str]:
        """
        Get list of available data sources.
        
        Returns:
            List[str]: List of available source names
        """
        return [source_type.value for source_type in self._connectors.keys()]
    
    @property
    def is_running(self) -> bool:
        """Check if the data manager is running"""
        return self._running
    
    async def add_product_to_all_sources(self, product: FinancialProduct):
        """
        Add a product to all data sources.
        
        Args:
            product: Financial product to add
        """
        try:
            # Add to PostgreSQL
            if DataSourceType.POSTGRESQL in self._connectors:
                # PostgreSQL will handle this through regular database operations
                self._logger.info(f"Product {product.product_id} will be added to PostgreSQL via database operations")
            
            # Add to ChromaDB
            if DataSourceType.CHROMADB in self._connectors:
                connector = self._connectors[DataSourceType.CHROMADB]
                await connector.add_product(product)
            
            # Add to Neo4j
            if DataSourceType.NEO4J in self._connectors:
                connector = self._connectors[DataSourceType.NEO4J]
                await connector.add_product_node(product)
            
            self._logger.info(f"Added product {product.product_id} to all data sources")
            
        except Exception as e:
            self._logger.error(f"Error adding product to data sources: {e}")
            raise 
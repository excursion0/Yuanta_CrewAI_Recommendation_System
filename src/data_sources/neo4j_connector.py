"""
Neo4j connector for the financial product recommendation system.

This module provides integration with Neo4j graph database for GraphRAG
functionality and relationship-based queries.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from neo4j import AsyncGraphDatabase
from neo4j.exceptions import ServiceUnavailable

from .base_connector import BaseDataConnector, DataSourceType
from src.data.models import FinancialProduct, UserProfile, GraphNode, GraphRelationship


class Neo4jConnector(BaseDataConnector):
    """
    Neo4j connector implementation.
    
    Handles connection to Neo4j graph database and provides
    graph-based query capabilities for financial products and relationships.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Neo4j connector.
        
        Args:
            config: Configuration dictionary with Neo4j connection details
        """
        super().__init__(DataSourceType.NEO4J, config)
        self._driver = None
        
    @property
    def source_name(self) -> str:
        """Return the source name"""
        return "neo4j"
    
    async def connect(self):
        """Connect to Neo4j database"""
        try:
            # Extract connection parameters
            uri = self.get_config("uri", "bolt://localhost:7687")
            username = self.get_config("username", "neo4j")
            password = self.get_config("password", "password")
            
            # Create driver
            self._driver = AsyncGraphDatabase.driver(uri, auth=(username, password))
            
            # Test connection
            async with self._driver.session() as session:
                result = await session.run("RETURN 1 as test")
                record = await result.single()
                if not record or record["test"] != 1:
                    raise Exception("Connection test failed")
            
            self._connected = True
            self._logger.info(f"Connected to Neo4j database: {uri}")
            
        except Exception as e:
            self._logger.error(f"Failed to connect to Neo4j: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from Neo4j database"""
        try:
            if self._driver:
                await self._driver.close()
                self._driver = None
            
            self._connected = False
            self._logger.info("Disconnected from Neo4j database")
            
        except Exception as e:
            self._logger.error(f"Error disconnecting from Neo4j: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the Neo4j connector.
        
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
            async with self._driver.session() as session:
                result = await session.run("RETURN 1 as test")
                record = await result.single()
                
                if record and record["test"] == 1:
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
        Execute a Cypher query on Neo4j.
        
        Args:
            query: Cypher query string
            params: Query parameters
            
        Returns:
            List[Dict[str, Any]]: Query results
        """
        try:
            await self.ensure_connected()
            
            async with self._driver.session() as session:
                result = await session.run(query, params or {})
                records = await result.data()
                
                return records
                
        except Exception as e:
            self._logger.error(f"Error executing query: {e}")
            return []
    
    async def _search_products_structured(self, query: str, filters: Dict[str, Any], 
                                        limit: int, offset: int) -> List[Dict[str, Any]]:
        """
        Search products using structured Cypher queries.
        
        Args:
            query: Search query
            filters: Search filters
            limit: Maximum number of results
            offset: Result offset
            
        Returns:
            List[Dict[str, Any]]: Product results
        """
        try:
            # Build Cypher query
            cypher_query = """
                MATCH (p:Product)
                WHERE 1=1
            """
            
            params = {}
            
            # Add search conditions
            if query:
                cypher_query += " AND (p.name CONTAINS $query OR p.description CONTAINS $query)"
                params["query"] = query
            
            # Add filters
            if filters:
                if "risk_level" in filters:
                    cypher_query += " AND p.risk_level = $risk_level"
                    params["risk_level"] = filters["risk_level"]
                
                if "product_type" in filters:
                    cypher_query += " AND p.type = $product_type"
                    params["product_type"] = filters["product_type"]
            
            # Add return and pagination
            cypher_query += """
                RETURN p
                ORDER BY p.name
                SKIP $offset
                LIMIT $limit
            """
            params["offset"] = offset
            params["limit"] = limit
            
            results = await self.execute_query(cypher_query, params)
            
            # Convert to product format
            products = []
            for record in results:
                product_node = record["p"]
                product_data = {
                    "product_id": product_node.get("product_id"),
                    "name": product_node.get("name"),
                    "type": product_node.get("type"),
                    "risk_level": product_node.get("risk_level"),
                    "description": product_node.get("description"),
                    "issuer": product_node.get("issuer"),
                    "expected_return": product_node.get("expected_return"),
                    "volatility": product_node.get("volatility"),
                    "sharpe_ratio": product_node.get("sharpe_ratio"),
                    "minimum_investment": product_node.get("minimum_investment"),
                    "expense_ratio": product_node.get("expense_ratio"),
                    "dividend_yield": product_node.get("dividend_yield"),
                    "regulatory_status": product_node.get("regulatory_status"),
                    "compliance_requirements": product_node.get("compliance_requirements", []),
                    "tags": product_node.get("tags", []),
                    "categories": product_node.get("categories", []),
                    "embedding_id": product_node.get("embedding_id"),
                    "created_at": product_node.get("created_at"),
                    "updated_at": product_node.get("updated_at")
                }
                products.append(product_data)
            
            return products
            
        except Exception as e:
            self._logger.error(f"Error in structured product search: {e}")
            return []
    
    async def _search_products_vector(self, query: str, filters: Dict[str, Any], 
                                    limit: int, offset: int) -> List[Dict[str, Any]]:
        """
        Search products using vector similarity (placeholder for Neo4j vector extension).
        
        Args:
            query: Search query
            filters: Search filters
            limit: Maximum number of results
            offset: Result offset
            
        Returns:
            List[Dict[str, Any]]: Product results
        """
        # Note: Using structured search as primary method
        # For advanced vector search, implement Neo4j vector extension:
        # - Install Neo4j vector extension
        # - Implement vector similarity search
        # - Use embeddings for semantic search
        self._logger.info("Vector search not implemented, falling back to structured search")
        return await self._search_products_structured(query, filters, limit, offset)
    
    async def _search_products_graph(self, query: str, filters: Dict[str, Any], 
                                   limit: int, offset: int) -> List[Dict[str, Any]]:
        """
        Search products using graph queries.
        
        Args:
            query: Search query
            filters: Search filters
            limit: Maximum number of results
            offset: Result offset
            
        Returns:
            List[Dict[str, Any]]: Product results
        """
        try:
            # Build graph query based on relationships
            cypher_query = """
                MATCH (p:Product)
                OPTIONAL MATCH (p)-[:SIMILAR_TO]->(similar:Product)
                OPTIONAL MATCH (p)-[:BELONGS_TO]->(category:Category)
                OPTIONAL MATCH (p)-[:ISSUED_BY]->(issuer:Issuer)
                WHERE 1=1
            """
            
            params = {}
            
            # Add search conditions
            if query:
                cypher_query += " AND (p.name CONTAINS $query OR p.description CONTAINS $query)"
                params["query"] = query
            
            # Add filters
            if filters:
                if "risk_level" in filters:
                    cypher_query += " AND p.risk_level = $risk_level"
                    params["risk_level"] = filters["risk_level"]
                
                if "product_type" in filters:
                    cypher_query += " AND p.type = $product_type"
                    params["product_type"] = filters["product_type"]
            
            # Add return with relationships
            cypher_query += """
                RETURN p, 
                       collect(DISTINCT similar) as similar_products,
                       collect(DISTINCT category) as categories,
                       collect(DISTINCT issuer) as issuers
                ORDER BY p.name
                SKIP $offset
                LIMIT $limit
            """
            params["offset"] = offset
            params["limit"] = limit
            
            results = await self.execute_query(cypher_query, params)
            
            # Convert to product format with relationship data
            products = []
            for record in results:
                product_node = record["p"]
                similar_products = record.get("similar_products", [])
                categories = record.get("categories", [])
                issuers = record.get("issuers", [])
                
                product_data = {
                    "product_id": product_node.get("product_id"),
                    "name": product_node.get("name"),
                    "type": product_node.get("type"),
                    "risk_level": product_node.get("risk_level"),
                    "description": product_node.get("description"),
                    "issuer": product_node.get("issuer"),
                    "expected_return": product_node.get("expected_return"),
                    "volatility": product_node.get("volatility"),
                    "sharpe_ratio": product_node.get("sharpe_ratio"),
                    "minimum_investment": product_node.get("minimum_investment"),
                    "expense_ratio": product_node.get("expense_ratio"),
                    "dividend_yield": product_node.get("dividend_yield"),
                    "regulatory_status": product_node.get("regulatory_status"),
                    "compliance_requirements": product_node.get("compliance_requirements", []),
                    "tags": product_node.get("tags", []),
                    "categories": product_node.get("categories", []),
                    "embedding_id": product_node.get("embedding_id"),
                    "created_at": product_node.get("created_at"),
                    "updated_at": product_node.get("updated_at"),
                    "graph_data": {
                        "similar_products": [p.get("product_id") for p in similar_products if p.get("product_id")],
                        "categories": [c.get("name") for c in categories if c.get("name")],
                        "issuers": [i.get("name") for i in issuers if i.get("name")]
                    }
                }
                products.append(product_data)
            
            return products
            
        except Exception as e:
            self._logger.error(f"Error in graph product search: {e}")
            return []
    
    async def _get_user_profile_structured(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile using structured queries (not supported in Neo4j)"""
        self._logger.warning("User profile retrieval not supported for Neo4j")
        return None
    
    async def _save_user_profile_structured(self, profile: UserProfile) -> bool:
        """Save user profile using structured queries (not supported in Neo4j)"""
        self._logger.warning("User profile saving not supported for Neo4j")
        return False
    
    async def _get_graph_nodes_neo4j(self, node_type: str, filters: Dict[str, Any], 
                                    limit: int) -> List[Dict[str, Any]]:
        """
        Get graph nodes from Neo4j.
        
        Args:
            node_type: Type of nodes to retrieve
            filters: Node filters
            limit: Maximum number of results
            
        Returns:
            List[Dict[str, Any]]: Graph node results
        """
        try:
            # Build Cypher query for nodes
            cypher_query = f"""
                MATCH (n:{node_type if node_type else 'Node'})
                WHERE 1=1
            """
            
            params = {}
            
            # Add filters
            if filters:
                for key, value in filters.items():
                    cypher_query += f" AND n.{key} = ${key}"
                    params[key] = value
            
            # Add return and limit
            cypher_query += f"""
                RETURN n
                LIMIT $limit
            """
            params["limit"] = limit
            
            results = await self.execute_query(cypher_query, params)
            
            # Convert to node format
            nodes = []
            for record in results:
                node = record["n"]
                node_data = {
                    "node_id": node.get("node_id"),
                    "node_type": node.get("node_type"),
                    "properties": dict(node),
                    "labels": list(node.labels) if hasattr(node, 'labels') else []
                }
                nodes.append(node_data)
            
            return nodes
            
        except Exception as e:
            self._logger.error(f"Error getting graph nodes: {e}")
            return []
    
    async def _get_graph_relationships_neo4j(self, source_node_id: str, target_node_id: str,
                                           relationship_type: str, limit: int) -> List[Dict[str, Any]]:
        """
        Get graph relationships from Neo4j.
        
        Args:
            source_node_id: Source node ID
            target_node_id: Target node ID
            relationship_type: Type of relationship
            limit: Maximum number of results
            
        Returns:
            List[Dict[str, Any]]: Graph relationship results
        """
        try:
            # Build Cypher query for relationships
            cypher_query = """
                MATCH (source)-[r]->(target)
                WHERE 1=1
            """
            
            params = {}
            
            # Add filters
            if source_node_id:
                cypher_query += " AND source.node_id = $source_node_id"
                params["source_node_id"] = source_node_id
            
            if target_node_id:
                cypher_query += " AND target.node_id = $target_node_id"
                params["target_node_id"] = target_node_id
            
            if relationship_type:
                cypher_query += f" AND type(r) = $relationship_type"
                params["relationship_type"] = relationship_type
            
            # Add return and limit
            cypher_query += """
                RETURN source, r, target
                LIMIT $limit
            """
            params["limit"] = limit
            
            results = await self.execute_query(cypher_query, params)
            
            # Convert to relationship format
            relationships = []
            for record in results:
                source = record["source"]
                rel = record["r"]
                target = record["target"]
                
                relationship_data = {
                    "relationship_id": rel.get("relationship_id"),
                    "source_node_id": source.get("node_id"),
                    "target_node_id": target.get("node_id"),
                    "relationship_type": type(rel).__name__,
                    "properties": dict(rel),
                    "source_properties": dict(source),
                    "target_properties": dict(target)
                }
                relationships.append(relationship_data)
            
            return relationships
            
        except Exception as e:
            self._logger.error(f"Error getting graph relationships: {e}")
            return []
    
    async def create_graph_schema(self):
        """Create graph schema and constraints"""
        try:
            # Create constraints
            constraints = [
                "CREATE CONSTRAINT product_id IF NOT EXISTS FOR (p:Product) REQUIRE p.product_id IS UNIQUE",
                "CREATE CONSTRAINT category_name IF NOT EXISTS FOR (c:Category) REQUIRE c.name IS UNIQUE",
                "CREATE CONSTRAINT issuer_name IF NOT EXISTS FOR (i:Issuer) REQUIRE i.name IS UNIQUE"
            ]
            
            for constraint in constraints:
                await self.execute_query(constraint)
            
            self._logger.info("Neo4j graph schema created successfully")
            
        except Exception as e:
            self._logger.error(f"Error creating graph schema: {e}")
            raise
    
    async def add_product_node(self, product: FinancialProduct):
        """
        Add a product node to Neo4j.
        
        Args:
            product: Financial product to add
        """
        try:
            cypher_query = """
                MERGE (p:Product {product_id: $product_id})
                SET p.name = $name,
                    p.type = $type,
                    p.risk_level = $risk_level,
                    p.description = $description,
                    p.issuer = $issuer,
                    p.expected_return = $expected_return,
                    p.volatility = $volatility,
                    p.sharpe_ratio = $sharpe_ratio,
                    p.minimum_investment = $minimum_investment,
                    p.expense_ratio = $expense_ratio,
                    p.dividend_yield = $dividend_yield,
                    p.regulatory_status = $regulatory_status,
                    p.compliance_requirements = $compliance_requirements,
                    p.tags = $tags,
                    p.categories = $categories,
                    p.embedding_id = $embedding_id,
                    p.created_at = $created_at,
                    p.updated_at = $updated_at
            """
            
            params = {
                "product_id": product.product_id,
                "name": product.name,
                "type": product.type,
                "risk_level": product.risk_level,
                "description": product.description,
                "issuer": product.issuer,
                "expected_return": product.expected_return,
                "volatility": product.volatility,
                "sharpe_ratio": product.sharpe_ratio,
                "minimum_investment": product.minimum_investment,
                "expense_ratio": product.expense_ratio,
                "dividend_yield": product.dividend_yield,
                "regulatory_status": product.regulatory_status,
                "compliance_requirements": product.compliance_requirements,
                "tags": product.tags,
                "categories": product.categories,
                "embedding_id": product.embedding_id,
                "created_at": product.created_at.isoformat() if product.created_at else None,
                "updated_at": product.updated_at.isoformat() if product.updated_at else None
            }
            
            await self.execute_query(cypher_query, params)
            self._logger.info(f"Added product node to Neo4j: {product.product_id}")
            
        except Exception as e:
            self._logger.error(f"Error adding product node to Neo4j: {e}")
            raise 
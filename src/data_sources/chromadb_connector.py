"""
ChromaDB connector for the financial product recommendation system.

This module provides integration with ChromaDB for vector similarity
search and semantic retrieval of financial products.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from .base_connector import BaseDataConnector, DataSourceType
from src.data.models import FinancialProduct, UserProfile, GraphNode, GraphRelationship


class ChromaDBConnector(BaseDataConnector):
    """
    ChromaDB connector implementation.
    
    Handles connection to ChromaDB and provides vector similarity
    search capabilities for financial products.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the ChromaDB connector.
        
        Args:
            config: Configuration dictionary with ChromaDB connection details
        """
        super().__init__(DataSourceType.CHROMADB, config)
        self._client = None
        self._collection = None
        self._embedding_model = None
        
    @property
    def source_name(self) -> str:
        """Return the source name"""
        return "chromadb"
    
    async def connect(self):
        """Connect to ChromaDB"""
        try:
            # Extract configuration
            host = self.get_config("host", "localhost")
            port = self.get_config("port", 8000)
            collection_name = self.get_config("collection_name", "financial_products")
            embedding_model = self.get_config("embedding_model", "sentence-transformers/all-MiniLM-L6-v2")
            
            # Initialize embedding model
            self._embedding_model = SentenceTransformer(embedding_model)
            
            # Create ChromaDB client
            self._client = chromadb.HttpClient(
                host=host,
                port=port,
                settings=Settings(
                    chroma_api_impl="rest",
                    chroma_server_host=host,
                    chroma_server_http_port=port
                )
            )
            
            # Get or create collection
            self._collection = self._client.get_or_create_collection(
                name=collection_name,
                metadata={"description": "Financial products for vector search"}
            )
            
            self._connected = True
            self._logger.info(f"Connected to ChromaDB: {host}:{port}")
            
        except Exception as e:
            self._logger.error(f"Failed to connect to ChromaDB: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from ChromaDB"""
        try:
            if self._client:
                self._client = None
                self._collection = None
            
            self._connected = False
            self._logger.info("Disconnected from ChromaDB")
            
        except Exception as e:
            self._logger.error(f"Error disconnecting from ChromaDB: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the ChromaDB connector.
        
        Returns:
            Dict[str, Any]: Health check results
        """
        try:
            if not self._connected:
                return {
                    "status": "disconnected",
                    "source": self.source_name,
                    "error": "Not connected to ChromaDB"
                }
            
            # Test connection by getting collection info
            collection_info = self._collection.get()
            
            return {
                "status": "healthy",
                "source": self.source_name,
                "connected": True,
                "collection_count": len(collection_info.get("ids", [])),
                "embedding_model": self._embedding_model.__class__.__name__,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "source": self.source_name,
                "error": str(e)
            }
    
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a query on ChromaDB.
        
        Args:
            query: Query string (for vector search)
            params: Query parameters
            
        Returns:
            List[Dict[str, Any]]: Query results
        """
        try:
            await self.ensure_connected()
            
            # For ChromaDB, we'll use vector similarity search
            if query:
                results = await self._search_products_vector(query, params or {}, 10, 0)
                return results
            
            # If no query, return all documents
            collection_data = self._collection.get()
            
            results = []
            for i, doc_id in enumerate(collection_data["ids"]):
                metadata = collection_data["metadatas"][i] if collection_data["metadatas"] else {}
                document = collection_data["documents"][i] if collection_data["documents"] else ""
                
                result = {
                    "id": doc_id,
                    "metadata": metadata,
                    "document": document
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            self._logger.error(f"Error executing query: {e}")
            return []
    
    async def _search_products_structured(self, query: str, filters: Dict[str, Any], 
                                        limit: int, offset: int) -> List[Dict[str, Any]]:
        """
        Search products using structured queries (limited support in ChromaDB).
        
        Args:
            query: Search query
            filters: Search filters
            limit: Maximum number of results
            offset: Result offset
            
        Returns:
            List[Dict[str, Any]]: Product results
        """
        try:
            # ChromaDB doesn't support complex structured queries like PostgreSQL
            # We'll use metadata filtering instead
            where_clause = {}
            
            if filters:
                if "risk_level" in filters:
                    where_clause["risk_level"] = filters["risk_level"]
                
                if "product_type" in filters:
                    where_clause["type"] = filters["product_type"]
            
            # Get documents with metadata filtering
            results = self._collection.get(
                where=where_clause,
                limit=limit
            )
            
            # Convert to product format
            products = []
            for i, doc_id in enumerate(results["ids"]):
                metadata = results["metadatas"][i] if results["metadatas"] else {}
                
                # Convert metadata to product format
                product_data = {
                    "product_id": doc_id,
                    "name": metadata.get("name", ""),
                    "type": metadata.get("type", ""),
                    "risk_level": metadata.get("risk_level", ""),
                    "description": metadata.get("description", ""),
                    "issuer": metadata.get("issuer", ""),
                    "expected_return": metadata.get("expected_return", ""),
                    "volatility": metadata.get("volatility", 0.0),
                    "sharpe_ratio": metadata.get("sharpe_ratio", 0.0),
                    "minimum_investment": metadata.get("minimum_investment", 0.0),
                    "expense_ratio": metadata.get("expense_ratio", 0.0),
                    "dividend_yield": metadata.get("dividend_yield", 0.0),
                    "regulatory_status": metadata.get("regulatory_status", ""),
                    "compliance_requirements": metadata.get("compliance_requirements", []),
                    "tags": metadata.get("tags", []),
                    "categories": metadata.get("categories", []),
                    "embedding_id": doc_id,
                    "created_at": metadata.get("created_at"),
                    "updated_at": metadata.get("updated_at")
                }
                
                products.append(product_data)
            
            return products
            
        except Exception as e:
            self._logger.error(f"Error in structured product search: {e}")
            return []
    
    async def _search_products_vector(self, query: str, filters: Dict[str, Any], 
                                    limit: int, offset: int) -> List[Dict[str, Any]]:
        """
        Search products using vector similarity.
        
        Args:
            query: Search query
            filters: Search filters
            limit: Maximum number of results
            offset: Result offset
            
        Returns:
            List[Dict[str, Any]]: Product results
        """
        try:
            # Generate embedding for the query
            query_embedding = self._embedding_model.encode(query).tolist()
            
            # Build where clause for metadata filtering
            where_clause = {}
            if filters:
                if "risk_level" in filters:
                    where_clause["risk_level"] = filters["risk_level"]
                
                if "product_type" in filters:
                    where_clause["type"] = filters["product_type"]
            
            # Perform vector similarity search
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where_clause if where_clause else None
            )
            
            # Convert to product format
            products = []
            if results["ids"] and results["ids"][0]:
                for i, doc_id in enumerate(results["ids"][0]):
                    metadata = results["metadatas"][0][i] if results["metadatas"] and results["metadatas"][0] else {}
                    distance = results["distances"][0][i] if results["distances"] and results["distances"][0] else 0.0
                    
                    # Convert metadata to product format
                    product_data = {
                        "product_id": doc_id,
                        "name": metadata.get("name", ""),
                        "type": metadata.get("type", ""),
                        "risk_level": metadata.get("risk_level", ""),
                        "description": metadata.get("description", ""),
                        "issuer": metadata.get("issuer", ""),
                        "expected_return": metadata.get("expected_return", ""),
                        "volatility": metadata.get("volatility", 0.0),
                        "sharpe_ratio": metadata.get("sharpe_ratio", 0.0),
                        "minimum_investment": metadata.get("minimum_investment", 0.0),
                        "expense_ratio": metadata.get("expense_ratio", 0.0),
                        "dividend_yield": metadata.get("dividend_yield", 0.0),
                        "regulatory_status": metadata.get("regulatory_status", ""),
                        "compliance_requirements": metadata.get("compliance_requirements", []),
                        "tags": metadata.get("tags", []),
                        "categories": metadata.get("categories", []),
                        "embedding_id": doc_id,
                        "similarity_score": 1.0 - distance,  # Convert distance to similarity
                        "created_at": metadata.get("created_at"),
                        "updated_at": metadata.get("updated_at")
                    }
                    
                    products.append(product_data)
            
            return products
            
        except Exception as e:
            self._logger.error(f"Error in vector product search: {e}")
            return []
    
    async def _search_products_graph(self, query: str, filters: Dict[str, Any], 
                                   limit: int, offset: int) -> List[Dict[str, Any]]:
        """
        Search products using graph queries (not applicable for ChromaDB).
        
        Args:
            query: Search query
            filters: Search filters
            limit: Maximum number of results
            offset: Result offset
            
        Returns:
            List[Dict[str, Any]]: Product results
        """
        self._logger.warning("Graph search not supported for ChromaDB")
        return []
    
    async def _get_user_profile_structured(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile using structured queries (not supported in ChromaDB)"""
        self._logger.warning("User profile retrieval not supported for ChromaDB")
        return None
    
    async def _save_user_profile_structured(self, profile: UserProfile) -> bool:
        """Save user profile using structured queries (not supported in ChromaDB)"""
        self._logger.warning("User profile saving not supported for ChromaDB")
        return False
    
    async def _get_graph_nodes_neo4j(self, node_type: str, filters: Dict[str, Any], 
                                    limit: int) -> List[Dict[str, Any]]:
        """Get graph nodes from Neo4j (not applicable for ChromaDB)"""
        self._logger.warning("Graph node retrieval not supported for ChromaDB")
        return []
    
    async def _get_graph_relationships_neo4j(self, source_node_id: str, target_node_id: str,
                                           relationship_type: str, limit: int) -> List[Dict[str, Any]]:
        """Get graph relationships from Neo4j (not applicable for ChromaDB)"""
        self._logger.warning("Graph relationship retrieval not supported for ChromaDB")
        return []
    
    async def add_product(self, product: FinancialProduct):
        """
        Add a product to ChromaDB.
        
        Args:
            product: Financial product to add
        """
        try:
            await self.ensure_connected()
            
            # Create document text for embedding
            document_text = f"{product.name} {product.description} {product.issuer}"
            
            # Generate embedding
            embedding = self._embedding_model.encode(document_text).tolist()
            
            # Create metadata
            metadata = {
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
                "created_at": product.created_at.isoformat() if product.created_at else None,
                "updated_at": product.updated_at.isoformat() if product.updated_at else None
            }
            
            # Add to collection
            self._collection.add(
                documents=[document_text],
                embeddings=[embedding],
                metadatas=[metadata],
                ids=[product.product_id]
            )
            
            self._logger.info(f"Added product to ChromaDB: {product.product_id}")
            
        except Exception as e:
            self._logger.error(f"Error adding product to ChromaDB: {e}")
            raise
    
    async def add_products_batch(self, products: List[FinancialProduct]):
        """
        Add multiple products to ChromaDB in batch.
        
        Args:
            products: List of financial products to add
        """
        try:
            await self.ensure_connected()
            
            documents = []
            embeddings = []
            metadatas = []
            ids = []
            
            for product in products:
                # Create document text for embedding
                document_text = f"{product.name} {product.description} {product.issuer}"
                
                # Generate embedding
                embedding = self._embedding_model.encode(document_text).tolist()
                
                # Create metadata
                metadata = {
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
                    "created_at": product.created_at.isoformat() if product.created_at else None,
                    "updated_at": product.updated_at.isoformat() if product.updated_at else None
                }
                
                documents.append(document_text)
                embeddings.append(embedding)
                metadatas.append(metadata)
                ids.append(product.product_id)
            
            # Add to collection in batch
            self._collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            self._logger.info(f"Added {len(products)} products to ChromaDB")
            
        except Exception as e:
            self._logger.error(f"Error adding products to ChromaDB: {e}")
            raise 
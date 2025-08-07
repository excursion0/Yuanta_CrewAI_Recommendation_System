"""
Data sources integration package for the financial product recommendation system.

This package contains connectors and managers for various data sources
including PostgreSQL, ChromaDB, and Neo4j for GraphRAG functionality.
"""

from .base_connector import BaseDataConnector, DataSourceType, QueryType
from .postgresql_connector import PostgreSQLConnector
from .chromadb_connector import ChromaDBConnector
from .neo4j_connector import Neo4jConnector
from .data_manager import DataManager, FusionStrategy
from .mock_data_manager import MockDataManager

__all__ = [
    "BaseDataConnector",
    "PostgreSQLConnector", 
    "ChromaDBConnector",
    "Neo4jConnector",
    "DataManager",
    "MockDataManager",
    "DataSourceType",
    "QueryType",
    "FusionStrategy"
] 
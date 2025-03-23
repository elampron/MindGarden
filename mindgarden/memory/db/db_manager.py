"""
Database manager module for Neo4j operations in MindGarden.
"""
import logging
import os
from typing import Optional, Dict, Any, List

from neo4j import GraphDatabase, Driver, Session
from pydantic import ValidationError

from mindgarden.config.settings import get_config

logger = logging.getLogger(__name__)


class Neo4jManager:
    """Manages Neo4j database connections and operations for MindGarden."""
    
    def __init__(self, uri: Optional[str] = None, user: Optional[str] = None, password: Optional[str] = None):
        """Initialize Neo4j manager with optional connection parameters."""
        config = get_config()
        self.uri = uri or config.neo4j_uri
        self.user = user or config.neo4j_user
        self.password = password or config.neo4j_password
        logger.info("Neo4jManager initialized with URI: %s, User: %s", self.uri, self.user)
        self.driver = None
        
    def connect(self) -> None:
        """Establish connection to Neo4j database."""
        if not self.password:
            raise ValueError("Neo4j password is required")
            
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            logger.info(f"Connected to Neo4j at {self.uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
            
    def close(self) -> None:
        """Close the database connection."""
        if self.driver:
            self.driver.close()
            logger.info("Closed Neo4j connection")
            
    def get_session(self) -> Session:
        """Get a new database session."""
        if not self.driver:
            self.connect()
        return self.driver.session()
        
    def run_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Run a Cypher query and return the results.
        
        Args:
            query: The Cypher query to execute.
            parameters: Optional parameters for the query.
            
        Returns:
            A list of dictionaries representing the query results.
        """
        if parameters is None:
            parameters = {}
            
        try:
            with self.get_session() as session:
                result = session.run(query, parameters)
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Parameters: {parameters}")
            raise
            
    def create_indexes(self) -> None:
        """Create necessary indexes for the database."""
        # Memory index
        self.run_query("CREATE INDEX IF NOT EXISTS FOR (m:Memory) ON (m.id)")
        # Document index
        self.run_query("CREATE INDEX IF NOT EXISTS FOR (d:Document) ON (d.id)")
        # Entity index
        self.run_query("CREATE INDEX IF NOT EXISTS FOR (e:Entity) ON (e.name)")
        # Topic index
        self.run_query("CREATE INDEX IF NOT EXISTS FOR (t:Topic) ON (t.name)")
        
        logger.info("Created database indexes")
        
    def setup_database(self) -> None:
        """Set up the database with necessary constraints and indexes."""
        try:
            self.create_indexes()
            logger.info("Database setup complete")
        except Exception as e:
            logger.error(f"Error setting up database: {e}")
            raise 
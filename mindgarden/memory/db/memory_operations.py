"""
Memory database operations for MindGarden.
"""
import logging
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from mindgarden.memory.db.db_manager import Neo4jManager
from mindgarden.memory.models.document import Memory

logger = logging.getLogger(__name__)


def store_memory(db_manager: Neo4jManager, content: str, source: str, 
                metadata: Optional[Dict[str, Any]] = None) -> str:
    """
    Store a memory in the Neo4j database.
    
    Args:
        db_manager: Neo4j database manager.
        content: The memory content.
        source: Source of the memory (e.g., 'user', 'assistant', 'document').
        metadata: Additional metadata about the memory.
        
    Returns:
        The ID of the stored memory.
    """
    if metadata is None:
        metadata = {}
        
    # Generate a unique ID
    memory_id = str(uuid.uuid4())
    
    # Get current timestamp
    timestamp = datetime.now().timestamp()
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create parameters for the query
    parameters = {
        "id": memory_id,
        "content": content,
        "source": source,
        "timestamp": timestamp,
        "date_str": date_str,
        "metadata": metadata
    }
    
    # Create memory node
    query = """
    CREATE (m:Memory {
        id: $id,
        content: $content,
        source: $source,
        timestamp: $timestamp,
        date_str: $date_str,
        metadata: $metadata
    })
    RETURN m.id as id
    """
    
    try:
        result = db_manager.run_query(query, parameters)
        logger.info(f"Stored memory {memory_id} from {source}")
        return memory_id
    except Exception as e:
        logger.error(f"Error storing memory: {e}")
        raise


def retrieve_memories(db_manager: Neo4jManager, limit: int = 10) -> List[Memory]:
    """
    Retrieve recent memories from the database.
    
    Args:
        db_manager: Neo4j database manager.
        limit: Maximum number of memories to retrieve.
        
    Returns:
        List of Memory objects.
    """
    query = """
    MATCH (m:Memory)
    RETURN m
    ORDER BY m.timestamp DESC
    LIMIT $limit
    """
    
    parameters = {
        "limit": limit
    }
    
    try:
        results = db_manager.run_query(query, parameters)
        memories = []
        
        for record in results:
            memory_data = record.get('m', {})
            try:
                memory = Memory(
                    id=memory_data.get('id'),
                    content=memory_data.get('content'),
                    source=memory_data.get('source'),
                    timestamp=memory_data.get('timestamp'),
                    date_str=memory_data.get('date_str'),
                    metadata=memory_data.get('metadata', {})
                )
                memories.append(memory)
            except Exception as e:
                logger.error(f"Error creating Memory object: {e}")
                
        return memories
    except Exception as e:
        logger.error(f"Error retrieving memories: {e}")
        return []


def search_memories(db_manager: Neo4jManager, query_text: str, limit: int = 5) -> List[Memory]:
    """
    Search memories by content similarity.
    
    Args:
        db_manager: Neo4j database manager.
        query_text: Text to search for.
        limit: Maximum number of memories to retrieve.
        
    Returns:
        List of Memory objects.
    """
    # In a future implementation, this would use vector embeddings
    # For now, we'll use a simple text search
    query = """
    MATCH (m:Memory)
    WHERE m.content CONTAINS $query_text
    RETURN m
    ORDER BY m.timestamp DESC
    LIMIT $limit
    """
    
    parameters = {
        "query_text": query_text,
        "limit": limit
    }
    
    try:
        results = db_manager.run_query(query, parameters)
        memories = []
        
        for record in results:
            memory_data = record.get('m', {})
            try:
                memory = Memory(
                    id=memory_data.get('id'),
                    content=memory_data.get('content'),
                    source=memory_data.get('source'),
                    timestamp=memory_data.get('timestamp'),
                    date_str=memory_data.get('date_str'),
                    metadata=memory_data.get('metadata', {})
                )
                memories.append(memory)
            except Exception as e:
                logger.error(f"Error creating Memory object: {e}")
                
        return memories
    except Exception as e:
        logger.error(f"Error searching memories: {e}")
        return []


def connect_memory_to_entities(db_manager: Neo4jManager, memory_id: str, entity_names: List[str]) -> None:
    """
    Connect a memory to entities.
    
    Args:
        db_manager: Neo4j database manager.
        memory_id: ID of the memory.
        entity_names: List of entity names to connect to.
    """
    for entity_name in entity_names:
        query = """
        MATCH (m:Memory {id: $memory_id})
        MATCH (e:Entity {name: $entity_name})
        MERGE (m)-[r:MENTIONS]->(e)
        RETURN r
        """
        
        parameters = {
            "memory_id": memory_id,
            "entity_name": entity_name
        }
        
        try:
            db_manager.run_query(query, parameters)
            logger.debug(f"Connected memory {memory_id} to entity {entity_name}")
        except Exception as e:
            logger.error(f"Error connecting memory to entity: {e}")


def connect_memory_to_topics(db_manager: Neo4jManager, memory_id: str, topics: List[str]) -> None:
    """
    Connect a memory to topics.
    
    Args:
        db_manager: Neo4j database manager.
        memory_id: ID of the memory.
        topics: List of topics to connect to.
    """
    for topic in topics:
        query = """
        MATCH (m:Memory {id: $memory_id})
        MERGE (t:Topic {name: $topic})
        MERGE (m)-[r:ABOUT]->(t)
        RETURN r
        """
        
        parameters = {
            "memory_id": memory_id,
            "topic": topic
        }
        
        try:
            db_manager.run_query(query, parameters)
            logger.debug(f"Connected memory {memory_id} to topic {topic}")
        except Exception as e:
            logger.error(f"Error connecting memory to topic: {e}")


def retrieve_memories_by_entity(db_manager: Neo4jManager, entity_name: str, limit: int = 5) -> List[Memory]:
    """
    Retrieve memories that mention a specific entity.
    
    Args:
        db_manager: Neo4j database manager.
        entity_name: Name of the entity.
        limit: Maximum number of memories to retrieve.
        
    Returns:
        List of Memory objects.
    """
    query = """
    MATCH (m:Memory)-[:MENTIONS]->(e:Entity {name: $entity_name})
    RETURN m
    ORDER BY m.timestamp DESC
    LIMIT $limit
    """
    
    parameters = {
        "entity_name": entity_name,
        "limit": limit
    }
    
    try:
        results = db_manager.run_query(query, parameters)
        memories = []
        
        for record in results:
            memory_data = record.get('m', {})
            try:
                memory = Memory(
                    id=memory_data.get('id'),
                    content=memory_data.get('content'),
                    source=memory_data.get('source'),
                    timestamp=memory_data.get('timestamp'),
                    date_str=memory_data.get('date_str'),
                    metadata=memory_data.get('metadata', {})
                )
                memories.append(memory)
            except Exception as e:
                logger.error(f"Error creating Memory object: {e}")
                
        return memories
    except Exception as e:
        logger.error(f"Error retrieving memories by entity: {e}")
        return [] 
"""
Memory manager for MindGarden knowledge storage and retrieval.
"""

import logging
import time
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime

from mindgarden.config.settings import get_config
from mindgarden.memory.db.db_manager import Neo4jManager
from mindgarden.memory.models.document import Memory
from mindgarden.memory.entity.entity_processor import EntityProcessor
from mindgarden.memory.db import memory_operations

logger = logging.getLogger(__name__)


class MemoryManager:
    """Memory manager for knowledge storage and retrieval."""

    def __init__(self):
        """Initialize the memory manager."""
        self.config = get_config()
        
        # For Phase 1, we'll have dual storage - both in-memory and Neo4j
        # In-memory storage for quick access and fallback
        self.memories = []
        
        # Neo4j for persistent storage
        self.use_neo4j = False  # Default to False for backward compatibility
        self.db_manager = None
        self.entity_processor = None
        
        # Try to initialize Neo4j connection if configured
        try:
            self.db_manager = Neo4jManager()
            self.db_manager.connect()
            self.db_manager.setup_database()
            self.entity_processor = EntityProcessor(self.db_manager)
            self.use_neo4j = True
            logger.info("Neo4j integration enabled for memory management")
        except Exception as e:
            logger.warning(f"Failed to initialize Neo4j connection: {e}")
            logger.warning("Falling back to in-memory storage only")

    def retrieve_relevant(self, query: str, limit: int = 5) -> List[str]:
        """
        Retrieve relevant memories based on a query.
        
        Args:
            query: The query to search for relevant memories.
            limit: Maximum number of memories to retrieve.
            
        Returns:
            List of relevant memory strings.
        """
        logger.debug(f"Retrieving memories relevant to: {query}")
        
        if self.use_neo4j:
            try:
                # Use Neo4j for semantic search
                relevant_memories_objects = memory_operations.search_memories(
                    self.db_manager, 
                    query_text=query, 
                    limit=limit
                )
                
                # Extract text from memory objects
                return [f"{memory.content} [From: {memory.source}, {memory.date_str}]" 
                       for memory in relevant_memories_objects]
            except Exception as e:
                logger.error(f"Error retrieving from Neo4j: {e}")
                # Fall back to in-memory if Neo4j fails
        
        # Default in-memory retrieval (fallback)
        relevant_memories = []
        
        if self.memories:
            # Sort memories by timestamp (newest first)
            sorted_memories = sorted(self.memories, key=lambda x: x.get('timestamp', 0), reverse=True)
            
            # Take the most recent ones up to limit
            for memory in sorted_memories[:limit]:
                memory_text = f"{memory.get('text', '')} [From: {memory.get('source', '')}, {memory.get('date', '')}]"
                relevant_memories.append(memory_text)
        
        return relevant_memories

    def store_conversation(self, user_message: str, assistant_response: str) -> None:
        """
        Store a conversation exchange in memory.
        
        Args:
            user_message: The user's message.
            assistant_response: The assistant's response.
        """
        timestamp = time.time()
        formatted_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
        # Store in both storage systems for redundancy
        
        # 1. Store in in-memory storage
        # Store user message
        self.memories.append({
            'text': user_message,
            'source': 'user',
            'timestamp': timestamp,
            'date': formatted_time
        })
        
        # Store assistant response
        self.memories.append({
            'text': assistant_response,
            'source': 'assistant',
            'timestamp': timestamp + 0.1,  # Slightly later to preserve order
            'date': formatted_time
        })
        
        # 2. Store in Neo4j if enabled
        if self.use_neo4j:
            try:
                # Store user message
                user_memory_id = memory_operations.store_memory(
                    self.db_manager,
                    content=user_message,
                    source='user',
                    metadata={'timestamp': timestamp, 'date': formatted_time}
                )
                
                # Extract entities from user message
                extracted = self.entity_processor.extract_entities_from_text(user_message)
                
                # Store entities and connect to memory
                self.entity_processor.store_entities(extracted)
                
                # Connect memory to entities and topics
                entity_names = [entity.name for entity in extracted.entities]
                memory_operations.connect_memory_to_entities(self.db_manager, user_memory_id, entity_names)
                memory_operations.connect_memory_to_topics(self.db_manager, user_memory_id, extracted.topics)
                
                # Store assistant response
                assistant_memory_id = memory_operations.store_memory(
                    self.db_manager,
                    content=assistant_response,
                    source='assistant',
                    metadata={'timestamp': timestamp + 0.1, 'date': formatted_time}
                )
                
                # Extract entities from assistant response
                extracted = self.entity_processor.extract_entities_from_text(assistant_response)
                
                # Store entities and connect to memory
                self.entity_processor.store_entities(extracted)
                
                # Connect memory to entities and topics
                entity_names = [entity.name for entity in extracted.entities]
                memory_operations.connect_memory_to_entities(self.db_manager, assistant_memory_id, entity_names)
                memory_operations.connect_memory_to_topics(self.db_manager, assistant_memory_id, extracted.topics)
                
            except Exception as e:
                logger.error(f"Error storing conversation in Neo4j: {e}")
        
        logger.debug(f"Stored conversation exchange at {formatted_time}")

    def store_document(self, content: str, source: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Store a document in memory.
        
        Args:
            content: The document content.
            source: The source of the document.
            metadata: Additional metadata for the document.
        """
        timestamp = time.time()
        formatted_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
        # 1. Store in in-memory storage
        memory_item = {
            'text': content,
            'source': source,
            'timestamp': timestamp,
            'date': formatted_time
        }
        
        if metadata:
            memory_item.update(metadata)
            
        self.memories.append(memory_item)
        
        # 2. Store in Neo4j if enabled
        if self.use_neo4j:
            try:
                # Store document as memory
                memory_id = memory_operations.store_memory(
                    self.db_manager,
                    content=content,
                    source=source,
                    metadata={
                        'timestamp': timestamp, 
                        'date': formatted_time,
                        **(metadata or {})
                    }
                )
                
                # Extract entities from document
                extracted = self.entity_processor.extract_entities_from_text(content)
                
                # Store entities and connect to memory
                self.entity_processor.store_entities(extracted)
                
                # Connect memory to entities and topics
                entity_names = [entity.name for entity in extracted.entities]
                memory_operations.connect_memory_to_entities(self.db_manager, memory_id, entity_names)
                memory_operations.connect_memory_to_topics(self.db_manager, memory_id, extracted.topics)
                
            except Exception as e:
                logger.error(f"Error storing document in Neo4j: {e}")
        
        logger.debug(f"Stored document from {source} at {formatted_time}")

    def clear_memory(self) -> None:
        """Clear all memories."""
        # Clear in-memory storage
        self.memories = []
        
        # Clear Neo4j if enabled
        if self.use_neo4j:
            try:
                # Warning: This deletes all memories - use with caution!
                query = "MATCH (m:Memory) DETACH DELETE m"
                self.db_manager.run_query(query)
                logger.info("Cleared all memories from Neo4j")
            except Exception as e:
                logger.error(f"Error clearing memories from Neo4j: {e}")
        
        logger.debug("Cleared all memories")
        
    def get_entity_information(self, entity_name: str) -> Dict[str, Any]:
        """
        Get information about a specific entity.
        
        Args:
            entity_name: The name of the entity.
            
        Returns:
            Dictionary with entity information.
        """
        if not self.use_neo4j:
            return {"name": entity_name, "error": "Neo4j integration not enabled"}
            
        try:
            # Get entity information
            query = """
            MATCH (e:Entity {name: $name})
            RETURN e
            """
            
            parameters = {
                "name": entity_name
            }
            
            results = self.db_manager.run_query(query, parameters)
            
            if not results:
                return {"name": entity_name, "found": False}
                
            entity_data = results[0].get('e', {})
            
            # Get related memories
            memories = memory_operations.retrieve_memories_by_entity(
                self.db_manager, 
                entity_name=entity_name,
                limit=5
            )
            
            # Get related entities
            related_query = """
            MATCH (e:Entity {name: $name})-[r]->(related:Entity)
            RETURN related.name as name, type(r) as relationship_type
            UNION
            MATCH (related:Entity)-[r]->(e:Entity {name: $name})
            RETURN related.name as name, type(r) as relationship_type
            LIMIT 10
            """
            
            related_results = self.db_manager.run_query(related_query, parameters)
            related_entities = [
                {"name": record.get('name'), "relationship": record.get('relationship_type')}
                for record in related_results
            ]
            
            return {
                "name": entity_name,
                "found": True,
                "entity_type": entity_data.get('entity_type', "unknown"),
                "aliases": entity_data.get('aliases', []),
                "description": entity_data.get('description', ""),
                "related_entities": related_entities,
                "memories": [memory.content for memory in memories]
            }
            
        except Exception as e:
            logger.error(f"Error getting entity information: {e}")
            return {"name": entity_name, "error": str(e)} 
"""
Entity processing module for MindGarden memory system.
"""
import logging
import uuid
from typing import List, Dict, Any, Optional

from openai import OpenAI

from mindgarden.config.settings import get_config
from mindgarden.memory.db.db_manager import Neo4jManager
from mindgarden.memory.models.entity import Entity, Relationship, ExtractedEntities

logger = logging.getLogger(__name__)


class EntityProcessor:
    """Processor for entity extraction and relationship identification."""
    
    def __init__(self, db_manager: Optional[Neo4jManager] = None):
        """
        Initialize the entity processor.
        
        Args:
            db_manager: Optional Neo4j database manager.
        """
        self.config = get_config()
        self.client = OpenAI(api_key=self.config.openai_api_key)
        self.db_manager = db_manager
        
    def extract_entities_from_text(self, text: str, instructions: str = "") -> ExtractedEntities:
        """
        Extract entities, topics, and relationships from text using OpenAI.
        
        Args:
            text: The text to extract entities from.
            instructions: Optional instructions for the extraction.
            
        Returns:
            An ExtractedEntities instance with the extracted information.
        """
        system_prompt = (
            "You are an expert text analysis assistant. Extract all relevant entities, topics, and relationships from the text. "
            "For entities, identify their 'name', 'entity_type', and optionally 'aliases' and 'description'. "
            "For topics, identify the main subjects discussed. "
            "For relationships, identify connections between entities with 'source', 'target', 'relationship_type', and optionally 'description'."
        )
        
        user_prompt = f"Text: {text}\nInstructions: {instructions}"
        
        try:
            completion = self.client.chat.completions.create(
                model=self.config.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
            )
            
            response_content = completion.choices[0].message.content
            
            # Parse the response into the ExtractedEntities model
            # You might need additional parsing logic here depending on the response format
            
            # For simplicity, we'll use a minimal approach for now
            import json
            data = json.loads(response_content)
            
            # Process entities
            entities = []
            for entity_data in data.get("entities", []):
                entity = Entity(
                    name=entity_data.get("name", "Unknown"),
                    entity_type=entity_data.get("entity_type", "unknown"),
                    aliases=entity_data.get("aliases", []),
                    description=entity_data.get("description"),
                    metadata=entity_data.get("metadata", {})
                )
                entities.append(entity)
                
            # Process relationships
            relationships = []
            for rel_data in data.get("relationships", []):
                relationship = Relationship(
                    source=rel_data.get("source", "Unknown"),
                    target=rel_data.get("target", "Unknown"),
                    relationship_type=rel_data.get("relationship_type", "unknown"),
                    description=rel_data.get("description"),
                    confidence=rel_data.get("confidence", 1.0),
                    metadata=rel_data.get("metadata", {})
                )
                relationships.append(relationship)
                
            # Get topics
            topics = data.get("topics", [])
            
            return ExtractedEntities(
                entities=entities,
                relationships=relationships,
                topics=topics
            )
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            # Return empty results on error
            return ExtractedEntities(entities=[], relationships=[], topics=[])
            
    def store_entities(self, extracted: ExtractedEntities) -> None:
        """
        Store extracted entities in the database.
        
        Args:
            extracted: The extracted entities to store.
        """
        if not self.db_manager:
            logger.warning("No database manager provided. Entities will not be stored.")
            return
            
        try:
            # Store entities
            for entity in extracted.entities:
                self._store_entity(entity)
                
            # Store relationships
            for relationship in extracted.relationships:
                self._store_relationship(relationship)
                
            # Store topics
            for topic in extracted.topics:
                self._store_topic(topic)
                
            logger.info("Stored %d entities, %d relationships, and %d topics", 
                      len(extracted.entities), len(extracted.relationships), len(extracted.topics))
                      
        except Exception as e:
            logger.error(f"Error storing entities: {e}")
            raise
            
    def _store_entity(self, entity: Entity) -> None:
        """
        Store a single entity in the database.
        
        Args:
            entity: The entity to store.
        """
        if not self.db_manager:
            return
            
        # Convert entity to a dictionary for the database
        entity_dict = entity.model_dump()
        
        # Check if entity exists
        query = """
        MERGE (e:Entity {name: $name})
        ON CREATE SET e.entity_type = $entity_type,
                      e.aliases = $aliases,
                      e.description = $description,
                      e.created_at = timestamp()
        ON MATCH SET e.entity_type = $entity_type,
                     e.aliases = $aliases,
                     e.description = $description,
                     e.updated_at = timestamp()
        RETURN e
        """
        
        parameters = {
            "name": entity.name,
            "entity_type": entity.entity_type,
            "aliases": entity.aliases,
            "description": entity.description or "",
        }
        
        # Execute query
        self.db_manager.run_query(query, parameters)
        
    def _store_relationship(self, relationship: Relationship) -> None:
        """
        Store a relationship between entities in the database.
        
        Args:
            relationship: The relationship to store.
        """
        if not self.db_manager:
            return
            
        # Create a relationship between entities
        query = """
        MATCH (source:Entity {name: $source})
        MATCH (target:Entity {name: $target})
        MERGE (source)-[r:`$relationship_type`]->(target)
        ON CREATE SET r.description = $description,
                      r.confidence = $confidence,
                      r.created_at = timestamp()
        ON MATCH SET r.description = $description,
                     r.confidence = $confidence,
                     r.updated_at = timestamp()
        RETURN r
        """
        
        # Replace the relationship_type placeholder
        query = query.replace("`$relationship_type`", f"`{relationship.relationship_type}`")
        
        parameters = {
            "source": relationship.source,
            "target": relationship.target,
            "description": relationship.description or "",
            "confidence": relationship.confidence,
        }
        
        # Execute query
        self.db_manager.run_query(query, parameters)
        
    def _store_topic(self, topic: str) -> None:
        """
        Store a topic in the database.
        
        Args:
            topic: The topic to store.
        """
        if not self.db_manager:
            return
            
        query = """
        MERGE (t:Topic {name: $name})
        ON CREATE SET t.created_at = timestamp()
        ON MATCH SET t.updated_at = timestamp()
        RETURN t
        """
        
        parameters = {
            "name": topic
        }
        
        # Execute query
        self.db_manager.run_query(query, parameters) 
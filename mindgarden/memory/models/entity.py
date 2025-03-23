"""
Entity models for MindGarden memory system.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Entity(BaseModel):
    """Pydantic model for an entity extracted from text or documents."""
    name: str = Field(..., description="The primary name of the entity.")
    entity_type: str = Field(..., description="The type of entity (e.g., 'person', 'organization', 'location', etc.).")
    aliases: List[str] = Field(default_factory=list, description="Alternative names for the entity.")
    description: Optional[str] = Field(None, description="A brief description of the entity.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata about the entity.")

    class Config:
        from_attributes = True


class Relationship(BaseModel):
    """Pydantic model for relationships between entities."""
    source: str = Field(..., description="The name of the source entity.")
    target: str = Field(..., description="The name of the target entity.")
    relationship_type: str = Field(..., description="The type of relationship between the entities.")
    description: Optional[str] = Field(None, description="A description of the relationship.")
    confidence: float = Field(default=1.0, description="Confidence score for the relationship (0.0 to 1.0).")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata about the relationship.")

    class Config:
        from_attributes = True


class ExtractedEntities(BaseModel):
    """Pydantic model for a collection of extracted entities and their relationships."""
    entities: List[Entity] = Field(default_factory=list, description="List of extracted entities.")
    relationships: List[Relationship] = Field(default_factory=list, description="List of entity relationships.")
    topics: List[str] = Field(default_factory=list, description="List of identified topics.")

    class Config:
        from_attributes = True 
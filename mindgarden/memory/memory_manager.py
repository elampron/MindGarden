"""
Memory manager for MindGarden knowledge storage and retrieval.
"""

import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

from mindgarden.config.settings import get_config

logger = logging.getLogger(__name__)


class MemoryManager:
    """Memory manager for knowledge storage and retrieval."""

    def __init__(self):
        """Initialize the memory manager."""
        self.config = get_config()
        # In Phase 1, we'll use a simple in-memory storage for conversation history
        # Later phases will integrate with Neo4j for persistent storage
        self.memories = []

    def retrieve_relevant(self, query: str, limit: int = 5) -> List[str]:
        """
        Retrieve relevant memories based on a query.
        
        Args:
            query: The query to search for relevant memories.
            limit: Maximum number of memories to retrieve.
            
        Returns:
            List of relevant memory strings.
        """
        # In Phase 1, this is a simple implementation that returns the latest memories
        # Later phases will implement semantic search via Neo4j or vector database
        logger.debug(f"Retrieving memories relevant to: {query}")
        
        # For now, just return the most recent memories up to the limit
        relevant_memories = []
        
        if self.memories:
            # Sort memories by timestamp (newest first)
            sorted_memories = sorted(self.memories, key=lambda x: x.get('timestamp', 0), reverse=True)
            
            # Take the most recent ones up to limit
            for memory in sorted_memories[:limit]:
                memory_text = f"{memory.get('text', '')} [From: {memory.get('source', '')}]"
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
        
        memory_item = {
            'text': content,
            'source': source,
            'timestamp': timestamp,
            'date': formatted_time
        }
        
        if metadata:
            memory_item.update(metadata)
            
        self.memories.append(memory_item)
        logger.debug(f"Stored document from {source} at {formatted_time}")

    def clear_memory(self) -> None:
        """Clear all memories."""
        self.memories = []
        logger.debug("Cleared all memories") 
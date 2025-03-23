"""
Tests for the memory manager.
"""

import pytest
from unittest.mock import patch, MagicMock
import time
from datetime import datetime

from mindgarden.memory.memory_manager import MemoryManager


@pytest.fixture
def memory_manager():
    """Fixture for a MemoryManager instance."""
    return MemoryManager()


def test_memory_manager_initialization():
    """Test memory manager initialization."""
    manager = MemoryManager()
    assert manager is not None
    assert manager.memories == []


def test_store_conversation(memory_manager):
    """Test storing a conversation in memory."""
    # Store a conversation
    memory_manager.store_conversation("Hello, Quinn!", "Hi there! How can I help you?")
    
    # Verify memories were stored
    assert len(memory_manager.memories) == 2
    
    # Check user message
    user_memory = memory_manager.memories[0]
    assert user_memory['text'] == "Hello, Quinn!"
    assert user_memory['source'] == "user"
    assert 'timestamp' in user_memory
    assert 'date' in user_memory
    
    # Check assistant message
    assistant_memory = memory_manager.memories[1]
    assert assistant_memory['text'] == "Hi there! How can I help you?"
    assert assistant_memory['source'] == "assistant"
    assert 'timestamp' in assistant_memory
    assert 'date' in assistant_memory
    
    # Assistant timestamp should be slightly later
    assert assistant_memory['timestamp'] > user_memory['timestamp']


def test_retrieve_relevant(memory_manager):
    """Test retrieving relevant memories."""
    # Add some test memories
    memory_manager.store_document("Document 1 content", "doc1", {"type": "text"})
    time.sleep(0.1)  # Ensure different timestamps
    memory_manager.store_document("Document 2 content", "doc2", {"type": "text"})
    time.sleep(0.1)  # Ensure different timestamps
    memory_manager.store_conversation("User question", "Assistant answer")
    
    # Retrieve memories
    relevant = memory_manager.retrieve_relevant("test query", limit=2)
    
    # Should return the 2 most recent memories
    assert len(relevant) == 2
    
    # First memory should be the latest (assistant response)
    assert "Assistant answer" in relevant[0]
    # Second memory should be the second latest (user question)
    assert "User question" in relevant[1]


def test_store_document(memory_manager):
    """Test storing a document in memory."""
    # Store a document
    memory_manager.store_document(
        content="This is a test document.",
        source="test.txt",
        metadata={"type": "text", "author": "Test User"}
    )
    
    # Verify document was stored
    assert len(memory_manager.memories) == 1
    
    # Check document properties
    doc = memory_manager.memories[0]
    assert doc['text'] == "This is a test document."
    assert doc['source'] == "test.txt"
    assert doc['type'] == "text"
    assert doc['author'] == "Test User"
    assert 'timestamp' in doc
    assert 'date' in doc


def test_clear_memory(memory_manager):
    """Test clearing memory."""
    # Add some test memories
    memory_manager.store_document("Test document", "test.txt")
    memory_manager.store_conversation("Hello", "Hi")
    
    # Verify memories were added
    assert len(memory_manager.memories) == 3
    
    # Clear memories
    memory_manager.clear_memory()
    
    # Verify memories were cleared
    assert len(memory_manager.memories) == 0 
"""
Tests for the Quinn agent.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio

from mindgarden.agent.agent import Agent


@pytest.fixture
def mock_openai_client():
    """Fixture for mocking OpenAI client."""
    with patch("mindgarden.agent.agent.OpenAI") as mock_openai:
        # Create a mock OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_agent():
    """Fixture for mocking Agent SDK."""
    with patch("mindgarden.agent.agent.AsyncAgent") as mock_agent_class:
        # Create mock agent and run
        mock_agent = MagicMock()
        mock_run = AsyncMock()
        mock_response = MagicMock()
        
        # Content setup with Pydantic model-like structure
        mock_content = MagicMock()
        mock_content.text = "This is a test response from Quinn."
        mock_response.content = [mock_content]
        
        # Set up the async methods
        mock_run.submit_message = AsyncMock(return_value=mock_response)
        mock_agent.create_run = AsyncMock(return_value=mock_run)
        
        # Return the mock agent instance when AsyncAgent is instantiated
        mock_agent_class.return_value = mock_agent
        
        yield mock_agent


@pytest.fixture
def mock_memory_manager():
    """Fixture for mocking MemoryManager."""
    with patch("mindgarden.agent.agent.MemoryManager") as mock_memory_manager_class:
        # Create a mock memory manager
        mock_manager = MagicMock()
        mock_memory_manager_class.return_value = mock_manager
        
        # Mock memory retrieval
        mock_manager.retrieve_relevant.return_value = [
            "Previous memory 1",
            "Previous memory 2"
        ]
        
        yield mock_manager


def test_agent_initialization():
    """Test agent initialization."""
    with patch("mindgarden.agent.agent.OpenAI"), \
         patch("mindgarden.agent.agent.AsyncAgent"), \
         patch("mindgarden.agent.agent.MemoryManager"):
        agent = Agent()
        assert agent is not None
        assert agent.conversation_history == []
        assert agent.state == {"conversation": []}


@pytest.mark.asyncio
async def test_process_message_async(mock_agent, mock_memory_manager):
    """Test async processing of a message."""
    with patch("mindgarden.agent.agent.AsyncAgent", return_value=mock_agent):
        agent = Agent()
        
        # Process a test message asynchronously
        response = await agent._process_message_async("Hello, Quinn!")
        
        # Check the response
        assert response == "This is a test response from Quinn."
        
        # Verify conversation history was updated
        assert len(agent.conversation_history) == 2
        assert agent.conversation_history[0]["role"] == "user"
        assert agent.conversation_history[0]["content"] == "Hello, Quinn!"
        assert agent.conversation_history[1]["role"] == "assistant"
        assert agent.conversation_history[1]["content"] == "This is a test response from Quinn."
        
        # Verify memory manager was used
        mock_memory_manager.retrieve_relevant.assert_called_once_with("Hello, Quinn!")
        mock_memory_manager.store_conversation.assert_called_once_with(
            "Hello, Quinn!", "This is a test response from Quinn."
        )
        
        # Verify agent run was created and message submitted
        mock_agent.create_run.assert_called_once()
        mock_agent.create_run.return_value.submit_message.assert_called_once_with("Hello, Quinn!")


def test_process_message(mock_agent, mock_memory_manager):
    """Test synchronous wrapper for processing a message."""
    with patch("mindgarden.agent.agent.AsyncAgent", return_value=mock_agent), \
         patch("mindgarden.agent.agent.asyncio.run") as mock_run:
        agent = Agent()
        
        # Mock the async run result
        mock_run.return_value = "This is a test response from Quinn."
        
        # Process a test message
        response = agent.process_message("Hello, Quinn!")
        
        # Check that asyncio.run was called with the async method
        mock_run.assert_called_once()
        assert response == "This is a test response from Quinn." 
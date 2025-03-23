"""
Quinn agent module for MindGarden using OpenAI Agent SDK.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Callable

from openai import OpenAI
from openai_agents import AsyncAgent
from openai_agents.tools import Tool
from openai_agents.types import AgentState
from openai_agents.prompts import PromptBuilder

from mindgarden.config.settings import get_config
from mindgarden.memory.memory_manager import MemoryManager

logger = logging.getLogger(__name__)


class Agent:
    """Quinn agent implementation using OpenAI Agent SDK."""

    def __init__(self):
        """Initialize the Quinn agent."""
        self.config = get_config()
        self.memory_manager = MemoryManager()
        self.conversation_history = []
        
        # Initialize OpenAI client with API key and optional org ID
        openai_args = {"api_key": self.config.openai_api_key}
        if self.config.openai_org_id:
            openai_args["organization"] = self.config.openai_org_id
            
        self.client = OpenAI(**openai_args)
        
        # Initialize agent state
        self.state = {"conversation": []}
        
        # Initialize the agent
        self.async_agent = self._create_agent()

    def process_message(self, message: str) -> str:
        """
        Process a user message and generate a response using Agent SDK.
        
        Args:
            message: The user message to process.
            
        Returns:
            The agent's response.
        """
        # Run the async method in a synchronous way
        response = asyncio.run(self._process_message_async(message))
        return response

    async def _process_message_async(self, message: str) -> str:
        """
        Async implementation of process_message.
        
        Args:
            message: The user message to process.
            
        Returns:
            The agent's response.
        """
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": message})
        
        # Retrieve relevant memories
        relevant_memories = self.memory_manager.retrieve_relevant(message)
        
        # Update agent state with relevant memories and new message
        self.state["relevant_memories"] = relevant_memories
        self.state["conversation"] = self.conversation_history[-10:]  # Last 10 messages
        
        # Run the agent
        try:
            run = await self.async_agent.create_run()
            response = await run.submit_message(message)
            
            # Extract the response text
            assistant_message = response.content[0].text
            
            # Add to conversation history
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            # Store conversation in memory
            self.memory_manager.store_conversation(message, assistant_message)
            
            return assistant_message
            
        except Exception as e:
            logger.error(f"Error running agent: {str(e)}")
            raise

    def _create_agent(self) -> AsyncAgent:
        """
        Create an OpenAI Agent instance.
        
        Returns:
            An AsyncAgent instance.
        """
        # Define tools
        tools = [
            self._create_memory_tool(),
        ]
        
        # Create prompt builder with system message
        prompt_builder = PromptBuilder(
            system_prompt=self._build_system_message
        )
        
        # Create the async agent with additional parameters from config
        agent_params = {
            "client": self.client,
            "model": self.config.model,
            "tools": tools,
            "prompt_builder": prompt_builder,
            "state": self.state,
            "temperature": self.config.agent_temperature,
        }
        
        # Add max_tokens if specified
        if self.config.agent_max_tokens:
            agent_params["max_tokens"] = self.config.agent_max_tokens
            
        return AsyncAgent(**agent_params)

    def _create_memory_tool(self) -> Tool:
        """
        Create a tool for accessing the memory system.
        
        Returns:
            A Tool instance for the memory system.
        """
        return Tool(
            name="memory_search",
            description="Search for information in the memory system",
            run=self._memory_search_tool,
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of memories to retrieve",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        )

    async def _memory_search_tool(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """
        Tool implementation for memory search.
        
        Args:
            query: The search query.
            limit: Maximum number of memories to retrieve.
            
        Returns:
            A dictionary with search results.
        """
        memories = self.memory_manager.retrieve_relevant(query, limit)
        return {
            "memories": memories,
            "count": len(memories),
        }

    def _build_system_message(self, state: Dict[str, Any]) -> str:
        """
        Build the system message with context from state.
        
        Args:
            state: The current agent state.
            
        Returns:
            The formatted system message.
        """
        base_prompt = f"""
        You are {self.config.agent_name}, a helpful, friendly, and knowledgeable assistant.
        
        Your goal is to provide helpful, accurate, and thoughtful responses to user queries.
        """
        
        # Add memory context if available
        memory_context = ""
        relevant_memories = state.get("relevant_memories", [])
        if relevant_memories:
            memory_context = "\n\nRelevant context from past interactions and knowledge:\n"
            for i, memory in enumerate(relevant_memories):
                memory_context += f"{i+1}. {memory}\n"
        
        return base_prompt + memory_context 
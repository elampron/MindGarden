# MindGarden / Quinn

MindGarden is a personal, integrated memory and assistant system designed for one-stop AI needs. It serves as the backbone for storing, retrieving, and processing personal data, documents, and conversation history. Quinn is the friendly, gender-neutral AI assistant that interacts with users via text and voice, orchestrating tasks, retrieving memories, and assisting with daily needs.

## Project Overview

MindGarden integrates several key components:
- **Quinn** - An AI assistant agent using OpenAI Agent SDK that interacts with users and orchestrates tasks
- **Knowledge Module (KN)** - Memory and knowledge storage system
- **Tools & Plugins** - Extensible functionality for various tasks through the Agent SDK tools interface

## Development Phases

1. **Phase 1 (Current)** - Initial MVP with basic agent loop and CLI interface
2. **Phase 2** - Voice support and simple web UI
3. **Phase 3** - Enhanced UI, admin portal, and extended tools
4. **Phase 4** - Refinement, optimization, and personalization

## Key Features

- **OpenAI Agent SDK Integration** - Utilizes OpenAI's latest agent framework for advanced assistant capabilities
- **Memory Management** - Stores and retrieves conversation history and documents
- **Tool Integration** - Extensible tool framework through Agent SDK
- **CLI Interface** - User-friendly command-line interface

## Getting Started

### Prerequisites
- Python 3.12+
- Docker and Docker Compose
- Neo4j database
- OpenAI API key

### Installation
1. Clone the repository
2. Set up a virtual environment (we use `uv` for package management)
3. Run `uv pip install -e .` to install in development mode
4. Create a `.env` file based on `.env.example` and add your OpenAI API key
5. Start the Neo4j database with Docker Compose

## Usage
Currently in development phase 1 with basic CLI interface.

## License
See LICENSE file.

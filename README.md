# Financial Product Recommendation Chatbot System

A comprehensive agent-based financial product recommendation system built with CrewAI, featuring event-driven architecture and multi-platform chatbot support.

## 🎯 Overview

This system provides intelligent financial product recommendations through a Discord chatbot interface with a robust event-driven architecture powered by CrewAI agents. The system has been extensively refactored for improved maintainability, performance, and code quality.

## 🏗️ Architecture

### Event-Driven Architecture
- **Event Bus**: Central message routing and delivery
- **Message Queue**: Persistent message storage with retry mechanisms
- **Event Handlers**: Specialized handlers for each system event
- **CrewAI Integration**: Agent orchestration for intelligent processing

### Core Components
- **Data Models**: Comprehensive Pydantic models for all entities
- **Session Management**: User session tracking and conversation history
- **Agent System**: CrewAI agents for intent analysis and response generation
- **Configuration Management**: Centralized configuration system
- **Professional Logging**: Structured logging with file output and performance tracking

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- pip package manager
- Discord Bot Token (for Discord bot)
- Anthropic API Key (for LLM integration)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd yuanta_recommendation_chatbot_crewai
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
Create a `.env` file with your API keys:
```env
ANTHROPIC_API_KEY=your_anthropic_api_key
DISCORD_BOT_TOKEN=your_discord_bot_token
```

4. **Run the application**

**Discord Bot**
```bash
python discord_bot_main.py
```
The Discord bot will connect and be ready to receive messages.

## 📁 Project Structure

```
yuanta_recommendation_chatbot_crewai/
├── src/
│   ├── agents/                 # CrewAI agent implementations
│   │   ├── __init__.py
│   │   ├── base_agent.py       # Base agent with logging & validation
│   │   ├── agent_factory.py    # Agent factory pattern
│   │   ├── crew_orchestrator.py # Main CrewAI orchestrator
│   │   ├── market_data_agent.py # Market data analysis
│   │   ├── recommendation_agent.py # Product recommendations
│   │   ├── report_writer_agent.py # Report generation
│   │   ├── supervisor_agent.py # Workflow coordination
│   │   └── [other agents...]
│   ├── core/                   # Core system components
│   │   └── event_bus.py
│   ├── data/                   # Data models and sources
│   │   ├── models.py
│   │   ├── product_database.py # financial products
│   │   └── mock_data_manager.py # Mock data for testing
│   ├── utils/                  # Utility modules
│   │   ├── __init__.py
│   │   ├── logger.py           # Professional logging system
│   │   └── session_manager.py
│   ├── config.py               # Centralized configuration
│   ├── exceptions.py           # Custom exception hierarchy
│   └── chatbot/               # Chatbot platform adapters
│       ├── discord_bot.py      # Real Discord bot implementation
│       ├── discord_adapter.py  # Discord adapter
│       ├── base_adapter.py     # Base adapter interface
│       └── manager.py          # Chatbot manager
├── tests/                     # Test suite
│   └── test_basic_functionality.py
├── memory-bank/               # Project documentation
├── discord_bot_main.py        # Discord bot entry point
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## 🔧 Core Features

### 1. Event-Driven Processing
- **Chat Message Events**: Process incoming messages from any platform
- **Intent Analysis**: AI-powered intent detection and entity extraction
- **Tool Selection**: Dynamic selection of data retrieval tools
- **Response Generation**: Intelligent response generation with recommendations

### 2. Discord Bot Support
- **Discord Bot**: Full-featured Discord bot with real-time financial advice
  - Intelligent financial recommendations
  - Bot commands (!help, !status, !ping)
  - Session management for Discord users
  - Rich response formatting with embeds
  - Automatic intent classification

### 3. Session Management
- **User Sessions**: Track conversation context across platforms
- **Session Validation**: Secure session management
- **Automatic Cleanup**: Expired session cleanup
- **Analytics**: Session statistics and performance metrics

### 4. CrewAI Agent System
- **Base Agent**: Common functionality (logging, validation, performance tracking)
- **Agent Factory**: Centralized agent creation and management
- **Crew Orchestrator**: Coordinates the entire recommendation process
- **Specialized Agents**: Market data, recommendations, reports, supervision
- **LLM Hallucination Prevention**: Product constraint system to prevent fake recommendations

### 5. Code Quality Features
- **Professional Logging**: Structured logging with file output and performance tracking
- **Configuration Management**: Centralized configuration system
- **Custom Exceptions**: Proper exception hierarchy for robust error handling
- **Performance Tracking**: Built-in performance monitoring and metrics
- **Input Validation**: Comprehensive validation throughout the system



## 🧪 Testing

Run the test suite:
```bash
pytest tests/ -v
```

### Test Coverage
- **Data Models**: Pydantic model validation
- **Event Bus**: Event publishing and subscription
- **Session Manager**: Session lifecycle management
- **Integration**: End-to-end flow testing
- **Agent System**: CrewAI agent functionality

### Optimization Strategies
- **Caching**: Product database caching to prevent regeneration
- **Async Processing**: Non-blocking event processing
- **Load Balancing**: Horizontal scaling support
- **Circuit Breakers**: Fault tolerance mechanisms
- **Performance Tracking**: Built-in metrics and monitoring


### Environment Variables
```bash
ANTHROPIC_API_KEY=your_anthropic_key
DISCORD_BOT_TOKEN=your_discord_bot_token
```

## 📚 Documentation

### Creative Phase Documents
- **System Architecture**: `memory-bank/creative/creative-system-architecture.md`
- **Agent Interactions**: `memory-bank/creative/creative-agent-interaction-patterns.md`
- **Data Models**: `memory-bank/creative/creative-data-model-design.md`
- **Integration Strategy**: `memory-bank/creative/creative-integration-strategy-design.md`
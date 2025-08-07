# Technical Context: Financial Product Recommendation Chatbot

## Technology Stack

### Core Framework
- **CrewAI**: Main orchestration framework for multi-agent coordination
- **Python 3.12.5**: Primary programming language
- **Pydantic**: Data validation and serialization

### Data Storage
- **ChromaDB**: Vector database for semantic search
- **PostgreSQL**: Primary relational database
- **Neo4j**: Graph database for GraphRAG implementation
- **Redis**: Caching and session management

### LLM Integration
- **Anthropic Claude**: Primary language model for generation
- **OpenAI GPT-4**: Fallback language model
- **LiteLLM**: Unified LLM interface

### Web Framework
- **FastAPI**: High-performance API framework
- **Streamlit**: Web interface for user interactions
- **Uvicorn**: ASGI server for FastAPI

### Development Tools
- **pytest**: Testing framework
- **black**: Code formatting
- **flake8**: Code linting
- **mypy**: Type checking

## Architecture Components

### 1. User Interaction Layer
- **Streamlit Interface**: Chat-based user interface
- **API Gateway**: RESTful API endpoints
- **WebSocket Support**: Real-time communication

### 2. Memory Context Layer
- **Conversation History**: Persistent chat history storage
- **User Profiles**: Personalized user data management
- **Session Management**: Active session handling

### 3. Orchestration Layer
- **Query Orchestrator**: Coordinates multiple agents
- **Intent Analyzer**: Determines user intent
- **Tool Selector**: Chooses appropriate tools for queries

### 4. Retrieval Layer
- **Sparse Search (BM25)**: Keyword-based search
- **Dense Search**: Vector-based semantic search
- **Structured Query**: Database queries for product data
- **GraphRAG**: Knowledge graph-based retrieval

### 5. Fusion Layer
- **Result Merging**: Combines results from multiple sources
- **Ranking Algorithm**: Prioritizes most relevant results
- **Deduplication**: Removes duplicate results

### 6. Generation Layer
- **LLM Integration**: Anthropic API integration (primary), OpenAI API integration (fallback)
- **Response Formatting**: Structured response generation
- **Quality Validation**: Response quality assessment

## Development Environment

### Local Development
- **Python Virtual Environment**: Isolated dependency management
- **Docker**: Containerized development environment
- **Environment Variables**: Configuration management

### Testing Strategy
- **Unit Tests**: Component-level testing
- **Integration Tests**: Service interaction testing
- **End-to-End Tests**: Complete workflow testing
- **Performance Tests**: Load and stress testing

### Deployment Strategy
- **Containerization**: Docker-based deployment
- **Orchestration**: Kubernetes for production scaling
- **CI/CD**: Automated testing and deployment
- **Monitoring**: Comprehensive system monitoring

## Performance Requirements

### Response Time
- **API Endpoints**: < 500ms average response time
- **Chat Interface**: < 3 seconds for recommendation generation
- **Search Operations**: < 1 second for retrieval

### Scalability
- **Concurrent Users**: Support for 10,000+ simultaneous users
- **Data Volume**: Handle millions of product records
- **Query Volume**: Process 100,000+ queries per hour

### Availability
- **Uptime**: 99.9% availability target
- **Fault Tolerance**: Graceful handling of component failures
- **Data Consistency**: ACID compliance for critical operations

## Security Considerations

### Authentication & Authorization
- **OAuth 2.0**: Standard authentication protocol
- **JWT Tokens**: Stateless session management
- **Role-Based Access**: Granular permission control

### Data Protection
- **Encryption**: Data encryption at rest and in transit
- **PII Handling**: Secure personal information processing
- **Audit Logging**: Comprehensive activity tracking

### Compliance
- **GDPR**: European data protection compliance
- **Financial Regulations**: Industry-specific compliance
- **Security Standards**: SOC 2, ISO 27001 considerations

## Integration Points

### External APIs
- **Financial Data Providers**: Real-time market data
- **Product Catalogs**: Comprehensive product information
- **Compliance Services**: Regulatory reporting

### Internal Systems
- **User Management**: Authentication and profile services
- **Analytics Platform**: Usage and performance tracking
- **Notification System**: Alert and notification services

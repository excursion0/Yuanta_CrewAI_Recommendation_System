"""
Main FastAPI application for the financial product recommendation system.

This module provides the core FastAPI application with middleware,
CORS configuration, and route registration.
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from src.core.event_bus import event_bus
from src.api.chat import router as chat_router
from src.api.session import router as session_router
from src.utils.session_manager import session_manager
from src.chatbot import ChatbotManagerFactory
from src.llm import LLMManager, LLMConfig
from src.data_sources.mock_data_manager import MockDataManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting financial product recommendation API")
    await event_bus.start()
    logger.info("Event bus started successfully")

    # Initialize session manager
    await session_manager.start()
    logger.info("Session manager started successfully")

    # Initialize chatbot manager
    app.state.chatbot_manager = ChatbotManagerFactory.create_manager(
        event_bus=event_bus,
        session_manager=session_manager,
        platforms=["discord"]
    )
    await app.state.chatbot_manager.start()
    logger.info("Chatbot manager started successfully")

    # Initialize mock data manager
    app.state.data_manager = MockDataManager()
    await app.state.data_manager.start()
    logger.info("Mock data manager started successfully")

    # Initialize LLM manager
    llm_config = LLMConfig(
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        fallback_enabled=True
    )
    app.state.llm_manager = LLMManager(llm_config)
    llm_initialized = await app.state.llm_manager.initialize()
    if llm_initialized:
        logger.info("LLM manager started successfully")
    else:
        logger.warning("LLM manager failed to initialize - some features may be limited")

    yield

    # Shutdown
    logger.info("Shutting down financial product recommendation API")
    await app.state.chatbot_manager.stop()
    logger.info("Chatbot manager stopped successfully")
    await app.state.data_manager.stop()
    logger.info("Mock data manager stopped successfully")
    await session_manager.stop()
    logger.info("Session manager stopped successfully")
    await event_bus.stop()
    logger.info("Event bus stopped successfully")

# Create FastAPI app
app = FastAPI(
    title="Financial Product Recommendation API",
    description="AI-powered financial product recommendation system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ],  # Restrict to specific origins
    allow_credentials=False,  # Disable credentials for security
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(session_router, prefix="/api/v1/session", tags=["session"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Financial Product Recommendation API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "event_bus": "running",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/chatbot/health")
async def chatbot_health_check(request: Request):
    """Chatbot health check endpoint"""
    chatbot_manager = request.app.state.chatbot_manager
    health_data = await chatbot_manager.health_check()

    return {
        "status": "healthy",
        "chatbot_manager": health_data,
        "platforms": chatbot_manager.get_platforms(),
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/llm/health")
async def llm_health_check(request: Request):
    """LLM health check endpoint"""
    llm_manager = request.app.state.llm_manager
    health_data = await llm_manager.health_check()

    return {
        "status": "healthy" if health_data.primary_provider != "none" else "degraded",
        "llm_manager": health_data.model_dump(),
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/llm/models")
async def llm_models(request: Request):
    """Get available LLM models"""
    llm_manager = request.app.state.llm_manager
    models = await llm_manager.get_available_models()

    return {
        "models": models,
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.post("/llm/test")
async def llm_test(request: Request):
    """Test LLM generation capabilities"""
    llm_manager = request.app.state.llm_manager
    test_result = await llm_manager.test_generation()

    return {
        "test_result": test_result,
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/data/health")
async def data_health_check(request: Request):
    """Check data manager health"""
    try:
        data_manager = request.app.state.data_manager
        health_status = await data_manager.health_check()
        return health_status
    except Exception as e:
        logger.error(f"Data health check failed: {e}")
        return {"error": str(e)}

@app.get("/data/products")
async def get_products(request: Request, limit: int = 10, offset: int = 0):
    """Get available financial products"""
    try:
        data_manager = request.app.state.data_manager
        products = await data_manager.search_products(limit=limit, offset=offset)
        return {
            "products": [product.model_dump() for product in products],
            "total": len(products),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Failed to get products: {e}")
        return {"error": str(e)}

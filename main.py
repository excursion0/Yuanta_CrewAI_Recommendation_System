"""
Main entry point for the Financial Product Recommendation Chatbot System.

This module provides the main application that starts the FastAPI server
and initializes all core components of the system.
"""

import asyncio
import logging
import uvicorn
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.api.main import app
from src.core.event_bus import event_bus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting Financial Product Recommendation Chatbot System")
    
    # Start event bus
    await event_bus.start()
    logger.info("✅ Event bus started successfully")
    
    logger.info("📊 System Status:")
    logger.info("   - Event Bus: Running")
    logger.info("   - API Server: Starting")
    logger.info("   - Session Manager: Ready")
    logger.info("   - CrewAI Agents: Ready")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Financial Product Recommendation Chatbot System")
    await event_bus.stop()
    logger.info("✅ Event bus stopped successfully")


def main():
    """Main application entry point"""
    logger.info("🎯 Financial Product Recommendation Chatbot System")
    logger.info("=" * 60)
    logger.info("📋 System Components:")
    logger.info("   • Event-Driven Architecture")
    logger.info("   • CrewAI Agent Orchestration")
    logger.info("   • FastAPI REST API")
    logger.info("   • Session Management")
    logger.info("   • Multi-Platform Chatbot Support")
    logger.info("=" * 60)
    
    # Update app lifespan
    app.router.lifespan_context = lifespan
    
    # Start the server
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8001,
        log_level="info",
        reload=True
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Discord Bot Main Entry Point

This module provides the main entry point for running the Discord bot
independently of the FastAPI server.
"""

import asyncio
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main Discord bot entry point"""
    logger.info("🤖 Starting Financial Advisor Discord Bot")
    logger.info("=" * 60)
    
    # Check for Discord token
    discord_token = os.getenv("DISCORD_BOT_TOKEN")
    if not discord_token:
        logger.error("❌ DISCORD_BOT_TOKEN not found in environment variables")
        logger.error("Please set DISCORD_BOT_TOKEN in your .env file")
        return
    
    # Check for Anthropic API key
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_api_key:
        logger.error("❌ ANTHROPIC_API_KEY not found in environment variables")
        logger.error("Please set ANTHROPIC_API_KEY in your .env file")
        return
    
    try:
        # Import required modules
        from src.core.event_bus import event_bus
        from src.utils.session_manager import SessionManager
        from src.chatbot.discord_bot import setup_discord_bot
        
        # Initialize core components
        logger.info("📡 Initializing core components...")
        
        # Start event bus
        await event_bus.start()
        logger.info("✅ Event bus started")
        
        # Initialize session manager
        session_manager = SessionManager()
        logger.info("✅ Session manager initialized")
        
        # Set up and start Discord bot
        logger.info("🤖 Starting Discord bot...")
        bot = await setup_discord_bot(event_bus, session_manager, discord_token)
        
        # Initialize bot components (LLM, CrewAI, etc.) BEFORE starting the bot
        logger.info("🔧 Initializing bot components...")
        await bot.initialize()
        logger.info("✅ Bot components initialized")
        
        # Now start the bot
        logger.info("🚀 Starting Discord bot...")
        await bot.start(discord_token)
        
        logger.info("🎉 Discord bot started successfully!")
        logger.info("📊 Bot Status:")
        logger.info(f"   • Bot Name: {bot.user.name}")
        logger.info(f"   • Bot ID: {bot.user.id}")
        logger.info(f"   • Servers: {len(bot.guilds)}")
        logger.info(f"   • Users: {len(bot.users)}")
        logger.info("=" * 60)
        logger.info("💡 The bot is now ready to receive messages!")
        logger.info("   Users can send financial queries and the bot will respond with recommendations.")
        logger.info("   Use !help for bot commands.")
        
        # Keep the bot running
        await asyncio.Event().wait()  # Wait indefinitely
        
    except KeyboardInterrupt:
        logger.info("🛑 Received shutdown signal")
    except Exception as e:
        logger.error(f"❌ Error starting Discord bot: {e}")
        raise
    finally:
        # Cleanup
        logger.info("🧹 Cleaning up...")
        try:
            await event_bus.stop()
            logger.info("✅ Event bus stopped")
        except Exception as e:
            logger.error(f"Error stopping event bus: {e}")
        
        logger.info("👋 Discord bot shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Discord bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        exit(1) 
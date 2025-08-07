"""
Refactored Discord bot implementation using discord.py.

This module provides the actual Discord bot functionality with proper
message handling, command processing, and integration with the financial
recommendation system. Functions have been broken down for better maintainability.
"""

import asyncio
import logging
import discord
from discord.ext import commands
from typing import Dict, Any, Optional, List
from datetime import datetime
import os

from src.core.event_bus import EventBus, EventType
from src.utils.session_manager import SessionManager, conversation_manager
from src.data.models import ChatResponse, ConversationMessage, MessageType, UserProfile
from src.data_sources.mock_data_manager import MockDataManager
from src.llm.crewai_manager import CrewAIManager
from src.llm.manager import LLMManager, LLMConfig
from src.constants import DISCORD_MAX_MESSAGE_LENGTH, DISCORD_TIMEOUT_SECONDS
from src.exceptions import DiscordBotError, ProcessingError


class FinancialDiscordBot(commands.Bot):
    """
    Discord bot for financial product recommendations.
    
    Handles Discord interactions, message processing, and integrates
    with the financial recommendation system.
    """
    
    def __init__(self, event_bus: EventBus, session_manager: SessionManager, 
                 command_prefix: str = "!", intents: discord.Intents = None):
        """
        Initialize the Discord bot.
        
        Args:
            event_bus: Event bus for publishing messages
            session_manager: Session manager for user sessions
            command_prefix: Bot command prefix
            intents: Discord intents configuration
        """
        # Set up intents if not provided
        if intents is None:
            intents = discord.Intents.default()
            intents.message_content = True
            intents.messages = True
        
        super().__init__(command_prefix=command_prefix, intents=intents)
        
        self.event_bus = event_bus
        self.session_manager = session_manager
        self._logger = logging.getLogger(__name__)
        
        # Track active sessions
        self._active_sessions: Dict[str, str] = {}  # user_id -> session_id
        
        # Track processed responses to avoid duplicates
        self._processed_responses: set = set()
        
        # Initialize managers
        self.data_manager = MockDataManager()
        # CrewAI manager will be initialized after LLM manager is set up
        self.crewai_manager = None
        
        # Subscribe to response events
        self.event_bus.subscribe(EventType.CHAT_RESPONSE, self._handle_response)
        
        # Set up bot events
        self.setup_events()
    
    def setup_events(self):
        """Set up bot event handlers"""
        
        @self.event
        async def on_ready():
            """Called when the bot is ready"""
            self._logger.info(f"🤖 Discord Bot Ready!")
            self._logger.info(f"   Bot Name: {self.user.name}")
            self._logger.info(f"   Bot ID: {self.user.id}")
            self._logger.info(f"   Servers: {len(self.guilds)}")
            self._logger.info(f"   Users: {len(self.users)}")
            
            # Set bot status
            await self.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name="financial advice"
                )
            )
            
            # Log available commands
            self._logger.info("📋 Available Commands:")
            self._logger.info("   • !financial_help - Show detailed help")
            self._logger.info("   • !status - Show bot status")
            self._logger.info("   • !ping - Test bot responsiveness")
            self._logger.info("   • Send any message for financial advice")
        
        @self.event
        async def on_disconnect():
            """Called when the bot disconnects"""
            self._logger.warning("🔌 Discord Bot Disconnected")
        
        @self.event
        async def on_resumed():
            """Called when the bot resumes connection"""
            self._logger.info("🔄 Discord Bot Connection Resumed")
        
        @self.event
        async def on_error(event, *args, **kwargs):
            """Called when an error occurs"""
            self._logger.error(f"❌ Discord Bot Error in {event}: {args}, {kwargs}")
        
        @self.event
        async def on_message(message):
            """Called when a message is received"""
            await self._handle_message(message)
    
    async def _handle_commands(self, message):
        """Handle Discord commands"""
        try:
            # Process commands
            await self.process_commands(message)
        except Exception as e:
            self._logger.error(f"Error handling command: {e}")
            await message.channel.send("I encountered an error processing your command. Please try again.")
    
    async def _handle_message(self, message):
        """Handle incoming Discord messages"""
        try:
            # Ignore bot messages
            if message.author == self.user:
                return

            # Check for commands
            if message.content.startswith('!'):
                await self._handle_commands(message)
                return

            # Start typing indicator immediately
            async with message.channel.typing():
                self._logger.info(f"🤔 Processing message from {message.author.display_name}: {message.content[:50]}...")
                
                # Process user message
                user_id = str(message.author.id)
                session_id = await self._get_or_create_session(user_id)
                await self._store_user_message(session_id, user_id, message.content)
                
                # Get conversation history and user profile
                history = await conversation_manager.get_conversation(session_id)
                user_profile = self._create_user_profile(user_id, message.author.display_name)
                products = await self.data_manager.search_products()
                
                # Process with CrewAI
                try:
                    result = await self._process_with_crewai(message.content, user_profile, history, products)
                    response_text = self._extract_response_text(result)
                    
                    # Send response to Discord
                    await self._send_response_to_discord(message, response_text)
                    
                    # Store bot response
                    await self._store_bot_response(session_id, user_id, result, response_text)
                        
                except Exception as e:
                    await self._handle_processing_error(message, session_id, user_id, e)
                
        except Exception as e:
            self._logger.error(f"Error handling Discord message: {e}")
            await message.channel.send("I apologize, but I encountered an error. Please try again.")
    
    async def _get_or_create_session(self, user_id: str) -> str:
        """Get existing session or create new one for user."""
        existing_sessions = await self.session_manager.get_user_sessions(user_id)
        if existing_sessions:
            session_id = existing_sessions[0].session_id
            self._logger.info(f"Using existing session: {session_id}")
            await self.session_manager.update_session_activity(session_id)
        else:
            session_id = await self.session_manager.create_session(user_id, "discord")
            self._logger.info(f"Created new session: {session_id}")
        return session_id
    
    async def _store_user_message(self, session_id: str, user_id: str, content: str):
        """Store user message in conversation."""
        user_msg = ConversationMessage(
            session_id=session_id,
            user_id=user_id,
            message_type=MessageType.USER_QUERY,
            content=content,
            timestamp=datetime.now()
        )
        await conversation_manager.add_message(session_id, user_msg)
    
    def _create_user_profile(self, user_id: str, display_name: str) -> UserProfile:
        """Create user profile for the request."""
        return UserProfile(
            user_id=user_id,
            name=display_name,
            email="",
            age=30,
            income_level="medium",
            investment_experience="beginner",
            risk_tolerance="medium",
            investment_goals=["growth"],
            time_horizon="medium",
            preferred_product_types=["mutual_fund"],
            preferred_sectors=["technology"],
            geographic_preferences=["domestic"],
            current_portfolio_value=50000,
            monthly_investment_capacity=2000
        )
    
    async def _process_with_crewai(self, query: str, user_profile: UserProfile, 
                                  history: list, products: list):
        """Process query with CrewAI manager."""
        if self.crewai_manager is None:
            self._logger.error("CrewAI manager is not initialized!")
            raise ProcessingError("CrewAI manager not initialized")
        
        self._logger.info(f"Processing query with CrewAI: {query[:50]}...")
        
        try:
            result = await asyncio.wait_for(
                self.crewai_manager.process_query_with_crewai(
                    query=query,
                    user_profile=user_profile,
                    conversation_history=history[-5:] if history else [],
                    available_products=products
                ),
                timeout=DISCORD_TIMEOUT_SECONDS
            )
        except asyncio.TimeoutError:
            self._logger.warning("CrewAI processing timed out, using fallback response")
            result = self._create_timeout_fallback_result()
        
        return result
    
    def _create_timeout_fallback_result(self):
        """Create fallback result for timeout scenarios."""
        return type('obj', (object,), {
            'analysis_result': (
                "🤖 I'm experiencing high demand right now and my AI services are taking longer than expected. "
                "Please try again in a few minutes. In the meantime, here are some general financial tips:\n\n"
                "• **Diversify your investments** across different asset classes\n"
                "• **Consider your risk tolerance** when choosing investment products\n"
                "• **Review your portfolio regularly** and rebalance as needed\n"
                "• **Consult with a financial advisor** for personalized advice\n\n"
                "Available Yuanta products:\n"
                "• **Conservative Fund** - Low risk, 4-6% returns\n"
                "• **Growth Fund** - High risk, 12-18% returns\n"
                "• **ETF Index Fund** - Medium risk, 8-12% returns\n"
                "• **Balanced Fund** - Medium risk, 8-12% returns"
            ),
            'crew_execution': {'fallback_used': True, 'original_error': 'timeout'}
        })
    
    def _extract_response_text(self, result) -> str:
        """Extract response text from CrewAI result."""
        if hasattr(result, 'analysis_result'):
            response_text = str(result.analysis_result)
        elif hasattr(result, 'content'):
            response_text = result.content
        elif hasattr(result, 'response'):
            response_text = result.response
        elif isinstance(result, dict):
            if 'analysis_result' in result:
                response_text = str(result['analysis_result'])
            elif 'response' in result:
                response_text = str(result['response'])
            else:
                response_text = str(result)
        else:
            response_text = str(result)
        
        # Add fallback note if needed
        crew_execution = getattr(result, 'crew_execution', {})
        if crew_execution.get('fallback_used', False):
            fallback_note = "\n\n*Note: This response was generated using our fallback system due to high AI service demand. For more detailed analysis, please try again in a few minutes.*"
            response_text += fallback_note
            self._logger.info("Added fallback note to response")
        
        return response_text
    
    async def _send_response_to_discord(self, message, response_text: str):
        """Send response to Discord channel."""
        if len(response_text) > DISCORD_MAX_MESSAGE_LENGTH:
            self._logger.info(f"Response is {len(response_text)} characters, splitting into multiple messages")
            message_chunks = self._split_long_message(response_text)
            self._logger.info(f"Split response into {len(message_chunks)} chunks")
            
            # Send first chunk with mention
            await message.channel.send(f"{message.author.mention} {message_chunks[0]}")
            
            # Send remaining chunks with continuation indicator
            for chunk in message_chunks[1:]:
                await message.channel.send(f"*[Continued...]*\n{chunk}")
            
            self._logger.info(f"✅ Successfully sent {len(message_chunks)} message chunks to Discord")
        else:
            # Send single message
            await message.channel.send(f"{message.author.mention} {response_text}")
            self._logger.info(f"✅ Successfully sent single response to Discord")
    
    async def _store_bot_response(self, session_id: str, user_id: str, result, response_text: str):
        """Store bot response in conversation."""
        # Convert FinancialProduct objects to dictionaries for storage
        recommendations = getattr(result, 'recommendations', [])
        if recommendations:
            converted_recommendations = []
            for rec in recommendations:
                if hasattr(rec, 'model_dump'):
                    # Pydantic model
                    converted_recommendations.append(rec.model_dump())
                elif hasattr(rec, '__dict__'):
                    # Regular object
                    converted_recommendations.append(rec.__dict__)
                else:
                    # Already a dict or other type
                    converted_recommendations.append(rec)
            recommendations = converted_recommendations
        
        bot_msg = ConversationMessage(
            session_id=session_id,
            user_id=user_id,
            message_type=MessageType.SYSTEM_RESPONSE,
            content=response_text,
            timestamp=datetime.now(),
            recommendations=recommendations,
            sources=getattr(result, 'sources', ['crewai']),
            generation_time=getattr(result, 'processing_time', 0.0)
        )
        await conversation_manager.add_message(session_id, bot_msg)
    
    async def _handle_processing_error(self, message, session_id: str, user_id: str, error: Exception):
        """Handle processing errors and send fallback response."""
        error_msg = str(error)
        self._logger.error(f"Error processing message: {error_msg}")
        
        # Determine fallback response based on error type
        if any(keyword in error_msg.lower() for keyword in ["overload", "overloaded", "llm", "anthropic", "api"]):
            fallback_response = self._get_overload_fallback_response()
        else:
            fallback_response = self._get_general_error_fallback_response(error_msg)
        
        # Store fallback response
        bot_msg = ConversationMessage(
            session_id=session_id,
            user_id=user_id,
            message_type=MessageType.SYSTEM_RESPONSE,
            content=fallback_response,
            timestamp=datetime.now(),
            recommendations=[],
            sources=['fallback'],
            generation_time=0.0
        )
        await conversation_manager.add_message(session_id, bot_msg)
        
        # Send fallback response
        try:
            await message.channel.send(fallback_response)
            self._logger.info("✅ Sent fallback response to Discord")
        except discord.Forbidden:
            self._logger.error("❌ Bot doesn't have permission to send messages in this channel")
    
    def _get_overload_fallback_response(self) -> str:
        """Get fallback response for overload scenarios."""
        return (
            f"🤖 I'm experiencing high demand right now and my AI services are temporarily overloaded. "
            f"Please try again in a few minutes. In the meantime, here are some general financial tips:\n\n"
            f"• **Diversify your investments** across different asset classes\n"
            f"• **Consider your risk tolerance** when choosing investment products\n"
            f"• **Review your portfolio regularly** and rebalance as needed\n"
            f"• **Consult with a financial advisor** for personalized advice\n\n"
            f"Available Yuanta products:\n"
            f"• **Conservative Fund** - Low risk, 4-6% returns\n"
            f"• **Growth Fund** - High risk, 12-18% returns\n"
            f"• **ETF Index Fund** - Medium risk, 8-12% returns\n"
            f"• **Balanced Fund** - Medium risk, 8-12% returns"
        )
    
    def _get_general_error_fallback_response(self, error_msg: str) -> str:
        """Get fallback response for general errors."""
        return (
            f"🤖 I encountered an error while processing your request. "
            f"Please try again or contact support if the issue persists.\n\n"
            f"Error: {error_msg[:100]}{'...' if len(error_msg) > 100 else ''}"
        )
    
    async def _handle_response(self, response_data: Dict[str, Any]):
        """Handle response events from the event bus"""
        try:
            # Extract session ID and user ID
            session_id = response_data.get('session_id')
            user_id = response_data.get('user_id')
            
            if not session_id or not user_id:
                self._logger.warning("Response missing session_id or user_id")
                return
            
            # Check if we've already processed this response
            response_id = f"{session_id}_{response_data.get('timestamp', '')}"
            if response_id in self._processed_responses:
                self._logger.debug(f"Already processed response: {response_id}")
                return
            
            # Mark as processed
            self._processed_responses.add(response_id)
            
            # Get user ID from session if needed
            if not user_id:
                user_id = self._extract_user_id_from_session(session_id)
            
            if not user_id:
                self._logger.warning(f"Could not find user for session: {session_id}")
                return
            
            # Format response for Discord
            formatted_response = self._format_response_for_discord(response_data)
            
            # Find the user's channel and send response
            # This would need to be implemented based on your channel tracking
            self._logger.info(f"Processed response for user {user_id}: {formatted_response[:50]}...")
            
        except Exception as e:
            self._logger.error(f"Error handling response: {e}")
    
    def _extract_user_id_from_session(self, session_id: str) -> Optional[str]:
        """Extract user ID from session ID"""
        try:
            # This is a simplified implementation
            # In a real system, you'd query the session manager
            return None  # Placeholder
        except Exception as e:
            self._logger.error(f"Error extracting user ID from session: {e}")
            return None
    
    def _format_response_for_discord(self, response_event) -> str:
        """Format response event for Discord display"""
        try:
            if isinstance(response_event, dict):
                content = response_event.get('content', '')
                recommendations = response_event.get('recommendations', [])
                
                # Format recommendations if present
                if recommendations:
                    content += "\n\n**Recommendations:**\n"
                    for i, rec in enumerate(recommendations[:3], 1):
                        content += f"{i}. {rec.get('name', 'Unknown')}\n"
                
                return content
            else:
                return str(response_event)
        except Exception as e:
            self._logger.error(f"Error formatting response: {e}")
            return "An error occurred while formatting the response."
    
    def _split_long_message(self, message: str, max_length: int = DISCORD_MAX_MESSAGE_LENGTH) -> list:
        """Split long message into chunks that fit Discord's limit"""
        if len(message) <= max_length:
            return [message]
        
        # Try splitting by paragraphs first
        paragraphs = message.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) + 2 <= max_length:
                current_chunk += paragraph + '\n\n'
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + '\n\n'
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # If we still have chunks that are too long, split by sentences
        final_chunks = []
        for chunk in chunks:
            if len(chunk) <= max_length:
                final_chunks.append(chunk)
            else:
                final_chunks.extend(self._split_by_sentences(chunk, max_length))
        
        return final_chunks
    
    def _split_by_sentences(self, text: str, max_length: int) -> list:
        """Split text by sentences while respecting max length"""
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 2 <= max_length:
                current_chunk += sentence + '. '
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + '. '
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the bot"""
        try:
            health_status = {
                'status': 'healthy',
                'bot_ready': self.is_ready(),
                'guild_count': len(self.guilds),
                'user_count': len(self.users),
                'crewai_initialized': self.crewai_manager is not None,
                'active_sessions': len(self._active_sessions),
                'processed_responses': len(self._processed_responses)
            }
            
            # Check for potential issues
            if not self.is_ready():
                health_status['status'] = 'not_ready'
            if self.crewai_manager is None:
                health_status['status'] = 'crewai_not_initialized'
            
            return health_status
            
        except Exception as e:
            self._logger.error(f"Health check failed: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def initialize(self):
        """Initialize the bot and its dependencies"""
        try:
            self._logger.info("🚀 Initializing Discord Bot...")
            
            # Initialize LLM manager
            llm_config = LLMConfig(
                provider="anthropic",
                model="claude-3-5-sonnet-20241022",
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
            
            llm_manager = LLMManager(llm_config)
            
            # Initialize CrewAI manager
            self.crewai_manager = CrewAIManager(llm_manager)
            
            self._logger.info("✅ Discord Bot initialization completed")
            
        except Exception as e:
            self._logger.error(f"❌ Discord Bot initialization failed: {e}")
            raise DiscordBotError(f"Failed to initialize Discord bot: {e}")


class FinancialCommands(commands.Cog):
    """Financial commands for the Discord bot"""
    
    def __init__(self, bot: FinancialDiscordBot):
        self.bot = bot
    
    @commands.command(name="financial_help")
    async def financial_help_command(self, ctx):
        """Show detailed help for financial commands"""
        help_text = """
🤖 **Financial Recommendation Bot Help**

**Available Commands:**
• `!financial_help` - Show this help message
• `!status` - Show bot status and health
• `!ping` - Test bot responsiveness
• `!history` - Show your conversation history
• `!clear_history` - Clear your conversation history

**How to Use:**
Simply send any message asking about financial advice, investment recommendations, or product information. For example:
• "What investment options do you recommend for a beginner?"
• "Tell me about mutual funds"
• "What's the best way to start investing with $10,000?"

**Features:**
• Personalized investment recommendations
• Risk assessment and portfolio analysis
• Product comparisons and market insights
• Conversation history and session management

**Privacy:**
Your conversations are stored securely and can be cleared at any time using `!clear_history`.
        """
        await ctx.send(help_text)
    
    @commands.command(name="status")
    async def status_command(self, ctx):
        """Show bot status and health information"""
        try:
            health = await self.bot.health_check()
            
            status_text = f"""
🤖 **Bot Status Report**

**Overall Status:** {health['status'].upper()}
**Bot Ready:** {'✅ Yes' if health['bot_ready'] else '❌ No'}
**Servers Connected:** {health['guild_count']}
**Total Users:** {health['user_count']}
**CrewAI Initialized:** {'✅ Yes' if health['crewai_initialized'] else '❌ No'}
**Active Sessions:** {health['active_sessions']}
**Processed Responses:** {health['processed_responses']}
            """
            
            await ctx.send(status_text)
            
        except Exception as e:
            await ctx.send(f"❌ Error getting status: {e}")
    
    @commands.command(name="ping")
    async def ping_command(self, ctx):
        """Test bot responsiveness"""
        await ctx.send(f"🏓 Pong! Bot latency: {round(self.bot.latency * 1000)}ms")
    
    @commands.command(name="history")
    async def history_command(self, ctx):
        """Show user's conversation history"""
        try:
            user_id = str(ctx.author.id)
            sessions = await self.bot.session_manager.get_user_sessions(user_id)
            
            if not sessions:
                await ctx.send("📝 No conversation history found.")
                return
            
            # Get the most recent session
            session = sessions[0]
            history = await conversation_manager.get_conversation(session.session_id)
            
            if not history:
                await ctx.send("📝 No messages in your conversation history.")
                return
            
            # Format history (limit to last 10 messages)
            history_text = "📝 **Your Recent Conversation History:**\n\n"
            for msg in history[-10:]:
                timestamp = msg.timestamp.strftime("%H:%M")
                if msg.message_type == MessageType.USER_QUERY:
                    history_text += f"**You ({timestamp}):** {msg.content[:100]}{'...' if len(msg.content) > 100 else ''}\n\n"
                else:
                    history_text += f"**Bot ({timestamp}):** {msg.content[:100]}{'...' if len(msg.content) > 100 else ''}\n\n"
            
            # Split if too long
            if len(history_text) > DISCORD_MAX_MESSAGE_LENGTH:
                chunks = self.bot._split_long_message(history_text)
                for chunk in chunks:
                    await ctx.send(chunk)
            else:
                await ctx.send(history_text)
                
        except Exception as e:
            await ctx.send(f"❌ Error retrieving history: {e}")
    
    @commands.command(name="clear_history")
    async def clear_history_command(self, ctx):
        """Clear user's conversation history"""
        try:
            user_id = str(ctx.author.id)
            sessions = await self.bot.session_manager.get_user_sessions(user_id)
            
            if not sessions:
                await ctx.send("📝 No conversation history to clear.")
                return
            
            # Clear all sessions for the user
            for session in sessions:
                await conversation_manager.clear_conversation(session.session_id)
            
            await ctx.send("🗑️ Your conversation history has been cleared successfully.")
            
        except Exception as e:
            await ctx.send(f"❌ Error clearing history: {e}")


async def setup_discord_bot(event_bus: EventBus, session_manager: SessionManager, 
                           token: str) -> FinancialDiscordBot:
    """
    Set up and return a configured Discord bot.
    
    Args:
        event_bus: Event bus for the bot
        session_manager: Session manager for user sessions
        token: Discord bot token
        
    Returns:
        FinancialDiscordBot: Configured Discord bot instance
    """
    try:
        # Create bot instance
        bot = FinancialDiscordBot(event_bus, session_manager)
        
        # Add commands cog
        await bot.add_cog(FinancialCommands(bot))
        
        # Initialize bot
        await bot.initialize()
        
        # Start the bot
        await bot.start(token)
        
        return bot
        
    except Exception as e:
        logging.error(f"Failed to setup Discord bot: {e}")
        raise DiscordBotError(f"Failed to setup Discord bot: {e}")

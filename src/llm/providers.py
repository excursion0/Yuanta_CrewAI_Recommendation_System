"""
LLM providers for the financial product recommendation system.

This module contains the base LLM provider interface and implementations
for Anthropic Claude (primary) and OpenAI (fallback).
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

import anthropic
import openai
from pydantic import BaseModel, Field

from src.data.models import FinancialProduct, UserProfile, ChatMessage

logger = logging.getLogger(__name__)


class LLMResponse(BaseModel):
    """Response from LLM provider"""
    content: str = Field(..., description="Generated response content")
    model: str = Field(..., description="Model used for generation")
    provider: str = Field(..., description="Provider name")
    tokens_used: Optional[int] = Field(None, description="Tokens used in generation")
    latency_ms: Optional[float] = Field(None, description="Response latency in milliseconds")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LLMProvider(ABC):
    """Base interface for LLM providers"""
    
    def __init__(self, api_key: str, model: str, **kwargs):
        self.api_key = api_key
        self.model = model
        self.kwargs = kwargs
        self._client = None
    
    @abstractmethod
    async def generate_response(
        self, 
        prompt: str, 
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate response from LLM"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is healthy"""
        pass
    
    @abstractmethod
    async def get_models(self) -> List[str]:
        """Get available models for this provider"""
        pass


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider implementation"""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.client = anthropic.Anthropic(api_key=api_key)
    
    async def generate_response(
        self, 
        prompt: str, 
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate response using Anthropic Claude"""
        start_time = datetime.now(timezone.utc)
        
        # Retry logic for overload errors
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Prepare system message if context is provided
                system_message = ""
                if context:
                    if "products" in context:
                        products_info = self._format_products_for_prompt(context["products"])
                        system_message += f"Available financial products:\n{products_info}\n\n"
                    
                    if "user_profile" in context:
                        user_info = self._format_user_profile_for_prompt(context["user_profile"])
                        system_message += f"User profile:\n{user_info}\n\n"
                    
                    if "conversation_history" in context:
                        history = self._format_conversation_history(context["conversation_history"])
                        system_message += f"Conversation history:\n{history}\n\n"
                
                # Add default system message for financial recommendations
                if not system_message:
                    system_message = """You are a financial product recommendation assistant. 
                    Provide helpful, accurate, and personalized financial product recommendations 
                    based on user queries and available products. Always consider risk tolerance, 
                    investment goals, and regulatory compliance."""
                
                # Prepare messages for Claude
                messages = []
                if system_message:
                    messages.append({
                        "role": "user",
                        "content": f"[System: {system_message}]\n\nUser query: {prompt}"
                    })
                else:
                    messages.append({
                        "role": "user", 
                        "content": prompt
                    })
                
                # Make API call with timeout and retry logic
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.client.messages.create,
                        model=self.model,
                        messages=messages,
                        max_tokens=4000,
                        temperature=0.7,
                        **kwargs
                    ),
                    timeout=30.0  # 30 second timeout
                )
                
                # Calculate latency
                end_time = datetime.now(timezone.utc)
                latency_ms = (end_time - start_time).total_seconds() * 1000
                
                # Extract response content
                content = response.content[0].text if response.content else ""
                
                return LLMResponse(
                    content=content,
                    model=self.model,
                    provider="anthropic",
                    tokens_used=getattr(response, 'usage', {}).get('total_tokens'),
                    latency_ms=latency_ms
                )
                
            except Exception as e:
                retry_count += 1
                error_msg = str(e)
                
                # Check if it's an overload error
                if "overloaded" in error_msg.lower() or "overload" in error_msg.lower():
                    logger.warning(f"Anthropic API overload detected (attempt {retry_count}/{max_retries})")
                    if retry_count < max_retries:
                        import time
                        time.sleep(2 ** retry_count)  # Exponential backoff
                        continue
                    else:
                        logger.error("Anthropic API overload after all retries")
                        raise e
                
                # Check if it's a timeout error
                elif "timeout" in error_msg.lower():
                    logger.warning(f"Anthropic API timeout (attempt {retry_count}/{max_retries})")
                    if retry_count < max_retries:
                        import time
                        time.sleep(1 * retry_count)  # Linear backoff
                        continue
                    else:
                        logger.error("Anthropic API timeout after all retries")
                        raise e
                
                # For other errors, don't retry
                else:
                    logger.error(f"Anthropic API error: {error_msg}")
                    raise e
    
    async def health_check(self) -> bool:
        """Check if Anthropic API is accessible"""
        try:
            # Simple health check by listing models
            models = await asyncio.to_thread(self.client.models.list)
            return True
        except Exception as e:
            logger.error(f"Anthropic health check failed: {e}")
            return False
    
    async def get_models(self) -> List[str]:
        """Get available Anthropic models"""
        try:
            models = await asyncio.to_thread(self.client.models.list)
            return [model.id for model in models.data]
        except Exception as e:
            logger.error(f"Failed to get Anthropic models: {e}")
            return ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-3-5-opus-20241022"]
    
    def _format_products_for_prompt(self, products: List[Any]) -> str:
        """Format products for prompt inclusion"""
        if not products:
            return "No products available"
        
        formatted = []
        for product in products:
            # Handle both FinancialProduct objects and dictionaries
            if isinstance(product, dict):
                name = product.get('name', 'Unknown Product')
                product_type = product.get('type', 'unknown')
                risk_level = product.get('risk_level', 'unknown')
                expected_return = product.get('expected_return', 'unknown')
                minimum_investment = product.get('minimum_investment', 0)
                expense_ratio = product.get('expense_ratio', 0)
            else:
                # Handle FinancialProduct objects
                name = product.name
                product_type = product.type
                risk_level = product.risk_level
                expected_return = product.expected_return
                minimum_investment = product.minimum_investment
                expense_ratio = product.expense_ratio or 0
            
            formatted.append(
                f"- {name} ({product_type}): "
                f"Risk: {risk_level}, "
                f"Expected Return: {expected_return}, "
                f"Min Investment: ${minimum_investment}, "
                f"Expense Ratio: {expense_ratio}%"
            )
        
        return "\n".join(formatted)
    
    def _format_user_profile_for_prompt(self, profile: UserProfile) -> str:
        """Format user profile for prompt inclusion"""
        return (
            f"User ID: {profile.user_id}\n"
            f"Risk Tolerance: {profile.risk_tolerance}\n"
            f"Investment Goals: {', '.join(profile.investment_goals)}\n"
            f"Time Horizon: {profile.time_horizon}\n"
            f"Preferred Products: {', '.join(profile.preferred_product_types)}"
        )
    
    def _format_conversation_history(self, history: List[Any]) -> str:
        """Format conversation history for prompt inclusion"""
        if not history:
            return "No conversation history"
        
        formatted = []
        for message in history[-5:]:  # Last 5 messages
            # Handle both ChatMessage and ConversationMessage objects
            if isinstance(message, dict):
                # Handle ConversationMessage (converted to dict)
                if "message_type" in message:
                    if message["message_type"] == "user_query":
                        role = "User"
                    elif message["message_type"] == "system_response":
                        role = "Assistant"
                    else:
                        role = "System"
                    content = message.get("content", "")
                # Handle ChatMessage (converted to dict)
                elif "role" in message:
                    role = "User" if message["role"] == "user" else "Assistant"
                    content = message.get("content", "")
                else:
                    continue
            else:
                # Handle actual objects
                if hasattr(message, "message_type"):
                    # ConversationMessage object
                    if message.message_type == "user_query":
                        role = "User"
                    elif message.message_type == "system_response":
                        role = "Assistant"
                    else:
                        role = "System"
                    content = message.content
                elif hasattr(message, "role"):
                    # ChatMessage object
                    role = "User" if message.role == "user" else "Assistant"
                    content = message.content
                else:
                    continue
            
            formatted.append(f"{role}: {content}")
        
        return "\n".join(formatted)


class OpenAIProvider(LLMProvider):
    """OpenAI provider implementation (fallback)"""
    
    def __init__(self, api_key: str, model: str = "gpt-4", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.client = openai.AsyncOpenAI(api_key=api_key)
    
    async def generate_response(
        self, 
        prompt: str, 
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate response using OpenAI"""
        start_time = datetime.now(timezone.utc)
        
        try:
            # Prepare system message
            system_message = """You are a financial product recommendation assistant. 
            Provide helpful, accurate, and personalized financial product recommendations 
            based on user queries and available products."""
            
            if context:
                if "products" in context:
                    products_info = self._format_products_for_prompt(context["products"])
                    system_message += f"\n\nAvailable financial products:\n{products_info}"
                
                if "user_profile" in context:
                    user_info = self._format_user_profile_for_prompt(context["user_profile"])
                    system_message += f"\n\nUser profile:\n{user_info}"
            
            # Prepare messages
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
            
            # Add conversation history if available
            if context and "conversation_history" in context:
                for message in context["conversation_history"][-5:]:  # Last 5 messages
                    messages.insert(-1, {
                        "role": message.role,
                        "content": message.content
                    })
            
            # Generate response
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 1000),
                temperature=kwargs.get("temperature", 0.7),
                **{k: v for k, v in kwargs.items() if k not in ["max_tokens", "temperature"]}
            )
            
            end_time = datetime.now(timezone.utc)
            latency_ms = (end_time - start_time).total_seconds() * 1000
            
            return LLMResponse(
                content=response.choices[0].message.content,
                model=self.model,
                provider="openai",
                tokens_used=response.usage.total_tokens if response.usage else None,
                latency_ms=latency_ms
            )
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check if OpenAI API is accessible"""
        try:
            # Simple health check by listing models
            await self.client.models.list()
            return True
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return False
    
    async def get_models(self) -> List[str]:
        """Get available OpenAI models"""
        try:
            models = await self.client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            logger.error(f"Failed to get OpenAI models: {e}")
            return ["gpt-4", "gpt-3.5-turbo"]
    
    def _format_products_for_prompt(self, products: List[Any]) -> str:
        """Format products for prompt inclusion"""
        if not products:
            return "No products available"
        
        formatted = []
        for product in products:
            # Handle both FinancialProduct objects and dictionaries
            if isinstance(product, dict):
                name = product.get('name', 'Unknown Product')
                product_type = product.get('type', 'unknown')
                risk_level = product.get('risk_level', 'unknown')
                expected_return = product.get('expected_return', 'unknown')
                minimum_investment = product.get('minimum_investment', 0)
                expense_ratio = product.get('expense_ratio', 0)
            else:
                # Handle FinancialProduct objects
                name = product.name
                product_type = product.type
                risk_level = product.risk_level
                expected_return = product.expected_return
                minimum_investment = product.minimum_investment
                expense_ratio = product.expense_ratio or 0
            
            formatted.append(
                f"- {name} ({product_type}): "
                f"Risk: {risk_level}, "
                f"Expected Return: {expected_return}, "
                f"Min Investment: ${minimum_investment}, "
                f"Expense Ratio: {expense_ratio}%"
            )
        
        return "\n".join(formatted)
    
    def _format_user_profile_for_prompt(self, profile: UserProfile) -> str:
        """Format user profile for prompt inclusion"""
        return (
            f"User ID: {profile.user_id}\n"
            f"Risk Tolerance: {profile.risk_tolerance}\n"
            f"Investment Goals: {', '.join(profile.investment_goals)}\n"
            f"Time Horizon: {profile.time_horizon}\n"
            f"Preferred Products: {', '.join(profile.preferred_product_types)}"
        ) 
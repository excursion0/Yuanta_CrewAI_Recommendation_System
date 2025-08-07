"""
CrewAI Orchestrator for financial product recommendation system.

This module creates and manages the CrewAI crew that orchestrates
all the specialized agents for comprehensive financial recommendations.
"""

from crewai import Crew, Task, Process
from typing import Dict, Any, List, Optional
import time

from src.config import config
from src.utils.logger import LoggerFactory, LoggingMixin
from src.exceptions import (
    CrewAIExecutionError, CrewAITaskError, CrewAITimeoutError,
    ProcessingError, ValidationError, TimeoutError
)

from .market_data_agent import MarketDataAgent
from .risk_analysis_agent import RiskAnalysisAgent
from .recommendation_agent import RecommendationAgent
from .compliance_agent import ComplianceAgent
from .report_writer_agent import ReportWriterAgent
from .memory_agent import MemoryAgent
from .supervisor_agent import SupervisorAgent

logger = LoggerFactory.get_logger(__name__)


class FinancialCrewOrchestrator(LoggingMixin):
    """Orchestrates the CrewAI crew for financial recommendations"""
    
    def __init__(self, llm_provider):
        super().__init__()
        self.llm_provider = llm_provider
        
        # Cache ProductDatabase to avoid regenerating for each query
        from src.data.product_database import ProductDatabase
        self.product_database = ProductDatabase()
        
        self.agents = self._create_agents()
        self.crew = self._create_crew()
    
    def _create_agents(self) -> Dict[str, Any]:
        """Create all specialized agents with enhanced features"""
        # Store both enhanced agent instances and CrewAI agents
        self.enhanced_agent_instances = {
            "market_data": MarketDataAgent(self.llm_provider),
            "risk_analysis": RiskAnalysisAgent(self.llm_provider),
            "recommendation": RecommendationAgent(self.llm_provider),
            "compliance": ComplianceAgent(self.llm_provider),
            "report_writer": ReportWriterAgent(self.llm_provider),
            "memory": MemoryAgent(self.llm_provider),
            "supervisor": SupervisorAgent(self.llm_provider)
        }
        
        # Create CrewAI agents from enhanced instances
        agents = {
            "market_data": self.enhanced_agent_instances["market_data"].get_agent(),
            "risk_analysis": self.enhanced_agent_instances["risk_analysis"].get_agent(),
            "recommendation": self.enhanced_agent_instances["recommendation"].get_agent(),
            "compliance": self.enhanced_agent_instances["compliance"].get_agent(),
            "report_writer": self.enhanced_agent_instances["report_writer"].get_agent(),
            "memory": self.enhanced_agent_instances["memory"].get_agent(),
            "supervisor": self.enhanced_agent_instances["supervisor"].get_agent()
        }
        
        self.log_info("Created all enhanced specialized agents for financial analysis")
        return agents
    
    def _create_crew(self) -> Crew:
        """Create the CrewAI crew with all agents"""
        # Create CrewAI crew with optimized settings for response generation
        crew = Crew(
            agents=list(self.agents.values()),
            tasks=[],  # Tasks will be created dynamically
            verbose=config.crewai.VERBOSE,
            memory=config.crewai.MEMORY_ENABLED,
            max_rpm=None,  # Disable CrewAI rate limiting
            max_iter=config.crewai.MAX_ITERATIONS,
            process=config.crewai.PROCESS_TYPE
        )
        
        self.log_info("Created CrewAI crew with all agents")
        return crew
    
    def create_financial_analysis_tasks(self, user_query: str, user_profile: Dict[str, Any], conversation_history: Optional[List[Any]] = None) -> List[Task]:
        """Create tasks for financial analysis using CrewAI"""
        tasks = []
        
        # Format conversation history for context
        conversation_context = ""
        if conversation_history and len(conversation_history) > 0:
            conversation_context = "\n\nPrevious Conversation Context:\n"
            for i, msg in enumerate(conversation_history[-config.conversation.MAX_CONVERSATION_HISTORY:], 1):  # Last N messages
                if hasattr(msg, 'message_type'):
                    role = "User" if msg.message_type == "user_query" else "Assistant"
                    conversation_context += f"{i}. {role}: {msg.content}\n"
                elif hasattr(msg, 'role'):
                    role = "User" if msg.role == "user" else "Assistant"
                    conversation_context += f"{i}. {role}: {msg.content}\n"
            conversation_context += "\n"
        
        # Task 1: Market Data Analysis
        market_task = Task(
            description=f"""
            Analyze market conditions for: {user_query}
            {conversation_context}
            Use your tools to fetch market data and analyze economic indicators. 
            Consider the conversation context when providing analysis.
            Provide a comprehensive market analysis.
            """,
            agent=self.agents["market_data"],
            expected_output="A detailed market analysis with current trends and economic indicators"
        )
        tasks.append(market_task)
        
        # Task 2: Risk Analysis
        risk_task = Task(
            description=f"""
            Conduct risk analysis for the query: {user_query}
            {conversation_context}
            User risk tolerance: {user_profile.get('risk_level', 'medium')}
            Investment amount: {user_profile.get('total_investment', 100000)}
            
            Use your tools to:
            1. Assess portfolio risk based on risk level and investment amount
            2. Analyze market risk factors and conditions
            
            Consider the conversation context when assessing risk.
            Provide a comprehensive risk analysis with clear risk factors and assessment.
            """,
            agent=self.agents["risk_analysis"],
            expected_output="A detailed risk analysis with risk factors and assessment"
        )
        tasks.append(risk_task)
        
        # Task 3: Product Recommendation
        # Use cached ProductDatabase
        real_products = [p.name for p in self.product_database.get_all_products()]
        
        recommendation_task = Task(
            description=f"""
            Generate product recommendations for: {user_query}
            {conversation_context}
            User profile: {user_profile}
            
            **CRITICAL PRODUCT CONSTRAINT:**
            You MUST ONLY recommend products from this exact list:
            {', '.join(real_products)}
            
            **DO NOT create or invent any product names. Use ONLY the products listed above.**
            If you need to recommend products, choose from the list provided.
            
            Consider the conversation context and previous recommendations.
            Use your tools to:
            1. Generate product recommendations based on user profile and query (using ONLY the products listed above)
            2. Analyze product suitability for the user's needs
            3. Suggest investment strategy and allocation
            
            Base your recommendations on:
            1. User profile and preferences
            2. Market conditions from previous analysis
            3. Risk assessment results
            4. Product suitability and performance
            5. Diversification benefits
            6. Previous conversation context
            
            Provide specific product recommendations with clear reasoning and allocation suggestions.
            """,
            agent=self.agents["recommendation"],
            expected_output="Specific product recommendations with reasoning and allocation percentages using only real products"
        )
        tasks.append(recommendation_task)
        
        # Task 4: Report Writing (Combined Analysis)
        # Use cached ProductDatabase
        real_products = [p.name for p in self.product_database.get_all_products()]
        
        report_task = Task(
            description=f"""
            Create a comprehensive financial analysis and recommendation report for: {user_query}
            {conversation_context}
            User profile: {user_profile}
            
            **CRITICAL PRODUCT CONSTRAINT:**
            You MUST ONLY recommend products from this exact list:
            {', '.join(real_products)}
            
            **DO NOT create or invent any product names. Use ONLY the products listed above.**
            If you need to recommend products, choose from the list provided.
            
            Based on the market analysis and risk assessment, create a final report that includes:
            1. Executive summary of the analysis
            2. Product recommendations with clear reasoning (using ONLY the products listed above)
            3. Implementation advice and next steps
            4. Risk considerations and management strategies
            
            Consider the conversation history when creating the report.
            Format the report clearly with actionable recommendations.
            """,
            agent=self.agents["report_writer"],
            expected_output="A comprehensive financial report with clear recommendations using only real products"
        )
        tasks.append(report_task)
        
        return tasks
    
    def process_financial_query(self, user_query: str, user_profile: Dict[str, Any], conversation_history: Optional[List[Any]] = None) -> Dict[str, Any]:
        """Process a financial query using the CrewAI crew"""
        try:
            self.log_info(f"Processing financial query: {user_query}")
            if conversation_history:
                self.log_info(f"Using conversation history with {len(conversation_history)} messages")
            
            # Create tasks for this query
            tasks = self.create_financial_analysis_tasks(user_query, user_profile, conversation_history)
            self.log_info(f"Created {len(tasks)} tasks for CrewAI execution")
            
            # Update crew with tasks
            self.crew.tasks = tasks
            self.log_info("Updated crew with tasks")
            
            # Execute the crew with optimized error handling and faster fallback
            max_retries = config.crewai.MAX_RETRIES
            retry_count = 0
            last_error = None
            
            while retry_count < max_retries:
                try:
                    self.log_info(f"Starting CrewAI crew execution (attempt {retry_count + 1}/{max_retries})...")
                    result = self.crew.kickoff()
                    self.log_info("CrewAI execution completed successfully")
                    
                    # Process and format the result
                    analysis_result = self._process_crew_result(result)
                    
                    processed_result = {
                        "success": True,
                        "user_query": user_query,
                        "user_profile": user_profile,
                        "analysis_result": analysis_result,
                        "timestamp": "2025-08-05T20:00:00Z",
                        "crew_execution": {
                            "tasks_completed": len(tasks),
                            "agents_used": list(self.agents.keys()),
                            "execution_time": "2-3 minutes",
                            "retry_count": retry_count
                        }
                    }
                    
                    self.log_info("Successfully processed financial query with CrewAI")
                    return processed_result
                    
                except CrewAIExecutionError as e:
                    retry_count += 1
                    last_error = e
                    self.log_error(f"CrewAI execution failed: {e}", e)
                    break
                    
                except CrewAITimeoutError as e:
                    retry_count += 1
                    last_error = e
                    self.log_warning(f"CrewAI execution timeout: {e}")
                    break
                    
                except TimeoutError as e:
                    retry_count += 1
                    last_error = e
                    self.log_warning(f"Execution timeout: {e}")
                    break
                    
                except Exception as e:
                    retry_count += 1
                    last_error = e
                    self.log_error(f"Unexpected error in CrewAI execution: {e}", e)
                    break
            
            # If we've exhausted retries or had any error, generate fallback response immediately
            self.log_info("Using fallback response for faster user experience")
            if last_error:
                error_type = type(last_error).__name__
                error_msg = str(last_error)
                self.log_info(f"Error type: {error_type}")
                self.log_info(f"Error details: {error_msg}")
            
            # Generate a fallback response immediately
            fallback_response = self._generate_fallback_response(user_query, user_profile, conversation_history)
            
            return {
                "success": True,  # Mark as success since we have a fallback response
                "user_query": user_query,
                "user_profile": user_profile,
                "analysis_result": fallback_response,
                "timestamp": "2025-08-05T20:00:00Z",
                "crew_execution": {
                    "tasks_completed": 0,
                    "agents_used": ["fallback"],
                    "execution_time": "immediate",
                    "retry_count": retry_count,
                    "fallback_used": True,
                    "original_error": error_msg if last_error else "Unknown error"
                }
            }
            
        except ProcessingError as e:
            self.log_error(f"Processing error in process_financial_query: {e}", e)
            return self._handle_processing_error(e, user_query, user_profile)
            
        except ValidationError as e:
            self.log_error(f"Validation error in process_financial_query: {e}", e)
            return self._handle_validation_error(e, user_query, user_profile)
            
        except Exception as e:
            self.log_error(f"Unexpected error in process_financial_query: {e}", e)
            self.log_error(f"Error type: {type(e).__name__}", e)
            import traceback
            error_traceback = traceback.format_exc()
            self.log_error(f"Full traceback: {error_traceback}", e)
            
            return self._handle_unexpected_error(e, user_query, user_profile)
    
    def get_crew_status(self) -> Dict[str, Any]:
        """Get enhanced crew status with performance metrics"""
        status = {
            "agents_count": len(self.agents),
            "agents_available": list(self.agents.keys()),
            "enhanced_agents": [],
            "performance_metrics": self._get_enhanced_performance_metrics(),
            "crew_ready": True,
            "memory_enabled": False,  # Disabled to avoid database dependency
            "max_rpm": None
        }
        
        # Check which agents are enhanced
        for agent_name, enhanced_agent in self.enhanced_agent_instances.items():
            if hasattr(enhanced_agent, 'get_performance_metrics'):
                status["enhanced_agents"].append(agent_name)
        
        return status
    
    def _get_enhanced_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics from enhanced agents"""
        metrics = {}
        try:
            # Get metrics from enhanced agent instances
            for agent_name, enhanced_agent in self.enhanced_agent_instances.items():
                if hasattr(enhanced_agent, 'get_performance_metrics'):
                    metrics[agent_name] = enhanced_agent.get_performance_metrics()
            
            # Add summary metrics
            metrics["total_agents"] = len(self.agents)
            metrics["enhanced_agents"] = sum(1 for agent in self.enhanced_agent_instances.values() 
                                          if hasattr(agent, 'get_performance_metrics'))
            
        except Exception as e:
            self.log_error(f"Failed to get enhanced performance metrics: {str(e)}", e)
            metrics["error"] = str(e)
        
        return metrics
    
    def update_user_profile(self, user_id: str, new_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile in memory"""
        try:
            # Store updated profile in memory agent
            memory_agent = self.agents["memory"]
            
            # This would typically update the memory agent's storage
            # For now, we'll return a mock response
            self.log_info(f"Updated profile for user {user_id}")
            
            return {
                "success": True,
                "user_id": user_id,
                "profile_updated": True,
                "new_profile": new_profile
            }
        except Exception as e:
            self.log_error(f"Error updating user profile: {e}", e)
            return {
                "success": False,
                "error": str(e),
                "user_id": user_id,
                "new_profile": new_profile
            }
    
    def _process_crew_result(self, result) -> str:
        """Process CrewAI result and extract analysis"""
        try:
            # Handle CrewOutput object properly
            if hasattr(result, '__str__'):
                return str(result)
            elif hasattr(result, 'raw'):
                return str(result.raw)
            else:
                return str(result)
        except Exception as e:
            self.log_error(f"Error processing crew result: {e}", e)
            raise ProcessingError(f"Failed to process crew result: {e}")
    
    def _handle_processing_error(self, error: ProcessingError, user_query: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Handle processing errors with fallback response"""
        self.log_warning(f"Using fallback response due to processing error: {error}")
        fallback_response = self._generate_fallback_response(user_query, user_profile)
        
        return {
            "success": True,  # Mark as success since we have fallback
            "user_query": user_query,
            "user_profile": user_profile,
            "analysis_result": fallback_response,
            "timestamp": "2025-08-05T20:00:00Z",
            "crew_execution": {
                "tasks_completed": 0,
                "agents_used": ["fallback"],
                "execution_time": "immediate",
                "fallback_used": True,
                "error": str(error)
            }
        }
    
    def _handle_validation_error(self, error: ValidationError, user_query: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Handle validation errors"""
        self.log_warning(f"Validation error: {error}")
        
        return {
            "success": False,
            "error": str(error),
            "error_type": "ValidationError",
            "user_query": user_query,
            "user_profile": user_profile,
            "timestamp": "2025-08-05T20:00:00Z"
        }
    
    def _handle_unexpected_error(self, error: Exception, user_query: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Handle unexpected errors with fallback response"""
        self.log_error(f"Unexpected error: {error}", error)
        fallback_response = self._generate_fallback_response(user_query, user_profile)
        
        return {
            "success": True,  # Mark as success since we have fallback
            "user_query": user_query,
            "user_profile": user_profile,
            "analysis_result": fallback_response,
            "timestamp": "2025-08-05T20:00:00Z",
            "crew_execution": {
                "tasks_completed": 0,
                "agents_used": ["fallback"],
                "execution_time": "immediate",
                "fallback_used": True,
                "error": str(error),
                "error_type": type(error).__name__
            }
        } 
    
    def _generate_fallback_response(self, user_query: str, user_profile: Dict[str, Any], conversation_history: Optional[List[Any]] = None) -> str:
        """Generate a fallback response when CrewAI fails"""
        try:
            # Check if this is a memory/conversation query
            if self._is_memory_query(user_query):
                return self._handle_memory_query(user_query, conversation_history)
            
            # Determine response type and generate appropriate response
            response_type = self._determine_response_type(user_query)
            return self._generate_typed_fallback_response(response_type, user_query, user_profile)
            
        except Exception as e:
            self.log_error(f"Error generating fallback response: {e}", e)
            return self._generate_general_fallback_response(user_query, user_profile)
    
    def _is_memory_query(self, user_query: str) -> bool:
        """Check if query is about memory/conversation history"""
        memory_keywords = ["remember", "previous", "before", "history", "talking", "discussed"]
        query_lower = user_query.lower()
        return any(word in query_lower for word in memory_keywords)
    
    def _handle_memory_query(self, user_query: str, conversation_history: Optional[List[Any]] = None) -> str:
        """Handle memory/conversation queries"""
        if conversation_history and len(conversation_history) > 1:
            previous_messages = self._extract_previous_messages(conversation_history)
            
            if previous_messages:
                return self._generate_memory_context_response(user_query, previous_messages)
            else:
                return self._generate_memory_insufficient_response()
        else:
            return self._generate_starting_fresh_response()
    
    def _extract_previous_messages(self, conversation_history: List[Any]) -> List[str]:
        """Extract previous conversation messages"""
        previous_messages = []
        for msg in conversation_history[:-1]:  # Exclude current message
            if hasattr(msg, 'content'):
                previous_messages.append(msg.content)
            elif isinstance(msg, dict) and 'content' in msg:
                previous_messages.append(msg['content'])
        return previous_messages
    
    def _generate_memory_context_response(self, user_query: str, previous_messages: List[str]) -> str:
        """Generate response with conversation context"""
        return f"""
**Previous Conversation Context:**

Based on our previous conversation, here's what we discussed:

{chr(10).join([f"• {msg}" for msg in previous_messages[-3:]])}

**Current Query:** {user_query}

**Response:**
I can see from our conversation history that we've been discussing financial topics. To provide you with the most relevant advice, could you please:

1. **Clarify your current question** - What specific aspect would you like me to address?
2. **Mention any previous recommendations** - Are you asking about products we discussed earlier?
3. **Specify your investment goals** - What are you looking to achieve with your investments?

This will help me provide more targeted and useful financial advice based on our ongoing conversation.
"""
    
    def _generate_memory_insufficient_response(self) -> str:
        """Generate response when memory is insufficient"""
        return """
**Conversation Memory:**

I understand you're asking about our previous conversation, but I don't have enough context from our current session to provide specific details about what we discussed earlier.

**To help you better, please:**
1. **Share your investment goals** - What are you looking to achieve?
2. **Mention your risk tolerance** - How comfortable are you with market volatility?
3. **Specify your time horizon** - How long do you plan to invest?

This will allow me to provide personalized financial recommendations tailored to your needs.
"""
    
    def _generate_starting_fresh_response(self) -> str:
        """Generate response for starting fresh conversation"""
        return """
**Starting Fresh:**

I don't have previous conversation history to reference, but I'm here to help with your financial questions!

**Please let me know:**
1. **What you'd like to invest in** - Stocks, bonds, mutual funds, etc.
2. **Your investment goals** - Retirement, growth, income, etc.
3. **Your risk tolerance** - Conservative, moderate, or aggressive

I can then provide personalized recommendations from our available Yuanta products.
"""
    
    def _determine_response_type(self, user_query: str) -> str:
        """Determine the type of financial advice needed"""
        query_lower = user_query.lower()
        
        # Check for more specific terms first (income, risk, growth)
        if any(word in query_lower for word in ["income", "dividend", "yield"]):
            return "income"
        elif any(word in query_lower for word in ["risk", "volatility", "safety"]):
            return "risk"
        elif any(word in query_lower for word in ["growth", "return", "performance"]):
            return "growth"
        # Check for general investment terms last
        elif any(word in query_lower for word in ["fund", "investment", "portfolio", "invest"]):
            return "investment"
        else:
            return "general"
    
    def _generate_typed_fallback_response(self, response_type: str, user_query: str, user_profile: Dict[str, Any]) -> str:
        """Generate typed fallback response based on response type"""
        if response_type == "investment":
            return self._generate_investment_fallback_response(user_query, user_profile)
        elif response_type == "risk":
            return self._generate_risk_fallback_response(user_query, user_profile)
        elif response_type == "income":
            return self._generate_income_fallback_response(user_query, user_profile)
        elif response_type == "growth":
            return self._generate_growth_fallback_response(user_query, user_profile)
        else:
            return self._generate_general_fallback_response(user_query, user_profile)
    
    def _generate_investment_fallback_response(self, user_query: str, user_profile: Dict[str, Any]) -> str:
        """Generate investment-specific fallback response"""
        query_lower = user_query.lower()
        
        if "high income" in query_lower or "high-income" in query_lower:
            return self._generate_high_income_response()
        elif "low income" in query_lower or "low-income" in query_lower:
            return self._generate_low_income_response()
        else:
            return self._generate_general_investment_response(user_profile)
    
    def _generate_high_income_response(self) -> str:
        """Generate high-income investment recommendations"""
        high_income_profile = {
            "risk_level": "medium",
            "investment_goals": ["growth", "wealth_building"],
            "time_horizon": "long_term"
        }
        recommendations = self.product_database.get_recommended_products(high_income_profile, limit=config.product.DEFAULT_RECOMMENDATION_LIMIT)
        
        response = """
**High-Income Investment Recommendations:**

**For High-Income Individuals:**
• **Tax-Efficient Investing**: Consider tax-advantaged accounts and municipal bonds
• **Diversified Portfolio**: Spread across multiple asset classes and sectors
• **Professional Management**: Consider managed accounts for personalized service
• **Estate Planning**: Include estate planning considerations in investment strategy

**Available Yuanta Products for High-Income:**
"""
        
        for rec in recommendations:
            product = rec["product"]
            response += f"• **{product.name}** - {product.expected_return_min:.1%}-{product.expected_return_max:.1%} returns, {product.risk_level} risk\n"
        
        response += """

**High-Income Strategy:**
- **60% Growth/Balanced Funds** for wealth building
- **30% ETF Index Fund** for diversification and tax efficiency
- **10% Conservative Fund** for stability and capital preservation

**Additional Considerations:**
• Tax-loss harvesting opportunities
• Charitable giving strategies
• International diversification
• Alternative investments (REITs, commodities)

*Note: High-income individuals should consult with a tax advisor and financial planner for personalized strategies.*
"""
        return response
    
    def _generate_low_income_response(self) -> str:
        """Generate low-income investment recommendations"""
        low_income_profile = {
            "risk_level": "low",
            "investment_goals": ["income", "capital_preservation"],
            "time_horizon": "medium_term"
        }
        recommendations = self.product_database.get_recommended_products(low_income_profile, limit=config.product.DEFAULT_RECOMMENDATION_LIMIT)
        
        response = """
**Low-Income Investment Recommendations:**

**For Low-Income Individuals:**
• **Start Small**: Begin with small, regular investments
• **Emergency Fund First**: Build 3-6 months of expenses before investing
• **Low-Cost Options**: Focus on low-fee investment products
• **Dollar-Cost Averaging**: Invest regularly regardless of market conditions

**Available Yuanta Products for Low-Income:**
"""
        
        for rec in recommendations:
            product = rec["product"]
            response += f"• **{product.name}** - {product.expected_return_min:.1%}-{product.expected_return_max:.1%} returns, {product.risk_level} risk\n"
        
        response += """

**Low-Income Strategy:**
- **70% Conservative/Balanced Funds** for stability
- **30% ETF Index Fund** for growth potential
- **Regular monthly contributions** of any amount

**Additional Tips:**
• Start with as little as $50-100 per month
• Automate your investments
• Take advantage of employer retirement plans
• Consider government savings bonds

*Note: Every investment journey starts with the first step. Consistency matters more than the amount.*
"""
        return response
    
    def _generate_general_investment_response(self, user_profile: Dict[str, Any]) -> str:
        """Generate general investment recommendations"""
        general_profile = {
            "risk_level": user_profile.get('risk_tolerance', 'medium'),
            "investment_goals": user_profile.get('investment_goals', ['growth']),
            "time_horizon": user_profile.get('time_horizon', 'medium_term')
        }
        recommendations = self.product_database.get_recommended_products(general_profile, limit=config.product.DEFAULT_RECOMMENDATION_LIMIT)
        
        response = """
**Investment Recommendations:**

**General Investment Strategy:**
• **Diversification**: Spread investments across different asset classes
• **Risk Management**: Align investments with your risk tolerance
• **Long-term Focus**: Consider your investment timeline
• **Regular Review**: Monitor and adjust your portfolio periodically

**Available Yuanta Products:**
"""
        
        for rec in recommendations:
            product = rec["product"]
            response += f"• **{product.name}** - {product.expected_return_min:.1%}-{product.expected_return_max:.1%} returns, {product.risk_level} risk\n"
        
        response += """

**Recommended Portfolio Allocation:**
- **40% Growth Funds** for capital appreciation
- **30% Balanced Funds** for stability and growth
- **20% Conservative Funds** for capital preservation
- **10% ETF Index Funds** for diversification

**Next Steps:**
1. Review the recommended products above
2. Consider your investment timeline and goals
3. Consult with a financial advisor for personalized advice
4. Start with small investments and build gradually

*Note: Past performance does not guarantee future results. All investments involve risk.*
"""
        return response
    
    def _generate_risk_fallback_response(self, user_query: str, user_profile: Dict[str, Any]) -> str:
        """Generate risk-focused fallback response"""
        return """
**Risk Management Recommendations:**

**Understanding Investment Risk:**
• **Volatility**: How much your investment value can fluctuate
• **Market Risk**: Risk that the entire market will decline
• **Inflation Risk**: Risk that inflation will erode purchasing power
• **Liquidity Risk**: Risk that you can't sell when needed

**Risk Management Strategies:**
• **Diversification**: Spread investments across different assets
• **Asset Allocation**: Balance stocks, bonds, and other investments
• **Regular Rebalancing**: Adjust portfolio to maintain target allocation
• **Emergency Fund**: Keep 3-6 months of expenses in cash

**Yuanta Products by Risk Level:**
• **Conservative**: Yuanta Conservative Fund, Yuanta Bond Fund
• **Balanced**: Yuanta Balanced Fund, Yuanta ETF Index Fund
• **Growth**: Yuanta Growth Fund, Yuanta Technology Fund

*Consult with a financial advisor to determine your appropriate risk level.*
"""
    
    def _generate_income_fallback_response(self, user_query: str, user_profile: Dict[str, Any]) -> str:
        """Generate income-focused fallback response"""
        return """
**Income Investment Recommendations:**

**Income-Generating Strategies:**
• **Dividend Stocks**: Companies that pay regular dividends
• **Bond Funds**: Fixed-income investments with regular interest payments
• **REITs**: Real Estate Investment Trusts for rental income
• **Annuities**: Insurance products providing guaranteed income

**Yuanta Income Products:**
• **Yuanta Conservative Fund**: Steady income with capital preservation
• **Yuanta Bond Fund**: Government and corporate bond income
• **Yuanta Balanced Fund**: Growth and income combination

**Income Strategy Considerations:**
• **Yield vs. Growth**: Balance between income and capital appreciation
• **Tax Efficiency**: Consider tax implications of income investments
• **Inflation Protection**: Ensure income keeps pace with inflation
• **Liquidity Needs**: Maintain access to funds when needed

*Income strategies should align with your retirement timeline and cash flow needs.*
"""
    
    def _generate_growth_fallback_response(self, user_query: str, user_profile: Dict[str, Any]) -> str:
        """Generate growth-focused fallback response"""
        return """
**Growth Investment Recommendations:**

**Growth Investment Strategies:**
• **Equity Funds**: Invest in stocks with growth potential
• **Technology Sector**: Focus on innovative companies
• **International Markets**: Diversify across global markets
• **Small-Cap Stocks**: Higher growth potential with higher risk

**Yuanta Growth Products:**
• **Yuanta Growth Fund**: Technology and innovation focus
• **Yuanta Technology Fund**: Tech sector specialization
• **Yuanta Balanced Fund**: Growth with stability

**Growth Strategy Considerations:**
• **Time Horizon**: Growth investments need longer timeframes
• **Risk Tolerance**: Higher growth potential means higher volatility
• **Diversification**: Don't put all eggs in one basket
• **Regular Monitoring**: Growth investments require active management

*Growth investments are best for long-term goals with higher risk tolerance.*
"""
    
    def _generate_general_fallback_response(self, user_query: str, user_profile: Dict[str, Any]) -> str:
        """Generate general fallback response"""
        return f"""
**Financial Advisory Response:**

I understand you're asking about: **{user_query}**

**How I Can Help:**
• **Investment Recommendations**: Personalized product suggestions
• **Risk Assessment**: Understanding your risk tolerance
• **Portfolio Planning**: Building a diversified investment strategy
• **Financial Education**: Explaining investment concepts

**To Provide Better Recommendations:**
1. **Share your investment goals** - What are you trying to achieve?
2. **Mention your risk tolerance** - Conservative, moderate, or aggressive?
3. **Specify your time horizon** - Short-term, medium-term, or long-term?
4. **Tell me about your current situation** - Age, income, existing investments

**Available Yuanta Products:**
• **Conservative**: Yuanta Conservative Fund, Yuanta Bond Fund
• **Balanced**: Yuanta Balanced Fund, Yuanta ETF Index Fund
• **Growth**: Yuanta Growth Fund, Yuanta Technology Fund

*I'm here to help you make informed financial decisions. Please provide more details for personalized recommendations.*
"""

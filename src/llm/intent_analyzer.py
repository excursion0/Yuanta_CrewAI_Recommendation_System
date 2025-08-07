"""
Intent analysis for financial product recommendation system.

This module analyzes user queries to determine intent and extract relevant
information for financial product recommendations.
"""

import logging
from typing import Dict, Any, List, Optional
from enum import Enum
from pydantic import BaseModel, Field

from .providers import LLMProvider, LLMResponse

logger = logging.getLogger(__name__)


class IntentType(str, Enum):
    """Types of user intents"""
    PRODUCT_RECOMMENDATION = "product_recommendation"
    PRODUCT_COMPARISON = "product_comparison"
    RISK_ASSESSMENT = "risk_assessment"
    INVESTMENT_GOALS = "investment_goals"
    PORTFOLIO_REVIEW = "portfolio_review"
    GENERAL_QUESTION = "general_question"
    UNKNOWN = "unknown"


class RiskLevel(str, Enum):
    """Risk levels for financial products"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class InvestmentGoal(str, Enum):
    """Common investment goals"""
    RETIREMENT = "retirement"
    EDUCATION = "education"
    HOME_PURCHASE = "home_purchase"
    EMERGENCY_FUND = "emergency_fund"
    WEALTH_BUILDING = "wealth_building"
    INCOME_GENERATION = "income_generation"
    TAX_EFFICIENCY = "tax_efficiency"


class ExtractedIntent(BaseModel):
    """Extracted intent from user query"""
    intent_type: IntentType = Field(..., description="Primary intent type")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    risk_tolerance: Optional[RiskLevel] = Field(None, description="Extracted risk tolerance")
    investment_goals: List[InvestmentGoal] = Field(default_factory=list, description="Extracted investment goals")
    investment_horizon: Optional[str] = Field(None, description="Investment time horizon")
    preferred_product_types: List[str] = Field(default_factory=list, description="Preferred product types")
    budget_range: Optional[Dict[str, float]] = Field(None, description="Budget range (min, max)")
    keywords: List[str] = Field(default_factory=list, description="Extracted keywords")
    entities: Dict[str, Any] = Field(default_factory=dict, description="Extracted entities")


class IntentAnalyzer:
    """Analyzes user queries to determine intent and extract information"""
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
    
    async def analyze_intent(self, query: str, context: Optional[Dict[str, Any]] = None) -> ExtractedIntent:
        """Analyze user query to determine intent and extract information"""
        try:
            # Create analysis prompt
            analysis_prompt = self._create_analysis_prompt(query)
            
            # Generate analysis using LLM
            response = await self.llm_provider.generate_response(
                prompt=analysis_prompt,
                context=context,
                temperature=0.3,  # Lower temperature for more consistent analysis
                max_tokens=500
            )
            
            # Parse the response to extract intent
            extracted_intent = self._parse_analysis_response(response.content, query)
            
            return extracted_intent
            
        except Exception as e:
            logger.error(f"Intent analysis failed: {e}")
            # Return default intent on failure
            return ExtractedIntent(
                intent_type=IntentType.UNKNOWN,
                confidence=0.0,
                keywords=self._extract_basic_keywords(query)
            )
    
    def _create_analysis_prompt(self, query: str) -> str:
        """Create prompt for intent analysis"""
        return f"""
Analyze the following user query for financial product recommendations and extract intent information.

Query: "{query}"

Please analyze this query and provide a structured response in the following format:

INTENT_TYPE: [product_recommendation|product_comparison|risk_assessment|investment_goals|portfolio_review|general_question|unknown]
CONFIDENCE: [0.0-1.0]
RISK_TOLERANCE: [low|medium|high|null]
INVESTMENT_GOALS: [retirement,education,home_purchase,emergency_fund,wealth_building,income_generation,tax_efficiency]
INVESTMENT_HORIZON: [short_term|medium_term|long_term|null]
PREFERRED_PRODUCTS: [mutual_fund,etf,bond,stock,real_estate,commodity]
BUDGET_MIN: [amount or null]
BUDGET_MAX: [amount or null]
KEYWORDS: [comma-separated keywords]
ENTITIES: [any specific entities mentioned]

Focus on:
1. What type of financial product or service the user is looking for
2. Their risk tolerance level
3. Investment goals and time horizon
4. Budget constraints
5. Specific product preferences
6. Any entities like company names, product names, etc.

Provide only the structured response, no additional text.
"""
    
    def _parse_analysis_response(self, response: str, original_query: str) -> ExtractedIntent:
        """Parse LLM response to extract intent information"""
        try:
            lines = response.strip().split('\n')
            parsed_data = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().upper()
                    value = value.strip()
                    parsed_data[key] = value
            
            # Extract intent type
            intent_type_str = parsed_data.get('INTENT_TYPE', 'unknown').lower()
            intent_type = IntentType.UNKNOWN
            for intent in IntentType:
                if intent.value in intent_type_str:
                    intent_type = intent
                    break
            
            # Extract confidence
            confidence = float(parsed_data.get('CONFIDENCE', '0.0'))
            
            # Extract risk tolerance
            risk_str = parsed_data.get('RISK_TOLERANCE', '').lower()
            risk_tolerance = None
            if risk_str in ['low', 'medium', 'high']:
                risk_tolerance = RiskLevel(risk_str)
            
            # Extract investment goals
            goals_str = parsed_data.get('INVESTMENT_GOALS', '')
            investment_goals = []
            if goals_str and goals_str != 'null':
                for goal in goals_str.split(','):
                    goal = goal.strip().lower()
                    for enum_goal in InvestmentGoal:
                        if enum_goal.value in goal:
                            investment_goals.append(enum_goal)
                            break
            
            # Extract investment horizon
            horizon = parsed_data.get('INVESTMENT_HORIZON', None)
            if horizon == 'null':
                horizon = None
            
            # Extract preferred products
            products_str = parsed_data.get('PREFERRED_PRODUCTS', '')
            preferred_products = []
            if products_str and products_str != 'null':
                preferred_products = [p.strip().lower() for p in products_str.split(',')]
            
            # Extract budget range
            budget_min = parsed_data.get('BUDGET_MIN', 'null')
            budget_max = parsed_data.get('BUDGET_MAX', 'null')
            budget_range = None
            if budget_min != 'null' or budget_max != 'null':
                try:
                    min_val = float(budget_min) if budget_min != 'null' else None
                    max_val = float(budget_max) if budget_max != 'null' else None
                    budget_range = {'min': min_val, 'max': max_val}
                except ValueError:
                    pass
            
            # Extract keywords
            keywords_str = parsed_data.get('KEYWORDS', '')
            keywords = []
            if keywords_str:
                keywords = [k.strip().lower() for k in keywords_str.split(',')]
            
            # Extract entities
            entities_str = parsed_data.get('ENTITIES', '')
            entities = {}
            if entities_str and entities_str != 'null':
                # Simple entity extraction - could be enhanced
                entities = {'mentioned_entities': entities_str}
            
            return ExtractedIntent(
                intent_type=intent_type,
                confidence=confidence,
                risk_tolerance=risk_tolerance,
                investment_goals=investment_goals,
                investment_horizon=horizon,
                preferred_product_types=preferred_products,
                budget_range=budget_range,
                keywords=keywords,
                entities=entities
            )
            
        except Exception as e:
            logger.error(f"Failed to parse analysis response: {e}")
            return ExtractedIntent(
                intent_type=IntentType.UNKNOWN,
                confidence=0.0,
                keywords=self._extract_basic_keywords(original_query)
            )
    
    def _extract_basic_keywords(self, query: str) -> List[str]:
        """Extract basic keywords from query as fallback"""
        # Simple keyword extraction
        keywords = []
        query_lower = query.lower()
        
        # Financial product keywords
        product_keywords = ['fund', 'etf', 'bond', 'stock', 'mutual', 'investment', 'portfolio']
        for keyword in product_keywords:
            if keyword in query_lower:
                keywords.append(keyword)
        
        # Risk keywords
        risk_keywords = ['risk', 'safe', 'conservative', 'aggressive', 'volatile']
        for keyword in risk_keywords:
            if keyword in query_lower:
                keywords.append(keyword)
        
        # Goal keywords
        goal_keywords = ['retirement', 'education', 'house', 'home', 'emergency', 'income']
        for keyword in goal_keywords:
            if keyword in query_lower:
                keywords.append(keyword)
        
        # If no specific keywords found, add general investment terms
        if not keywords:
            general_keywords = ['invest', 'money', 'save', 'financial']
            for keyword in general_keywords:
                if keyword in query_lower:
                    keywords.append(keyword)
        
        return keywords
    
    async def validate_intent(self, intent: ExtractedIntent) -> bool:
        """Validate extracted intent for consistency"""
        # Basic validation rules
        if intent.confidence < 0.3:
            return False
        
        if intent.intent_type == IntentType.UNKNOWN:
            return False
        
        # Check for conflicting information
        if intent.risk_tolerance == RiskLevel.LOW and 'aggressive' in intent.keywords:
            return False
        
        return True 
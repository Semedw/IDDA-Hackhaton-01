"""
AI utility functions for OpenAI/Groq integration
"""
import os
from openai import OpenAI
from django.conf import settings

# Initialize client lazily to avoid errors at import time
client = None
api_provider = None  # 'openai' or 'groq'

def get_client():
    """Get or create OpenAI/Groq client"""
    global client, api_provider
    api_key = settings.OPENAI_API_KEY
    
    if not api_key:
        return None
    
    # Detect provider based on API key prefix
    current_provider = 'groq' if api_key.startswith('gsk_') else 'openai'
    
    # Always reinitialize to pick up new keys
    try:
        api_provider = current_provider
        if api_provider == 'groq':
            # Groq API
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1"
            )
        else:
            # OpenAI API
            client = OpenAI(api_key=api_key)
    except Exception as e:
        print(f"Error initializing AI client: {e}")
        client = False  # Mark as failed
        api_provider = None
    return client if client else None

def get_model():
    """Get the appropriate model based on provider"""
    global api_provider
    # Ensure client is initialized to set api_provider
    get_client()
    if api_provider == 'groq':
        return "llama-3.3-70b-versatile"  # Groq's current model
    else:
        return "gpt-3.5-turbo"  # OpenAI model


def ai_analyze_text(text: str) -> dict:
    """
    Analyze text and return summary, sentiment, and risk rating
    """
    client = get_client()
    if not client:
        return {
            'summary': 'AI analysis unavailable. Please configure OPENAI_API_KEY.',
            'sentiment': 'neutral',
            'risk_rating': 'medium'
        }

    prompt = f"""Analyze the following financial information and provide:
1. A concise summary (2-3 sentences)
2. Sentiment: positive, neutral, or negative
3. Risk rating: low, medium, or high

Information:
{text}

Respond in JSON format:
{{
    "summary": "...",
    "sentiment": "positive|neutral|negative",
    "risk_rating": "low|medium|high"
}}"""

    try:
        model = get_model()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a financial analyst. Provide objective analysis in JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            response_format={"type": "json_object"} if api_provider == 'openai' else None
        )
        
        import json
        content = response.choices[0].message.content
        # Try to parse JSON, handle if it's not valid JSON (Groq sometimes returns text)
        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            # If not JSON, try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                # Fallback: create a basic structure
                result = {
                    'summary': content[:200] if len(content) > 200 else content,
                    'sentiment': 'neutral',
                    'risk_rating': 'medium'
                }
        return result
    except Exception as e:
        return {
            'summary': f'Analysis error: {str(e)}',
            'sentiment': 'neutral',
            'risk_rating': 'medium'
        }


def ai_chat(prompt: str, context: dict = None) -> str:
    """
    Chat with AI about assets and market data
    """
    client = get_client()
    if not client:
        return "AI chat is unavailable. Please configure OPENAI_API_KEY."

    system_prompt = "You are a helpful financial assistant. Answer questions about stocks, cryptocurrencies, and market analysis. Always remind users that your advice is not financial advice."
    
    if context:
        context_str = f"\n\nContext:\n- Tracked assets: {context.get('assets', [])}\n- User budget: ${context.get('budget', 0)}\n- Risk profile: {context.get('risk_profile', 'moderate')}"
        system_prompt += context_str

    try:
        model = get_model()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"


def ai_generate_recommendations(assets: list, budget: float, risk_profile: str) -> dict:
    """
    Generate investment recommendations based on assets, budget, and risk profile
    """
    client = get_client()
    if not client:
        return {
            'recommendations': [],
            'disclaimer': 'AI recommendations unavailable. Please configure OPENAI_API_KEY.'
        }

    assets_str = ', '.join([f"{a['symbol']} ({a['name']})" for a in assets])
    
    prompt = f"""Given the following information, provide investment recommendations:

User Budget: ${budget}
Risk Profile: {risk_profile}
Tracked Assets: {assets_str}

For each asset, provide:
- Action: BUY, HOLD, or SELL
- Recommended amount (as percentage of budget)
- Rationale (1-2 sentences)
- Confidence level: low, medium, or high

Respond in JSON format:
{{
    "recommendations": [
        {{
            "asset_symbol": "...",
            "action": "BUY|HOLD|SELL",
            "amount_percentage": 0-100,
            "rationale": "...",
            "confidence": "low|medium|high"
        }}
    ],
    "disclaimer": "This is not financial advice. Always do your own research."
}}"""

    try:
        model = get_model()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a financial advisor. Provide balanced, conservative recommendations. Respond ONLY with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            response_format={"type": "json_object"} if api_provider == 'openai' else None
        )
        
        import json
        content = response.choices[0].message.content
        # Try to parse JSON, handle if it's not valid JSON
        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            # If not JSON, try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                # Fallback: create a basic structure
                result = {
                    'recommendations': [],
                    'disclaimer': 'Error parsing AI response. Please try again.'
                }
        return result
    except Exception as e:
        return {
            'recommendations': [],
            'disclaimer': f'Error generating recommendations: {str(e)}'
        }


import requests
import json
from typing import List, Dict, Any
from duckduckgo_search import DDGS
import config

OLLAMA_URL = config.OLLAMA_URL
MODEL = config.AI_MODEL

class AIService:
    @staticmethod
    def search_web(query: str) -> str:
        try:
            with DDGS() as ddgs:
                results = [r for r in ddgs.text(query, max_results=3)]
                return "\n".join([f"{r['title']}: {r['body']}" for r in results])
        except Exception as e:
            return ""

    @staticmethod
    def chat(message: str, history: List[Dict[str, str]] = None) -> str:
        search_keywords = ["price", "news", "today", "current", "market"]
        context = ""
        if any(word in message.lower() for word in search_keywords):
            search_data = AIService.search_web(message)
            if search_data:
                context = f"\nReal-time Data: {search_data}"

        prompt = f"""You are a professional Indian Stock Market Expert.
Analyze the following stock: {message}
{context}

Provide a point-wise report with:
1. PROS (2-3 solid points)
2. CONS (2-3 potential risks)
3. Technical Sentiment (Current trend)
4. Investment Verdict (Buy/Hold/Sell)

Use professional, concise language.
"""
        
        try:
            resp = requests.post(OLLAMA_URL, json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 500,
                    "num_thread": 4
                }
            }, timeout=60)
            resp.raise_for_status()
            return resp.json().get("response", "Could not generate response.")
        except Exception as e:
            return f"AI Logic Error: {str(e)}"

    @staticmethod
    def summarize_portfolio(holdings: List[Dict[str, Any]]) -> str:
        if not holdings:
            return "No active holdings found."
        
        portfolio_summary = "\n".join([
            f"- {h['tradingsymbol']}: Qty {h['quantity']}, Avg Price {h['averageprice']}, LTP {h.get('ltp', 0)}, P&L {h.get('pnlpercentage', 0)}%"
            for h in holdings
        ])
        
        prompt = f"""You are Insight_Engine, a financial expert AI. 
Analyze the following portfolio and provide a concise summary, key risks, and 1-2 suggestions.
The user wants a professional and encouraging tone.

Portfolio Holdings:
{portfolio_summary}

Provide your summary in markdown format.
"""
        
        try:
            resp = requests.post(OLLAMA_URL, json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            }, timeout=60)
            resp.raise_for_status()
            return resp.json().get("response", "Could not generate summary.")
        except Exception as e:
            return f"AI Summarization Error: {str(e)}"

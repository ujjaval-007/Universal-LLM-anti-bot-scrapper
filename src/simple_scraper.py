"""
Improved LLM-powered scraper - Optimized for books.toscrape.com
"""

import json
import re
from typing import Dict, Any
from bs4 import BeautifulSoup
import httpx
import ollama


class AdaptiveScraper:
    def __init__(self, model_name: str = "llama3.2", verbose: bool = True):
        self.model_name = model_name
        self.verbose = verbose
        
    def _log(self, message: str):
        if self.verbose:
            print(message)
    
    def fetch_page(self, url: str) -> str:
        self._log(f"📡 Fetching: {url}")
        
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            response = client.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            return response.text
    
    def extract_text(self, html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted tags
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            tag.decompose()
        
        # Get all product information
        products = []
        for article in soup.find_all('article', class_='product_pod'):
            name_elem = article.find('h3').find('a')
            name = name_elem.get('title', '') if name_elem else ''
            
            price_elem = article.find('p', class_='price_color')
            price = price_elem.text.strip().replace('£', '') if price_elem else ''
            
            rating_elem = article.find('p', class_='star-rating')
            rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
            rating = rating_map.get(rating_elem.get('class')[1], 0) if rating_elem else 0
            
            if name:
                products.append({'name': name, 'price': price, 'rating': rating})
        
        if products:
            self._log(f"📦 Found {len(products)} products via BeautifulSoup")
            return {"products": products}
        
        # Fallback to LLM if no products found
        text = soup.get_text(separator=' ', strip=True)
        text = re.sub(r'\s+', ' ', text)
        if len(text) > 5000:
            text = text[:5000]
        return text
    
    async def extract_products(self, url: str, use_javascript: bool = False) -> Dict[str, Any]:
        self._log(f"\n🛒 Extracting products from: {url}")
        
        html = self.fetch_page(url)
        result = self.extract_text(html)
        
        # If BeautifulSoup found products, return them directly (faster!)
        if isinstance(result, dict) and "products" in result:
            return result
        
        # Otherwise use LLM
        content = result
        self._log("🤖 Using LLM for extraction...")
        
        prompt = f"""Extract product information from this webpage.

Content:
{content}

Return a JSON object with a "products" array. Each product should have:
- "name": the product title
- "price": the price as a number (without £ or $ symbol)
- "rating": the rating as a number from 1-5

Example: {{"products": [{{"name": "Book Title", "price": 19.99, "rating": 4.5}}]}}

Return ONLY valid JSON, no other text."""

        response = ollama.chat(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            # Extract JSON from response
            response_text = response.message.content
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return json.loads(response_text)
        except:
            return {"products": [], "error": "Failed to parse LLM response"}
    
    async def extract(self, url: str, instruction: str, use_javascript: bool = False) -> Dict[str, Any]:
        html = self.fetch_page(url)
        content = self.extract_text(html)
        
        if isinstance(content, dict):
            return content
        
        prompt = f"""Based on this webpage: {instruction}

Content: {content}

Return ONLY valid JSON. No explanations."""

        response = ollama.chat(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            return json.loads(response.message.content)
        except:
            return {"error": "Failed to parse response"}
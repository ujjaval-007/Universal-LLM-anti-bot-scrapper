"""
Quick test - Run: python run.py
"""

import asyncio
from src.simple_scraper import AdaptiveScraper

async def test():
    print("🕷️ Testing LLM Adaptive Scraper\n")
    
    scraper = AdaptiveScraper(model_name="llama3.2", verbose=True)
    
    url = "https://books.toscrape.com"
    print(f"Testing with: {url}\n")
    
    result = await scraper.extract_products(url, use_javascript=False)
    
    print("\n" + "="*50)
    print("RESULTS:")
    print("="*50)
    
    if "products" in result:
        print(f"\n✅ Found {len(result['products'])} products")
        for i, product in enumerate(result['products'][:3]):
            print(f"\n{i+1}. {product.get('name', 'N/A')}")
            print(f"   Price: {product.get('price', 'N/A')}")
    else:
        print(result)

if __name__ == "__main__":
    asyncio.run(test())
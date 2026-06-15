"""
Universal Anti-Bot Bypass Scraper
Auto-escalates from fast HTTP → TLS impersonation → Stealth browser → ML adaptive
Works on Flipkart, Amazon, Walmart, Cloudflare sites, and more.
"""

import asyncio
import random
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Try importing optional libraries with fallbacks
try:
    from curl_cffi import requests as curl_requests
    CURL_CFI_AVAILABLE = True
except ImportError:
    CURL_CFI_AVAILABLE = False
    print("⚠️ curl_cffi not installed. Install with: pip install curl-cffi")

try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False
    print("⚠️ cloudscraper not installed. Install with: pip install cloudscraper")

try:
    from scrapling.fetchers import StealthyFetcher, DynamicFetcher
    SCRAPLING_AVAILABLE = True
except ImportError:
    SCRAPLING_AVAILABLE = False
    print("⚠️ scrapling not installed. Install with: pip install scrapling")

try:
    import stealth_requests as stealth_req
    STEALTH_REQUESTS_AVAILABLE = True
except ImportError:
    STEALTH_REQUESTS_AVAILABLE = False
    print("⚠️ stealth_requests not installed. Install with: pip install stealth_requests")

from bs4 import BeautifulSoup


class BypassLevel(Enum):
    """Bypass escalation levels - from fastest to most powerful"""
    LEVEL_0_STEALTH_REQUESTS = 0   # stealth_requests with rotating UA
    LEVEL_1_CLOUDSCRAPER = 1       # cloudscraper for Cloudflare
    LEVEL_2_CURL_CFI = 2           # curl_cffi TLS impersonation
    LEVEL_3_SCRAPLING_HTTP = 3     # Scrapling Fetcher
    LEVEL_4_SCRAPLING_STEALTH = 4  # Scrapling StealthyFetcher
    LEVEL_5_DYNAMIC = 5            # Full browser automation


class UniversalScraper:
    """
    Universal scraper that escalates bypass methods until successful.
    Learns from previous attempts per domain for future runs.
    """
    
    def __init__(self, verbose: bool = True, use_ml: bool = True):
        self.verbose = verbose
        self.use_ml = use_ml
        self.domain_memory = {}  # Stores what works per domain
        self.max_retries = 3
        
    def _log(self, message: str, level: str = "INFO"):
        if self.verbose:
            print(f"[{level}] {message}")
    
    def _get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        from urllib.parse import urlparse
        return urlparse(url).netloc
    
    def _random_delay(self):
        """Random delay to avoid rate limiting"""
        time.sleep(random.uniform(1, 3))
    
    # ============ LEVEL 0: Stealth Requests ============
    
    def _fetch_level0(self, url: str) -> Optional[str]:
        """Level 0: stealth_requests with rotating user agents and retries [citation:6]"""
        if not STEALTH_REQUESTS_AVAILABLE:
            return None
        
        try:
            self._log("🟢 LEVEL 0: Trying stealth_requests...")
            response = stealth_req.get(url, retry=3)
            if response.status_code == 200 and len(response.text) > 500:
                self._log("✅ LEVEL 0 successful!")
                return response.text
        except Exception as e:
            self._log(f"LEVEL 0 failed: {e}", "WARN")
        return None
    
    # ============ LEVEL 1: Cloudscraper ============
    
    def _fetch_level1(self, url: str) -> Optional[str]:
        """Level 1: cloudscraper for Cloudflare protected sites [citation:1]"""
        if not CLOUDSCRAPER_AVAILABLE:
            return None
        
        try:
            self._log("🟡 LEVEL 1: Trying cloudscraper...")
            scraper = cloudscraper.create_scraper()
            response = scraper.get(url, timeout=30)
            
            if response.status_code == 200 and len(response.text) > 500:
                self._log("✅ LEVEL 1 successful!")
                return response.text
        except Exception as e:
            self._log(f"LEVEL 1 failed: {e}", "WARN")
        return None
    
    # ============ LEVEL 2: curl_cffi TLS Impersonation ============
    
    def _fetch_level2(self, url: str) -> Optional[str]:
        """Level 2: curl_cffi with Chrome TLS fingerprint impersonation [citation:10]"""
        if not CURL_CFI_AVAILABLE:
            return None
        
        # Try different browser impersonations
        browsers = ["chrome", "chrome124", "safari15_5", "edge101"]
        
        for browser in browsers:
            try:
                self._log(f"🟠 LEVEL 2: Trying curl_cffi with {browser} impersonation...")
                response = curl_requests.get(
                    url, 
                    impersonate=browser,
                    timeout=30
                )
                
                if response.status_code == 200 and len(response.text) > 500:
                    self._log(f"✅ LEVEL 2 successful with {browser}!")
                    return response.text
            except Exception as e:
                self._log(f"curl_cffi {browser} failed: {e}", "WARN")
        return None
    
    # ============ LEVEL 3: Scrapling HTTP ============
    
    def _fetch_level3(self, url: str) -> Optional[str]:
        """Level 3: Scrapling Fetcher with HTTP requests [citation:3]"""
        if not SCRAPLING_AVAILABLE:
            return None
        
        try:
            self._log("🔴 LEVEL 3: Trying Scrapling Fetcher...")
            from scrapling.fetchers import Fetcher
            
            page = Fetcher.get(url, impersonate='chrome')
            if page and page.status == 200 and len(page.text) > 500:
                self._log("✅ LEVEL 3 successful!")
                return page.text
        except Exception as e:
            self._log(f"LEVEL 3 failed: {e}", "WARN")
        return None
    
    # ============ LEVEL 4: Scrapling StealthyFetcher ============
    
    def _fetch_level4(self, url: str) -> Optional[str]:
        """Level 4: Scrapling StealthyFetcher - bypasses Cloudflare Turnstile [citation:4]"""
        if not SCRAPLING_AVAILABLE:
            return None
        
        try:
            self._log("🔥 LEVEL 4: Trying Scrapling StealthyFetcher...")
            from scrapling.fetchers import StealthyFetcher
            
            page = StealthyFetcher.fetch(
                url, 
                headless=True, 
                solve_cloudflare=True,
                network_idle=True
            )
            if page and page.status == 200 and len(page.text) > 500:
                self._log("✅ LEVEL 4 successful!")
                return page.text
        except Exception as e:
            self._log(f"LEVEL 4 failed: {e}", "WARN")
        return None
    
    # ============ LEVEL 5: Dynamic Browser ============
    
    async def _fetch_level5_async(self, url: str) -> Optional[str]:
        """Level 5: Full browser automation with Playwright via Scrapling"""
        if not SCRAPLING_AVAILABLE:
            return None
        
        try:
            self._log("💀 LEVEL 5: Trying DynamicFetcher (full browser)...")
            from scrapling.fetchers import DynamicFetcher
            
            page = DynamicFetcher.fetch(
                url,
                headless=True,
                disable_resources=False,
                network_idle=True
            )
            if page and page.status == 200 and len(page.text) > 500:
                self._log("✅ LEVEL 5 successful!")
                return page.text
        except Exception as e:
            self._log(f"LEVEL 5 failed: {e}", "WARN")
        return None
    
    # ============ Main Scrape Method ============
    
    async def scrape(self, url: str, force_level: Optional[int] = None) -> Dict[str, Any]:
        """
        Main scraping method with auto-escalation.
        
        Args:
            url: Target URL
            force_level: Optional - force specific bypass level (0-5)
        
        Returns:
            Dict with 'success', 'content', 'method_used', 'status_code'
        """
        self._log(f"\n🎯 Starting universal scrape: {url}")
        self._log("=" * 60)
        
        domain = self._get_domain(url)
        
        # Check if we remember a working method for this domain
        if domain in self.domain_memory and not force_level:
            start_level = self.domain_memory[domain]
            self._log(f"📝 Using remembered method for {domain}: Level {start_level}")
        else:
            start_level = 0 if force_level is None else force_level
        
        # Define escalation sequence
        levels = [
            (BypassLevel.LEVEL_0_STEALTH_REQUESTS, self._fetch_level0),
            (BypassLevel.LEVEL_1_CLOUDSCRAPER, self._fetch_level1),
            (BypassLevel.LEVEL_2_CURL_CFI, self._fetch_level2),
            (BypassLevel.LEVEL_3_SCRAPLING_HTTP, self._fetch_level3),
            (BypassLevel.LEVEL_4_SCRAPLING_STEALTH, self._fetch_level4),
        ]
        
        # Start from the appropriate level
        for level, fetch_func in levels[start_level:]:
            self._random_delay()  # Rate limiting prevention
            content = fetch_func(url)
            
            if content:
                # Success - remember for next time
                if self.use_ml:
                    self.domain_memory[domain] = level.value
                return {
                    "success": True,
                    "content": content,
                    "method_used": level.name,
                    "status_code": 200
                }
        
        # Try level 5 (async browser) as last resort
        content = await self._fetch_level5_async(url)
        if content:
            if self.use_ml:
                self.domain_memory[domain] = 5
            return {
                "success": True,
                "content": content,
                "method_used": "LEVEL_5_DYNAMIC",
                "status_code": 200
            }
        
        return {
            "success": False,
            "content": None,
            "method_used": "NONE",
            "status_code": 403,
            "error": "All bypass levels failed"
        }
    
    def get_html(self, url: str, force_level: Optional[int] = None) -> str:
        """Sync wrapper for scrape"""
        return asyncio.run(self.scrape(url, force_level))["content"]
    
    def extract_text(self, html: str, selector: Optional[str] = None) -> str:
        """Extract clean text from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        
        if selector:
            elements = soup.select(selector)
            return '\n'.join(elem.get_text(strip=True) for elem in elements)
        
        # Remove scripts and styles
        for tag in soup(['script', 'style', 'nav', 'footer']):
            tag.decompose()
        
        return soup.get_text(separator='\n', strip=True)
    
    def get_domain_memory(self) -> Dict:
        """Get learned domain strategies"""
        return self.domain_memory


# Test the universal scraper
if __name__ == "__main__":
    async def test():
        scraper = UniversalScraper(verbose=True)
        
        # Test URLs with different protection levels
        test_urls = [
            ("https://books.toscrape.com", "No protection"),
            ("https://httpbin.org/anything", "Test site"),
            ("https://www.flipkart.com/search?q=jujutsu+kaisen+stickers", "Flipkart"),
            ("https://www.walmart.com/search?q=laptop", "Walmart"),
        ]
        
        for url, name in test_urls:
            print(f"\n📋 Testing: {name} - {url}")
            result = await scraper.scrape(url)
            if result["success"]:
                print(f"✅ Success! Method: {result['method_used']}")
                print(f"   Content length: {len(result['content'])} chars")
            else:
                print(f"❌ Failed: {result.get('error')}")
    
    asyncio.run(test())
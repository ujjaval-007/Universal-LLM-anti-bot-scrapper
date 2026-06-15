"""
Streamlit Web Interface - Universal Anti-Bot Scraper
Run: streamlit run app/streamlit_app.py
"""

import streamlit as st
import asyncio
import pandas as pd
import json
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import universal scraper, fallback to simple scraper
try:
    from src.universal_scraper import UniversalScraper
    UNIVERSAL_AVAILABLE = True
except ImportError:
    UNIVERSAL_AVAILABLE = False
    from src.simple_scraper import AdaptiveScraper

st.set_page_config(
    page_title="Universal Anti-Bot Scraper", 
    page_icon="🛡️", 
    layout="wide"
)

st.title("🛡️ Universal Anti-Bot Scraper")
st.markdown("*Bypasses Cloudflare, Flipkart, Amazon, Walmart - Auto escalates bypass methods*")
st.markdown("---")

# Session state to store results
if 'scrape_result' not in st.session_state:
    st.session_state.scrape_result = None
if 'method_used' not in st.session_state:
    st.session_state.method_used = None

with st.sidebar:
    st.header("⚙️ Settings")
    
    st.info("💰 **100% FREE** - Local LLM, No API keys")
    
    # Model selection
    model = st.selectbox("🧠 LLM Model", ["llama3.2 (Fast)", "mistral (Better)"])
    model_name = "llama3.2" if "llama" in model else "mistral"
    
    st.divider()
    
    # Anti-bot settings
    st.subheader("🛡️ Anti-Bot Protection")
    
    auto_escalate = st.checkbox("🚀 Auto-escalate bypass methods", value=True, 
                                 help="Automatically try stronger bypass methods if blocked")
    
    if not auto_escalate:
        force_level = st.selectbox(
            "Force bypass level",
            ["Auto", "Level 0: stealth_requests", "Level 1: cloudscraper", 
             "Level 2: curl_cffi", "Level 3: Scrapling HTTP", 
             "Level 4: Scrapling Stealth", "Level 5: Full Browser"]
        )
        level_map = {
            "Auto": None,
            "Level 0: stealth_requests": 0,
            "Level 1: cloudscraper": 1,
            "Level 2: curl_cffi": 2,
            "Level 3: Scrapling HTTP": 3,
            "Level 4: Scrapling Stealth": 4,
            "Level 5: Full Browser": 5
        }
        forced_level = level_map.get(force_level, None)
    else:
        forced_level = None
    
    st.divider()
    
    # JavaScript rendering
    js_mode = st.checkbox("🌐 Force JavaScript rendering", value=False,
                          help="Use for React/Vue/Angular websites")
    
    st.divider()
    
    # Quick templates
    preset = st.radio("Quick Template", ["Custom", "🛒 Products", "💼 Jobs", "📰 News"])
    
    st.divider()
    
    # Show learned strategies
    if UNIVERSAL_AVAILABLE and st.button("📊 Show Learned Strategies"):
        try:
            temp_scraper = UniversalScraper(verbose=False)
            memory = temp_scraper.get_domain_memory()
            if memory:
                st.json(memory)
            else:
                st.info("No strategies learned yet. Scrape some sites first!")
        except:
            st.info("Start scraping to build strategy memory")

# Main area
col1, col2 = st.columns([2, 1])

with col1:
    url = st.text_input("🌐 URL", placeholder="https://books.toscrape.com or https://www.flipkart.com/search?q=stickers")
    
    if preset == "Custom":
        instruction = st.text_area("📝 What to extract?", 
                                   placeholder="Example: Extract all product names and prices",
                                   height=100)
    elif preset == "🛒 Products":
        instruction = "Extract all products with name, price, rating, and availability. Return as JSON with products array."
        st.info("📋 Extracting: Products with name, price, rating, availability")
    elif preset == "💼 Jobs":
        instruction = "Extract all jobs with title, company, location, and salary if available. Return as JSON with jobs array."
        st.info("📋 Extracting: Job title, company, location, salary")
    elif preset == "📰 News":
        instruction = "Extract all articles with headline, author, date, and summary. Return as JSON with articles array."
        st.info("📋 Extracting: Headline, author, date, summary")

with col2:
    st.write("")
    verbose = st.checkbox("🔍 Show detailed logs", value=True)
    st.write("")
    
    # Show available bypass methods
    if UNIVERSAL_AVAILABLE:
        st.info("🛡️ Available bypass methods: stealth_requests, cloudscraper, curl_cffi, Scrapling, Full browser")
    else:
        st.warning("⚠️ Universal scraper not available. Install: pip install curl-cffi cloudscraper scrapling")
    
    scrape_btn = st.button("🚀 START SCRAPING", type="primary", use_container_width=True)

# Status display area
status_placeholder = st.empty()

# Scraping logic
if scrape_btn and url:
    if preset == "Custom" and not instruction:
        st.error("Please describe what data you want to extract")
    else:
        status_placeholder.info("🕷️ Starting scraper...")
        
        with st.spinner("🛡️ Scraping with anti-bot bypass..."):
            
            # Use universal scraper if available
            if UNIVERSAL_AVAILABLE:
                scraper = UniversalScraper(verbose=verbose, use_ml=True)
                
                try:
                    # Run the universal scraper
                    result = asyncio.run(scraper.scrape(url, force_level=forced_level))
                    
                    if result["success"]:
                        st.session_state.method_used = result["method_used"]
                        status_placeholder.success(f"✅ Success! Method used: {result['method_used']}")
                        
                        html_content = result["content"]
                        clean_text = scraper.extract_text(html_content)
                        
                        # Now use LLM to extract structured data
                        status_placeholder.info("🤖 Analyzing with LLM...")
                        
                        # Prepare prompt for LLM
                        prompt = f"""{instruction}

Based on this webpage content, extract the requested information.

Content:
{clean_text[:5000]}

Return ONLY valid JSON. No explanations."""

                        # Use Ollama for extraction
                        import ollama
                        llm_response = ollama.chat(
                            model=model_name,
                            messages=[{"role": "user", "content": prompt}],
                            format="json"
                        )
                        
                        try:
                            extracted_data = json.loads(llm_response.message.content)
                            
                            if extracted_data and "error" not in extracted_data:
                                st.success("✅ Extraction complete!")
                                
                                # Display as table if possible
                                if "products" in extracted_data and extracted_data["products"]:
                                    df = pd.DataFrame(extracted_data["products"])
                                    st.dataframe(df, use_container_width=True)
                                    st.caption(f"📊 Found {len(extracted_data['products'])} products")
                                elif "jobs" in extracted_data and extracted_data["jobs"]:
                                    df = pd.DataFrame(extracted_data["jobs"])
                                    st.dataframe(df, use_container_width=True)
                                    st.caption(f"📊 Found {len(extracted_data['jobs'])} jobs")
                                elif "articles" in extracted_data and extracted_data["articles"]:
                                    df = pd.DataFrame(extracted_data["articles"])
                                    st.dataframe(df, use_container_width=True)
                                    st.caption(f"📊 Found {len(extracted_data['articles'])} articles")
                                else:
                                    st.json(extracted_data)
                                
                                # Download buttons
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    st.download_button(
                                        "📥 Download JSON",
                                        json.dumps(extracted_data, indent=2),
                                        "scraped_data.json",
                                        "application/json"
                                    )
                                
                                # Add method info to download
                                method_info = {
                                    "scraping_method": result["method_used"],
                                    "data": extracted_data
                                }
                                with col_b:
                                    st.download_button(
                                        "📥 Download with Metadata",
                                        json.dumps(method_info, indent=2),
                                        "scraped_data_with_method.json",
                                        "application/json"
                                    )
                            else:
                                st.error(f"❌ LLM extraction failed: {extracted_data.get('error', 'Unknown error')}")
                                
                        except json.JSONDecodeError:
                            st.error("❌ Failed to parse LLM response as JSON")
                            st.text(llm_response.message.content[:500])
                    else:
                        status_placeholder.error(f"❌ Scraping failed: {result.get('error', 'All bypass methods failed')}")
                        st.info("💡 Try: 1. Check your internet connection 2. Wait a few minutes and try again 3. Try a different URL")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("Make sure Ollama is running: ollama serve in another terminal")
            
            else:
                # Fallback to simple scraper
                from src.simple_scraper import AdaptiveScraper
                scraper = AdaptiveScraper(model_name=model_name, verbose=verbose)
                
                try:
                    if preset == "🛒 Products":
                        result = asyncio.run(scraper.extract_products(url, js_mode))
                    else:
                        result = asyncio.run(scraper.extract(url, instruction, js_mode))
                    
                    if result and "error" not in result:
                        st.success("✅ Extraction complete!")
                        
                        if "products" in result and result["products"]:
                            st.dataframe(pd.DataFrame(result["products"]))
                        else:
                            st.json(result)
                        
                        st.download_button("📥 Download JSON", 
                                          json.dumps(result, indent=2),
                                          "scraped_data.json")
                    else:
                        st.error(f"❌ {result.get('error', 'No data extracted')}")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("Make sure Ollama is running: open a NEW terminal and run 'ollama serve'")

# Footer
st.divider()
st.markdown("### 🎯 How Anti-Bot Bypass Works")

st.markdown("""
| Level | Method | What It Does | Best For |
|-------|--------|--------------|----------|
| L0 | stealth_requests | Rotating user agents | Simple sites |
| L1 | cloudscraper | Solves Cloudflare challenges | Cloudflare sites |
| L2 | curl_cffi | TLS fingerprint impersonation | Flipkart, Walmart |
| L3 | Scrapling HTTP | HTTP with browser impersonation | General e-commerce |
| L4 | Scrapling Stealth | Bypasses Turnstile | High-protection sites |
| L5 | Full Browser | Complete browser automation | Last resort |
""")

st.markdown("""
### 📋 Instructions
1. Make sure Ollama is running: `ollama serve` in a new terminal
2. Pull the model: `ollama pull llama3.2` (one time)
3. Enter any URL - the scraper automatically finds the right bypass method
4. Click START SCRAPING
""")

# Auto-refresh method display
if st.session_state.method_used:
    st.sidebar.success(f"✅ Last used: {st.session_state.method_used}")
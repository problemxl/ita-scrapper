# ITA Scrapper Troubleshooting Guide

## Common Issues and Solutions

This guide covers the most common issues encountered when using ITA Scrapper and provides step-by-step solutions.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Browser and Playwright Issues](#browser-and-playwright-issues)
- [Website Access Issues](#website-access-issues)
- [Parsing and Data Issues](#parsing-and-data-issues)
- [Performance Issues](#performance-issues)
- [Authentication and Blocking](#authentication-and-blocking)
- [Development and Debugging](#development-and-debugging)

## Installation Issues

### Issue: Playwright Browser Installation Fails

**Symptoms:**
```
Error: Executable doesn't exist at /path/to/browser
```

**Solution:**
```bash
# Install Playwright browsers explicitly
playwright install chromium

# Or install all browsers
playwright install

# For specific Python environment
python -m playwright install chromium
```

**Alternative for restricted environments:**
```bash
# Install browsers in custom location
PLAYWRIGHT_BROWSERS_PATH=/custom/path playwright install chromium
```

### Issue: Dependencies Conflict

**Symptoms:**
```
ERROR: pip's dependency resolver does not currently consider all the packages
```

**Solution:**
```bash
# Create fresh virtual environment
python -m venv fresh_env
source fresh_env/bin/activate  # Linux/Mac
# fresh_env\Scripts\activate  # Windows

# Install with specific versions
pip install ita-scrapper==latest
pip install playwright==1.40.0

# Or use uv for better dependency resolution
uv pip install ita-scrapper
```

### Issue: Import Errors

**Symptoms:**
```python
ImportError: cannot import name 'ITAScrapper' from 'ita_scrapper'
```

**Solution:**
```python
# Check correct import syntax
from ita_scrapper import ITAScrapper, CabinClass, Flight

# Verify installation
import ita_scrapper
print(ita_scrapper.__version__)

# Check Python path
import sys
print(sys.path)
```

## Browser and Playwright Issues

### Issue: Browser Fails to Launch

**Symptoms:**
```
Error: Failed to launch browser: spawn ENOENT
```

**Solution:**
```python
# Check browser installation
import asyncio
from playwright.async_api import async_playwright

async def check_browser():
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch()
            print("Browser launch successful")
            await browser.close()
        except Exception as e:
            print(f"Browser launch failed: {e}")

asyncio.run(check_browser())
```

**If browser launch fails:**
```bash
# Reinstall browsers
playwright uninstall
playwright install chromium

# Check system dependencies (Linux)
sudo apt-get update
sudo apt-get install -y libnss3 libatk-bridge2.0-0 libxss1 libgtk-3-0

# Check system dependencies (macOS)
brew install --cask google-chrome
```

### Issue: Headless Mode Problems

**Symptoms:**
- Works in non-headless mode but fails in headless mode
- Different behavior between headless and non-headless

**Solution:**
```python
# Debug with visible browser first
scrapper = ITAScrapper(headless=False, timeout=60000)

# If it works, try headless with additional options
scrapper = ITAScrapper(
    headless=True,
    timeout=60000,
    viewport_size=(1920, 1080)  # Ensure consistent viewport
)

# Alternative: use virtual display (Linux)
from pyvirtualdisplay import Display

display = Display(visible=0, size=(1920, 1080))
display.start()

try:
    # Run scrapper
    async with ITAScrapper(headless=False) as scrapper:
        result = await scrapper.search_flights(...)
finally:
    display.stop()
```

### Issue: Browser Crashes or Hangs

**Symptoms:**
- Browser process becomes unresponsive
- Operations timeout unexpectedly

**Solution:**
```python
# Implement browser restart mechanism
import asyncio

class RobustScrapper:
    def __init__(self):
        self.max_retries = 3
        self.current_scrapper = None
    
    async def restart_browser(self):
        """Restart browser if it becomes unresponsive."""
        if self.current_scrapper:
            try:
                await self.current_scrapper.close()
            except:
                pass
        
        self.current_scrapper = ITAScrapper(
            headless=True,
            timeout=30000
        )
        await self.current_scrapper.start()
    
    async def robust_search(self, **kwargs):
        """Search with automatic browser restart on failure."""
        for attempt in range(self.max_retries):
            try:
                if not self.current_scrapper:
                    await self.restart_browser()
                
                return await self.current_scrapper.search_flights(**kwargs)
                
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                await self.restart_browser()
                
                if attempt == self.max_retries - 1:
                    raise
```

## Website Access Issues

### Issue: "Access Denied" or "Blocked" Messages

**Symptoms:**
```
NavigationError: Site blocking detected
```

**Solution:**
```python
# Try different user agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
]

for user_agent in USER_AGENTS:
    try:
        scrapper = ITAScrapper(
            headless=True,
            user_agent=user_agent
        )
        async with scrapper:
            result = await scrapper.search_flights(...)
            break
    except NavigationError:
        continue
else:
    print("All user agents failed")
```

**Additional anti-detection measures:**
```python
# Implement delays and randomization
import random

scrapper = ITAScrapper(headless=True)

async def human_like_search(**kwargs):
    """Search with human-like timing."""
    async with scrapper:
        # Random delay before starting
        await asyncio.sleep(random.uniform(2, 5))
        
        # Navigate with delays
        await scrapper._navigate_to_flights()
        await asyncio.sleep(random.uniform(3, 7))
        
        # Fill form with delays between fields
        # ... (implement gradual form filling)
        
        return await scrapper.search_flights(**kwargs)
```

### Issue: CAPTCHA Challenges

**Symptoms:**
- Page loads but shows CAPTCHA
- Search form is not accessible

**Solution:**
```python
# Detect CAPTCHA and handle gracefully
async def check_for_captcha(page):
    """Check if CAPTCHA is present on page."""
    captcha_indicators = [
        '[class*="captcha"]',
        '[id*="captcha"]',
        'iframe[src*="recaptcha"]',
        '[class*="challenge"]'
    ]
    
    for selector in captcha_indicators:
        elements = await page.query_selector_all(selector)
        if elements:
            return True
    
    # Check page text for CAPTCHA keywords
    content = await page.content()
    if any(word in content.lower() for word in ["captcha", "robot", "verify", "challenge"]):
        return True
    
    return False

# Usage
async with ITAScrapper(headless=False) as scrapper:
    await scrapper._navigate_to_flights()
    
    if await check_for_captcha(scrapper._page):
        print("CAPTCHA detected - manual intervention required")
        input("Please solve CAPTCHA and press Enter...")
    
    result = await scrapper.search_flights(...)
```

### Issue: Rate Limiting

**Symptoms:**
- Requests become progressively slower
- Temporary blocks after multiple searches

**Solution:**
```python
# Implement exponential backoff
import time
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=60)
)
async def rate_limited_search(**kwargs):
    """Search with automatic retry and backoff."""
    async with ITAScrapper() as scrapper:
        return await scrapper.search_flights(**kwargs)

# Implement request spacing
class RateLimitedScrapper:
    def __init__(self, min_delay=10):
        self.min_delay = min_delay
        self.last_request = 0
    
    async def search_with_rate_limit(self, **kwargs):
        """Ensure minimum delay between requests."""
        now = time.time()
        time_since_last = now - self.last_request
        
        if time_since_last < self.min_delay:
            await asyncio.sleep(self.min_delay - time_since_last)
        
        try:
            async with ITAScrapper() as scrapper:
                result = await scrapper.search_flights(**kwargs)
                self.last_request = time.time()
                return result
        except NavigationError:
            # Increase delay on blocks
            self.min_delay *= 2
            raise
```

## Parsing and Data Issues

### Issue: No Flights Found

**Symptoms:**
```python
result.flights == []  # Empty list
```

**Diagnostic steps:**
```python
async def diagnose_no_results(scrapper, **search_kwargs):
    """Diagnose why no flights were found."""
    
    async with scrapper:
        # Navigate and search
        await scrapper._navigate_to_flights()
        await scrapper._fill_search_form(SearchParams(**search_kwargs))
        
        # Take screenshot for inspection
        await scrapper._page.screenshot(path="no_results_debug.png")
        
        # Check for error messages
        error_selectors = [
            '[class*="error"]',
            '[class*="no-results"]',
            '[class*="not-found"]'
        ]
        
        for selector in error_selectors:
            elements = await scrapper._page.query_selector_all(selector)
            if elements:
                for element in elements:
                    text = await element.inner_text()
                    print(f"Error message: {text}")
        
        # Check page content
        content = await scrapper._page.content()
        if "no flights" in content.lower():
            print("Site reports no flights available")
        
        # Check if results are still loading
        loading_selectors = [
            '[class*="loading"]',
            '[class*="spinner"]',
            '[aria-label*="loading"]'
        ]
        
        for selector in loading_selectors:
            if await scrapper._page.query_selector(selector):
                print("Page still loading - increase timeout")
                return
        
        print("No obvious issues found - check search parameters")
```

### Issue: Parsing Errors

**Symptoms:**
```
ParseError: Failed to parse flight results
```

**Solution:**
```python
# Enable debug logging
import logging
logging.getLogger('ita_scrapper').setLevel(logging.DEBUG)

# Use fallback parsing
async def robust_parsing(scrapper, **kwargs):
    """Parse with multiple strategies."""
    
    try:
        # Primary parsing
        result = await scrapper.search_flights(**kwargs)
        return result
    
    except ParseError as e:
        print(f"Primary parsing failed: {e}")
        
        # Try with longer wait
        scrapper.timeout = 60000  # 1 minute
        try:
            result = await scrapper.search_flights(**kwargs)
            return result
        except ParseError:
            pass
    
    # Manual parsing inspection
    async with scrapper:
        await scrapper._navigate_to_flights()
        await scrapper._fill_search_form(SearchParams(**kwargs))
        
        # Wait extra long for results
        await scrapper._page.wait_for_timeout(15000)
        
        # Check what elements are available
        all_elements = await scrapper._page.query_selector_all('*')
        print(f"Page has {len(all_elements)} elements")
        
        # Look for any flight-related content
        flight_indicators = ["flight", "price", "$", "airline", "duration"]
        page_text = await scrapper._page.inner_text('body')
        
        found_indicators = [ind for ind in flight_indicators if ind in page_text.lower()]
        print(f"Found flight indicators: {found_indicators}")
        
        return FlightResult(flights=[], search_params=SearchParams(**kwargs), total_results=0)
```

### Issue: Incomplete Flight Data

**Symptoms:**
- Flights returned but missing price, duration, or airline information
- Default values used instead of parsed data

**Solution:**
```python
def validate_flight_data(flights: list[Flight]) -> list[Flight]:
    """Validate and filter flight data quality."""
    
    valid_flights = []
    
    for flight in flights:
        issues = []
        
        # Check price validity
        if flight.price <= 0:
            issues.append("Invalid price")
        
        # Check duration validity
        if flight.total_duration_minutes <= 0:
            issues.append("Invalid duration")
        
        # Check segment completeness
        if not flight.segments:
            issues.append("No segments")
        
        for segment in flight.segments:
            if segment.airline.code == "XX":
                issues.append("Unknown airline")
            if segment.flight_number.endswith("0000"):
                issues.append("Default flight number")
        
        if not issues:
            valid_flights.append(flight)
        else:
            print(f"Flight quality issues: {', '.join(issues)}")
    
    return valid_flights

# Usage
result = await scrapper.search_flights(...)
valid_flights = validate_flight_data(result.flights)
print(f"Quality filtered: {len(valid_flights)}/{len(result.flights)} flights")
```

## Performance Issues

### Issue: Slow Search Performance

**Symptoms:**
- Searches take much longer than expected
- Timeouts occur frequently

**Solution:**
```python
# Profile search performance
import time

async def profile_search(**kwargs):
    """Profile search performance."""
    
    start_time = time.time()
    
    async with ITAScrapper(headless=True) as scrapper:
        nav_start = time.time()
        await scrapper._navigate_to_flights()
        nav_time = time.time() - nav_start
        
        form_start = time.time()
        # Fill form...
        form_time = time.time() - form_start
        
        parse_start = time.time()
        result = await scrapper.search_flights(**kwargs)
        parse_time = time.time() - parse_start
    
    total_time = time.time() - start_time
    
    print(f"Performance breakdown:")
    print(f"  Navigation: {nav_time:.2f}s")
    print(f"  Form filling: {form_time:.2f}s") 
    print(f"  Parsing: {parse_time:.2f}s")
    print(f"  Total: {total_time:.2f}s")
    
    return result

# Optimize based on bottlenecks
async def optimized_search(**kwargs):
    """Optimized search configuration."""
    
    scrapper = ITAScrapper(
        headless=True,              # Faster than non-headless
        timeout=45000,              # Reasonable timeout
        viewport_size=(1280, 720),  # Smaller viewport
    )
    
    # Limit result scope
    kwargs['max_results'] = min(kwargs.get('max_results', 20), 10)
    
    return await scrapper.search_flights(**kwargs)
```

### Issue: Memory Usage

**Symptoms:**
- Memory usage increases over time
- Out of memory errors with multiple searches

**Solution:**
```python
import gc
import psutil
import os

def monitor_memory():
    """Monitor memory usage."""
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"Memory usage: {memory_mb:.2f} MB")
    return memory_mb

async def memory_efficient_searches(search_list):
    """Perform multiple searches with memory management."""
    
    results = []
    
    for i, search_params in enumerate(search_list):
        print(f"Search {i+1}/{len(search_list)}")
        
        # Monitor memory before search
        memory_before = monitor_memory()
        
        # Perform search with explicit cleanup
        async with ITAScrapper() as scrapper:
            result = await scrapper.search_flights(**search_params)
            results.append(result)
        
        # Force garbage collection
        gc.collect()
        
        # Monitor memory after search
        memory_after = monitor_memory()
        memory_diff = memory_after - memory_before
        
        print(f"Memory change: {memory_diff:+.2f} MB")
        
        # Optional: delay between searches
        if i < len(search_list) - 1:
            await asyncio.sleep(2)
    
    return results
```

## Authentication and Blocking

### Issue: Login Required

**Symptoms:**
- Redirected to login page
- Limited search functionality without account

**Solution:**
```python
async def handle_login_flow(scrapper, username, password):
    """Handle login if required."""
    
    # Check if login is required
    current_url = scrapper._page.url
    if "login" in current_url or "signin" in current_url:
        print("Login required")
        
        # Fill login form
        await scrapper._page.fill('input[name="username"]', username)
        await scrapper._page.fill('input[name="password"]', password)
        await scrapper._page.click('button[type="submit"]')
        
        # Wait for redirect
        await scrapper._page.wait_for_load_state('networkidle')
        
        # Verify login success
        if "login" not in scrapper._page.url:
            print("Login successful")
        else:
            raise NavigationError("Login failed")

# Usage
async with ITAScrapper(headless=False) as scrapper:
    await scrapper._navigate_to_flights()
    await handle_login_flow(scrapper, "username", "password")
    result = await scrapper.search_flights(...)
```

### Issue: IP Blocking

**Symptoms:**
- All requests fail immediately
- Connection refused errors

**Solution:**
```python
# Test with proxy rotation
PROXY_LIST = [
    "http://proxy1:8080",
    "http://proxy2:8080", 
    # Add your proxy servers
]

async def search_with_proxy_rotation(**kwargs):
    """Try search with different proxies."""
    
    for proxy in PROXY_LIST:
        try:
            # Launch browser with proxy
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    proxy={"server": proxy}
                )
                
                context = await browser.new_context()
                page = await context.new_page()
                
                # Create scrapper with existing page
                scrapper = ITAScrapper()
                scrapper._page = page
                
                result = await scrapper.search_flights(**kwargs)
                await browser.close()
                return result
                
        except Exception as e:
            print(f"Proxy {proxy} failed: {e}")
            continue
    
    raise NavigationError("All proxies failed")
```

## Development and Debugging

### Issue: Development Setup

**Environment setup for debugging:**
```bash
# Clone repository
git clone https://github.com/yourusername/ita-scrapper.git
cd ita-scrapper

# Create development environment
python -m venv dev_env
source dev_env/bin/activate

# Install in development mode
pip install -e ".[dev]"

# Install additional debugging tools
pip install ipdb pudb

# Run tests to verify setup
pytest tests/ -v
```

### Issue: Debugging Browser Automation

**Interactive debugging:**
```python
import asyncio
from playwright.async_api import async_playwright

async def debug_session():
    """Interactive debugging session."""
    
    async with async_playwright() as p:
        # Launch with devtools
        browser = await p.chromium.launch(
            headless=False,
            devtools=True,  # Opens developer tools
            slow_mo=1000    # Slow down operations
        )
        
        context = await browser.new_context()
        page = await context.new_page()
        
        # Navigate to site
        await page.goto("https://matrix.itasoftware.com")
        
        # Set breakpoint for inspection
        await page.pause()  # Pauses execution for manual inspection
        
        # Continue with automation...
        await browser.close()

# Run debug session
asyncio.run(debug_session())
```

### Issue: Test Data Generation

**Create test fixtures:**
```python
# tests/conftest.py
import pytest
from datetime import date, timedelta

@pytest.fixture
def sample_search_params():
    """Sample search parameters for testing."""
    return {
        "origin": "JFK",
        "destination": "LAX",
        "departure_date": date.today() + timedelta(days=30),
        "return_date": date.today() + timedelta(days=37),
        "adults": 2,
        "cabin_class": CabinClass.ECONOMY
    }

@pytest.fixture
def mock_flight_data():
    """Mock flight data for testing parsers."""
    return {
        "price": "299.00",
        "airline": "Delta Air Lines",
        "flight_number": "DL123",
        "departure_time": "8:30 AM",
        "arrival_time": "11:45 AM",
        "duration": "6h 15m"
    }

# Usage in tests
def test_search_params_validation(sample_search_params):
    params = SearchParams(**sample_search_params)
    assert params.origin == "JFK"
    assert params.adults == 2
```

This troubleshooting guide covers the most common issues encountered in production use of ITA Scrapper. For additional support, check the GitHub issues page or contact the development team.
# FAQ

## General Questions

### What is ITA Scrapper?
ITA Scrapper is a Python library for automating flight searches on the ITA Matrix platform. It provides a programmatic interface to search for flights, parse results, and handle complex travel scenarios.

### Is this legal?
The library is designed for personal use and research purposes. Users should respect the terms of service of the ITA Matrix platform and implement appropriate rate limiting to avoid overloading their servers.

### What makes this different from other flight APIs?
- **Free to use**: No API keys or subscription fees required
- **Comprehensive data**: Access to the same data as ITA Matrix web interface
- **Flexible searching**: Support for complex routing and date combinations
- **Type safety**: Full Pydantic model validation for reliable data handling

## Installation & Setup

### Why do I need Chrome browser?
ITA Matrix is a dynamic web application that requires JavaScript execution. Chrome provides the most reliable automation experience through Selenium WebDriver.

### Can I use Firefox or other browsers?
Currently, only Chrome is supported. Firefox support may be added in future versions based on user demand.

### Do I need ChromeDriver?
No, the library automatically manages ChromeDriver installation and updates.

## Usage Questions

### How do I search for multi-city trips?
```python
from ita_scrapper.models import SearchParams

params = SearchParams(
    origin="NYC",
    destination="LAX", 
    departure_date="2024-03-15",
    intermediate_stops=["CHI", "DEN"],
    return_date="2024-03-22"
)

results = scrapper.search_flights_with_params(params)
```

### Can I search flexible dates?
Yes, use the `date_flexibility` parameter:
```python
params = SearchParams(
    origin="NYC",
    destination="LAX",
    departure_date="2024-03-15",
    date_flexibility=3  # ±3 days
)
```

### How do I handle rate limiting?
```python
from ita_scrapper.config import ScrapperConfig

config = ScrapperConfig(
    request_delay=2.0,  # 2 seconds between requests
    max_retries=3,
    backoff_factor=1.5
)

scrapper = ITAScrapper(config=config)
```

### Why are my searches taking so long?
- **Complex routes**: Multi-city and flexible date searches take longer
- **Network speed**: Slow internet affects page loading times
- **Rate limiting**: Intentional delays to respect server resources
- **Browser startup**: Initial Chrome launch adds overhead

To optimize:
```python
# Keep browser session alive
scrapper = ITAScrapper()
# Perform multiple searches without recreating browser
results1 = scrapper.search_flights("NYC", "LAX", "2024-03-15")
results2 = scrapper.search_flights("NYC", "SFO", "2024-03-16")
scrapper.close()  # Clean up when done
```

## Error Handling

### What if a search returns no results?
```python
results = scrapper.search_flights("NYC", "LAX", "2024-03-15")

if not results.flights:
    print("No flights found. Try:")
    print("- Different dates")
    print("- Flexible airports (JFK instead of NYC)")
    print("- Increased connection tolerance")
```

### How do I handle parsing errors?
```python
from ita_scrapper.exceptions import ParsingError

try:
    results = scrapper.search_flights("NYC", "LAX", "2024-03-15")
except ParsingError as e:
    print(f"Failed to parse results: {e}")
    # Retry with different parameters or report issue
```

### What about network timeouts?
```python
from ita_scrapper.config import ScrapperConfig

# Increase timeout for slow connections
config = ScrapperConfig(timeout=60)  # 60 seconds
scrapper = ITAScrapper(config=config)
```

## Performance

### How can I speed up searches?
1. **Reuse browser sessions**: Don't create new ITAScrapper instances for each search
2. **Optimize search parameters**: Be specific to reduce result processing time
3. **Use headless mode**: Default headless=True is faster than visible browser
4. **Cache results**: Store results for repeated queries

### Can I run multiple searches in parallel?
```python
import asyncio

async def parallel_searches():
    scrapper = ITAScrapper()
    
    tasks = [
        scrapper.search_flights_async("NYC", "LAX", "2024-03-15"),
        scrapper.search_flights_async("NYC", "SFO", "2024-03-15"),
        scrapper.search_flights_async("NYC", "SEA", "2024-03-15")
    ]
    
    results = await asyncio.gather(*tasks)
    return results
```

### How much memory does it use?
Typical memory usage:
- **Base library**: ~50MB
- **Chrome browser**: ~200-500MB depending on page complexity
- **Large result sets**: Additional ~10-50MB per 1000 flights

## Development

### How do I contribute?
See the [Contributing Guide](contributing.md) for detailed instructions on:
- Development setup
- Code standards
- Testing requirements
- Pull request process

### How do I report bugs?
1. Check [existing issues](https://github.com/problemxl/ita-scrapper/issues)
2. Create new issue with:
   - Python version
   - Chrome version
   - Search parameters that failed
   - Complete error traceback
   - Minimal reproduction code

### Can I add support for other flight search sites?
The current architecture is specifically designed for ITA Matrix. Supporting other sites would require:
- New parser implementations
- Site-specific automation logic
- Different data models

Consider creating a separate library or contributing a plugin system.

## Troubleshooting

### Chrome crashes or won't start
1. **Update Chrome**: Ensure you have the latest version
2. **Check permissions**: Chrome needs appropriate system permissions
3. **Clear data**: Remove Chrome user data directory
4. **Try different flags**: Modify Chrome options in configuration

### Results seem incomplete or incorrect
1. **Verify manually**: Check same search on ITA Matrix website
2. **Update library**: Ensure you have the latest version
3. **Check parsing**: ITA Matrix may have changed their HTML structure
4. **Report issue**: Help improve the parser by reporting problems

### Searches are blocked or failing
1. **Check rate limiting**: Reduce search frequency
2. **Rotate user agents**: Use different browser signatures
3. **Clear cookies**: Reset browser session
4. **Try different networks**: Some networks may have restrictions

For more specific issues, see the [Troubleshooting Guide](troubleshooting.md).
# ITA Scrapper

[![PyPI version](https://badge.fury.io/py/ita-scrapper.svg)](https://badge.fury.io/py/ita-scrapper)
[![Python versions](https://img.shields.io/pypi/pyversions/ita-scrapper.svg)](https://pypi.org/project/ita-scrapper/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/yourusername/ita-scrapper/workflows/CI/badge.svg)](https://github.com/yourusername/ita-scrapper/actions)

A powerful Python library for scraping ITA Matrix flight data using Playwright. Get flight prices, schedules, and travel information programmatically with a clean, async API.

## ✨ Features

- 🛫 **Flight Search**: Search flights between any airports worldwide
- 📅 **Flexible Dates**: Support for one-way, round-trip, and multi-city searches  
- 💰 **Price Parsing**: Parse and normalize flight prices from various formats
- ⏱️ **Duration Handling**: Parse flight durations and format them consistently
- 🌍 **Airport Codes**: Validate and normalize IATA/ICAO airport codes
- 🎯 **Type Safety**: Full Pydantic model support with type hints
- ⚡ **Async Support**: Built with async/await for high performance
- � **Tested**: Comprehensive test suite with 95%+ coverage
- 🖥️ **CLI Interface**: Command-line tool for quick searches
- 🔧 **MCP Server**: Model Context Protocol server for AI integration

## 📦 Installation

```bash
pip install ita-scrapper
```

For development with all extras:
```bash
pip install ita-scrapper[dev,mcp]
```

### Install Playwright browsers:
```bash
playwright install chromium
```

## 🚀 Quick Start

### Python API

```python
import asyncio
from datetime import date, timedelta
from ita_scrapper import ITAScrapper, CabinClass

async def search_flights():
    async with ITAScrapper(headless=True) as scrapper:
        # Search for flights
        results = await scrapper.search_flights(
            origin="JFK",
            destination="LAX", 
            departure_date=date.today() + timedelta(days=30),
            return_date=date.today() + timedelta(days=37),
            adults=2,
            cabin_class=CabinClass.BUSINESS
        )
        
        # Print results
        for i, flight in enumerate(results.flights, 1):
            print(f"Flight {i}:")
            print(f"  Price: ${flight.price}")
            print(f"  Duration: {flight.duration}")
            print(f"  Stops: {flight.stops}")
            print(f"  Airline: {flight.airline}")
            print()

# Run the search
asyncio.run(search_flights())
```

### Command Line Interface

```bash
# Search for flights
ita-scrapper search --origin JFK --destination LAX \
    --departure-date 2024-08-15 --return-date 2024-08-22 \
    --adults 2 --cabin-class BUSINESS

# Parse flight data
ita-scrapper parse "2h 30m" --type duration
ita-scrapper parse "$1,234.56" --type price  
ita-scrapper parse "14:30" --type time --reference-date 2024-08-15

# Get help
ita-scrapper --help
```

## 📚 Documentation

### Quick Links

- **[📖 API Documentation](docs/api.md)** - Complete API reference with examples
- **[🔧 Developer Guide](docs/developer-guide.md)** - Architecture and extension guide  
- **[🚨 Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions
- **[📊 Project Summary](PROJECT_SUMMARY.md)** - High-level project overview

### API Documentation

Comprehensive API documentation is available in the [docs/api.md](docs/api.md) file, covering:

- **Core Classes**: ITAScrapper, ITAMatrixParser
- **Data Models**: Flight, SearchParams, FlightResult
- **Utility Functions**: Price parsing, duration formatting, validation
- **Exception Handling**: Complete error handling strategies
- **Best Practices**: Recommended usage patterns

### Developer Guide

For developers wanting to extend or contribute to ITA Scrapper, see [docs/developer-guide.md](docs/developer-guide.md):

- **Architecture Overview**: Component design and data flow
- **Parser Architecture**: Multi-strategy parsing system
- **Browser Automation**: Playwright integration and anti-detection
- **Extension Points**: Adding new parsers and data models
- **Debugging Guide**: Tools and techniques for troubleshooting
- **Performance Optimization**: Memory and speed optimization

### Troubleshooting

Having issues? Check [docs/troubleshooting.md](docs/troubleshooting.md) for solutions to:

- **Installation Issues**: Dependencies and browser setup
- **Website Access**: Blocking, CAPTCHAs, and rate limiting  
- **Parsing Problems**: Data extraction and validation issues
- **Performance**: Memory usage and speed optimization
- **Development Setup**: Environment configuration and debugging

## 🚀 Quick Start

### Core Classes

#### ITAScrapper
Main scraper class for flight searches.

```python
class ITAScrapper:
    def __init__(self, headless: bool = True, timeout: int = 30000):
        """Initialize the scrapper."""
        
    async def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        return_date: Optional[date] = None,
        adults: int = 1,
        children: int = 0,
        infants: int = 0,
        cabin_class: CabinClass = CabinClass.ECONOMY
    ) -> FlightResult:
        """Search for flights."""
```

#### Models

```python
from ita_scrapper import (
    Flight,           # Individual flight details
    FlightResult,     # Search results container
    SearchParams,     # Search parameters
    CabinClass,       # Enum for cabin classes
    TripType,         # Enum for trip types
    Airport,          # Airport information
)
```

### Utility Functions

```python
from ita_scrapper import (
    parse_price,           # Parse price strings
    parse_duration,        # Parse duration strings
    parse_time,            # Parse time strings  
    validate_airport_code, # Validate airport codes
    format_duration,       # Format durations
    is_valid_date_range,   # Validate date ranges
)

# Examples
price = parse_price("$1,234.56")  # Returns Decimal('1234.56')
duration = parse_duration("2h 30m")  # Returns 150 (minutes)
code = validate_airport_code("jfk")  # Returns "JFK"
```

## 🎯 Advanced Usage

### Context Manager
```python
# Recommended: Use as context manager
async with ITAScrapper(headless=True) as scrapper:
    results = await scrapper.search_flights(...)

# Manual management
scrapper = ITAScrapper()
await scrapper.start()
try:
    results = await scrapper.search_flights(...)
finally:
    await scrapper.close()
```

### Error Handling
```python
from ita_scrapper import ITAScrapperError, NavigationError, TimeoutError

try:
    async with ITAScrapper() as scrapper:
        results = await scrapper.search_flights(...)
except NavigationError:
    print("Failed to navigate to search page")
except TimeoutError:
    print("Search timed out")
except ITAScrapperError as e:
    print(f"General error: {e}")
```

### Custom Configuration
```python
scrapper = ITAScrapper(
    headless=False,        # Show browser window
    timeout=60000,         # 60 second timeout
)
```

## 🧪 Testing

Run the test suite:

```bash
# All tests
pytest

# Unit tests only (fast)  
pytest -m "not slow"

# Integration tests (slow, requires browser)
pytest -m slow

# With coverage
pytest --cov=src/ita_scrapper --cov-report=html
```

## 🔧 MCP Server

Use ITA Scrapper as a Model Context Protocol server:

```python
# Install MCP support
pip install ita-scrapper[mcp]

# Create MCP server (see examples/mcp_integration.py)
from ita_scrapper.mcp import create_mcp_server
server = create_mcp_server()
```

Configure in Claude Desktop:
```json
{
  "mcpServers": {
    "ita-scrapper": {
      "command": "python",
      "args": ["/path/to/ita_scrapper_mcp_server.py"]
    }
  }
}
```

## 🌟 Examples

Check out the `/examples` directory for more usage examples:

- `basic_usage.py` - Simple flight search
- `demo_usage.py` - Interactive demo
- `matrix_examples.py` - Advanced search patterns
- `mcp_integration.py` - MCP server setup
- `test_real_sites.py` - Real-world testing

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/ita-scrapper.git
cd ita-scrapper

# Install with uv (recommended)
uv sync --all-extras

# Install Playwright browsers
uv run playwright install

# Run tests
uv run pytest

# Run linting
uv run ruff check .
uv run ruff format .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational and research purposes only. Please respect the terms of service of any websites you scrape and be mindful of rate limits. The authors are not responsible for any misuse of this software.

## 🙋‍♂️ Support

- 📖 [Documentation](https://github.com/yourusername/ita-scrapper#readme)
- 🐛 [Issue Tracker](https://github.com/yourusername/ita-scrapper/issues)
- 💬 [Discussions](https://github.com/yourusername/ita-scrapper/discussions)

## 📊 Stats

- **Language**: Python 3.10+
- **Framework**: Playwright + Pydantic
- **Test Coverage**: 95%+
- **Dependencies**: Minimal, well-maintained
- **Performance**: Async/await optimized

---

Made with ❤️ for travel enthusiasts and developers!

# ITA Scrapper

Professional flight search automation with ITA Matrix scraping capabilities.

## Overview

ITA Scrapper is a powerful Python library for automating flight searches using the ITA Matrix platform. It provides a clean, type-safe interface for searching flights, parsing results, and handling complex travel scenarios.

## Key Features

- **Automated Flight Search**: Search for flights using natural language queries
- **Multi-layered Parsing**: Robust parsing system with fallback strategies
- **Type Safety**: Full Pydantic model validation for all data structures
- **Browser Automation**: Headless Chrome integration for dynamic content
- **Flexible Search**: Support for complex routing, multi-city trips, and date ranges
- **Error Handling**: Comprehensive exception handling with recovery strategies

## Quick Start

```python
from ita_scrapper import ITAScrapper

# Initialize the scrapper
scrapper = ITAScrapper()

# Search for flights
results = scrapper.search_flights(
    origin="NYC",
    destination="LAX", 
    departure_date="2024-03-15"
)

# Process results
for flight in results.flights:
    print(f"{flight.airline} - ${flight.price}")
```

## Installation

```bash
pip install ita-scrapper
```

For development:
```bash
git clone https://github.com/problemxl/ita-scrapper
cd ita-scrapper
uv pip install -e ".[dev]"
```

## Documentation Structure

- **[Getting Started](getting-started/installation.md)**: Installation and basic usage
- **[API Reference](api.md)**: Complete API documentation
- **[Developer Guide](developer-guide.md)**: Architecture and contributing
- **[Troubleshooting](troubleshooting.md)**: Common issues and solutions

## Support

- GitHub Issues: [Report bugs and request features](https://github.com/problemxl/ita-scrapper/issues)
- Documentation: This site provides comprehensive guides and API reference
- Examples: Check out the `examples/` directory for real-world usage patterns
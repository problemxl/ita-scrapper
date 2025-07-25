# Testing Guide

## Test Organization

The test suite is organized to mirror the source code structure:

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── test_integration.py      # End-to-end integration tests
├── test_models.py          # Pydantic model validation tests
├── test_utils.py           # Utility function tests
├── test_scrapper.py        # Core scrapper functionality
├── test_parsers.py         # HTML parsing tests
└── test_exceptions.py      # Exception handling tests
```

## Running Tests

### Basic Test Execution
```bash
# Run all tests
uv run pytest -v

# Run specific test file
uv run pytest -v tests/test_models.py

# Run specific test function
uv run pytest -v -k "test_search_flights"

# Run tests matching pattern
uv run pytest -v -k "flight and not integration"
```

### Test Categories

#### Unit Tests (Fast)
```bash
# Run only unit tests (exclude integration)
uv run pytest -v -m "not integration"
```

#### Integration Tests (Slower)
```bash
# Run only integration tests
uv run pytest -v -m integration

# Skip integration tests
uv run pytest -v -m "not integration"
```

### Test Coverage
```bash
# Run tests with coverage report
uv run pytest --cov=src/ita_scrapper --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Writing Tests

### Test Structure

Follow the Arrange-Act-Assert pattern:

```python
def test_should_parse_flight_when_valid_html():
    # Arrange
    html_content = load_test_html("valid_flight.html")
    parser = ITAMatrixParser()
    
    # Act
    result = parser.parse_flights(html_content)
    
    # Assert
    assert len(result.flights) == 1
    assert result.flights[0].price == 299.99
    assert result.flights[0].airline == "Delta"
```

### Using Fixtures

Common test data and objects are provided via fixtures:

```python
def test_search_with_valid_params(mock_scrapper, sample_search_params):
    # Use pre-configured mock scrapper and sample parameters
    result = mock_scrapper.search_flights_with_params(sample_search_params)
    assert result.success
```

Available fixtures (see `conftest.py`):
- `mock_scrapper`: Pre-configured ITAScrapper with mocked browser
- `sample_search_params`: Valid SearchParams instance
- `sample_flight_data`: Mock flight data for testing
- `mock_browser`: Selenium WebDriver mock

### Mocking External Dependencies

#### Browser Automation
```python
from unittest.mock import patch, MagicMock

@patch('ita_scrapper.scrapper.webdriver.Chrome')
def test_browser_initialization(mock_chrome):
    mock_driver = MagicMock()
    mock_chrome.return_value = mock_driver
    
    scrapper = ITAScrapper()
    scrapper._initialize_browser()
    
    mock_chrome.assert_called_once()
    assert scrapper.driver == mock_driver
```

#### Network Requests
```python
import responses

@responses.activate
def test_api_call():
    responses.add(
        responses.GET,
        'https://matrix.itasoftware.com/search',
        json={'flights': []},
        status=200
    )
    
    # Test code that makes HTTP requests
    result = make_api_call()
    assert result == {'flights': []}
```

### Testing Error Conditions

```python
import pytest
from ita_scrapper.exceptions import NetworkError, ParsingError

def test_should_raise_network_error_when_connection_fails():
    with patch('requests.get', side_effect=ConnectionError()):
        with pytest.raises(NetworkError, match="Connection failed"):
            scrapper.search_flights("NYC", "LAX", "2024-03-15")

def test_should_handle_invalid_html_gracefully():
    parser = ITAMatrixParser()
    
    with pytest.raises(ParsingError):
        parser.parse_flights("<invalid>html</invalid>")
```

### Parameterized Tests

Test multiple scenarios efficiently:

```python
@pytest.mark.parametrize("origin,destination,expected", [
    ("NYC", "LAX", True),
    ("New York", "Los Angeles", True),
    ("", "LAX", False),
    ("NYC", "", False),
])
def test_validate_route_inputs(origin, destination, expected):
    is_valid = validate_route(origin, destination)
    assert is_valid == expected
```

### Async Testing

For asynchronous functionality:

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_search():
    scrapper = ITAScrapper()
    
    result = await scrapper.search_flights_async("NYC", "LAX", "2024-03-15")
    
    assert result.success
    assert len(result.flights) > 0
```

## Integration Testing

### Real Browser Testing

Mark tests that require real browser interaction:

```python
@pytest.mark.integration
@pytest.mark.slow
def test_full_search_workflow():
    """Test complete search workflow with real browser."""
    scrapper = ITAScrapper(headless=True)
    
    try:
        result = scrapper.search_flights("NYC", "LAX", "2024-03-15")
        assert result.success
        assert len(result.flights) > 0
    finally:
        scrapper.close()
```

### Test Data Management

Use realistic test data for integration tests:

```python
# tests/data/sample_responses.py
SAMPLE_ITA_HTML = """
<div class="flight-result">
    <span class="price">$299</span>
    <span class="airline">Delta</span>
    <!-- ... more realistic HTML ... -->
</div>
"""

def load_test_html(filename: str) -> str:
    """Load HTML test data from tests/data/ directory."""
    test_data_dir = Path(__file__).parent / "data"
    return (test_data_dir / filename).read_text()
```

## Performance Testing

### Benchmark Critical Paths

```python
import time
import pytest

@pytest.mark.performance
def test_parsing_performance():
    """Ensure parsing large HTML doesn't exceed time limits."""
    large_html = generate_large_flight_html(1000)  # 1000 flights
    parser = ITAMatrixParser()
    
    start_time = time.time()
    result = parser.parse_flights(large_html)
    end_time = time.time()
    
    # Should parse 1000 flights in under 5 seconds
    assert end_time - start_time < 5.0
    assert len(result.flights) == 1000
```

### Memory Usage Testing

```python
import psutil
import os

@pytest.mark.performance
def test_memory_usage():
    """Ensure scrapper doesn't leak memory during long operations."""
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    scrapper = ITAScrapper()
    
    # Perform multiple searches
    for i in range(10):
        scrapper.search_flights("NYC", "LAX", "2024-03-15")
    
    final_memory = process.memory_info().rss
    memory_growth = final_memory - initial_memory
    
    # Memory growth should be reasonable (< 100MB)
    assert memory_growth < 100 * 1024 * 1024
```

## Test Configuration

### Custom Test Markers

Define in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = [
    "integration: marks tests as integration tests (may be slow)",
    "performance: marks tests as performance benchmarks",
    "slow: marks tests as slow running",
    "network: marks tests that require network access"
]
```

### Environment-Specific Testing

```python
import os
import pytest

@pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason="Skipping browser tests in CI environment"
)
def test_browser_functionality():
    # Test that requires interactive browser
    pass

@pytest.mark.skipif(
    not os.getenv("INTEGRATION_TESTS"),
    reason="Integration tests disabled"
)
def test_real_api_integration():
    # Test against real ITA Matrix
    pass
```

## Debugging Tests

### Verbose Output
```bash
# Show print statements and detailed output
uv run pytest -v -s

# Show local variables on failure
uv run pytest --tb=long

# Drop into debugger on failure
uv run pytest --pdb
```

### Test-Specific Browser Debugging

```python
@pytest.mark.integration
def test_search_with_browser_debug():
    # Run with visible browser for debugging
    scrapper = ITAScrapper(headless=False, debug=True)
    
    # Add breakpoint for manual inspection
    import pdb; pdb.set_trace()
    
    result = scrapper.search_flights("NYC", "LAX", "2024-03-15")
```

## Continuous Integration

### GitHub Actions Integration

Tests run automatically on:
- Pull requests
- Pushes to main branch
- Scheduled runs (nightly)

### Test Matrix

CI runs tests across:
- Python versions: 3.9, 3.10, 3.11, 3.12
- Operating systems: Ubuntu, macOS, Windows
- Chrome versions: Latest stable, beta

### Flaky Test Handling

For tests that occasionally fail due to external factors:

```python
@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_external_api_call():
    # Test that might fail due to network issues
    # Will retry up to 3 times with 2-second delay
    pass
```
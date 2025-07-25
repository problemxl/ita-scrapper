"""
Custom exception hierarchy for ITA Scrapper error handling.

This module defines a comprehensive set of exceptions for handling various
error conditions that can occur during flight data scraping operations.
The exceptions are organized in a hierarchy to allow for both specific
error handling and broad exception catching.

Exception Hierarchy:
    ITAScrapperError (base)
    ├── NavigationError (website access issues)
    ├── ParseError (data parsing failures)
    ├── ITATimeoutError (operation timeouts)
    └── ValidationError (input validation failures)

Each exception includes contextual information to help with debugging
and error recovery. The hierarchy allows code to catch specific exceptions
for targeted handling or catch the base ITAScrapperError for general
error handling.

Usage:
    try:
        result = await scrapper.search_flights("JFK", "LAX", date.today())
    except NavigationError as e:
        print(f"Could not access website: {e}")
    except ParseError as e:
        print(f"Could not parse results: {e}")
    except ITAScrapperError as e:
        print(f"General scraping error: {e}")
"""


class ITAScrapperError(Exception):
    """
    Base exception class for all ITA Scrapper related errors.

    This is the parent class for all custom exceptions in the ITA Scrapper
    library. It provides a common base for exception handling and allows
    code to catch all library-specific errors with a single except clause.

    Use this exception directly for general errors that don't fit into
    more specific categories, or catch it to handle any error from the
    ITA Scrapper library.

    Attributes:
        message: Error message describing what went wrong

    Example:
        >>> try:
        ...     # Some ITA Scrapper operation
        ...     pass
        ... except ITAScrapperError as e:
        ...     print(f"Scrapper error occurred: {e}")
        ...     logger.error(f"Error details: {e}")
    """

    pass


class NavigationError(ITAScrapperError):
    """
    Raised when navigation to travel booking websites fails.

    This exception occurs when the scrapper cannot access the target
    website (ITA Matrix or Google Flights) due to network issues,
    website blocking, or other access-related problems.

    Common Causes:
    - Network connectivity issues
    - Website blocking automated access (CAPTCHA, bot detection)
    - Website temporarily unavailable (maintenance, outages)
    - HTTP errors (404, 500, etc.)
    - DNS resolution failures
    - SSL/TLS certificate issues

    Recovery Strategies:
    - Retry with exponential backoff
    - Switch to alternative website (Google Flights vs ITA Matrix)
    - Check network connectivity
    - Verify website accessibility manually
    - Implement proxy rotation if blocked

    Example:
        >>> try:
        ...     await scrapper._navigate_to_flights()
        ... except NavigationError as e:
        ...     print(f"Cannot access website: {e}")
        ...     # Try alternative approach or notify user
    """

    pass


class ParseError(ITAScrapperError):
    """
    Raised when parsing flight data from website content fails.

    This exception occurs when the scrapper successfully loads a page
    but cannot extract meaningful flight data from the content. This
    typically happens when website layouts change, elements are missing,
    or data is in an unexpected format.

    Common Causes:
    - Website layout or structure changes
    - CSS selectors no longer matching elements
    - Data format changes (price, time, airline format)
    - Missing or empty result containers
    - JavaScript errors preventing content loading
    - Incomplete page loading before parsing

    Recovery Strategies:
    - Retry with longer wait times for page loading
    - Update CSS selectors and parsing logic
    - Fall back to alternative parsing strategies
    - Verify page state before parsing
    - Use demo mode for testing/development

    Example:
        >>> try:
        ...     flights = await parser.parse_flight_results(page)
        ... except ParseError as e:
        ...     print(f"Could not parse flight data: {e}")
        ...     # Fall back to alternative parsing or demo data
    """

    pass


class ITATimeoutError(ITAScrapperError):
    """
    Raised when scrapper operations exceed their allowed time limits.

    This exception occurs when operations take longer than expected,
    which can happen with slow websites, complex searches, or network
    issues. Different operations have different timeout thresholds.

    Common Causes:
    - Slow website response times
    - Complex flight searches with many results
    - Network latency or bandwidth issues
    - Website under heavy load
    - Large result sets requiring extensive parsing
    - Browser automation delays

    Timeout Categories:
    - Page navigation timeouts (30s default)
    - Element wait timeouts (varies by operation)
    - Search completion timeouts (site-dependent)
    - Parsing operation timeouts (internal limits)

    Recovery Strategies:
    - Increase timeout values for complex operations
    - Retry with reduced search scope (fewer results)
    - Check network performance
    - Use headless mode for faster execution
    - Implement progressive timeout strategies

    Example:
        >>> try:
        ...     await scrapper.search_flights("JFK", "LAX", date.today())
        ... except ITATimeoutError as e:
        ...     print(f"Operation timed out: {e}")
        ...     # Retry with increased timeout or smaller scope
    """

    pass


class ValidationError(ITAScrapperError):
    """
    Raised when input validation fails for search parameters or data.

    This exception occurs when user-provided inputs don't meet the
    requirements for flight searches or other operations. It helps
    catch problems early before attempting network operations.

    Common Validation Failures:
    - Invalid airport codes (wrong length, non-alphabetic)
    - Invalid date ranges (past dates, return before departure)
    - Invalid passenger counts (negative, exceeding limits)
    - Missing required parameters (origin, destination, dates)
    - Invalid cabin class or trip type values
    - Malformed input formats

    Validation Rules:
    - Airport codes: 3-letter IATA or 4-letter ICAO format
    - Dates: Today or future, reasonable advance booking window
    - Passengers: Positive counts within airline limits
    - Trip types: Valid enum values
    - Price/duration formats: Parseable numeric values

    Example:
        >>> try:
        ...     params = SearchParams(origin="INVALID", destination="LAX")
        ... except ValidationError as e:
        ...     print(f"Invalid search parameters: {e}")
        ...     # Prompt user for correct input format

        >>> try:
        ...     airport_code = validate_airport_code("12A")
        ... except ValidationError as e:
        ...     print(f"Invalid airport code: {e}")
    """

    pass

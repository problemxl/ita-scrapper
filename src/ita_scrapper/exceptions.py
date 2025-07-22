"""
Custom exceptions for ITA Scrapper.
"""


class ITAScrapperError(Exception):
    """Base exception for all ITA Scrapper errors."""

    pass


class NavigationError(ITAScrapperError):
    """Raised when navigation to ITA website fails."""

    pass


class ParseError(ITAScrapperError):
    """Raised when parsing flight data fails."""

    pass


class ITATimeoutError(ITAScrapperError):
    """Raised when operations timeout."""

    pass


class ValidationError(ITAScrapperError):
    """Raised when input validation fails."""

    pass

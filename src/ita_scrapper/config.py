"""
Configuration settings for ITA Scrapper.
"""

import os
from typing import Any, ClassVar


class Config:
    """Configuration class for ITA Scrapper."""

    # Browser settings
    DEFAULT_TIMEOUT = int(os.getenv("ITA_TIMEOUT", "30000"))  # milliseconds
    DEFAULT_HEADLESS = os.getenv("ITA_HEADLESS", "true").lower() == "true"
    DEFAULT_VIEWPORT = (
        int(os.getenv("ITA_VIEWPORT_WIDTH", "1920")),
        int(os.getenv("ITA_VIEWPORT_HEIGHT", "1080")),
    )

    # User agents for different browsers
    USER_AGENTS: ClassVar[dict[str, str]] = {
        "chrome": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "firefox": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/121.0",
        "safari": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
        ),
    }

    # Scraping settings
    MAX_RETRIES = int(os.getenv("ITA_MAX_RETRIES", "3"))
    RETRY_DELAY = float(os.getenv("ITA_RETRY_DELAY", "1.0"))  # seconds
    MAX_RESULTS_DEFAULT = int(os.getenv("ITA_MAX_RESULTS", "20"))

    # Rate limiting
    REQUEST_DELAY = float(
        os.getenv("ITA_REQUEST_DELAY", "0.5")
    )  # seconds between requests

    # Logging
    LOG_LEVEL = os.getenv("ITA_LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # URLs
    GOOGLE_FLIGHTS_URL = "https://www.google.com/travel/flights"
    ITA_MATRIX_URL = "https://matrix.itasoftware.com/search"

    # CSS Selectors for Google Flights
    GOOGLE_SELECTORS: ClassVar[dict[str, str]] = {
        "flight_card": '[data-testid="flight-card"]',
        "price": '[data-testid="price"]',
        "airline": '[data-testid="airline"]',
        "departure_time": '[data-testid="departure-time"]',
        "arrival_time": '[data-testid="arrival-time"]',
        "duration": '[data-testid="duration"]',
        "stops": '[data-testid="stops"]',
        "search_button": 'button[aria-label*="Search"]',
        "origin_input": 'input[placeholder*="Where from"]',
        "destination_input": 'input[placeholder*="Where to"]',
        "departure_date": 'input[placeholder*="Departure"]',
        "return_date": 'input[placeholder*="Return"]',
        "passengers_button": 'button[aria-label*="passenger"]',
        "cabin_class_button": 'button[aria-label*="class"]',
        "one_way_button": 'button[aria-label*="One way"]',
        "round_trip_button": 'button[aria-label*="Round trip"]',
        "multi_city_button": 'button[aria-label*="Multi-city"]',
        "flexible_dates_button": 'button[aria-label*="Flexible dates"]',
    }

    # CSS Selectors for ITA Matrix (Updated for Angular Material)
    ITA_MATRIX_SELECTORS: ClassVar[dict[str, str]] = {
        "flight_card": ".itinerary, .mat-mdc-card",
        "price": ".price, .currency, .mat-mdc-card .price-value",
        "airline": ".airline, .airline-name",
        "departure_time": ".departure-time, .time-departure",
        "arrival_time": ".arrival-time, .time-arrival",
        "duration": ".duration, .flight-duration",
        "stops": ".stops, .stop-info",
        "search_button": 'button.mat-mdc-raised-button[type="submit"], button[type="submit"]',
        "origin_input": 'matrix-location-field[formcontrolname="origin"] input, input[placeholder*="From"]',
        "destination_input": 'matrix-location-field[formcontrolname="destination"] input, input[placeholder*="To"]',
        "departure_date": 'input.mat-datepicker-input, input[placeholder*="Departure"]',
        "return_date": 'input.mat-datepicker-input.mat-end-date, input[placeholder*="Return"]',
        "one_way_tab": '#mat-tab-group-0-label-1, div[role="tab"]:has-text("One way")',
        "round_trip_tab": '#mat-tab-group-0-label-0, div[role="tab"]:has-text("Round trip")',
        "passengers_input": 'input[name="passengers"], .mat-mdc-form-field.pax-field input',
        "cabin_class_select": 'select[name="class"], mat-select[formcontrolname="cabinClass"]',
    }

    # Legacy selectors (kept for backward compatibility)
    SELECTORS = GOOGLE_SELECTORS

    # XPath selectors as backup
    XPATH_SELECTORS: ClassVar[dict[str, str]] = {
        "flight_cards": "//div[contains(@class, 'flight-card')]",
        "price": ".//span[contains(@class, 'price')]",
        "airline_logo": ".//img[contains(@alt, 'airline')]",
    }

    @classmethod
    def get_browser_args(cls) -> list[str]:
        """Get browser launch arguments."""
        return [
            "--no-sandbox",
            "--disable-blink-features=AutomationControlled",
            "--disable-web-security",
            "--disable-features=VizDisplayCompositor",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-dev-shm-usage",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-extensions",
            "--disable-plugins",
            "--disable-default-apps",
        ]

    @classmethod
    def get_context_options(cls) -> dict[str, Any]:
        """Get browser context options."""
        return {
            "viewport": {
                "width": cls.DEFAULT_VIEWPORT[0],
                "height": cls.DEFAULT_VIEWPORT[1],
            },
            "user_agent": cls.USER_AGENTS["chrome"],
            "locale": "en-US",
            "timezone_id": "America/New_York",
            "permissions": [],
            "extra_http_headers": {
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;q=0.9,"
                    "image/webp,*/*;q=0.8"
                ),
            },
        }


# Environment-specific configs
DEVELOPMENT_CONFIG = {
    "headless": False,
    "timeout": 60000,
    "log_level": "DEBUG",
}

PRODUCTION_CONFIG = {
    "headless": True,
    "timeout": 30000,
    "log_level": "WARNING",
}

TESTING_CONFIG = {
    "headless": True,
    "timeout": 10000,
    "log_level": "ERROR",
}


def get_config(environment: str = "development") -> dict[str, Any]:
    """
    Get configuration for specific environment.

    Args:
        environment: Environment name (development, production, testing)

    Returns:
        Configuration dictionary
    """
    base_config = {
        "timeout": Config.DEFAULT_TIMEOUT,
        "headless": Config.DEFAULT_HEADLESS,
        "viewport": Config.DEFAULT_VIEWPORT,
        "max_retries": Config.MAX_RETRIES,
        "retry_delay": Config.RETRY_DELAY,
        "request_delay": Config.REQUEST_DELAY,
        "log_level": Config.LOG_LEVEL,
    }

    env_configs = {
        "development": DEVELOPMENT_CONFIG,
        "production": PRODUCTION_CONFIG,
        "testing": TESTING_CONFIG,
    }

    env_config = env_configs.get(environment, {})
    base_config.update(env_config)

    return base_config

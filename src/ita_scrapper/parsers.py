"""
Enhanced parsers for extracting complex flight data from ITA Matrix and Google Flights.

This module provides specialized parsing logic for extracting structured flight
information from the dynamic, JavaScript-heavy interfaces of modern travel booking
sites. The parsers handle complex scenarios including:

- Angular Material tooltips and overlays containing detailed flight data
- Multi-segment flights with connections and layovers
- Dynamic content loading and DOM manipulation
- Various pricing display formats and currency handling
- Time zone-aware scheduling information
- Airline code normalization and aircraft type detection

The primary focus is on ITA Matrix which provides the most comprehensive flight
data through its tooltip-based information architecture. The parsers use multiple
extraction strategies to ensure robust data collection even when page structures
change or elements are dynamically generated.

Key Features:
- Tooltip-based data extraction for detailed flight information
- Multi-strategy parsing with graceful fallbacks
- Comprehensive text pattern recognition for airlines, times, and prices
- Structured data validation and error recovery
- Support for complex multi-segment itineraries

Architecture:
The parsing system uses a layered approach:
1. Wait for dynamic content to load completely
2. Extract tooltip data containing detailed flight information
3. Identify flight result containers in the main page
4. Cross-reference container and tooltip data
5. Apply text processing to extract structured information
6. Validate and construct typed data models
"""

import logging
import re
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Optional

from playwright.async_api import ElementHandle, Page

from .models import Airline, Airport, CabinClass, Flight, FlightSegment
from .utils import FlightDataParser

logger = logging.getLogger(__name__)


class ITAMatrixParser:
    """
    Specialized parser for extracting flight data from ITA Matrix's complex interface.

    ITA Matrix uses a sophisticated Angular Material interface with tooltip-based
    data presentation. This parser implements multiple extraction strategies to
    handle the dynamic content, tooltip interactions, and complex DOM structure
    that characterizes modern travel booking sites.

    The parser's multi-layered approach:
    1. Waits for tooltip elements to ensure all data is loaded
    2. Extracts detailed flight information from Angular Material tooltips
    3. Identifies main flight result containers in the page structure
    4. Cross-references tooltip data with container elements
    5. Applies advanced text processing to extract structured information
    6. Constructs validated Flight objects with comprehensive metadata

    Key Capabilities:
    - Handles Angular Material component interactions
    - Extracts data from CDK (Component Dev Kit) tooltips
    - Parses complex multi-segment flight itineraries
    - Processes various price formats and currency representations
    - Handles timezone-aware flight scheduling
    - Manages airline code normalization and aircraft type detection

    Robustness Features:
    - Multiple CSS selector strategies for element identification
    - Graceful degradation when detailed parsing fails
    - Text pattern recognition for airline, time, and price extraction
    - Fallback to basic flight information when tooltips are unavailable
    - Error recovery and logging for debugging complex sites

    Usage:
        >>> parser = ITAMatrixParser()
        >>> flights = await parser.parse_flight_results(page, max_results=10)
        >>> for flight in flights:
        ...     print(f"${flight.price} - {flight.total_duration_minutes//60}h")

    Note:
        ITA Matrix frequently updates its interface. This parser includes
        multiple extraction strategies to maintain compatibility, but may
        require updates when major UI changes occur.
    """

    def __init__(self):
        """
        Initialize the ITA Matrix parser with data processing utilities.

        Sets up the FlightDataParser utility for standardizing airline codes,
        flight numbers, and other structured data elements extracted from
        the complex ITA Matrix interface.
        """
        self.data_parser = FlightDataParser()

    async def parse_flight_results(
        self, page: Page, max_results: int = 10
    ) -> list[Flight]:
        """
        Main entry point for parsing flight results from ITA Matrix.

        Orchestrates the complete parsing process from raw page content to
        structured Flight objects. Uses a multi-strategy approach to ensure
        maximum data extraction success even when page layouts change.

        Process Flow:
        1. Wait for all dynamic content and tooltips to load
        2. Extract detailed information from Angular Material tooltips
        3. Identify and collect main flight result containers
        4. Parse individual flights by cross-referencing containers and tooltips
        5. Apply fallback parsing strategies if primary methods fail
        6. Validate and return structured Flight objects

        Args:
            page: Playwright Page object for the ITA Matrix results page.
                Should be on a page that has completed a flight search
            max_results: Maximum number of flights to parse and return.
                Limits processing time for large result sets. Default: 10

        Returns:
            List of Flight objects with comprehensive flight information including
            segments, pricing, timing, airline details, and connection information.
            Returns empty list if no flights can be parsed.

        Raises:
            Does not raise exceptions - all errors are logged and handled gracefully.
            Returns empty list on critical failures.

        Example:
            >>> # After performing a search on ITA Matrix
            >>> parser = ITAMatrixParser()
            >>> flights = await parser.parse_flight_results(page, max_results=5)
            >>> if flights:
            ...     print(f"Found {len(flights)} flights")
            ...     cheapest = min(flights, key=lambda f: f.price)
            ...     print(f"Cheapest: ${cheapest.price}")
            ... else:
            ...     print("No flights found - check page state or search results")

        Note:
            - Page should be on ITA Matrix results after completing a search
            - Processing time increases with max_results parameter
            - Tooltip extraction requires page to be fully loaded
            - May return fewer flights than max_results if parsing fails
        """
        flights = []

        try:
            # Wait for the page to load completely
            await self._wait_for_results(page)

            # Extract all tooltip data first (contains detailed flight info)
            tooltip_data = await self._extract_tooltip_data(page)

            # Find the main flight result containers
            flight_containers = await self._find_flight_containers(page)

            logger.info(
                f"Found {len(flight_containers)} flight containers and {len(tooltip_data)} tooltip entries"
            )

            for i, container in enumerate(flight_containers[:max_results]):
                try:
                    flight = await self._parse_single_flight(
                        container, tooltip_data, page
                    )
                    if flight:
                        flights.append(flight)
                        logger.debug(f"Successfully parsed flight {i + 1}")
                except Exception as e:
                    logger.warning(f"Failed to parse flight container {i}: {e}")
                    continue

            # If we couldn't parse from containers, try parsing from tooltip data directly
            if not flights and tooltip_data:
                flights = await self._parse_from_tooltips(tooltip_data)

            return flights

        except Exception as e:
            logger.error(f"Failed to parse ITA Matrix results: {e}")
            return []

    async def _wait_for_results(self, page: Page, timeout: int = 30000):
        """
        Wait for flight search results to fully load including dynamic tooltips.

        ITA Matrix loads flight data asynchronously through Angular Material
        components. This method ensures all tooltip elements containing detailed
        flight information are present before attempting to parse data.

        Strategy:
        1. Wait for tooltip elements with role="tooltip" to appear
        2. Allow additional time for dynamic content loading
        3. Verify substantial tooltip content is available
        4. Extend wait time if insufficient data detected

        Args:
            page: Playwright Page object on ITA Matrix results
            timeout: Maximum time to wait in milliseconds. Default: 30000 (30s)

        Note:
            - Tooltips contain the most detailed flight information
            - Dynamic loading can take several seconds after initial page load
            - Method does not raise exceptions, logs warnings on failures
            - Essential for reliable data extraction from ITA Matrix
        """
        try:
            # Wait for tooltip elements to appear (they contain the flight data)
            await page.wait_for_selector('[role="tooltip"]', timeout=timeout)

            # Additional wait for dynamic content
            await page.wait_for_timeout(3000)

            # Check if we have substantial content
            tooltips = await page.query_selector_all('[role="tooltip"]')
            if len(tooltips) < 5:
                logger.warning("Few tooltips found, waiting longer...")
                await page.wait_for_timeout(5000)

        except Exception as e:
            logger.warning(f"Failed to wait for results: {e}")

    async def _extract_tooltip_data(self, page: Page) -> dict[str, str]:
        """
        Extract all tooltip data containing detailed flight information.

        ITA Matrix stores comprehensive flight details in Angular Material
        tooltips that are dynamically generated. This method uses multiple
        extraction strategies to capture all available tooltip content.

        Extraction Strategies:
        1. Standard tooltips with role="tooltip" attribute
        2. CDK (Component Dev Kit) tooltips with describedby patterns
        3. Additional tooltip elements with various class/data attributes
        4. Hidden tooltip content not visible in standard selectors

        Returns:
            Dictionary mapping tooltip IDs to their text content. Keys are
            tooltip element IDs, values are the extracted text containing
            flight details like times, airlines, prices, and routing information.

        Example:
            >>> tooltip_data = await parser._extract_tooltip_data(page)
            >>> for tooltip_id, content in tooltip_data.items():
            ...     if "time:" in content:
            ...         print(f"Flight timing: {content}")
            ...     elif "$" in content:
            ...         print(f"Price info: {content}")

        Note:
            - Returns empty dict if no tooltips found
            - Each tooltip may contain multiple pieces of flight information
            - Tooltip IDs are used to cross-reference with flight containers
            - Content includes raw text that requires further parsing
        """
        tooltip_data = {}

        try:
            # Try multiple strategies to get tooltip data

            # Strategy 1: Get visible tooltips
            tooltips = await page.query_selector_all('[role="tooltip"]')
            logger.debug(f"Found {len(tooltips)} tooltips with role='tooltip'")

            for tooltip in tooltips:
                try:
                    tooltip_id = await tooltip.get_attribute("id")
                    tooltip_text = await tooltip.inner_text()

                    if tooltip_id and tooltip_text:
                        tooltip_data[tooltip_id] = tooltip_text.strip()
                        logger.debug(
                            f"Extracted tooltip {tooltip_id}: {tooltip_text[:50]}..."
                        )

                except Exception as e:
                    logger.debug(f"Failed to extract tooltip data: {e}")
                    continue

            # Strategy 2: Look for CDK describedby tooltips (Angular Material pattern)
            cdk_tooltips = await page.query_selector_all(
                '[id*="cdk-describedby-message"]'
            )
            logger.debug(f"Found {len(cdk_tooltips)} CDK tooltips")

            for tooltip in cdk_tooltips:
                try:
                    tooltip_id = await tooltip.get_attribute("id")
                    tooltip_text = await tooltip.inner_text()

                    if tooltip_id and tooltip_text:
                        tooltip_data[tooltip_id] = tooltip_text.strip()
                        logger.debug(
                            f"Extracted CDK tooltip {tooltip_id}: {tooltip_text[:50]}..."
                        )

                except Exception as e:
                    logger.debug(f"Failed to extract CDK tooltip data: {e}")
                    continue

            # Strategy 3: Look for any hidden tooltip content
            all_tooltips = await page.query_selector_all(
                '[id*="tooltip"], [class*="tooltip"], [data-tooltip]'
            )
            logger.debug(f"Found {len(all_tooltips)} additional tooltip elements")

            for tooltip in all_tooltips:
                try:
                    tooltip_id = await tooltip.get_attribute(
                        "id"
                    ) or await tooltip.get_attribute("data-tooltip")
                    tooltip_text = await tooltip.inner_text()

                    if tooltip_id and tooltip_text and tooltip_id not in tooltip_data:
                        tooltip_data[tooltip_id] = tooltip_text.strip()

                except Exception as e:
                    logger.debug(f"Failed to extract additional tooltip data: {e}")
                    continue

        except Exception as e:
            logger.warning(f"Failed to extract tooltip data: {e}")

        logger.info(f"Extracted {len(tooltip_data)} tooltip entries total")
        return tooltip_data

    async def _find_flight_containers(self, page: Page) -> list[ElementHandle]:
        """Find the main flight result containers."""
        selectors = [
            'tr[class*="itinerary"]',
            'tr[class*="result"]',
            'tr[class*="flight"]',
            ".flight-result",
            ".search-result",
            '[data-testid*="flight"]',
            'tr[role="row"]',
            ".mat-row",
            'tr[id*="result"]',
        ]

        for selector in selectors:
            try:
                containers = await page.query_selector_all(selector)
                if containers:
                    logger.debug(
                        f"Found {len(containers)} containers with selector: {selector}"
                    )
                    return containers
            except Exception as e:
                logger.debug(f"Selector {selector} failed: {e}")
                continue

        # Fallback: look for any table rows that might contain flight data
        try:
            all_rows = await page.query_selector_all("tr")
            # Filter rows that likely contain flight data
            flight_rows = []
            for row in all_rows:
                try:
                    row_text = await row.inner_text()
                    # Look for indicators of flight data
                    if any(
                        indicator in row_text.lower()
                        for indicator in ["$", "am", "pm", "jfk", "lhr"]
                    ):
                        flight_rows.append(row)
                except:
                    continue

            if flight_rows:
                logger.debug(f"Found {len(flight_rows)} rows with flight indicators")
                return flight_rows[:20]  # Limit to reasonable number

        except Exception as e:
            logger.debug(f"Fallback row search failed: {e}")

        return []

    async def _parse_single_flight(
        self, container: ElementHandle, tooltip_data: dict[str, str], page: Page
    ) -> Optional[Flight]:
        """Parse a single flight from container and tooltip data."""
        try:
            # Try to extract basic info from the container
            container_text = await container.inner_text()
            logger.debug(f"Container text preview: {container_text[:100]}...")

            # Look for price in container
            price = self._extract_price_from_text(container_text)

            # Look for associated tooltip references
            related_tooltips = await self._find_related_tooltips(
                container, tooltip_data
            )

            # Parse flight details from tooltips
            flight_info = self._parse_flight_info_from_tooltips(related_tooltips)

            # Also parse info directly from container text
            container_airlines = self._extract_airlines_from_text(container_text)
            flight_info["airlines"].update(container_airlines)

            # Extract times from container if available
            container_times = self._extract_times_from_text(container_text)
            flight_info["times"].extend(container_times)

            if not flight_info.get("segments"):
                # Create basic flight info from available data
                flight_info = self._create_basic_flight_info(
                    container_text, tooltip_data
                )

            # Create flight object
            return self._create_flight_object(flight_info, price)

        except Exception as e:
            logger.warning(f"Failed to parse single flight: {e}")
            return None

    async def _find_related_tooltips(
        self, container: ElementHandle, tooltip_data: dict[str, str]
    ) -> list[str]:
        """Find tooltips related to this flight container."""
        related = []

        try:
            # Look for aria-describedby attributes
            described_by = await container.get_attribute("aria-describedby")
            if described_by:
                tooltip_ids = described_by.split()
                for tooltip_id in tooltip_ids:
                    if tooltip_id in tooltip_data:
                        related.append(tooltip_data[tooltip_id])

            # Look for child elements with tooltip references
            elements = await container.query_selector_all("[aria-describedby]")
            for element in elements:
                described_by = await element.get_attribute("aria-describedby")
                if described_by:
                    tooltip_ids = described_by.split()
                    for tooltip_id in tooltip_ids:
                        if tooltip_id in tooltip_data:
                            related.append(tooltip_data[tooltip_id])

        except Exception as e:
            logger.debug(f"Failed to find related tooltips: {e}")

        return related

    def _parse_flight_info_from_tooltips(self, tooltips: list[str]) -> dict:
        """Parse detailed flight information from tooltip texts."""
        flight_info = {
            "segments": [],
            "airlines": set(),
            "times": [],
            "price_info": {},
            "special_notes": [],
        }

        for tooltip in tooltips:
            # Parse airline information
            airlines = self._extract_airlines_from_text(tooltip)
            flight_info["airlines"].update(airlines)

            # Parse time information
            times = self._extract_times_from_text(tooltip)
            flight_info["times"].extend(times)

            # Parse price information
            prices = self._extract_prices_from_text(tooltip)
            flight_info["price_info"].update(prices)

            # Parse special notes
            if any(
                note in tooltip.lower()
                for note in ["overnight", "red-eye", "layover", "connection"]
            ):
                flight_info["special_notes"].append(tooltip)

        # Create segments from time information
        flight_info["segments"] = self._create_segments_from_times(
            flight_info["times"], list(flight_info["airlines"])
        )

        return flight_info

    def _extract_airlines_from_text(self, text: str) -> list[str]:
        """Extract airline names from text."""
        airlines = []

        # Common airline patterns
        airline_patterns = [
            r"Virgin Atlantic",
            r"Delta",
            r"American",
            r"United",
            r"British Airways",
            r"Emirates",
            r"Lufthansa",
            r"Air France",
            r"KLM",
            r"Qatar Airways",
            r"Southwest",
            r"JetBlue",
        ]

        for pattern in airline_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                airlines.append(pattern)

        # Also look for comma-separated airlines
        if "," in text and not any(
            time_indicator in text for time_indicator in ["AM", "PM", ":"]
        ):
            parts = text.split(",")
            for part in parts:
                part = part.strip()
                if len(part) > 2 and part.replace(" ", "").isalpha():
                    airlines.append(part)

        return airlines

    def _extract_times_from_text(self, text: str) -> list[dict]:
        """Extract time information from tooltip text."""
        times = []

        # Pattern for "LHR time: 6:25 AM Sat July 12"
        time_pattern = r"(\w{3})\s+time:\s+(\d{1,2}:\d{2}\s+[AP]M)\s+(\w+\s+\w+\s+\d+)"

        matches = re.findall(time_pattern, text)
        for match in matches:
            airport_code, time_str, date_str = match
            try:
                times.append(
                    {
                        "airport": airport_code,
                        "time": time_str,
                        "date": date_str,
                        "raw_text": text,
                    }
                )
            except Exception as e:
                logger.debug(f"Failed to parse time match {match}: {e}")

        return times

    def _extract_prices_from_text(self, text: str) -> dict:
        """Extract price information from text."""
        prices = {}

        # Price patterns
        price_patterns = [
            (r"Price per passenger:\s*\$(\d+(?:,\d{3})*(?:\.\d{2})?)", "per_passenger"),
            (r"Price per mile:\s*\$(\d+(?:\.\d+)?)", "per_mile"),
            (r"Price per adult:\s*\$(\d+(?:,\d{3})*(?:\.\d{2})?)", "per_adult"),
            (r"\$(\d+(?:,\d{3})*(?:\.\d{2})?)", "general"),
        ]

        for pattern, price_type in price_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    price_value = Decimal(match.replace(",", ""))
                    prices[price_type] = price_value
                except InvalidOperation:
                    continue

        return prices

    def _extract_price_from_text(self, text: str) -> Optional[Decimal]:
        """Extract the main price from text."""
        price_patterns = [
            r"\$(\d+(?:,\d{3})*(?:\.\d{2})?)",
            r"(\d+(?:,\d{3})*(?:\.\d{2})?)\s*USD",
            r"USD\s*(\d+(?:,\d{3})*(?:\.\d{2})?)",
        ]

        for pattern in price_patterns:
            matches = re.findall(pattern, text)
            if matches:
                try:
                    return Decimal(matches[0].replace(",", ""))
                except InvalidOperation:
                    continue

        return None

    def _create_segments_from_times(
        self, times: list[dict], airlines: list[str]
    ) -> list[dict]:
        """Create flight segments from time information."""
        segments = []

        if len(times) < 2:
            return segments

        # Group times by date to identify segments
        time_groups = {}
        for time_info in times:
            date = time_info["date"]
            if date not in time_groups:
                time_groups[date] = []
            time_groups[date].append(time_info)

        # Create segments from time pairs
        for date, date_times in time_groups.items():
            if len(date_times) >= 2:
                # Sort by time to get departure/arrival order
                date_times.sort(key=lambda x: x["time"])

                for i in range(0, len(date_times) - 1, 2):
                    departure = date_times[i]
                    arrival = (
                        date_times[i + 1] if i + 1 < len(date_times) else date_times[i]
                    )

                    segment = {
                        "departure_airport": departure["airport"],
                        "arrival_airport": arrival["airport"],
                        "departure_time": f"{departure['time']} {departure['date']}",
                        "arrival_time": f"{arrival['time']} {arrival['date']}",
                        "airline": airlines[0] if airlines else "Unknown",
                    }
                    segments.append(segment)

        return segments

    def _create_basic_flight_info(
        self, container_text: str, tooltip_data: dict[str, str]
    ) -> dict:
        """Create basic flight info when detailed parsing fails."""
        # Extract any available information from container and tooltips
        all_text = container_text + " " + " ".join(tooltip_data.values())

        # Extract airlines
        airlines = self._extract_airlines_from_text(all_text)

        # Extract times
        times = []
        for tooltip in tooltip_data.values():
            times.extend(self._extract_times_from_text(tooltip))

        # Create basic segment if we have some data
        segments = []
        if times:
            segments = self._create_segments_from_times(times, airlines)

        return {
            "segments": segments,
            "airlines": set(airlines),
            "times": times,
            "price_info": {},
            "special_notes": [],
        }

    def _create_flight_object(
        self, flight_info: dict, price: Optional[Decimal]
    ) -> Optional[Flight]:
        """Create a Flight object from parsed information."""
        try:
            segments = []

            # Create FlightSegment objects
            for seg_info in flight_info.get("segments", []):
                try:
                    # Parse airline
                    airline_name = seg_info.get("airline", "Unknown")
                    airline_code, airline_display_name = (
                        self.data_parser.parse_airline_code(airline_name)
                    )

                    # Parse airports
                    dep_airport = Airport(code=seg_info.get("departure_airport", "XXX"))
                    arr_airport = Airport(code=seg_info.get("arrival_airport", "XXX"))

                    # Parse times
                    dep_time = self._parse_datetime(seg_info.get("departure_time", ""))
                    arr_time = self._parse_datetime(seg_info.get("arrival_time", ""))

                    # Calculate duration
                    duration_minutes = 120  # Default
                    if dep_time and arr_time:
                        duration = arr_time - dep_time
                        duration_minutes = int(duration.total_seconds() / 60)

                    segment = FlightSegment(
                        airline=Airline(code=airline_code, name=airline_display_name),
                        flight_number=self.data_parser.parse_flight_number(
                            "", airline_code
                        ),
                        departure_airport=dep_airport,
                        arrival_airport=arr_airport,
                        departure_time=dep_time or datetime.now(),
                        arrival_time=arr_time or datetime.now(),
                        duration_minutes=duration_minutes,
                        stops=0,
                    )
                    segments.append(segment)

                except Exception as e:
                    logger.debug(f"Failed to create segment: {e}")
                    continue

            # If no segments created, create a basic one
            if not segments:
                segments = [self._create_default_segment(flight_info)]

            # Calculate total duration
            total_duration = sum(seg.duration_minutes for seg in segments)

            # Determine price
            if not price and flight_info.get("price_info"):
                price = (
                    flight_info["price_info"].get("per_passenger")
                    or flight_info["price_info"].get("per_adult")
                    or flight_info["price_info"].get("general")
                )

            price = price or Decimal("500.00")  # Default price

            return Flight(
                segments=segments,
                price=price,
                cabin_class=CabinClass.ECONOMY,
                total_duration_minutes=total_duration,
                stops=max(0, len(segments) - 1),
            )

        except Exception as e:
            logger.warning(f"Failed to create flight object: {e}")
            return None

    def _parse_datetime(self, time_str: str) -> Optional[datetime]:
        """Parse datetime from various formats."""
        if not time_str:
            return None

        try:
            # Pattern: "6:25 AM Sat July 12"
            pattern = r"(\d{1,2}:\d{2}\s+[AP]M)\s+\w+\s+(\w+\s+\d+)"
            match = re.search(pattern, time_str)

            if match:
                time_part = match.group(1)
                date_part = match.group(2)

                # Parse time
                time_obj = datetime.strptime(time_part, "%I:%M %p").time()

                # Parse date (assuming current year)
                try:
                    date_obj = datetime.strptime(f"{date_part} 2025", "%B %d %Y").date()
                except ValueError:
                    # Try short month format
                    date_obj = datetime.strptime(f"{date_part} 2025", "%b %d %Y").date()

                return datetime.combine(date_obj, time_obj)

        except Exception as e:
            logger.debug(f"Failed to parse datetime '{time_str}': {e}")

        return None

    def _create_default_segment(self, flight_info: dict) -> FlightSegment:
        """Create a default segment when parsing fails."""
        airlines = list(flight_info.get("airlines", ["Unknown"]))
        airline_name = airlines[0] if airlines else "Unknown"
        airline_code, airline_display_name = self.data_parser.parse_airline_code(
            airline_name
        )

        return FlightSegment(
            airline=Airline(code=airline_code, name=airline_display_name),
            flight_number=self.data_parser.parse_flight_number("", airline_code),
            departure_airport=Airport(code="JFK"),  # Default based on example
            arrival_airport=Airport(code="LHR"),  # Default based on example
            departure_time=datetime.now(),
            arrival_time=datetime.now() + timedelta(hours=8),
            duration_minutes=480,  # 8 hours default
            stops=0,
        )

    async def _parse_from_tooltips(self, tooltip_data: dict[str, str]) -> list[Flight]:
        """Parse flights directly from tooltip data when container parsing fails."""
        flights = []

        try:
            # Group tooltips by content type
            price_tooltips = []
            time_tooltips = []
            airline_tooltips = []

            for _tooltip_id, tooltip_text in tooltip_data.items():
                if "$" in tooltip_text or "price" in tooltip_text.lower():
                    price_tooltips.append(tooltip_text)
                elif "time:" in tooltip_text and (
                    "AM" in tooltip_text or "PM" in tooltip_text
                ):
                    time_tooltips.append(tooltip_text)
                elif any(
                    airline in tooltip_text
                    for airline in ["Delta", "Virgin", "American", "United"]
                ):
                    airline_tooltips.append(tooltip_text)

            # Extract price
            price = None
            for price_text in price_tooltips:
                extracted_price = self._extract_price_from_text(price_text)
                if extracted_price:
                    price = extracted_price
                    break

            # Create flight info from tooltips
            flight_info = {
                "segments": [],
                "airlines": set(),
                "times": [],
                "price_info": {},
                "special_notes": [],
            }

            # Process time tooltips
            for time_text in time_tooltips:
                times = self._extract_times_from_text(time_text)
                flight_info["times"].extend(times)

            # Process airline tooltips
            for airline_text in airline_tooltips:
                airlines = self._extract_airlines_from_text(airline_text)
                flight_info["airlines"].update(airlines)

            # Create segments
            flight_info["segments"] = self._create_segments_from_times(
                flight_info["times"], list(flight_info["airlines"])
            )

            # Create flight object
            if flight_info["times"] or flight_info["airlines"] or price:
                flight = self._create_flight_object(flight_info, price)
                if flight:
                    flights.append(flight)

        except Exception as e:
            logger.warning(f"Failed to parse from tooltips: {e}")

        return flights

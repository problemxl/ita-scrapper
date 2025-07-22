"""
Example MCP Server integration with ITA Scrapper.

This demonstrates how to integrate the ITA Scrapper library
with an MCP server for travel planning applications.
"""

import asyncio
import json
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Any

from ita_scrapper import ITAScrapper
from ita_scrapper.models import CabinClass, TripType, FlightResult
from ita_scrapper.exceptions import ITAScrapperError


class TravelPlannerMCP:
    """
    MCP Server integration for travel planning using ITA Scrapper.

    This class provides MCP-compatible methods for flight search
    and travel planning operations.
    """

    def __init__(self, use_matrix: bool = True, demo_mode: bool = True):
        """
        Initialize the MCP travel planner.

        Args:
            use_matrix: Whether to use ITA Matrix (recommended) or Google Flights
            demo_mode: Whether to use demo data (for testing)
        """
        self.use_matrix = use_matrix
        self.demo_mode = demo_mode
        self.scrapper: Optional[ITAScrapper] = None

    async def initialize(self):
        """Initialize the scrapper."""
        self.scrapper = ITAScrapper(
            headless=True, use_matrix=self.use_matrix, demo_mode=self.demo_mode
        )
        await self.scrapper.start()

    async def cleanup(self):
        """Clean up resources."""
        if self.scrapper:
            await self.scrapper.close()

    async def search_flights(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for flights - MCP tool implementation.

        Args:
            params: Flight search parameters

        Returns:
            Structured flight search results
        """
        try:
            # Parse input parameters
            origin = params.get("origin", "").upper()
            destination = params.get("destination", "").upper()
            departure_date = self._parse_date(params.get("departure_date"))
            return_date = self._parse_date(params.get("return_date"))

            cabin_class = CabinClass(params.get("cabin_class", "economy"))
            adults = params.get("adults", 1)
            children = params.get("children", 0)
            infants = params.get("infants", 0)

            # Validate required parameters
            if not origin or not destination or not departure_date:
                return {
                    "error": "Missing required parameters: origin, destination, departure_date"
                }

            if not self.scrapper:
                return {"error": "Scrapper not initialized"}

            # Perform search
            result = await self.scrapper.search_flights(
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                return_date=return_date,
                cabin_class=cabin_class,
                adults=adults,
                children=children,
                infants=infants,
                max_results=params.get("max_results", 10),
            )

            # Format response for MCP
            return self._format_flight_results(result)

        except ITAScrapperError as e:
            return {"error": f"Scrapper error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    async def get_price_calendar(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get price calendar for flexible dates - MCP tool implementation.

        Args:
            params: Price calendar parameters

        Returns:
            Price calendar data
        """
        try:
            origin = params.get("origin", "").upper()
            destination = params.get("destination", "").upper()
            month = self._parse_date(params.get("month"))
            cabin_class = CabinClass(params.get("cabin_class", "economy"))

            if not origin or not destination or not month:
                return {
                    "error": "Missing required parameters: origin, destination, month"
                }

            if not self.scrapper:
                return {"error": "Scrapper not initialized"}

            calendar = await self.scrapper.get_price_calendar(
                origin=origin,
                destination=destination,
                departure_month=month,
                cabin_class=cabin_class,
            )

            return self._format_price_calendar(calendar)

        except ITAScrapperError as e:
            return {"error": f"Scrapper error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    async def find_cheapest_flights(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Find cheapest flights with flexible dates - MCP tool implementation.

        Args:
            params: Search parameters with date flexibility

        Returns:
            Cheapest flight options
        """
        try:
            origin = params.get("origin", "").upper()
            destination = params.get("destination", "").upper()
            departure_window = params.get("departure_window", 7)  # days
            trip_length = params.get("trip_length", 7)  # days

            if not origin or not destination:
                return {"error": "Missing required parameters: origin, destination"}

            # Search multiple departure dates
            base_date = date.today() + timedelta(days=30)
            cheapest_options = []

            for offset in range(departure_window):
                departure_date = base_date + timedelta(days=offset)
                return_date = departure_date + timedelta(days=trip_length)

                try:
                    result = await self.search_flights(
                        {
                            "origin": origin,
                            "destination": destination,
                            "departure_date": departure_date.isoformat(),
                            "return_date": return_date.isoformat(),
                            "cabin_class": params.get("cabin_class", "economy"),
                            "adults": params.get("adults", 1),
                            "max_results": 3,
                        }
                    )

                    if not result.get("error") and result.get("flights"):
                        cheapest_flight = min(
                            result["flights"], key=lambda f: f["price"]
                        )
                        cheapest_options.append(
                            {
                                "departure_date": departure_date.isoformat(),
                                "return_date": return_date.isoformat(),
                                "flight": cheapest_flight,
                            }
                        )

                except Exception:
                    continue  # Skip failed searches

            # Sort by price
            cheapest_options.sort(key=lambda x: x["flight"]["price"])

            return {
                "cheapest_options": cheapest_options[:5],
                "search_params": {
                    "origin": origin,
                    "destination": destination,
                    "departure_window_days": departure_window,
                    "trip_length_days": trip_length,
                },
            }

        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    async def compare_routes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare flight prices between multiple routes - MCP tool implementation.

        Args:
            params: Route comparison parameters

        Returns:
            Route comparison results
        """
        try:
            routes = params.get("routes", [])
            departure_date = self._parse_date(params.get("departure_date"))
            return_date = self._parse_date(params.get("return_date"))

            if not routes or not departure_date:
                return {"error": "Missing required parameters: routes, departure_date"}

            route_results = []

            for route in routes:
                origin = route.get("origin", "").upper()
                destination = route.get("destination", "").upper()

                if not origin or not destination:
                    continue

                try:
                    result = await self.search_flights(
                        {
                            "origin": origin,
                            "destination": destination,
                            "departure_date": departure_date.isoformat(),
                            "return_date": return_date.isoformat()
                            if return_date
                            else None,
                            "cabin_class": params.get("cabin_class", "economy"),
                            "adults": params.get("adults", 1),
                            "max_results": 3,
                        }
                    )

                    if not result.get("error") and result.get("flights"):
                        cheapest = min(result["flights"], key=lambda f: f["price"])
                        route_results.append(
                            {
                                "route": f"{origin} → {destination}",
                                "origin": origin,
                                "destination": destination,
                                "cheapest_price": cheapest["price"],
                                "cheapest_flight": cheapest,
                                "total_flights": len(result["flights"]),
                            }
                        )

                except Exception:
                    continue

            # Sort by price
            route_results.sort(key=lambda x: x["cheapest_price"])

            return {
                "route_comparison": route_results,
                "search_params": {
                    "departure_date": departure_date.isoformat(),
                    "return_date": return_date.isoformat() if return_date else None,
                    "total_routes_searched": len(route_results),
                },
            }

        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    def _parse_date(self, date_str: Optional[str]) -> Optional[date]:
        """Parse date string to date object."""
        if not date_str:
            return None

        try:
            return datetime.fromisoformat(date_str).date()
        except ValueError:
            try:
                return datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return None

    def _format_flight_results(self, result: FlightResult) -> Dict[str, Any]:
        """Format flight results for MCP response."""
        return {
            "flights": [
                {
                    "price": float(flight.price),
                    "currency": "USD",
                    "duration_minutes": flight.total_duration_minutes,
                    "stops": flight.stops,
                    "airlines": flight.airlines,
                    "departure_time": flight.departure_time.isoformat(),
                    "arrival_time": flight.arrival_time.isoformat(),
                    "cabin_class": flight.cabin_class.value,
                    "is_refundable": flight.is_refundable,
                    "baggage_included": flight.baggage_included,
                }
                for flight in result.flights
            ],
            "search_params": {
                "origin": result.search_params.origin,
                "destination": result.search_params.destination,
                "departure_date": result.search_params.departure_date.isoformat(),
                "return_date": result.search_params.return_date.isoformat()
                if result.search_params.return_date
                else None,
                "trip_type": result.search_params.trip_type.value,
                "cabin_class": result.search_params.cabin_class.value,
                "adults": result.search_params.adults,
                "children": result.search_params.children,
                "infants": result.search_params.infants,
            },
            "summary": {
                "total_results": result.total_results,
                "cheapest_price": float(result.cheapest_flight.price)
                if result.cheapest_flight
                else None,
                "fastest_duration": result.fastest_flight.total_duration_minutes
                if result.fastest_flight
                else None,
                "search_timestamp": result.search_timestamp.isoformat(),
            },
        }

    def _format_price_calendar(self, calendar) -> Dict[str, Any]:
        """Format price calendar for MCP response."""
        return {
            "origin": calendar.origin,
            "destination": calendar.destination,
            "cabin_class": calendar.cabin_class.value,
            "calendar_entries": [
                {
                    "date": entry.date.isoformat(),
                    "price": float(entry.price) if entry.price else None,
                    "available": entry.available,
                    "day_of_week": entry.date.strftime("%A"),
                }
                for entry in calendar.entries
            ],
            "cheapest_dates": [
                {
                    "date": entry.date.isoformat(),
                    "price": float(entry.price),
                    "day_of_week": entry.date.strftime("%A"),
                }
                for entry in calendar.get_cheapest_dates(5)
            ],
        }


# Example MCP server implementation
async def main():
    """Example usage of TravelPlannerMCP."""
    mcp = TravelPlannerMCP()

    try:
        await mcp.initialize()

        # Example 1: Basic flight search
        print("🛫 Basic Flight Search")
        result = await mcp.search_flights(
            {
                "origin": "JFK",
                "destination": "LAX",
                "departure_date": (date.today() + timedelta(days=30)).isoformat(),
                "return_date": (date.today() + timedelta(days=37)).isoformat(),
                "cabin_class": "economy",
                "adults": 1,
                "max_results": 3,
            }
        )
        print(json.dumps(result, indent=2))

        # Example 2: Find cheapest flights
        print("\n💰 Cheapest Flights Search")
        result = await mcp.find_cheapest_flights(
            {
                "origin": "NYC",
                "destination": "LON",
                "departure_window": 5,
                "trip_length": 7,
                "cabin_class": "economy",
            }
        )
        print(json.dumps(result, indent=2))

        # Example 3: Compare routes
        print("\n🔍 Route Comparison")
        result = await mcp.compare_routes(
            {
                "routes": [
                    {"origin": "JFK", "destination": "CDG"},
                    {"origin": "JFK", "destination": "LHR"},
                    {"origin": "EWR", "destination": "CDG"},
                ],
                "departure_date": (date.today() + timedelta(days=45)).isoformat(),
                "return_date": (date.today() + timedelta(days=52)).isoformat(),
                "cabin_class": "economy",
            }
        )
        print(json.dumps(result, indent=2))

    finally:
        await mcp.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

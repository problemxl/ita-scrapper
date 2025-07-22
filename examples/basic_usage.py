#!/usr/bin/env python3
"""
Example usage of ITA Scrapper library.
"""

import asyncio
import logging
from datetime import date, timedelta
from decimal import Decimal

from ita_scrapper import ITAScrapper
from ita_scrapper.models import CabinClass, TripType
from ita_scrapper.exceptions import ITAScrapperError


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def basic_flight_search():
    """Example: Basic round-trip flight search."""
    print("🛫 Basic Flight Search Example")
    print("=" * 50)

    try:
        async with ITAScrapper(headless=True) as scrapper:
            result = await scrapper.search_flights(
                origin="JFK",
                destination="LAX",
                departure_date=date.today() + timedelta(days=30),
                return_date=date.today() + timedelta(days=37),
                cabin_class=CabinClass.ECONOMY,
                adults=1,
            )

            print(f"Found {len(result.flights)} flights")
            print(
                f"Search from {result.search_params.origin} to {result.search_params.destination}"
            )
            print(f"Departure: {result.search_params.departure_date}")
            print(f"Return: {result.search_params.return_date}")
            print()

            if result.flights:
                cheapest = result.cheapest_flight
                fastest = result.fastest_flight

                if cheapest:
                    print(f"💰 Cheapest flight: ${cheapest.price}")
                    print(f"   Airlines: {', '.join(cheapest.airlines)}")
                    print(
                        f"   Duration: {cheapest.total_duration_minutes // 60}h {cheapest.total_duration_minutes % 60}m"
                    )
                    print()

                if fastest and fastest != cheapest:
                    print(f"⚡ Fastest flight: ${fastest.price}")
                    print(f"   Airlines: {', '.join(fastest.airlines)}")
                    print(
                        f"   Duration: {fastest.total_duration_minutes // 60}h {fastest.total_duration_minutes % 60}m"
                    )
                    print()

                print("All flights:")
                for i, flight in enumerate(result.flights[:5], 1):
                    duration_h = flight.total_duration_minutes // 60
                    duration_m = flight.total_duration_minutes % 60
                    print(
                        f"  {i}. ${flight.price} - {duration_h}h {duration_m}m - {', '.join(flight.airlines)}"
                    )

    except ITAScrapperError as e:
        logger.error(f"Scrapper error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


async def one_way_search():
    """Example: One-way flight search."""
    print("\n🎯 One-Way Flight Search Example")
    print("=" * 50)

    try:
        async with ITAScrapper(headless=True) as scrapper:
            result = await scrapper.search_flights(
                origin="SFO",
                destination="NYC",
                departure_date=date.today() + timedelta(days=15),
                cabin_class=CabinClass.PREMIUM_ECONOMY,
                adults=2,
                children=1,
            )

            print(
                f"One-way search: {result.search_params.origin} → {result.search_params.destination}"
            )
            print(
                f"Passengers: {result.search_params.adults} adults, {result.search_params.children} children"
            )
            print(f"Cabin class: {result.search_params.cabin_class.value}")
            print(f"Found {len(result.flights)} flights")

            if result.flights:
                avg_price = sum(f.price for f in result.flights) / len(result.flights)
                print(f"Average price: ${avg_price:.2f}")

                # Show price range
                prices = [f.price for f in result.flights]
                print(f"Price range: ${min(prices)} - ${max(prices)}")

    except ITAScrapperError as e:
        logger.error(f"Scrapper error: {e}")


async def business_class_search():
    """Example: Business class flight search."""
    print("\n💼 Business Class Search Example")
    print("=" * 50)

    try:
        async with ITAScrapper(headless=True) as scrapper:
            result = await scrapper.search_flights(
                origin="LAX",
                destination="LHR",  # London Heathrow
                departure_date=date.today() + timedelta(days=45),
                return_date=date.today() + timedelta(days=52),
                cabin_class=CabinClass.BUSINESS,
                adults=2,
            )

            print(
                f"Business class search: {result.search_params.origin} ↔ {result.search_params.destination}"
            )
            print(f"Found {len(result.flights)} business class flights")

            if result.flights:
                # Show premium options
                print("\nBusiness class options:")
                for i, flight in enumerate(result.flights[:3], 1):
                    duration_h = flight.total_duration_minutes // 60
                    duration_m = flight.total_duration_minutes % 60
                    stops_text = (
                        "Direct" if flight.stops == 0 else f"{flight.stops} stop(s)"
                    )
                    print(
                        f"  {i}. ${flight.price:,} - {duration_h}h {duration_m}m - {stops_text}"
                    )
                    print(f"     Airlines: {', '.join(flight.airlines)}")
                    print(f"     Refundable: {'Yes' if flight.is_refundable else 'No'}")
                    print()

    except ITAScrapperError as e:
        logger.error(f"Scrapper error: {e}")


async def price_calendar_example():
    """Example: Get price calendar for flexible dates."""
    print("\n📅 Price Calendar Example")
    print("=" * 50)

    try:
        async with ITAScrapper(headless=True) as scrapper:
            calendar = await scrapper.get_price_calendar(
                origin="JFK",
                destination="CDG",  # Paris Charles de Gaulle
                departure_month=date.today() + timedelta(days=30),
                cabin_class=CabinClass.ECONOMY,
            )

            print(f"Price calendar: {calendar.origin} → {calendar.destination}")
            print(f"Total entries: {len(calendar.entries)}")

            # Show cheapest dates
            cheapest_dates = calendar.get_cheapest_dates(5)
            if cheapest_dates:
                print("\n💰 Cheapest dates:")
                for entry in cheapest_dates:
                    if entry.price:
                        print(f"  {entry.date.strftime('%Y-%m-%d')}: ${entry.price}")

            # Show weekend vs weekday average
            weekend_prices = []
            weekday_prices = []

            for entry in calendar.entries:
                if entry.price and entry.available:
                    if entry.date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                        weekend_prices.append(entry.price)
                    else:
                        weekday_prices.append(entry.price)

            if weekend_prices and weekday_prices:
                avg_weekend = sum(weekend_prices) / len(weekend_prices)
                avg_weekday = sum(weekday_prices) / len(weekday_prices)

                print(f"\n📊 Price comparison:")
                print(f"  Average weekday price: ${avg_weekday:.2f}")
                print(f"  Average weekend price: ${avg_weekend:.2f}")

                savings = avg_weekend - avg_weekday
                if savings > 0:
                    print(f"  💡 Save ${savings:.2f} by flying on weekdays!")
                else:
                    print(f"  💡 Weekend flights are ${abs(savings):.2f} cheaper!")

    except ITAScrapperError as e:
        logger.error(f"Scrapper error: {e}")


async def error_handling_example():
    """Example: Error handling and validation."""
    print("\n🚨 Error Handling Example")
    print("=" * 50)

    # Example 1: Invalid airport code
    try:
        async with ITAScrapper(headless=True) as scrapper:
            await scrapper.search_flights(
                origin="INVALID",  # Invalid airport code
                destination="LAX",
                departure_date=date.today() + timedelta(days=30),
            )
    except ITAScrapperError as e:
        print(f"✅ Caught expected error: {e}")

    # Example 2: Past date
    try:
        async with ITAScrapper(headless=True) as scrapper:
            await scrapper.search_flights(
                origin="JFK",
                destination="LAX",
                departure_date=date.today() - timedelta(days=1),  # Past date
            )
    except ITAScrapperError as e:
        print(f"✅ Caught expected error: {e}")

    # Example 3: Invalid return date
    try:
        async with ITAScrapper(headless=True) as scrapper:
            departure = date.today() + timedelta(days=30)
            return_date = departure - timedelta(days=1)  # Before departure

            await scrapper.search_flights(
                origin="JFK",
                destination="LAX",
                departure_date=departure,
                return_date=return_date,
            )
    except ITAScrapperError as e:
        print(f"✅ Caught expected error: {e}")


async def main():
    """Run all examples."""
    print("🚀 ITA Scrapper Examples")
    print("=" * 50)
    print("This script demonstrates various features of the ITA Scrapper library.")
    print(
        "Note: These examples use mock data. Real implementation would scrape Google Flights."
    )
    print()

    # Run examples
    await basic_flight_search()
    await one_way_search()
    await business_class_search()
    await price_calendar_example()
    await error_handling_example()

    print("\n✅ All examples completed!")
    print("\nFor MCP server integration, use this library as a dependency:")
    print("  1. Import ITAScrapper in your MCP server")
    print("  2. Create async functions for flight search operations")
    print("  3. Return structured data for trip planning")


if __name__ == "__main__":
    asyncio.run(main())

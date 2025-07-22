#!/usr/bin/env python3
"""
Demo examples for the ITA Scrapper library.
This version uses demo mode to show functionality without scraping.
"""

import asyncio
import logging
from datetime import date, timedelta
from ita_scrapper import ITAScrapper, SearchParams, CabinClass

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def basic_flight_search_demo():
    """Demonstrate basic flight search with demo data."""
    print("\n🛫 Basic Flight Search Demo")
    print("=" * 50)

    # Create scrapper in demo mode
    async with ITAScrapper(demo_mode=True) as scrapper:
        result = await scrapper.search_flights(
            origin="JFK",
            destination="LAX",
            departure_date=date.today() + timedelta(days=30),
            cabin_class=CabinClass.ECONOMY,
            adults=1,
        )

        print(f"Found {result.total_results} flights:")
        for i, flight in enumerate(result.flights, 1):
            first_segment = flight.segments[0]
            last_segment = flight.segments[-1]
            print(f"\n{i}. {first_segment.airline.name} {first_segment.flight_number}")
            print(
                f"   {flight.departure_time.strftime('%H:%M')} → {flight.arrival_time.strftime('%H:%M')}"
            )
            print(
                f"   {first_segment.departure_airport.code} → {last_segment.arrival_airport.code}"
            )
            print(
                f"   Duration: {flight.total_duration_minutes // 60}h {flight.total_duration_minutes % 60}m"
            )
            print(f"   Stops: {flight.stops}")
            print(f"   Price: ${flight.price}")
            if len(flight.segments) > 1:
                print(f"   Segments:")
                for j, segment in enumerate(flight.segments, 1):
                    print(
                        f"     {j}. {segment.departure_airport.code} → {segment.arrival_airport.code}"
                    )


async def one_way_flight_demo():
    """Demonstrate one-way flight search."""
    print("\n🎯 One-Way Flight Search Demo")
    print("=" * 50)

    async with ITAScrapper(demo_mode=True) as scrapper:
        result = await scrapper.search_flights(
            origin="SFO",
            destination="NYC",
            departure_date=date.today() + timedelta(days=14),
            cabin_class=CabinClass.ECONOMY,
            adults=2,
        )

        print(f"One-way flights for 2 adults:")
        cheapest = min(result.flights, key=lambda f: f.price)
        print(
            f"Cheapest: {cheapest.segments[0].airline.name} {cheapest.segments[0].flight_number} - ${cheapest.price}"
        )

        fastest = min(result.flights, key=lambda f: f.total_duration_minutes)
        print(
            f"Fastest: {fastest.segments[0].airline.name} {fastest.segments[0].flight_number} - {fastest.total_duration_minutes // 60}h {fastest.total_duration_minutes % 60}m"
        )


async def business_class_demo():
    """Demonstrate business class search."""
    print("\n💼 Business Class Search Demo")
    print("=" * 50)

    async with ITAScrapper(demo_mode=True) as scrapper:
        result = await scrapper.search_flights(
            origin="LAX",
            destination="LHR",
            departure_date=date.today() + timedelta(days=60),
            return_date=date.today() + timedelta(days=67),
            cabin_class=CabinClass.BUSINESS,
            adults=1,
        )

        print(f"Business class round-trip flights:")
        for flight in result.flights[:2]:  # Show first 2
            print(
                f"• {flight.segments[0].airline.name} {flight.segments[0].flight_number}"
            )
            print(f"  Price: ${flight.price} ({flight.cabin_class.value})")


async def price_calendar_demo():
    """Demonstrate price calendar functionality."""
    print("\n📅 Price Calendar Demo")
    print("=" * 50)

    async with ITAScrapper(demo_mode=True) as scrapper:
        calendar = await scrapper.get_price_calendar(
            origin="JFK",
            destination="CDG",
            departure_month=date.today() + timedelta(days=30),
            cabin_class=CabinClass.ECONOMY,
        )

        print(f"Price calendar for {calendar.origin} → {calendar.destination}:")

        # Show first week of prices
        week_entries = calendar.entries[:7]
        for entry in week_entries:
            day_name = entry.date.strftime("%A")
            print(f"  {entry.date} ({day_name}): ${entry.price}")

        # Find cheapest day
        cheapest = min(calendar.entries, key=lambda e: e.price)
        print(f"\nCheapest day: {cheapest.date} - ${cheapest.price}")

        # Find most expensive day
        most_expensive = max(calendar.entries, key=lambda e: e.price)
        print(f"Most expensive: {most_expensive.date} - ${most_expensive.price}")


async def main():
    """Run all demo examples."""
    print("🚀 ITA Scrapper Demo Examples")
    print("=" * 50)
    print("This demo uses mock data to show library functionality.")

    try:
        await basic_flight_search_demo()
        await one_way_flight_demo()
        await business_class_demo()
        await price_calendar_demo()

        print("\n✅ All demos completed successfully!")
        print("\nTo use with real data:")
        print("1. Set demo_mode=False in ITAScrapper()")
        print("2. Update selectors in scrapper.py for current Google Flights UI")
        print("3. Handle rate limiting and CAPTCHA challenges")

    except Exception as e:
        logger.error(f"Demo error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

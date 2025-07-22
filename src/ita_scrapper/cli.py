#!/usr/bin/env python3
"""
Command line interface for ITA Scrapper.
"""

import asyncio
import json
import sys
from datetime import date
from typing import Optional

import click

from .models import CabinClass
from .scrapper import ITAScrapper


@click.group()
@click.version_option()
def main():
    """ITA Matrix flight scraper command line interface."""
    pass


@main.command()
@click.option(
    "--origin", "-o", required=True, help="Origin airport code (e.g., JFK, NYC)"
)
@click.option(
    "--destination",
    "-d",
    required=True,
    help="Destination airport code (e.g., LAX, SFO)",
)
@click.option(
    "--departure-date", "-dep", required=True, help="Departure date (YYYY-MM-DD)"
)
@click.option("--return-date", "-ret", help="Return date (YYYY-MM-DD) for round-trip")
@click.option("--adults", "-a", default=1, help="Number of adult passengers (1-9)")
@click.option("--children", "-c", default=0, help="Number of child passengers (0-8)")
@click.option("--infants", "-i", default=0, help="Number of infant passengers (0-8)")
@click.option(
    "--cabin-class",
    type=click.Choice(["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"]),
    default="ECONOMY",
    help="Cabin class",
)
@click.option(
    "--headless/--no-headless", default=True, help="Run browser in headless mode"
)
@click.option(
    "--format",
    type=click.Choice(["json", "table"]),
    default="table",
    help="Output format",
)
@click.option("--limit", "-l", default=10, help="Limit number of results")
def search(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str],
    adults: int,
    children: int,
    infants: int,
    cabin_class: str,
    headless: bool,
    format: str,
    limit: int,
):
    """Search for flights between two airports."""

    async def _search():
        try:
            # Parse dates
            dep_date = date.fromisoformat(departure_date)
            ret_date = date.fromisoformat(return_date) if return_date else None

            # Create scrapper instance
            async with ITAScrapper(headless=headless) as scrapper:
                click.echo(f"Searching flights from {origin} to {destination}...")

                result = await scrapper.search_flights(
                    origin=origin,
                    destination=destination,
                    departure_date=dep_date,
                    return_date=ret_date,
                    adults=adults,
                    children=children,
                    infants=infants,
                    cabin_class=CabinClass[cabin_class],
                )

                if format == "json":
                    # Convert to serializable format
                    output = {
                        "search_params": {
                            "origin": result.search_params.origin,
                            "destination": result.search_params.destination,
                            "departure_date": result.search_params.departure_date.isoformat(),
                            "return_date": result.search_params.return_date.isoformat()
                            if result.search_params.return_date
                            else None,
                            "adults": result.search_params.adults,
                            "children": result.search_params.children,
                            "infants": result.search_params.infants,
                            "cabin_class": result.search_params.cabin_class.value,
                            "trip_type": result.search_params.trip_type.value,
                        },
                        "flights": [],
                    }

                    for flight in result.flights[:limit]:
                        flight_data = {
                            "price": str(flight.price) if flight.price else None,
                            "duration": flight.duration,
                            "stops": flight.stops,
                            "departure_time": flight.departure_time.isoformat()
                            if flight.departure_time
                            else None,
                            "arrival_time": flight.arrival_time.isoformat()
                            if flight.arrival_time
                            else None,
                            "airline": flight.airline,
                            "flight_number": flight.flight_number,
                        }
                        output["flights"].append(flight_data)

                    click.echo(json.dumps(output, indent=2))

                else:  # table format
                    click.echo(f"\n🛫 Flight Results: {origin} → {destination}")
                    click.echo("=" * 60)
                    click.echo(f"Departure: {dep_date}")
                    if ret_date:
                        click.echo(f"Return: {ret_date}")
                    click.echo(
                        f"Passengers: {adults} adult(s), {children} child(ren), {infants} infant(s)"
                    )
                    click.echo(f"Cabin Class: {cabin_class}")
                    click.echo()

                    if not result.flights:
                        click.echo("No flights found.")
                        return

                    for i, flight in enumerate(result.flights[:limit], 1):
                        click.echo(f"✈️  Flight {i}")
                        click.echo("-" * 30)

                        if flight.price:
                            click.echo(f"💰 Price: ${flight.price}")

                        if flight.duration:
                            duration_str = (
                                f"{flight.duration} min"
                                if isinstance(flight.duration, int)
                                else flight.duration
                            )
                            click.echo(f"⏱️  Duration: {duration_str}")

                        if flight.stops is not None:
                            stops_str = (
                                "Direct"
                                if flight.stops == 0
                                else f"{flight.stops} stop(s)"
                            )
                            click.echo(f"🔄 Stops: {stops_str}")

                        if flight.departure_time:
                            click.echo(f"🛫 Departure: {flight.departure_time}")

                        if flight.arrival_time:
                            click.echo(f"🛬 Arrival: {flight.arrival_time}")

                        if flight.airline:
                            airline_str = flight.airline
                            if flight.flight_number:
                                airline_str += f" {flight.flight_number}"
                            click.echo(f"✈️  Airline: {airline_str}")

                        click.echo()

        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)

    asyncio.run(_search())


@main.command()
@click.argument("text")
@click.option(
    "--type",
    "data_type",
    type=click.Choice(["price", "duration", "time", "airport"]),
    required=True,
    help="Type of data to parse",
)
@click.option("--reference-date", help="Reference date for time parsing (YYYY-MM-DD)")
def parse(text: str, data_type: str, reference_date: Optional[str]):
    """Parse flight-related data from text."""
    from .utils import parse_duration, parse_price, parse_time, validate_airport_code

    try:
        if data_type == "price":
            result = parse_price(text)
            click.echo(
                f"Parsed price: ${result}" if result else "Could not parse price"
            )

        elif data_type == "duration":
            result = parse_duration(text)
            if result:
                hours = result // 60
                minutes = result % 60
                duration_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                click.echo(f"Parsed duration: {duration_str} ({result} minutes)")
            else:
                click.echo("Could not parse duration")

        elif data_type == "time":
            ref_date = date.fromisoformat(reference_date) if reference_date else None
            result = parse_time(text, ref_date)
            click.echo(f"Parsed time: {result}" if result else "Could not parse time")

        elif data_type == "airport":
            result = validate_airport_code(text)
            click.echo(f"Valid airport code: {result}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
def version():
    """Show version information."""
    from . import __version__

    click.echo(f"ITA Scrapper version {__version__}")


if __name__ == "__main__":
    main()

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
import argparse, csv


# * ── Flight Class
@dataclass(frozen=True, eq=True)
class Flight:
    flight_no: str
    origin: str
    destination: str
    departure: datetime
    arrival: datetime
    base_price: Decimal
    bag_price: Decimal
    bags_allowed: int

    def __repr__(self):
        return f"{self.flight_no} | {self.origin} -> {self.destination} | {self.departure.strftime('%d.%b %H:%M')} - {self.arrival.strftime('%d.%b %H:%M')}"


# * ── Get Flights Input
def get_flights(path: str) -> dict:
    """
    Converts a CSV file, containing the flight data, into a dictionary:
    - Key: Airports (airports)
    - Value: List of respective flights (as a Flight Dataclass Instance) departing from that airport.
    """

    airports = {}
    with open(path, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            flight = Flight(
                flight_no=row["flight_no"],
                origin=row["origin"],
                destination=row["destination"],
                departure=datetime.strptime(row["departure"], "%Y-%m-%dT%H:%M:%S"),
                arrival=datetime.strptime(row["arrival"], "%Y-%m-%dT%H:%M:%S"),
                base_price=Decimal(row["base_price"]),
                bag_price=Decimal(row["bag_price"]),
                bags_allowed=int(row["bags_allowed"]),
            )
            airports.setdefault(row["origin"], []).append(flight)

    return airports


# * ── Get Connecting Flights
def get_connecting_flights(node: Flight, airports: dict, bags_allowed: int, layover: tuple = (1, 6)) -> list:
    """
    Returns a list of connecting flights (departing flights from the destination airport of the input flight)
    - Connecting flights that travel to an airport that is already on the route (stopover or starting airport) are filtered out
    """

    flight = node.state

    route_flights = get_route_flights(node)
    prev_connection_flights = [route_flights[0].origin] + [i.destination for i in route_flights]
    next_connection_flights = []

    layover_min = flight.arrival + timedelta(hours=layover[0])
    layover_max = flight.arrival + timedelta(hours=layover[1])

    for i in sorted(airports[flight.destination], key=lambda x: x.departure):
        if i.departure >= layover_min and i.departure <= layover_max:
            if i.bags_allowed >= bags_allowed:
                if i.destination not in prev_connection_flights:
                    next_connection_flights.append(i)

    return next_connection_flights


# * ── Get Flight Route
def get_route_flights(node: Flight) -> list:
    """Returns the current route (parent nodes) for a given node."""
    route_flights = []

    # Moving Up the Parent Nodes to collect all Route Information.s
    if node.parent:
        while node.parent is not None:
            route_flights.append(node.state)
            node = node.parent

        route_flights.append(node.state)
        route_flights.reverse()

    else:
        # No Parent Node, therefore a direct flight.
        route_flights.append(node.state)

    return tuple(route_flights)


# * ── Get Flight Route
def route_formatting(args: argparse, route: list, with_return: bool = False) -> list:
    """Format the data according to the specifications"""

    information = {"flights": []}
    information["bags_allowed"] = min([j.bags_allowed for j in route])
    information["bags_count"] = args.bags_count
    information["destination"] = args.destination
    information["origin"] = args.destination if with_return else args.origin
    information["total_price"] = str(sum([j.base_price + (j.bag_price * args.bags_count) for j in route]))
    information["travel_time"] = str(route[-1].arrival - route[0].departure)
    # information["route"] = " > ".join([f"{j.flight_no}({j.origin} - {j.destination})" for j in route])

    for flight in route:
        information["flights"].append(
            {
                "flight_no": flight.flight_no,
                "origin": flight.origin,
                "destination": flight.destination,
                "departure": flight.departure,
                "arrival": flight.arrival,
                "base_price": flight.base_price,
                "bag_price": flight.bag_price,
                "bags_allowed": flight.bags_allowed,
            }
        )

    return information

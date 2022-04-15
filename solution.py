#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" ── Kiwi's Python weekend entry task
    Write a python script/module/package, that for a given flight data in a form of csv file (check the examples), prints out a structured
    list of all flight combinations for a selected route between airports A -> B, sorted by the final price for the trip.

    • Search restrictions
        1. By default you're performing search on ALL available combinations, according to search parameters.
        2. In case of a combination of A -> B -> C, the layover time in B should not be less than 1 hour and more than 6 hours.
        3. No repeating airports in the same trip! 
            A -> B -> A -> C is not a valid combination for search A -> C.
        4. Output is sorted by the final price of the trip.

    • Points of interest
        1. input, output - what if we input garbage?
        2. modules, packages & code structure (hint: it's easy to overdo it)
        3. usage of standard library and built-in data structures
        4. code readability, clarity, used conventions, documentation and comments
    """

# fmt: off
__author__  = "Alexander Semerad"
__contact__ = "hello@alpinewerk.com"
__date__    = "07.04.2022 (DD-MM-YYYY)"
__version__ = "0.1"
# fmt: on


from datetime import datetime
import argparse, json, time
from utils import get_flights, get_connecting_flights, get_route_flights, route_formatting


# * ── Node
class Node:
    def __init__(self, state, parent):
        """
        - The State represents the current flight
        - The Parent is the previous flight that leads to the complete route from the origin airport to the current State/Flight
        """

        self.state = state
        self.parent = parent

    def __repr__(self):
        return repr(self.state)


# * ── Frontier
class StackFrontier:
    """The StackFrontier keeps track of the route combinations to be explored"""

    def __init__(self):
        self.frontier = []
        self.solutions = []

    def add(self, node):
        self.frontier.append(node)

    def extend(self, node_list):
        self.frontier.extend(node_list)

    def contains_state(self, state) -> bool:
        return any(node.state == state for node in self.frontier)

    def empty(self) -> bool:
        return len(self.frontier) == 0

    def pop(self) -> Node:
        return self.frontier.pop()


# * ── Filter Flights
def filter_flights(airports: list, origin: str, bags_allowed: int = 0, departure: datetime = None) -> list:
    """
    Filters the Flights departing from a given Airport (origin), by:
        - The number bags allowed
        - The departure time (relevant for the return flight)
    """

    init_flights = []
    for flight in sorted(airports[origin], key=lambda x: x.departure):

        # Ignore any flights passed the departure date.
        if departure and flight.departure < departure:
            continue

        # Only select flights that allow the specified number of bags or more.
        if flight.bags_allowed >= bags_allowed:
            init_flights.append(Node(state=flight, parent=None))

    return init_flights


# * ── Search Engine
def search_engine(input_path: str, origin: str, destination: str, bags_allowed: int = 0, departure: datetime = None) -> list:
    """
    The Search Engine is the centerpiece of the script and runs a While loop to explore all relevant route combinations:
    - Taking the last Node from the frontier list and checking if the destination of said flight matches with our goal, the destination airport.
    - If it matches, it will be added to the solutions list.
    - Next, valid connecting flights will be added to the frontier to be further explored.
    - Once the frontier is exhausted (no combinations left), the While loop will be exited.
    """

    # * Verify Origin/Destination Input
    airports = get_flights(input_path)
    if origin not in airports or destination not in airports:
        print("Origin / Destination Airport not found.")
        return []

    # * Init Frontier
    frontier = StackFrontier()
    frontier.extend(filter_flights(airports, origin, bags_allowed, departure))

    # * Searching Connections
    while True:
        # Resume Search
        if frontier.empty():
            break

        # Select Node from Frontier
        node = frontier.pop()

        # Connection Found
        if node.state.destination == destination:
            frontier.solutions.append(get_route_flights(node))

        # Add Connecting airports to frontier
        for flight in get_connecting_flights(node, airports, bags_allowed):
            if not frontier.contains_state(flight):
                child = Node(state=flight, parent=node)
                frontier.add(child)

    return frontier.solutions


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Python weekend entry task.")
    parser.add_argument("-i", "--input", type=str, required=True, help="Flight data in a form of csv file.")
    parser.add_argument("-o", "--origin", type=str, required=True, help="Origin airport code.")
    parser.add_argument("-d", "--destination", type=str, required=True, help="Destination airport code")
    parser.add_argument("-b", "--bags_count", type=int, default=0, required=False, help="Number of requested bags.")
    parser.add_argument("-r", "--with_return", action="store_true", default=False, required=False, help="Is it a return flight?")
    args = parser.parse_args()

    # * Timer
    timer = time.perf_counter()

    # * Results
    output = []
    outbound_connections = search_engine(args.input, args.origin, args.destination, args.bags_count)

    # * Format Results
    for outbound_route in outbound_connections:

        # Return Ticket: for each outbound route a matching list of inbound routes will be searched.
        if args.with_return:
            inbound_connections = search_engine(args.input, args.destination, args.origin, args.bags_count, outbound_route[-1].arrival)

            # Only routes with at least one valid inbound route will be considered.
            if inbound_connections:
                for inbound_route in inbound_connections:
                    round_trip = outbound_route + inbound_route
                    output.append(route_formatting(args, round_trip, True))

        else:
            output.append(route_formatting(args, outbound_route))

    # * Sorting & Exproting output
    sorted_output = sorted(output, key=lambda d: d["total_price"])
    with open("results.json", "w") as f:
        f.write(json.dumps(sorted_output, indent=4, default=str))

    print(f"\nTimer: { round(time.perf_counter() - timer, 5) } | Flights Count: {len(sorted_output)}\n")

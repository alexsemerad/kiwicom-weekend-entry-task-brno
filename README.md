# Python weekend entry task

## Summary

1. A stack with possible routes, starting with the flights from the origin airport, is initialised. From there, we explore if the destination of any of these flights is our goal destination.
2. If it is the case, we had it to our solutions list. If not, we add the connecting flights (the flights originating from the destination of the respective flight) to the stack.
3. While adding new flights to the stack, we keep track of the previous flights leading to each route (e.g. A, A -> B, A -> B -> C) and subsequently only retrieve connecting flights from airports that are not in the route (e.g. D, E, F, etc.).
4. Finally, once each combination is explored (no stopover airports with connecting flights left) and the stack is empty, we format and return the list of solutions.
5. The output is a JSON file! Additionally, the time performance and route count will be printed in the console.

## Full Description

Given the arguments: input, origin, destination, bags_count and with_return returns a JSON compatible list of suitable flights, sorted by price.

1. First, the input data is read and converted into a list Dataclasses ("Flight"), formatting the following attributes:
    * departure and arrival to datetime objects.
    * base_price and bag_price to Decimal objects.
    * bags_allowed to an integer.

2. This list is further processed into a dictionary (function get_flights), with:
    * Key: the origin airport.
    * Value: list of flights departing from said aiport.

3. Lastly, we initialise the search with a list of outbound flights from the origin airport that is filtered by:
    * the bags allowed.
    * The departure time (relevant for return flights)

4. Each flight is saved in a Node with 2 attributes:
    * state: the current flight information.
    * parent: the previous Node of the connecting flight information, which may have it's own parent and so on.

5. The list of nodes (containing the flight information) will be added to a StackFrontier that keeps track of the combinations to be explored.

6. The search begins (While Loop in the function search_engine) by:
    * Taking the last Node from the frontier list and checking if the destination of said flight matches with our goal, the destination airport.
    * If it matches, it will be added to the solutions list.

7. Next, valid connecting flights (function get_connection_flights) will be added to the frontier. with the following considerations:
    * Only flights within the acceptable layover timeframe.
    * Only flights with the allowed number of bags.
    * Only flights that don't arrive at the original airport.
    * Only flights that don't arrive at any previous airport of the current route.

8. Once the frontier is exhausted (no combinations left), the While loop will be exited.

9. If the keyword "with_return" is passed, then for each outbound route a matching list of inbound routes will be searched:
    * Steps 2-7 will be repeated with the destination and origin from the outbound flight as origin and destination input for the inbound flights.
    * Additionally, the arrival time from the last outbound flight on the route will be passed as departure time to limit the search for flights from that point in time.
    * In the final output, only routes with at least one valid inbound route will be considered.

10. The last step is to format the output according to the specifications (structured list of trips sorted by price) and to write it in a JSON file in the current directory.

## Argument Details

To run the script, use the command `python3 -m solution -i PATH_TO_CSV_FILE -o ORIGIN -d DESTINATION -b BAGS_COUNT` replacing the argument placeholders in capital letters with values.

| Argument name | flag | type    | Description                                                                                                    |
|---------------|-----|---------|----------------------------------------------------------------------------------------------------------------|
| `input`       | -i  | string  | Path to input CSV file containing flight data                                                                    |
| `origin`      | -o  | string  | Origin airport code                                                                                            |
| `destination` | -d  | string  | Destination airport code                                                                                       |
| `bags_count`  | -b  | integer | Number of bags                                                                                                 |
| `with_return` | -r  | boolean | With return flight back to original airport. Only outbound flights with at least one return flight will be shown. |

## Example with run time and result count

| Run Time | Results | Command                                                                        |
|----------|---------|--------------------------------------------------------------------------------|
| 0.00303  | 3       | `python3 -m solution -i example/example0.csv -o RFZ -d WIW -b 1`               |
| 0.00606  | 3       | `python3 -m solution -i example/example0.csv -o RFZ -d WIW -b 1 --with_return` |
| 0.00771  | 14      | `python3 -m solution -i example/example1.csv -o DHE -d NIZ -b 1`               |
| 0.04132  | 69      | `python3 -m solution -i example/example1.csv -o DHE -d NIZ -b 1 --with_return` |
| 0.01052  | 18      | `python3 -m solution -i example/example2.csv -o GXV -d LOM -b 1`               |
| 0.1261   | 189     | `python3 -m solution -i example/example2.csv -o GXV -d LOM -b 1 --with_return` |
| 0.04529  | 89      | `python3 -m solution -i example/example3.csv -o EZO -d NNB -b 1`               |
| 2.08391  | 2194    | `python3 -m solution -i example/example3.csv -o EZO -d NNB -b 1 --with_return` |

## Notes

* We assume that the input file path and the data in the input file is correct!
* Searching for the return flight might not have been ideally implemented.
* I hope the results are correct!

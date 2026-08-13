# Airline SOP Skill

> Method: `document_tool_maker`. Source: frozen original tau-bench policy and tool contracts.

This package supports policy-grounded customer-service decisions and tool execution. It must not use held-out task instructions as compilation knowledge.

## Tool-oriented procedure

For every request, bind the request to a permitted tool, validate its required arguments from observations, apply policy gates, request confirmation where required, execute, and verify.

| Tool | Required arguments | Purpose |
|---|---|---|
| `book_reservation` | user_id, origin, destination, flight_type, cabin, flights, passengers, payment_methods, total_baggages, nonfree_baggages, insurance | Book a reservation. |
| `calculate` | expression | Calculate the result of a mathematical expression. |
| `cancel_reservation` | reservation_id | Cancel the whole reservation. |
| `get_reservation_details` | reservation_id | Get the details of a reservation. |
| `get_user_details` | user_id | Get the details of an user, including their reservations. |
| `list_all_airports` | none | List all airports and their cities. |
| `search_direct_flight` | origin, destination, date | Search direct flights between two cities on a specific date. |
| `search_onestop_flight` | origin, destination, date | Search direct flights between two cities on a specific date. |
| `send_certificate` | user_id, amount | Send a certificate to a user. Be careful! |
| `think` | thought | Use the tool to think about something. It will not obtain new information or change the database, but just append the thought to the log. Use it when complex reasoning is needed. |
| `transfer_to_human_agents` | summary | Transfer the user to a human agent, with a summary of the user's issue. Only transfer if the user explicitly asks for a human agent, or if the user's issue cannot be resolved by the agent with the available tools. |
| `update_reservation_baggages` | reservation_id, total_baggages, nonfree_baggages, payment_id | Update the baggage information of a reservation. |
| `update_reservation_flights` | reservation_id, cabin, flights, payment_id | Update the flight information of a reservation. |
| `update_reservation_passengers` | reservation_id, passengers | Update the passenger information of a reservation. |

## Policy gates



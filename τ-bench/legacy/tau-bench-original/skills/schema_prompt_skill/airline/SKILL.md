# Airline SOP Skill

> Method: `schema_prompt_skill`. Source: frozen original tau-bench policy and tool contracts.

This package supports policy-grounded customer-service decisions and tool execution. It must not use held-out task instructions as compilation knowledge.


## Scope

Handle only requests supported by the domain policy and available tools.

## Decision procedure

1. Identify the user and requested outcome.
2. Retrieve current state with read-only tools.
3. Check eligibility, required inputs, prohibitions, and confirmation requirements.
4. Choose `execute`, `clarify`, `deny`, `escalate`, `no_action`, or `execution_failed`.
5. Before a mutation, state the exact transaction and obtain any required authorization.
6. Execute one tool at a time and verify the resulting state.

## Policy sections

- **Airline Agent Policy**: The current time is 2024-05-15 15:00:00 EST.

As an airline agent, you can help users book, modify, or cancel flight reservations.

- Before taking any actions that update the booking database (booking, modifying flights, editing baggage, upgrading cabin class, or updating passenger information), yo
- **Domain Basic**: - Each user has a profile containing user id, email, addresses, date of birth, payment methods, reservation numbers, and membership tier.

- Each reservation has an reservation id, user id, trip type (one way, round trip), flights, passengers, payment methods, created time, baggages, and travel insu
- **Book flight**: - The agent must first obtain the user id, then ask for the trip type, origin, destination.

- Passengers: Each reservation can have at most five passengers. The agent needs to collect the first name, last name, and date of birth for each passenger. All passengers must fly the same flights in the sa
- **Modify flight**: - The agent must first obtain the user id and the reservation id.

- Change flights: Basic economy flights cannot be modified. Other reservations can be modified without changing the origin, destination, and trip type. Some flight segments can be kept, but their prices will not be updated based on t
- **Cancel flight**: - The agent must first obtain the user id, the reservation id, and the reason for cancellation (change of plan, airline cancelled flight, or other reasons)

- All reservations can be cancelled within 24 hours of booking, or if the airline cancelled the flight. Otherwise, basic economy or economy fli
- **Refund**: - If the user is silver/gold member or has travel insurance or flies business, and complains about cancelled flights in a reservation, the agent can offer a certificate as a gesture after confirming the facts, with the amount being $100 times the number of passengers.

- If the user is silver/gold m

## Tool schema

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

## Output

Return status, answer, tool actions, policy evidence IDs, missing inputs, and final-state verification.

# Airline SOP Skill

> Method: `evoskill_compiler`. Source: frozen original tau-bench policy and tool contracts.

This package supports policy-grounded customer-service decisions and tool execution. It must not use held-out task instructions as compilation knowledge.

## Knowledge atoms

- `KA-0001` **Airline Agent Policy** (policy_section): The current time is 2024-05-15 15:00:00 EST.

As an airline agent, you can help users book, modify, or cancel flight reservations.

- Before taking any actions that update the booking database (booking, modifying flights, editing baggage, upgrading cabin class, or updating passenger information), you must list the action details and obtain explicit user confirmation (yes) to proceed.

- You should not provide any inf
- `KA-0002` **Domain Basic** (policy_section): - Each user has a profile containing user id, email, addresses, date of birth, payment methods, reservation numbers, and membership tier.

- Each reservation has an reservation id, user id, trip type (one way, round trip), flights, passengers, payment methods, created time, baggages, and travel insurance information.

- Each flight has a flight number, an origin, destination, scheduled departure and arrival time (loc
- `KA-0003` **Book flight** (policy_section): - The agent must first obtain the user id, then ask for the trip type, origin, destination.

- Passengers: Each reservation can have at most five passengers. The agent needs to collect the first name, last name, and date of birth for each passenger. All passengers must fly the same flights in the same cabin.

- Payment: each reservation can use at most one travel certificate, at most one credit card, and at most thre
- `KA-0004` **Modify flight** (policy_section): - The agent must first obtain the user id and the reservation id.

- Change flights: Basic economy flights cannot be modified. Other reservations can be modified without changing the origin, destination, and trip type. Some flight segments can be kept, but their prices will not be updated based on the current price. The API does not check these for the agent, so the agent must make sure the rules apply before calling
- `KA-0005` **Cancel flight** (policy_section): - The agent must first obtain the user id, the reservation id, and the reason for cancellation (change of plan, airline cancelled flight, or other reasons)

- All reservations can be cancelled within 24 hours of booking, or if the airline cancelled the flight. Otherwise, basic economy or economy flights can be cancelled only if travel insurance is bought and the condition is met, and business flights can always be ca
- `KA-0006` **Refund** (policy_section): - If the user is silver/gold member or has travel insurance or flies business, and complains about cancelled flights in a reservation, the agent can offer a certificate as a gesture after confirming the facts, with the amount being $100 times the number of passengers.

- If the user is silver/gold member or has travel insurance or flies business, and complains about delayed flights in a reservation and wants to chang
- `KA-0007` **book_reservation** (tool_contract): Book a reservation.
- `KA-0008` **calculate** (tool_contract): Calculate the result of a mathematical expression.
- `KA-0009` **cancel_reservation** (tool_contract): Cancel the whole reservation.
- `KA-0010` **get_reservation_details** (tool_contract): Get the details of a reservation.
- `KA-0011` **get_user_details** (tool_contract): Get the details of an user, including their reservations.
- `KA-0012` **list_all_airports** (tool_contract): List all airports and their cities.
- `KA-0013` **search_direct_flight** (tool_contract): Search direct flights between two cities on a specific date.
- `KA-0014` **search_onestop_flight** (tool_contract): Search direct flights between two cities on a specific date.
- `KA-0015` **send_certificate** (tool_contract): Send a certificate to a user. Be careful!
- `KA-0016` **think** (tool_contract): Use the tool to think about something. It will not obtain new information or change the database, but just append the thought to the log. Use it when complex reasoning is needed.
- `KA-0017` **transfer_to_human_agents** (tool_contract): Transfer the user to a human agent, with a summary of the user's issue. Only transfer if the user explicitly asks for a human agent, or if the user's issue cannot be resolved by the agent with the available tools.
- `KA-0018` **update_reservation_baggages** (tool_contract): Update the baggage information of a reservation.
- `KA-0019` **update_reservation_flights** (tool_contract): Update the flight information of a reservation.
- `KA-0020` **update_reservation_passengers** (tool_contract): Update the passenger information of a reservation.

## Governance policy



## Execution strategy

Retrieve policy atoms and tool contracts separately. Check identity, current state, eligibility, required arguments, authorization, mutation result, and provenance in that order. A frequent workflow never overrides a policy atom.

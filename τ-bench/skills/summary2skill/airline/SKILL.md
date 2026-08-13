# Airline τ³ SOP Skill

> Method: `summary2skill`. Compile-time sources are frozen τ³-bench policy, tool contracts, knowledge documents where applicable, and training tasks only where an official train split exists.

## Policy summary

- **Airline Agent Policy**: The current time is 2024-05-15 15:00:00 EST.

As an airline agent, you can help users **book**, **modify**, or **cancel** flight reservations. You also handle **refunds and compensation**.

Before taking any actions that update the booking database (booking, modifying flights, editing baggage, changing cabin class, or updating passenger information), you must list the action details and obtain explicit user confirmat
- **Domain Basic**: 
- **User**: Each user has a profile containing:
- user id
- email
- addresses
- date of birth
- payment methods
- membership level
- reservation numbers

There are three types of payment methods: **credit card**, **gift card**, **travel certificate**.

There are three membership levels: **regular**, **silver**, **gold**.
- **Flight**: Each flight has the following attributes:
- flight number
- origin
- destination
- scheduled departure and arrival time (local time)

A flight can be available at multiple dates. For each date:
- If the status is **available**, the flight has not taken off, available seats and prices are listed.
- If the status is **delayed** or **on time**, the flight has not taken off, cannot be booked.
- If the status is **flying*
- **Reservation**: Each reservation specifies the following:
- reservation id
- user id
- trip type
- flights
- passengers
- payment methods
- created time
- baggages
- travel insurance information

There are two types of trip: **one way** and **round trip**.
- **Book flight**: The agent must first obtain the user id from the user. 

The agent should then ask for the trip type, origin, destination.

Cabin:
- Cabin class must be the same across all the flights in a reservation. 

Passengers: 
- Each reservation can have at most five passengers. 
- The agent needs to collect the first name, last name, and date of birth for each passenger. 
- All passengers must fly the same flights in the sam
- **Modify flight**: First, the agent must obtain the user id and reservation id. 
- The user must provide their user id. 
- If the user doesn't know their reservation id, the agent should help locate it using available tools.

Change flights: 
- Basic economy flights cannot be modified.
- Other reservations can be modified without changing the origin, destination, and trip type.
- Some flight segments can be kept, but their prices will 
- **Cancel flight**: First, the agent must obtain the user id and reservation id. 
- The user must provide their user id. 
- If the user doesn't know their reservation id, the agent should help locate it using available tools.

The agent must also obtain the reason for cancellation (change of plan, airline cancelled flight, or other reasons)

If any portion of the flight has already been flown, the agent cannot help and transfer is neede
- **Refunds and Compensation**: Do not proactively offer a compensation unless the user explicitly asks for one.

Do not compensate if the user is regular member and has no travel insurance and flies (basic) economy.

Always confirms the facts before offering compensation.

Only compensate if the user is a silver/gold member or has travel insurance or flies business.

- If the user complains about cancelled flights in a reservation, the agent can o

## Training workflow summaries

- `WF-0001` (3): assistant:get_reservation_details
- `WF-0002` (2): assistant:get_user_details → assistant:get_reservation_details
- `WF-0003` (2): assistant:get_user_details → assistant:get_reservation_details → assistant:get_reservation_details → assistant:get_reservation_details → assistant:get_reservation_details → assistant:get_reservation_details
- `WF-0004` (2): assistant:get_user_details
- `WF-0005` (2): assistant:update_reservation_flights
- `WF-0006` (1): assistant:get_reservation_details → assistant:get_user_details
- `WF-0007` (1): assistant:get_reservation_details → assistant:get_reservation_details → assistant:update_reservation_flights → assistant:cancel_reservation → assistant:cancel_reservation
- `WF-0008` (1): assistant:search_direct_flight
- `WF-0009` (1): assistant:get_reservation_details → assistant:search_direct_flight → assistant:search_direct_flight → assistant:calculate → assistant:update_reservation_baggages
- `WF-0010` (1): assistant:cancel_reservation → assistant:book_reservation
- `WF-0011` (1): assistant:update_reservation_flights → assistant:update_reservation_passengers → assistant:update_reservation_baggages
- `WF-0012` (1): assistant:book_reservation
- `WF-0013` (1): assistant:update_reservation_flights → assistant:update_reservation_baggages
- `WF-0014` (1): assistant:cancel_reservation → assistant:book_reservation → assistant:book_reservation → assistant:book_reservation
- `WF-0015` (1): assistant:get_reservation_details → assistant:search_direct_flight → assistant:search_direct_flight → assistant:update_reservation_flights → assistant:update_reservation_baggages
- `WF-0016` (1): assistant:get_user_details → assistant:get_reservation_details → assistant:get_reservation_details → assistant:get_reservation_details → assistant:get_reservation_details → assistant:get_reservation_details → assistant:get_reservation_details → assistant:get_reservation_details → assistant:cancel_reservation → assistant:cancel_reservation → assistant:cancel_reservation
- `WF-0017` (1): assistant:get_reservation_details → assistant:update_reservation_passengers
- `WF-0018` (1): assistant:get_user_details → assistant:get_reservation_details → assistant:get_reservation_details → assistant:get_reservation_details → assistant:get_reservation_details → assistant:get_reservation_details → assistant:get_reservation_details → assistant:get_reservation_details
- `WF-0019` (1): assistant:get_user_details → assistant:get_reservation_details → assistant:get_reservation_details → assistant:get_reservation_details → assistant:get_reservation_details → assistant:get_reservation_details → assistant:get_reservation_details → assistant:get_reservation_details → assistant:cancel_reservation → assistant:cancel_reservation

Workflow frequency is not policy and does not define a unique correct trajectory.

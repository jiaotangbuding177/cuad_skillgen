# Airline Skill Catalog

> Method: `a2sc`. Full module instructions are loaded on demand by the runtime.

## Modules

- `airline.book_reservation`: Use for tasks involving book reservation; the declared tool actor is assistant. Tools: book_reservation.

- `airline.calculate`: Use for tasks involving calculate; the declared tool actor is assistant. Tools: calculate.

- `airline.cancel_reservation`: Use for tasks involving cancel reservation; the declared tool actor is assistant. Tools: get_reservation_details, cancel_reservation.

- `airline.get_flight_status`: Use for tasks involving get flight status; the declared tool actor is assistant. Tools: get_flight_status.

- `airline.get_reservation_details`: Use for tasks involving get reservation details; the declared tool actor is assistant. Tools: get_user_details, get_reservation_details, search_direct_flight.

- `airline.get_user_details`: Use for tasks involving get user details; the declared tool actor is assistant. Tools: get_user_details, get_reservation_details.

- `airline.list_all_airports`: Use for tasks involving list all airports; the declared tool actor is assistant. Tools: list_all_airports.

- `airline.search_direct_flight`: Use for tasks involving search direct flight; the declared tool actor is assistant. Tools: get_reservation_details, search_direct_flight.

- `airline.search_onestop_flight`: Use for tasks involving search onestop flight; the declared tool actor is assistant. Tools: search_onestop_flight.

- `airline.send_certificate`: Use for tasks involving send certificate; the declared tool actor is assistant. Tools: send_certificate.

- `airline.transfer_to_human_agents`: Use for tasks involving transfer to human agents; the declared tool actor is assistant. Tools: transfer_to_human_agents.

- `airline.update_reservation_baggages`: Use for tasks involving update reservation baggages; the declared tool actor is assistant. Tools: update_reservation_baggages.

- `airline.update_reservation_flights`: Use for tasks involving update reservation flights; the declared tool actor is assistant. Tools: update_reservation_flights.

- `airline.update_reservation_passengers`: Use for tasks involving update reservation passengers; the declared tool actor is assistant. Tools: update_reservation_passengers.

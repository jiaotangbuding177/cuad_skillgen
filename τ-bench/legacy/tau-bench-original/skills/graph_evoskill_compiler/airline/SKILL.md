# Airline SOP Skill

> Method: `graph_evoskill_compiler`. Source: frozen original tau-bench policy and tool contracts.

This package supports policy-grounded customer-service decisions and tool execution. It must not use held-out task instructions as compilation knowledge.

## Graph-selected SOP Pattern Cards

### PAT-001: Airline Agent Policy

- Central atom: `KA-0001`
- Related atoms: `KA-0002`, `KA-0003`, `KA-0004`, `KA-0005`, `KA-0006`, `KA-0007`, `KA-0009`, `KA-0010`, `KA-0011`, `KA-0012`, `KA-0013`, `KA-0014`
- Related tools: `book_reservation`, `cancel_reservation`, `get_reservation_details`, `get_user_details`, `list_all_airports`, `search_direct_flight`, `search_onestop_flight`, `transfer_to_human_agents`, `update_reservation_baggages`, `update_reservation_flights`, `update_reservation_passengers`
- Required reasoning: retrieve state → check conditions/exceptions → choose status → obtain authorization if required → execute → verify.

### PAT-002: Domain Basic

- Central atom: `KA-0002`
- Related atoms: `KA-0001`, `KA-0003`, `KA-0004`, `KA-0005`, `KA-0006`, `KA-0007`, `KA-0009`, `KA-0010`, `KA-0013`, `KA-0014`, `KA-0016`, `KA-0017`
- Related tools: `book_reservation`, `cancel_reservation`, `get_reservation_details`, `search_direct_flight`, `search_onestop_flight`, `update_reservation_baggages`, `update_reservation_flights`, `update_reservation_passengers`
- Required reasoning: retrieve state → check conditions/exceptions → choose status → obtain authorization if required → execute → verify.

### PAT-003: Book flight

- Central atom: `KA-0003`
- Related atoms: `KA-0001`, `KA-0002`, `KA-0004`, `KA-0005`, `KA-0006`, `KA-0007`, `KA-0009`, `KA-0010`, `KA-0012`, `KA-0013`, `KA-0014`, `KA-0015`
- Related tools: `book_reservation`, `cancel_reservation`, `get_reservation_details`, `list_all_airports`, `search_direct_flight`, `search_onestop_flight`, `send_certificate`, `update_reservation_baggages`, `update_reservation_flights`, `update_reservation_passengers`
- Required reasoning: retrieve state → check conditions/exceptions → choose status → obtain authorization if required → execute → verify.

### PAT-004: Modify flight

- Central atom: `KA-0004`
- Related atoms: `KA-0001`, `KA-0002`, `KA-0003`, `KA-0005`, `KA-0006`, `KA-0007`, `KA-0009`, `KA-0010`, `KA-0011`, `KA-0012`, `KA-0013`, `KA-0014`
- Related tools: `book_reservation`, `cancel_reservation`, `get_reservation_details`, `list_all_airports`, `search_direct_flight`, `search_onestop_flight`, `transfer_to_human_agents`, `update_reservation_baggages`, `update_reservation_flights`, `update_reservation_passengers`
- Required reasoning: retrieve state → check conditions/exceptions → choose status → obtain authorization if required → execute → verify.

### PAT-005: Cancel flight

- Central atom: `KA-0005`
- Related atoms: `KA-0001`, `KA-0002`, `KA-0003`, `KA-0004`, `KA-0006`, `KA-0007`, `KA-0009`, `KA-0010`, `KA-0011`, `KA-0012`, `KA-0013`, `KA-0014`
- Related tools: `book_reservation`, `cancel_reservation`, `get_reservation_details`, `list_all_airports`, `search_direct_flight`, `search_onestop_flight`, `transfer_to_human_agents`, `update_reservation_baggages`, `update_reservation_flights`, `update_reservation_passengers`
- Required reasoning: retrieve state → check conditions/exceptions → choose status → obtain authorization if required → execute → verify.

### PAT-006: Refund

- Central atom: `KA-0006`
- Related atoms: `KA-0001`, `KA-0002`, `KA-0003`, `KA-0004`, `KA-0005`, `KA-0007`, `KA-0009`, `KA-0010`, `KA-0013`, `KA-0014`, `KA-0015`, `KA-0016`
- Related tools: `book_reservation`, `cancel_reservation`, `get_reservation_details`, `send_certificate`, `update_reservation_baggages`, `update_reservation_flights`, `update_reservation_passengers`
- Required reasoning: retrieve state → check conditions/exceptions → choose status → obtain authorization if required → execute → verify.

## Governance policy



## Runtime boundary

The graph is compile-time organization only. Runtime still uses the same tools and environment as every baseline.

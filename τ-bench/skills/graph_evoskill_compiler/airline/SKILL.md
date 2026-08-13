# Airline τ³ SOP Skill

> Method: `graph_evoskill_compiler`. Compile-time sources are frozen τ³-bench policy, tool contracts, knowledge documents where applicable, and training tasks only where an official train split exists.

## Graph-selected Pattern Cards

### PAT-0001: Airline Agent Policy

Central atom `KA-00001`; related atoms: KA-00006, KA-00007, KA-00008, KA-00009, KA-00019, KA-00021.

### PAT-0002: Domain Basic

Central atom `KA-00002`; related atoms: none.

### PAT-0003: User

Central atom `KA-00003`; related atoms: KA-00005, KA-00006, KA-00009, KA-00020, KA-00021.

### PAT-0004: Flight

Central atom `KA-00004`; related atoms: KA-00005, KA-00006, KA-00007, KA-00008, KA-00009, KA-00010, KA-00016, KA-00017, KA-00023.

### PAT-0005: Reservation

Central atom `KA-00005`; related atoms: KA-00003, KA-00004, KA-00006, KA-00007, KA-00008, KA-00009, KA-00010, KA-00021, KA-00022.

### PAT-0006: Book flight

Central atom `KA-00006`; related atoms: KA-00001, KA-00003, KA-00004, KA-00005, KA-00007, KA-00008, KA-00009, KA-00010, KA-00020, KA-00021.

### PAT-0007: Modify flight

Central atom `KA-00007`; related atoms: KA-00001, KA-00004, KA-00005, KA-00006, KA-00008, KA-00009, KA-00010, KA-00020, KA-00021.

### PAT-0008: Cancel flight

Central atom `KA-00008`; related atoms: KA-00001, KA-00004, KA-00005, KA-00006, KA-00007, KA-00009, KA-00019.

### PAT-0009: Refunds and Compensation

Central atom `KA-00009`; related atoms: KA-00001, KA-00003, KA-00004, KA-00005, KA-00006, KA-00007, KA-00008, KA-00010, KA-00019.

## Runtime boundary

The graph changes compile-time organization only. Runtime tools, environment, task evaluator and retrieval budget remain fixed.

## Governance

- `POL-0001` Airline Agent Policy
- `POL-0002` Domain Basic
- `POL-0003` User
- `POL-0004` Flight
- `POL-0005` Reservation
- `POL-0006` Book flight
- `POL-0007` Modify flight
- `POL-0008` Cancel flight
- `POL-0009` Refunds and Compensation
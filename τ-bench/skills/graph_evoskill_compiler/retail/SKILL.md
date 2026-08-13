# Retail τ³ SOP Skill

> Method: `graph_evoskill_compiler`. Compile-time sources are frozen τ³-bench policy, tool contracts, knowledge documents where applicable, and training tasks only where an official train split exists.

## Graph-selected Pattern Cards

### PAT-0001: Retail agent policy

Central atom `KA-00001`; related atoms: KA-00004, KA-00005, KA-00006, KA-00007, KA-00008, KA-00010, KA-00011, KA-00012, KA-00014, KA-00015, KA-00016, KA-00023, KA-00024, KA-00025, KA-00026, KA-00027, KA-00028.

### PAT-0002: Domain basic

Central atom `KA-00002`; related atoms: KA-00022.

### PAT-0003: User

Central atom `KA-00003`; related atoms: KA-00004, KA-00005, KA-00010, KA-00011, KA-00012, KA-00022.

### PAT-0004: Product

Central atom `KA-00004`; related atoms: KA-00001, KA-00003, KA-00005, KA-00008, KA-00010, KA-00012, KA-00015, KA-00020, KA-00022, KA-00024, KA-00027.

### PAT-0005: Order

Central atom `KA-00005`; related atoms: KA-00001, KA-00003, KA-00004, KA-00006, KA-00007, KA-00008, KA-00009, KA-00010, KA-00011, KA-00012, KA-00014, KA-00015, KA-00022, KA-00024, KA-00025, KA-00027.

### PAT-0006: Generic action rules

Central atom `KA-00006`; related atoms: KA-00001, KA-00005, KA-00007, KA-00008, KA-00009, KA-00010, KA-00011, KA-00012, KA-00015, KA-00022, KA-00024.

### PAT-0007: Cancel pending order

Central atom `KA-00007`; related atoms: KA-00001, KA-00005, KA-00006, KA-00008, KA-00009, KA-00010, KA-00011, KA-00012, KA-00014, KA-00015, KA-00023, KA-00024, KA-00025, KA-00026, KA-00027.

### PAT-0008: Modify pending order

Central atom `KA-00008`; related atoms: KA-00001, KA-00004, KA-00005, KA-00006, KA-00007, KA-00009, KA-00010, KA-00011, KA-00012, KA-00014, KA-00015, KA-00022, KA-00023, KA-00024, KA-00025, KA-00027, KA-00028.

### PAT-0009: Modify payment

Central atom `KA-00009`; related atoms: KA-00005, KA-00006, KA-00007, KA-00008, KA-00010, KA-00011, KA-00012, KA-00014, KA-00015, KA-00024, KA-00025, KA-00027.

### PAT-0010: Modify items

Central atom `KA-00010`; related atoms: KA-00001, KA-00003, KA-00004, KA-00005, KA-00006, KA-00007, KA-00008, KA-00009, KA-00011, KA-00012, KA-00014, KA-00015, KA-00016, KA-00022, KA-00023, KA-00024, KA-00025, KA-00027, KA-00028.

### PAT-0011: Return delivered order

Central atom `KA-00011`; related atoms: KA-00001, KA-00003, KA-00005, KA-00006, KA-00007, KA-00008, KA-00009, KA-00010, KA-00012, KA-00014, KA-00015, KA-00016, KA-00024, KA-00025, KA-00027.

### PAT-0012: Exchange delivered order

Central atom `KA-00012`; related atoms: KA-00001, KA-00003, KA-00004, KA-00005, KA-00006, KA-00007, KA-00008, KA-00009, KA-00010, KA-00011, KA-00014, KA-00015, KA-00016, KA-00022, KA-00024, KA-00025, KA-00027.

## Runtime boundary

The graph changes compile-time organization only. Runtime tools, environment, task evaluator and retrieval budget remain fixed.

## Governance

- `POL-0001` Retail agent policy
- `POL-0002` Domain basic
- `POL-0003` User
- `POL-0004` Product
- `POL-0005` Order
- `POL-0006` Generic action rules
- `POL-0007` Cancel pending order
- `POL-0008` Modify pending order
- `POL-0009` Modify payment
- `POL-0010` Modify items
- `POL-0011` Return delivered order
- `POL-0012` Exchange delivered order
# Retail SOP Skill

> Method: `graph_evoskill_compiler`. Source: frozen original tau-bench policy and tool contracts.

This package supports policy-grounded customer-service decisions and tool execution. It must not use held-out task instructions as compilation knowledge.

## Graph-selected SOP Pattern Cards

### PAT-001: Retail agent policy

- Central atom: `KA-0001`
- Related atoms: `KA-0002`, `KA-0003`, `KA-0004`, `KA-0005`, `KA-0006`, `KA-0007`, `KA-0008`, `KA-0009`, `KA-0010`, `KA-0011`, `KA-0012`, `KA-0013`
- Related tools: `cancel_pending_order`, `exchange_delivered_order_items`, `find_user_id_by_email`, `find_user_id_by_name_zip`, `get_order_details`, `get_product_details`, `list_all_product_types`, `modify_pending_order_address`, `modify_pending_order_items`, `modify_pending_order_payment`, `modify_user_address`, `return_delivered_order_items`, `transfer_to_human_agents`
- Required reasoning: retrieve state → check conditions/exceptions → choose status → obtain authorization if required → execute → verify.

### PAT-002: Domain basic

- Central atom: `KA-0002`
- Related atoms: `KA-0001`, `KA-0003`, `KA-0004`, `KA-0005`, `KA-0006`, `KA-0007`, `KA-0008`, `KA-0009`, `KA-0010`, `KA-0011`, `KA-0012`, `KA-0013`
- Related tools: `cancel_pending_order`, `exchange_delivered_order_items`, `find_user_id_by_email`, `get_order_details`, `get_product_details`, `list_all_product_types`, `modify_pending_order_address`, `modify_pending_order_items`, `modify_pending_order_payment`, `modify_user_address`, `return_delivered_order_items`
- Required reasoning: retrieve state → check conditions/exceptions → choose status → obtain authorization if required → execute → verify.

### PAT-003: Cancel pending order

- Central atom: `KA-0003`
- Related atoms: `KA-0001`, `KA-0002`, `KA-0004`, `KA-0005`, `KA-0006`, `KA-0007`, `KA-0008`, `KA-0009`, `KA-0010`, `KA-0011`, `KA-0012`, `KA-0013`
- Related tools: `cancel_pending_order`, `exchange_delivered_order_items`, `get_order_details`, `modify_pending_order_address`, `modify_pending_order_items`, `modify_pending_order_payment`, `return_delivered_order_items`
- Required reasoning: retrieve state → check conditions/exceptions → choose status → obtain authorization if required → execute → verify.

### PAT-004: Modify pending order

- Central atom: `KA-0004`
- Related atoms: `KA-0001`, `KA-0002`, `KA-0003`, `KA-0005`, `KA-0006`, `KA-0007`, `KA-0008`, `KA-0009`, `KA-0010`, `KA-0011`, `KA-0012`, `KA-0013`
- Related tools: `cancel_pending_order`, `exchange_delivered_order_items`, `get_order_details`, `get_product_details`, `list_all_product_types`, `modify_pending_order_address`, `modify_pending_order_items`, `modify_pending_order_payment`, `modify_user_address`, `return_delivered_order_items`
- Required reasoning: retrieve state → check conditions/exceptions → choose status → obtain authorization if required → execute → verify.

### PAT-005: Modify payment

- Central atom: `KA-0005`
- Related atoms: `KA-0001`, `KA-0002`, `KA-0003`, `KA-0004`, `KA-0006`, `KA-0007`, `KA-0008`, `KA-0009`, `KA-0012`, `KA-0017`, `KA-0018`, `KA-0019`
- Related tools: `cancel_pending_order`, `exchange_delivered_order_items`, `get_order_details`, `modify_pending_order_address`, `modify_pending_order_items`, `modify_pending_order_payment`, `modify_user_address`, `return_delivered_order_items`
- Required reasoning: retrieve state → check conditions/exceptions → choose status → obtain authorization if required → execute → verify.

### PAT-006: Modify items

- Central atom: `KA-0006`
- Related atoms: `KA-0001`, `KA-0002`, `KA-0003`, `KA-0004`, `KA-0005`, `KA-0007`, `KA-0008`, `KA-0009`, `KA-0010`, `KA-0011`, `KA-0012`, `KA-0014`
- Related tools: `cancel_pending_order`, `exchange_delivered_order_items`, `get_order_details`, `get_product_details`, `get_user_details`, `list_all_product_types`, `modify_pending_order_address`, `modify_pending_order_items`, `modify_pending_order_payment`, `modify_user_address`, `return_delivered_order_items`
- Required reasoning: retrieve state → check conditions/exceptions → choose status → obtain authorization if required → execute → verify.

### PAT-007: Return delivered order

- Central atom: `KA-0007`
- Related atoms: `KA-0001`, `KA-0002`, `KA-0003`, `KA-0004`, `KA-0005`, `KA-0006`, `KA-0008`, `KA-0009`, `KA-0010`, `KA-0011`, `KA-0012`, `KA-0013`
- Related tools: `cancel_pending_order`, `exchange_delivered_order_items`, `find_user_id_by_email`, `get_order_details`, `list_all_product_types`, `modify_pending_order_address`, `modify_pending_order_items`, `modify_pending_order_payment`, `return_delivered_order_items`
- Required reasoning: retrieve state → check conditions/exceptions → choose status → obtain authorization if required → execute → verify.

### PAT-008: Exchange delivered order

- Central atom: `KA-0008`
- Related atoms: `KA-0001`, `KA-0002`, `KA-0003`, `KA-0004`, `KA-0005`, `KA-0006`, `KA-0007`, `KA-0009`, `KA-0010`, `KA-0011`, `KA-0012`, `KA-0013`
- Related tools: `cancel_pending_order`, `exchange_delivered_order_items`, `find_user_id_by_email`, `get_order_details`, `get_product_details`, `list_all_product_types`, `modify_pending_order_address`, `modify_pending_order_items`, `modify_pending_order_payment`, `modify_user_address`, `return_delivered_order_items`
- Required reasoning: retrieve state → check conditions/exceptions → choose status → obtain authorization if required → execute → verify.

## Governance policy

- `POL-001` You are a customer service representative for an online retail company. You are chatting with a customer, and you can call tools or respond to the user.
- `POL-002` The agent should always first confirm the user id by email or name+zip before proceeding with any task.
- `POL-003` The agent should not proceed with any task if the user id is not found.
- `POL-004` For any change to the backend database, e.g., address update, refund, or order cancellation, the agent must confirm the transaction details with the user and ask for permission, and get explicit authorization (yes) to proceed.
- `POL-005` The agent should solve the user task given the tools, without transferring to a human agent.
- `POL-006` The agent should not make up any information or knowledge not provided from the user or the tools.
- `POL-007` The agent should at most make one tool call at a time, and if the agent makes a tool call, it does not respond to the user at the same time.

## Runtime boundary

The graph is compile-time organization only. Runtime still uses the same tools and environment as every baseline.

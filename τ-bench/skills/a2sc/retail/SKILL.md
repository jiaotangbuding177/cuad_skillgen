# Retail Skill Catalog

> Method: `a2sc`. Full module instructions are loaded on demand by the runtime.

## Modules

- `retail.calculate`: Use for tasks involving calculate; the declared tool actor is assistant. Tools: get_order_details, get_product_details, calculate.

- `retail.cancel_pending_order`: Use for tasks involving cancel pending order; the declared tool actor is assistant. Tools: get_order_details, cancel_pending_order.

- `retail.exchange_delivered_order_items`: Use for tasks involving exchange delivered order items; the declared tool actor is assistant. Tools: get_product_details, exchange_delivered_order_items.

- `retail.find_user_id_by_email`: Use for tasks involving find user id by email; the declared tool actor is assistant. Tools: find_user_id_by_email, get_user_details.

- `retail.find_user_id_by_name_zip`: Use for tasks involving find user id by name zip; the declared tool actor is assistant. Tools: find_user_id_by_name_zip, get_user_details, get_order_details, get_product_details.

- `retail.get_item_details`: Use for tasks involving get item details; the declared tool actor is assistant. Tools: get_item_details, get_product_details.

- `retail.get_order_details`: Use for tasks involving get order details; the declared tool actor is assistant. Tools: get_user_details, find_user_id_by_name_zip, get_order_details, get_product_details, calculate.

- `retail.get_product_details`: Use for tasks involving get product details; the declared tool actor is assistant. Tools: get_order_details, find_user_id_by_name_zip, get_item_details, get_product_details, get_user_details, calculate.

- `retail.get_user_details`: Use for tasks involving get user details; the declared tool actor is assistant. Tools: find_user_id_by_name_zip, find_user_id_by_email, get_product_details, get_user_details, get_order_details.

- `retail.list_all_product_types`: Use for tasks involving list all product types; the declared tool actor is assistant. Tools: list_all_product_types.

- `retail.modify_pending_order_address`: Use for tasks involving modify pending order address; the declared tool actor is assistant. Tools: get_order_details, modify_pending_order_address.

- `retail.modify_pending_order_items`: Use for tasks involving modify pending order items; the declared tool actor is assistant. Tools: calculate, get_user_details, modify_pending_order_items.

- `retail.modify_pending_order_payment`: Use for tasks involving modify pending order payment; the declared tool actor is assistant. Tools: modify_pending_order_payment.

- `retail.modify_user_address`: Use for tasks involving modify user address; the declared tool actor is assistant. Tools: modify_user_address.

- `retail.return_delivered_order_items`: Use for tasks involving return delivered order items; the declared tool actor is assistant. Tools: get_order_details, get_product_details, calculate, return_delivered_order_items.

- `retail.transfer_to_human_agents`: Use for tasks involving transfer to human agents; the declared tool actor is assistant. Tools: transfer_to_human_agents.

# Retail τ³ SOP Skill

> Method: `evoskill_compiler`. Compile-time sources are frozen τ³-bench policy, tool contracts, knowledge documents where applicable, and training tasks only where an official train split exists.

## Knowledge atoms

- `KA-00001` [policy_section] **Retail agent policy**: As a retail agent, you can help users:

- **cancel or modify pending orders**
- **return or exchange delivered orders**
- **modify their default user address**
- **provide information about their own profile, orders, and related products**

At the beginning of the conversation, you have to authenticate the user identity by locating their user id via email, or via name + zip code. This has to be done even when the user already provides the user id.

Once the user has been authenticated, you can p
- `KA-00002` [policy_section] **Domain basic**: - All times in the database are EST and 24 hour based. For example "02:30:00" means 2:30 AM EST.
- `KA-00003` [policy_section] **User**: Each user has a profile containing:

- unique user id
- email
- default address
- payment methods.

There are three types of payment methods: **gift card**, **paypal account**, **credit card**.
- `KA-00004` [policy_section] **Product**: Our retail store has 50 types of products.

For each **type of product**, there are **variant items** of different **options**.

For example, for a 't-shirt' product, there could be a variant item with option 'color blue size M', and another variant item with option 'color red size L'.

Each product has the following attributes:

- unique product id
- name
- list of variants

Each variant item has the following attributes:

- unique item id
- information about the value of the product options fo
- `KA-00005` [policy_section] **Order**: Each order has the following attributes:

- unique order id
- user id
- address
- items ordered
- status
- fullfilments info (tracking id and item ids)
- payment history

The status of an order can be: **pending**, **processed**, **delivered**, or **cancelled**.

Orders can have other optional attributes based on the actions that have been taken (cancellation reason, which items have been exchanged, what was the exchane price difference etc)
- `KA-00006` [policy_section] **Generic action rules**: Generally, you can only take action on pending or delivered orders.

Exchange or modify order tools can only be called once per order. Be sure that all items to be changed are collected into a list before making the tool call!!!
- `KA-00007` [policy_section] **Cancel pending order**: An order can only be cancelled if its status is 'pending', and you should check its status before taking the action.

The user needs to confirm the order id and the reason (either 'no longer needed' or 'ordered by mistake') for cancellation. Other reasons are not acceptable.

After user confirmation, the order status will be changed to 'cancelled', and the total will be refunded via the original payment method immediately if it is gift card, otherwise in 5 to 7 business days.
- `KA-00008` [policy_section] **Modify pending order**: An order can only be modified if its status is 'pending', and you should check its status before taking the action.

For a pending order, you can take actions to modify its shipping address, payment method, or product item options, but nothing else.
- `KA-00009` [policy_section] **Modify payment**: The user can only choose a single payment method different from the original payment method.

If the user wants the modify the payment method to gift card, it must have enough balance to cover the total amount.

After user confirmation, the order status will be kept as 'pending'. The original payment method will be refunded immediately if it is a gift card, otherwise it will be refunded within 5 to 7 business days.
- `KA-00010` [policy_section] **Modify items**: This action can only be called once, and will change the order status to 'pending (items modifed)'. The agent will not be able to modify or cancel the order anymore. So you must confirm all the details are correct and be cautious before taking this action. In particular, remember to remind the customer to confirm they have provided all the items they want to modify.

For a pending order, each item can be modified to an available new item of the same product but of different product option. There
- `KA-00011` [policy_section] **Return delivered order**: An order can only be returned if its status is 'delivered', and you should check its status before taking the action.

The user needs to confirm the order id and the list of items to be returned.

The user needs to provide a payment method to receive the refund.

The refund must either go to the original payment method, or an existing gift card.

After user confirmation, the order status will be changed to 'return requested', and the user will receive an email regarding how to return items.
- `KA-00012` [policy_section] **Exchange delivered order**: An order can only be exchanged if its status is 'delivered', and you should check its status before taking the action. In particular, remember to remind the customer to confirm they have provided all items to be exchanged.

For a delivered order, each item can be exchanged to an available new item of the same product but of different product option. There cannot be any change of product types, e.g. modify shirt to shoe.

The user must provide a payment method to pay or receive refund of the pric
- `KA-00013` [tool_contract] **calculate**: Calculate the result of a mathematical expression.

Args:
    expression: The mathematical expression to calculate, such as '2 + 2'. The expression can contain numbers, operators (+, -, *, /), parentheses, and spaces.

Returns:
    The result of the mathematical expression.

Raises:
    ValueError: If the expression is invalid.
- `KA-00014` [tool_contract] **cancel_pending_order**: Cancel a pending order. If the order is already processed or delivered,
it cannot be cancelled. The agent needs to explain the cancellation detail
and ask for explicit user confirmation (yes/no) to proceed. If the user confirms,
the order status will be changed to 'cancelled' and the payment will be refunded.
The refund will be added to the user's gift card balance immediately if the payment
was made using a gift card, otherwise the refund would take 5-7 business days to process.
The function re
- `KA-00015` [tool_contract] **exchange_delivered_order_items**: Exchange items in a delivered order to new items of the same product type.
For a delivered order, return or exchange can be only done once by the agent.
The agent needs to explain the exchange detail and ask for explicit user confirmation (yes/no) to proceed.

Args:
    order_id: The order id, such as '#W0000000'. Be careful there is a '#' symbol at the beginning of the order id.
    item_ids: The item ids to be exchanged, each such as '1008292230'. There could be duplicate items in the list.
  
- `KA-00016` [tool_contract] **find_user_id_by_name_zip**: Find user id by first name, last name, and zip code. If the user is not found, the function
will return an error message. By default, find user id by email, and only call this function
if the user is not found by email or cannot remember email.

Args:
    first_name: The first name of the customer, such as 'John'.
    last_name: The last name of the customer, such as 'Doe'.
    zip: The zip code of the customer, such as '12345'.

Returns:
    str: The user id if found, otherwise an error message
- `KA-00017` [tool_contract] **find_user_id_by_email**: Find user id by email. If the user is not found, the function will return an error message.

Args:
    email: The email of the user, such as 'something@example.com'.

Returns:
    str: The user id if found, otherwise an error message.

Raises:
    ValueError: If the user is not found.
- `KA-00018` [tool_contract] **get_order_details**: Get the status and details of an order.

Args:
    order_id: The order id, such as '#W0000000'. Be careful there is a '#' symbol at the beginning of the order id.

Returns:
    Order: The order details.

Raises:
    ValueError: If the order is not found.
- `KA-00019` [tool_contract] **get_product_details**: Get the inventory details of a product.

Args:
    product_id: The product id, such as '6086499569'. Be careful the product id is different from the item id.

Returns:
    Product: The product details.

Raises:
    ValueError: If the product is not found.
- `KA-00020` [tool_contract] **get_item_details**: Get the inventory details of an item.

Args:
    item_id: The item id, such as '6086499569'. Be careful the item id is different from the product id.

Returns:
    Variant: The item details.

Raises:
    ValueError: If the item is not found.
- `KA-00021` [tool_contract] **get_user_details**: Get the details of a user, including their orders.

Args:
    user_id: The user id, such as 'sara_doe_496'.

Returns:
    User: The user details.

Raises:
    ValueError: If the user is not found.
- `KA-00022` [tool_contract] **list_all_product_types**: List the name and product id of all product types.
Each product type has a variety of different items with unique item ids and options.
There are only 50 product types in the store.

Returns:
    str: A JSON string mapping product names to their product IDs, sorted alphabetically by name.
- `KA-00023` [tool_contract] **modify_pending_order_address**: Modify the shipping address of a pending order. The agent needs to explain the modification detail and ask for explicit user confirmation (yes/no) to proceed.

Args:
    order_id: The order id, such as '#W0000000'. Be careful there is a '#' symbol at the beginning of the order id.
    address1: The first line of the address, such as '123 Main St'.
    address2: The second line of the address, such as 'Apt 1' or ''.
    city: The city, such as 'San Francisco'.
    state: The state, such as 'CA'.

- `KA-00024` [tool_contract] **modify_pending_order_items**: Modify items in a pending order to new items of the same product type. For a pending order, this function can only be called once. The agent needs to explain the exchange detail and ask for explicit user confirmation (yes/no) to proceed.

Args:
    order_id: The order id, such as '#W0000000'. Be careful there is a '#' symbol at the beginning of the order id.
    item_ids: The item ids to be modified, each such as '1008292230'. There could be duplicate items in the list.
    new_item_ids: The ite
- `KA-00025` [tool_contract] **modify_pending_order_payment**: Modify the payment method of a pending order. The agent needs to explain the modification detail and ask for explicit user confirmation (yes/no) to proceed.

Args:
    order_id: The order id, such as '#W0000000'. Be careful there is a '#' symbol at the beginning of the order id.
    payment_method_id: The payment method id to pay or receive refund for the item price difference, such as 'gift_card_0000000' or 'credit_card_0000000'. These can be looked up from the user or order details.

Returns:

- `KA-00026` [tool_contract] **modify_user_address**: Modify the default address of a user. The agent needs to explain the modification detail and ask for explicit user confirmation (yes/no) to proceed.

Args:
    user_id: The user id, such as 'sara_doe_496'.
    address1: The first line of the address, such as '123 Main St'.
    address2: The second line of the address, such as 'Apt 1' or ''.
    city: The city, such as 'San Francisco'.
    state: The state, such as 'CA'.
    country: The country, such as 'USA'.
    zip: The zip code, such as '123
- `KA-00027` [tool_contract] **return_delivered_order_items**: Return some items of a delivered order.
The order status will be changed to 'return requested'.
The agent needs to explain the return detail and ask for explicit user confirmation (yes/no) to proceed.
The user will receive follow-up email for how and where to return the item.

Args:
    order_id: The order id, such as '#W0000000'. Be careful there is a '#' symbol at the beginning of the order id.
    item_ids: The item ids to be returned, each such as '1008292230'. There could be duplicate items
- `KA-00028` [tool_contract] **transfer_to_human_agents**: Transfer the user to a human agent, with a summary of the user's issue.
Only transfer if
 -  the user explicitly asks for a human agent
 -  given the policy and the available tools, you cannot solve the user's issue.

Args:
    summary: A summary of the user's issue.

Returns:
    A message indicating the user has been transferred to a human agent.

## Governance rules

- `POL-0001` Retail agent policy — sources KA-00001
- `POL-0002` Domain basic — sources KA-00002
- `POL-0003` User — sources KA-00003
- `POL-0004` Product — sources KA-00004
- `POL-0005` Order — sources KA-00005
- `POL-0006` Generic action rules — sources KA-00006
- `POL-0007` Cancel pending order — sources KA-00007
- `POL-0008` Modify pending order — sources KA-00008
- `POL-0009` Modify payment — sources KA-00009
- `POL-0010` Modify items — sources KA-00010
- `POL-0011` Return delivered order — sources KA-00011
- `POL-0012` Exchange delivered order — sources KA-00012

## Runtime strategy

Retrieve knowledge and policy separately, identify the acting party, check state and exceptions, execute or instruct, verify all reward dimensions, and retain provenance.

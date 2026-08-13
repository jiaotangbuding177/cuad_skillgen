# Retail SOP Skill

> Method: `summary2skill`. Source: frozen original tau-bench policy and tool contracts.

This package supports policy-grounded customer-service decisions and tool execution. It must not use held-out task instructions as compilation knowledge.

## Policy summary

- **Retail agent policy**: As a retail agent, you can help users cancel or modify pending orders, return or exchange delivered orders, modify their default user address, or provide information about their own profile, orders, and related products.

- At the beginning of the conversation, you have to authenticate the user identity by locating their user id via email, or via name + zip 
- **Domain basic**: - All times in the database are EST and 24 hour based. For example "02:30:00" means 2:30 AM EST.

- Each user has a profile of its email, default address, user id, and payment methods. Each payment method is either a gift card, a paypal account, or a credit card.

- Our retail store has 50 types of products. For each type of product, there are variant items 
- **Cancel pending order**: - An order can only be cancelled if its status is 'pending', and you should check its status before taking the action.

- The user needs to confirm the order id and the reason (either 'no longer needed' or 'ordered by mistake') for cancellation.

- After user confirmation, the order status will be changed to 'cancelled', and the total will be refunded via th
- **Modify pending order**: - An order can only be modified if its status is 'pending', and you should check its status before taking the action.

- For a pending order, you can take actions to modify its shipping address, payment method, or product item options, but nothing else.
- **Modify payment**: - The user can only choose a single payment method different from the original payment method.

- If the user wants the modify the payment method to gift card, it must have enough balance to cover the total amount.

- After user confirmation, the order status will be kept 'pending'. The original payment method will be refunded immediately if it is a gift car
- **Modify items**: - This action can only be called once, and will change the order status to 'pending (items modifed)', and the agent will not be able to modify or cancel the order anymore. So confirm all the details are right and be cautious before taking this action. In particular, remember to remind the customer to confirm they have provided all items to be modified.

- Fo
- **Return delivered order**: - An order can only be returned if its status is 'delivered', and you should check its status before taking the action.

- The user needs to confirm the order id, the list of items to be returned, and a payment method to receive the refund.

- The refund must either go to the original payment method, or an existing gift card.

- After user confirmation, the 
- **Exchange delivered order**: - An order can only be exchanged if its status is 'delivered', and you should check its status before taking the action. In particular, remember to remind the customer to confirm they have provided all items to be exchanged.

- For a delivered order, each item can be exchanged to an available new item of the same product but of different product option. Ther

## Frequent training workflows

- `WF-001` (98 train examples): exchange_delivered_order_items
- `WF-002` (87 train examples): return_delivered_order_items
- `WF-003` (81 train examples): cancel_pending_order
- `WF-004` (68 train examples): modify_pending_order_items
- `WF-005` (14 train examples): modify_pending_order_payment → modify_pending_order_items
- `WF-006` (13 train examples): modify_pending_order_address → modify_pending_order_items
- `WF-007` (9 train examples): cancel_pending_order → cancel_pending_order
- `WF-008` (6 train examples): cancel_pending_order → modify_pending_order_items
- `WF-009` (6 train examples): cancel_pending_order → exchange_delivered_order_items
- `WF-010` (6 train examples): return_delivered_order_items → cancel_pending_order
- `WF-011` (5 train examples): exchange_delivered_order_items → cancel_pending_order
- `WF-012` (5 train examples): modify_pending_order_items → return_delivered_order_items
- `WF-013` (5 train examples): modify_pending_order_items → exchange_delivered_order_items
- `WF-014` (5 train examples): exchange_delivered_order_items → return_delivered_order_items
- `WF-015` (4 train examples): modify_pending_order_items → cancel_pending_order
- `WF-016` (4 train examples): cancel_pending_order → return_delivered_order_items
- `WF-017` (4 train examples): exchange_delivered_order_items → exchange_delivered_order_items
- `WF-018` (4 train examples): return_delivered_order_items → return_delivered_order_items
- `WF-019` (4 train examples): exchange_delivered_order_items → modify_pending_order_items
- `WF-020` (3 train examples): return_delivered_order_items → modify_pending_order_address → modify_pending_order_items

## Guardrail

Training workflow frequency is not policy. The current policy and backend state always take precedence.

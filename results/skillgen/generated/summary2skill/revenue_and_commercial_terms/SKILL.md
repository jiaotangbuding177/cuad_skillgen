# SKILL.md: Revenue and Commercial Terms Review

## Covered Categories

1.  **Revenue/Profit Sharing**
    *   **Discovery Frequency:** 28.1% of contracts (86/306)
    *   **Common Patterns:** Royalty payments based on Net/Gross Sales, fixed commission structures, joint venture profit splits (e.g., 50/50), and minimum guarantees/advances.

2.  **Minimum Commitment**
    *   **Discovery Frequency:** 27.5% of contracts (84/306)
    *   **Common Patterns:** Minimum purchase obligations (dollar/unit), performance milestones for exclusivity, and termination triggers for failing to meet sales thresholds.

3.  **Price Restrictions**
    *   **Discovery Frequency:** 18.6% of contracts (57/306)
    *   **Common Patterns:** CPI/Index-linked adjustments, Most Favored Nation (MFN) clauses, advance notice requirements for changes, and caps on annual increase percentages.

4.  **Volume Restriction**
    *   **Discovery Frequency:** 9.5% of contracts (29/306)
    *   **Common Patterns:** Tiered pricing structures, capacity caps/maximum order limits, forecast-based discretion for excess orders, and overage fees.

## Common Patterns

### Revenue/Profit Sharing
*   **Royalty Calculations:** Payments defined as a percentage of "Net Sales," "Gross Receipts," or "Net Revenue."
    *   *Example:* "Zynga is required to pay WPT a royalty equal to ten percent of the cumulative Net Revenue..."
*   **Joint Venture Splits:** Equal or defined splits of income, credits, and losses.
    *   *Example:* "...all income, credits, losses, and deductions are shared equally (50/50) between the two joint venturers."
*   **Recoupable Advances:** Minimum guarantees that are credited against future royalties.
    *   *Example:* "Zynga is obligated to pay WPT an Annual Minimum Guarantee of three million U.S. dollars... payable in semi-annual installments."

### Price Restrictions
*   **Index-Linked Adjustments:** Price changes tied to external metrics like CPI or commodity prices.
    *   *Example:* "...restricts price adjustments to specific triggers, such as changes in the Consumer Price Index (CPI)..."
*   **MFN Clauses:** Guarantees that prices are not less favorable than those offered to other partners.
    *   *Example:* "...rates charged to the Client do not exceed those charged to any other party."
*   **Notice and Cap Requirements:** Limits on frequency (e.g., once per year) and mandatory advance notice (e.g., 30-90 days).
    *   *Example:* "...capping annual increases at ten percent and requiring thirty days' prior notice."

### Minimum Commitment
*   **Purchase Obligations:** Binding requirements to buy specific quantities or dollar amounts.
    *   *Example:* "The Distributor is obligated to purchase a minimum agreed quantity of products in the first, second, and third years..."
*   **Performance Milestones:** Targets required to maintain rights (e.g., exclusivity) or avoid termination.
    *   *Example:* "...if the Company fails to sell a minimum of 708,050 Shares, the agreement shall terminate..."
*   **Liquidated Damages/Make-up Provisions:** Penalties for missing targets or options to carry over unmet minimums.
    *   *Example:* "...liquidated damages applied for failure to meet this volume."

### Volume Restriction
*   **Tiered Pricing:** Rates change based on volume thresholds (increasing or decreasing).
    *   *Example:* "...tiered fee structure where the fee rate per million traded decreases as the Monthly Notional Volume increases..."
*   **Capacity Caps:** Maximum limits on orders or usage.
    *   *Example:* "FCC is not obligated to accept purchase orders that exceed the Maximum Quantity... unless the parties agree in writing..."
*   **Forecast Discretion:** Provider discretion over orders exceeding forecasts.
    *   *Example:* "...orders exceeding forecasts by a certain percentage are subject to discretion."

## Review Checklist

*   **Revenue/Profit Sharing:**
    *   [ ] Is the base for calculation clearly defined (Gross vs. Net Sales/Revenue)?
    *   [ ] Are there minimum guarantees or advances, and are they recoupable?
    *   [ ] Is the payment frequency and reporting mechanism specified?
*   **Price Restrictions:**
    *   [ ] Are price increases capped by a percentage or tied to an external index?
    *   [ ] Is there a Most Favored Nation (MFN) clause protecting against higher pricing than competitors?
    *   [ ] What is the required advance notice period for any price change?
*   **Minimum Commitment:**
    *   [ ] Are there specific minimum purchase volumes or dollar amounts per period?
    *   [ ] What are the consequences of failing to meet these minimums (termination, damages, loss of exclusivity)?
    *   [ ] Are there "make-up" provisions allowing unmet minimums to be carried forward?
*   **Volume Restriction:**
    *   [ ] Are there maximum order limits or capacity constraints?
    *   [ ] Do pricing tiers change at specific volume thresholds?
    *   [ ] Is there a process for handling orders that exceed forecasts or caps (e.g., mutual agreement required)?

## Evidence Extraction Rules

1.  **Locate Financial Sections:** Search for sections titled "Payment," "Fees," "Royalties," "Pricing," "Purchase Obligations," or "Commercial Terms."
2.  **Identify Keywords:**
    *   *Revenue Sharing:* "royalty," "percentage of," "net sales," "gross receipts," "revenue share," "joint venture," "profit split."
    *   *Price Restrictions:* "price increase," "CPI," "index," "most favored nation," "MFN," "notice," "cap," "adjustment."
    *   *Minimum Commitment:* "minimum purchase," "minimum order," "guarantee," "milestone," "threshold," "termination if," "liquidated damages."
    *   *Volume Restriction:* "maximum quantity," "cap," "tier," "overage," "forecast," "excess," "capacity."
3.  **Extract Context:** When extracting evidence, include the specific metric (e.g., "5% of Gross Sales"), the condition (e.g., "if volume exceeds 1M units"), and the consequence (e.g., "fee increases by 2%").
4.  **Handle Variations:** Note if definitions vary (e.g., "Gross Profit" vs. "Net Sales") or if structures are complex (e.g., tiered percentages based on subscriber counts).

## Output Format

```json
{
  "status": "success|failure",
  "answer": {
    "revenue_sharing": {
      "exists": true|false,
      "details": "string describing the sharing model (e.g., '10% royalty on Net Revenue')",
      "base_metric": "string (e.g., 'Net Sales', 'Gross Receipts')"
    },
    "price_restrictions": {
      "exists": true|false,
      "mechanism": "string (e.g., 'CPI-linked', 'MFN clause', 'Fixed Cap')",
      "notice_period": "string (e.g., '30 days')",
      "cap_percentage": "number|null"
    },
    "minimum_commitment": {
      "exists": true|false,
      "type": "string (e.g., 'Purchase Volume', 'Sales Target')",
      "amount": "string (e.g., '708,050 Shares', '$3M Annual')",
      "consequence": "string (e.g., 'Termination', 'Liquidated Damages')"
    },
    "volume_restriction": {
      "exists": true|false,
      "type": "string (e.g., 'Tiered Pricing', 'Capacity Cap')",
      "threshold": "string (e.g., '1M units')",
      "impact": "string (e.g., 'Price decrease', 'Mutual agreement required')"
    }
  },
  "evidence_unit_ids": ["string", "string"],
  "source_contract_ids": ["string"],
  "missing_inputs": ["string"],
  "human_review_required": true|false
}
```

## Boundary Rules

*   **Do Not** infer revenue sharing or price restrictions if they are not explicitly stated in the contract text.
*   **Do Not** confuse "Minimum Commitment" (obligation to buy/sell) with "Volume Restriction" (limits on how much can be bought/sold or pricing changes due to volume).
*   **Do Not** extract standard payment terms (e.g., "Net 30") as Price Restrictions unless they involve dynamic pricing adjustments.
*   **Do** flag if "Net Sales" or "Gross Revenue" is defined in a way that significantly alters the calculation base (e.g., excluding taxes, returns, or discounts).
*   **Do** distinguish between unilateral rights to change prices (with notice) and mutual agreement requirements.
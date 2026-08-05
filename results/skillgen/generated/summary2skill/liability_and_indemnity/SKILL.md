# SKILL.md: Liability and Indemnity Review

## Covered Categories

Based on the analysis of 306 contracts, the following categories are covered with their respective discovery frequencies and common patterns:

1.  **Uncapped Liability** (26.1% of contracts)
    *   **Common Patterns:** Explicit exclusions of indemnification/confidentiality from general caps; statutory mandates preventing caps for personal injury/death; absence of any limitation clause; exclusions for fraud, willful misconduct, or gross negligence.
2.  **Cap on Liability** (37.3% of contracts)
    *   **Common Patterns:** Fixed monetary maximums (e.g., $1M, fees paid); exclusion of consequential/indirect damages; liability limited to insurance coverage amounts; statute of limitations/time bars for claims.
3.  **Liquidated Damages** (11.8% of contracts)
    *   **Common Patterns:** Penalties for late delivery/performance failures (% per day/week); multipliers for breach of exclusivity/non-solicitation; fixed fees for late payments; termination fees/buyout prices for early termination.
4.  **Warranty Duration** (17.0% of contracts)
    *   **Common Patterns:** Survival clauses for reps/warranties post-closing/termination; bug fixing/defect correction periods; warranties lasting for "reasonable shelf life" or the "term of the agreement."

## Common Patterns

### Uncapped Liability
*   **Explicit Carve-outs:** The contract establishes a general liability cap but explicitly excludes specific obligations (e.g., indemnification, confidentiality, IP infringement) from that cap.
    *   *Example Phrasing:* "The limitations of liability in this Section shall not apply to any liability arising out of or relating to a breach of Confidentiality or Indemnification obligations."
*   **Total Absence of Limitation:** The contract contains no "Limitation of Liability" clause, implying default uncapped exposure under applicable law for all breaches.
    *   *Example Phrasing:* (No clause found) "The contract does not specify a monetary cap on liability, leaving the Provider's indemnification obligations... uncapped."
*   **Statutory/Conduct-Based Exclusions:** Liability is uncapped for specific severe conduct or statutory violations.
    *   *Example Phrasing:* "Liability shall not be limited for cases of gross negligence, willful misconduct, fraud, or bodily injury/death."

### Cap on Liability
*   **Monetary Caps Tied to Fees:** Liability is capped at a specific monetary amount or a multiple of fees paid during a specific period.
    *   *Example Phrasing:* "The Company's aggregate liability is capped to the total amount actually paid by the Distributor for the specific products that caused the damage."
*   **Exclusion of Consequential Damages:** The primary mechanism for capping exposure is the exclusion of indirect, special, incidental, or punitive damages.
    *   *Example Phrasing:* "Neither party shall be liable for any special, indirect, consequential, or punitive damages, including lost profits."
*   **Time-Based Caps (Statute of Limitations):** Liability is effectively capped by restricting the time window in which claims can be brought.
    *   *Example Phrasing:* "Any claim must be brought within one (1) year of the occurrence of the event giving rise to such claim."

### Liquidated Damages
*   **Performance/Delivery Penalties:** Specific financial penalties calculated as a percentage of value or fixed fee for failing to meet delivery or performance metrics.
    *   *Example Phrasing:* "A penalty of 0.5% for every seven days of late delivery, capped at 5% of the goods' value."
*   **Termination Fees/Buyouts:** Fixed fees or accelerated payments required upon early termination or breach of exclusivity.
    *   *Example Phrasing:* "Upon termination for cause, Party B must pay a termination fee equal to two times the commissions on business produced during the last 12 months."
*   **Late Payment Interest/Fees:** Fixed fees or daily percentages for overdue payments.
    *   *Example Phrasing:* "A daily penalty of 0.05% of the overdue payment if Party B fails to pay within 60 days."

### Warranty Duration
*   **Fixed Periods:** Warranties defined by a specific number of days, months, or years from delivery or commencement.
    *   *Example Phrasing:* "The Warranty Period lasts for twenty-one (21) years from the date of Commencement of Operations."
*   **Shelf Life/Quality Standards:** Warranties tied to the physical lifespan or quality of the product at the time of shipment.
    *   *Example Phrasing:* "Products will have a remaining shelf life of at least twelve months at the time of shipment."
*   **Survival Clauses:** Representations and warranties that survive the termination or closing of the agreement for a specified period or indefinitely.
    *   *Example Phrasing:* "Representations and warranties survive the delivery of shares and payment, remaining in full force and effect regardless of any termination."

## Review Checklist

*   **Uncapped Liability:**
    *   [ ] Does the contract contain a "Limitation of Liability" clause? If not, flag as potentially uncapped.
    *   [ ] Are indemnification, confidentiality, IP infringement, or gross negligence/willful misconduct explicitly excluded from any liability caps?
    *   [ ] Are there statutory mandates (e.g., personal injury) that prevent capping?
*   **Cap on Liability:**
    *   [ ] Is there a defined monetary cap (fixed amount or formula based on fees paid)?
    *   [ ] Are consequential, indirect, special, or punitive damages excluded?
    *   [ ] Is there a statute of limitations or time bar for bringing claims?
    *   [ ] Is the cap symmetric (applies to both parties) or asymmetric (applies only to one)?
*   **Liquidated Damages:**
    *   [ ] Are there specific penalties for late delivery, performance failures, or late payments?
    *   [ ] Are there termination fees, buyout prices, or accelerated payment clauses upon early termination?
    *   [ ] Are there multipliers for breach of exclusivity or non-solicitation?
*   **Warranty Duration:**
    *   [ ] Is there a defined warranty period for products/services (e.g., 12 months, 21 years)?
    *   [ ] Do representations and warranties survive termination/closing? If so, for how long?
    *   [ ] Are warranties disclaimed entirely ("AS IS")?

## Evidence Extraction Rules

1.  **Locate Clauses:** Search for sections titled "Limitation of Liability," "Indemnification," "Liquidated Damages," "Warranties," "Survival," or "Termination."
2.  **Extract Monetary Values:** For "Cap on Liability," extract specific dollar amounts, percentages, or formulas (e.g., "fees paid in the preceding 12 months").
3.  **Identify Exceptions:** For "Uncapped Liability," extract text that explicitly excludes certain obligations (indemnity, confidentiality, fraud) from the general cap.
4.  **Capture Timeframes:** For "Warranty Duration" and "Cap on Liability" (time bars), extract specific durations (e.g., "120 days," "1 year," "reasonable shelf life").
5.  **Note Penalties:** For "Liquidated Damages," extract the calculation method (e.g., "0.5% per week," "2x commissions") and the triggering event (e.g., "late delivery," "termination for cause").
6.  **Handle Absence:** If no "Limitation of Liability" clause is found, note the absence as evidence for "Uncapped Liability." If no warranty period is defined, note if warranties are disclaimed or implied.

## Output Format

```json
{
  "status": "success|error",
  "answer": {
    "uncapped_liability": {
      "is_uncapped": true|false,
      "reason": "string describing why (e.g., 'Explicit exclusion of indemnification from cap', 'No limitation clause found')",
      "excluded_categories": ["indemnification", "confidentiality", "gross negligence"]
    },
    "cap_on_liability": {
      "has_cap": true|false,
      "cap_type": "monetary|time_based|exclusion_only",
      "cap_value": "string (e.g., '$1,000,000', 'Fees paid in last 12 months', '1 year')",
      "excluded_damages": ["consequential", "indirect", "punitive"]
    },
    "liquidated_damages": {
      "has_ld": true|false,
      "triggers": ["late_delivery", "termination_for_cause", "late_payment"],
      "calculation": "string (e.g., '0.5% per week', '2x commissions')",
      "cap_on_ld": "string or null"
    },
    "warranty_duration": {
      "has_warranty": true|false,
      "duration": "string (e.g., '12 months', '21 years', 'reasonable shelf life')",
      "survival_period": "string or null",
      "disclaimer": true|false
    }
  },
  "evidence_unit_ids": ["string", "string"],
  "source_contract_ids": ["string"],
  "missing_inputs": ["string"],
  "human_review_required": true|false
}
```

## Boundary Rules

*   **Do Not Infer Caps from Silence:** If a contract lacks a "Limitation of Liability" clause, do not assume a cap exists. Flag as "Uncapped Liability" due to absence.
*   **Distinguish Between Cap and Exclusion:** A clause that only excludes consequential damages but has no monetary cap is still a "Cap on Liability" (via exclusion), but the `cap_value` should reflect the exclusion nature, not a monetary figure.
*   **Ignore Standard Interest:** Do not classify standard late payment interest (e.g., "prime rate + 2%") as "Liquidated Damages" unless it is a fixed penalty fee or significantly punitive. Focus on explicit "Liquidated Damages" or "Penalty" clauses.
*   **Separate Warranty from SLA:** Do not confuse Service Level Agreement (SLA) credits with "Warranty Duration." Warranties relate to defects/errors in technology/products; SLAs relate to performance metrics.
*   **Handle Redactions:** If a limitation clause is redacted, assume the redacted portion may contain exceptions (uncapped liability) and flag for human review.
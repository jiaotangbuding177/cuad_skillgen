# SKILL.md: Liability and Indemnity Review

## Overview
This skill performs a comprehensive review of contractual liability provisions, focusing on risk allocation between parties. It analyzes four key areas: **Cap on Liability** (limits on recovery), **Uncapped Liability** (exceptions to caps such as IP or confidentiality breaches), **Liquidated Damages** (predetermined penalties/fees), and **Warranty Duration** (timeframes for defect claims). 

The skill utilizes specialized extraction tools to identify specific clauses, extract relevant text, and determine the presence or absence of these critical legal protections.

## Available Tools

### 1. check_cap_on_liability
*   **Category:** Cap on Liability
*   **Description:** Identifies if the contract includes a general cap on liability, such as limiting recourse to specific assets or excluding personal liability for trustees/advisors.
*   **Parameters:** `contract_text` (string)
*   **Returns:** `{ found: boolean, extracted_text: string, confidence: float }`
*   **Usage Notes:** Use this as a primary scan for broad liability limitations that do not necessarily tie to a specific breach amount but limit the scope of liable entities or assets.

### 2. check_liability_cap
*   **Category:** Cap on Liability
*   **Description:** Checks if the contract includes a specific cap on liability triggered upon the breach of a party's obligation.
*   **Parameters:** `contract_text` (string)
*   **Returns:** `{ found: boolean, extracted_text: string, confidence: float }`
*   **Usage Notes:** Focuses on breach-specific caps. Often used in conjunction with `check_liability_caps` to ensure all monetary limits are captured.

### 3. check_liability_caps
*   **Category:** Cap on Liability
*   **Description:** Identifies caps on liability for breach of obligation, specifically looking for time limitations or maximum recovery amounts (monetary ceilings).
*   **Parameters:** `contract_text` (string)
*   **Returns:** `{ found: boolean, extracted_text: string, confidence: float }`
*   **Usage Notes:** Best for extracting specific dollar amounts or percentage-based caps tied to contract value.

### 4. check_time_limitation_for_claims
*   **Category:** Cap on Liability
*   **Description:** Determines if there is a specific time limit (statute of limitations) within which a party must bring a claim or action arising from the agreement.
*   **Parameters:** `contract_text` (string)
*   **Returns:** `{ found: boolean, extracted_text: string, confidence: float }`
*   **Usage Notes:** Critical for determining the "tail" of liability. Look for phrases like "must bring suit within X years."

### 5. check_cap_on_liability_waiver_punitive
*   **Category:** Cap on Liability
*   **Description:** Checks for waivers of punitive damages, which effectively cap recovery amounts by excluding certain types of damages.
*   **Parameters:** `contract_text` (string)
*   **Returns:** `{ found: boolean, extracted_text: string, confidence: float }`
*   **Usage Notes:** Essential for risk assessment in jurisdictions where punitive damages are common.

### 6. check_cap_on_liability_time_limitation
*   **Category:** Cap on Liability
*   **Description:** Identifies clauses that impose a time limitation on the ability to bring claims or actions under the contract.
*   **Parameters:** `contract_text` (string)
*   **Returns:** `{ found: boolean, extracted_text: string, confidence: float }`
*   **Usage Notes:** Similar to `check_time_limitation_for_claims`; use both to ensure robust coverage of temporal restrictions on liability.

### 7. check_uncapped_liability
*   **Category:** Uncapped Liability
*   **Description:** Checks for clauses where liability is explicitly uncapped or unlimited for specific breaches (e.g., IP infringement, confidentiality, indemnity, gross negligence, willful misconduct, fraud). Identifies exceptions to general liability caps.
*   **Parameters:** `contract_text` (string)
*   **Returns:** `{ found: boolean, extracted_text: string, confidence: float }`
*   **Usage Notes:** This is a high-risk indicator. Even if a cap exists, this tool identifies if major risks (like IP theft) bypass that cap.

### 8. check_tax_responsibility
*   **Category:** Tax Responsibility
*   **Description:** Checks if the contract specifies which party is responsible for taxes related to the agreement.
*   **Parameters:** `contract_text` (string)
*   **Returns:** `{ found: boolean, extracted_text: string, confidence: float }`
*   **Usage Notes:** While primarily tax-focused, tax liabilities can sometimes be uncapped financial obligations. Include in review if tax indemnities are part of the broader liability framework.

### 9. check_warranty_duration
*   **Category:** Warranty Duration
*   **Description:** Extracts the specific duration, time period, or survival clause for warranties against defects, errors, or non-conformance in technology, products, or services.
*   **Parameters:** `contract_text` (string)
*   **Returns:** `{ found: boolean, extracted_text: string, confidence: float }`
*   **Usage Notes:** Look for "warranty period," "survival of representations," or specific month/year durations from delivery/acceptance.

### 10. check_liquidated_damages
*   **Category:** Liquidated Damages
*   **Description:** Identifies clauses specifying predetermined damages, termination fees, or fixed monetary penalties payable upon breach or termination, distinguishing them from general indemnification.
*   **Parameters:** `contract_text` (string)
*   **Returns:** `{ found: boolean, extracted_text: string, confidence: float }`
*   **Usage Notes:** Key for identifying fixed financial exposures. Distinguish between true liquidated damages and unenforceable penalties.

## Review Workflow

1.  **Input Ingestion**: Receive the full contract text.
2.  **Liability Cap Analysis**:
    *   Run `check_cap_on_liability`, `check_liability_cap`, and `check_liability_caps` to establish the baseline financial limit.
    *   Run `check_cap_on_liability_waiver_punitive` to check for exclusions of punitive damages.
    *   Run `check_time_limitation_for_claims` and `check_cap_on_liability_time_limitation` to determine temporal limits on bringing claims.
3.  **Uncapped Liability Check**:
    *   Run `check_uncapped_liability` to identify any carve-outs where the caps identified in Step 2 do not apply (e.g., IP, Confidentiality, Fraud).
4.  **Warranty & Damages Analysis**:
    *   Run `check_warranty_duration` to determine how long defect claims can be made.
    *   Run `check_liquidated_damages` to identify any fixed penalty clauses or termination fees.
5.  **Tax Responsibility Check**:
    *   Run `check_tax_responsibility` to identify any uncapped tax indemnities.
6.  **Synthesis**: Aggregate findings. If a cap exists but significant risks (IP, Confidentiality) are uncapped, flag as high risk. If liquidated damages are present, note the amount. If warranty duration is short, note the limited window for claims.

## Output Format

```json
{
  "status": "success",
  "answer": {
    "liability_cap_exists": true,
    "liability_cap_details": "Liability limited to fees paid in the 12 months preceding the claim.",
    "uncapped_liability_exists": true,
    "uncapped_liability_details": "Liability for IP infringement and breach of confidentiality is uncapped.",
    "time_limitation_exists": true,
    "time_limitation_details": "Claims must be brought within 2 years of the event giving rise to the claim.",
    "punitive_damages_waived": true,
    "warranty_duration": "12 months from acceptance.",
    "liquidated_damages_exists": false,
    "liquidated_damages_details": null,
    "tax_responsibility_defined": true,
    "tax_responsibility_details": "Each party bears its own taxes."
  },
  "evidence_unit_ids": [
    "unit_123",
    "unit_124",
    "unit_125"
  ],
  "source_contract_ids": [
    "contract_abc"
  ],
  "missing_inputs": [],
  "human_review_required": false
}
```

## Boundary Rules

*   **DO** extract exact text snippets supporting the findings.
*   **DO** distinguish between general liability caps and specific uncapped exceptions.
*   **DO** identify both monetary caps and time-based limitations (statutes of limitation).
*   **DO NOT** provide legal advice on the enforceability of liquidated damages vs. penalties; only identify their presence and stated amount.
*   **DO NOT** infer liability caps if they are not explicitly stated in the text.
*   **DO NOT** merge distinct concepts (e.g., do not conflate warranty duration with the statute of limitations for bringing claims unless the contract explicitly links them).
*   **SHOULD** flag cases where `check_uncapped_liability` returns true for high-risk categories (IP, Confidentiality, Gross Negligence) as these significantly alter the risk profile despite the existence of a general cap.
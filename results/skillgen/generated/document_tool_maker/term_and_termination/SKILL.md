# SKILL.md: Contract Term and Termination Review

## Overview
This skill specializes in analyzing the temporal lifecycle of commercial contracts. It focuses on three critical areas: **Renewal Terms** (how a contract extends beyond its initial period), **Notice Periods for Non-Renewal** (deadlines to prevent automatic extension), and **Termination for Convenience** (rights to exit the agreement without cause). 

The skill utilizes specialized extraction tools to identify specific clauses, extract duration values, notice windows, and conditional logic regarding contract continuation or early exit.

## Available Tools

### 1. check_renewal_term
*   **Category:** Renewal Term
*   **Description:** Identifies if the contract contains provisions for automatic renewal, unilateral extension, or a defined renewal term after the initial period expires. It extracts the duration of these renewal periods (e.g., "successive one-year periods") and any associated conditions.
*   **Parameters:** 
    *   `contract_text`: The full text or relevant section of the agreement.
*   **Returns:** 
    *   `found` (boolean): Whether a renewal clause exists.
    *   `extracted_text` (string): The specific clause defining the renewal mechanism.
    *   `confidence` (float): Confidence score of the extraction.
*   **Usage Notes:** Use this first to determine if the contract has an auto-renewal mechanism. Look for keywords like "automatically renew," "successive terms," or "extend."
*   **Example:**
    *   *Input:* "Upon expiration of the Initial Term, this Agreement shall automatically renew for successive one (1) year periods..."
    *   *Output:* `{ "found": true, "extracted_text": "automatically renew for successive one (1) year periods...", "confidence": 0.98 }`

### 2. check_notice_period_to_terminate_renewal
*   **Category:** Notice Period to Terminate Renewal
*   **Description:** Extracts the specific notice period required to prevent automatic renewal or to terminate a renewal term. This is distinct from general termination; it specifically targets the window to stop the contract from rolling over.
*   **Parameters:** 
    *   `contract_text`: The full text or relevant section of the agreement.
*   **Returns:** 
    *   `found` (boolean): Whether a non-renewal notice period is specified.
    *   `extracted_text` (string): The specific duration and timing requirement (e.g., "60 days prior").
    *   `confidence` (float): Confidence score of the extraction.
*   **Usage Notes:** Often found in the same paragraph as the renewal term. Look for phrases like "notice of non-renewal," "prior to the end of the then-current term."
*   **Example:**
    *   *Input:* "...unless either party provides written notice of non-renewal at least sixty (60) days prior to the expiration..."
    *   *Output:* `{ "found": true, "extracted_text": "sixty (60) days", "confidence": 0.98 }`

### 3. check_termination_for_convenience
*   **Category:** Termination for Convenience
*   **Description:** Determines if either party has the right to terminate the agreement without cause (for convenience). It identifies the existence of this right and extracts the required notice period and any waiting periods.
*   **Parameters:** 
    *   `contract_text`: The full text or relevant section of the agreement.
*   **Returns:** 
    *   `found` (boolean): Whether a termination for convenience clause exists.
    *   `extracted_text` (string): The clause granting the right and specifying notice requirements.
    *   `confidence` (float): Confidence score of the extraction.
*   **Usage Notes:** Look for keywords like "terminate without cause," "for convenience," "sole discretion," or "no penalty." Distinguish this from termination for breach/cause.
*   **Example:**
    *   *Input:* "Either party may terminate this Agreement without cause by providing thirty (30) days written notice..."
    *   *Output:* `{ "found": true, "extracted_text": "Either party may terminate this Agreement without cause by providing thirty (30) days written notice...", "confidence": 0.98 }`

### 4. check_notice_period_to_terminate
*   **Category:** Notice Period to Terminate
*   **Description:** A broader tool that identifies the general notice period required to terminate the contract, which may apply to both convenience and cause scenarios if not explicitly separated.
*   **Parameters:** 
    *   `contract_text`: The full text or relevant section of the agreement.
*   **Returns:** 
    *   `found` (boolean): Whether a general termination notice period is specified.
    *   `extracted_text` (string): The specific notice duration.
    *   `confidence` (float): Confidence score of the extraction.
*   **Usage Notes:** Use this as a fallback if `check_termination_for_convenience` does not yield a clear notice period, or to capture general termination mechanics.

## Review Workflow

1.  **Analyze Renewal Mechanics:**
    *   Invoke `check_renewal_term`.
    *   If `found` is true, note the renewal duration (e.g., 1 year, 3 years).
    *   If `found` is false, mark renewal as "None" or "Fixed Term Only."

2.  **Determine Non-Renewal Requirements:**
    *   If a renewal term was found, invoke `check_notice_period_to_terminate_renewal`.
    *   Extract the specific number of days/months required to opt-out.
    *   If no specific non-renewal notice is found but renewal exists, flag as "Missing Non-Renewal Notice" (potential risk).

3.  **Assess Early Exit Rights:**
    *   Invoke `check_termination_for_convenience`.
    *   If `found` is true, extract the notice period (e.g., 30 days, 90 days).
    *   Identify if the right is mutual ("Either party") or unilateral ("Licensor may...").

4.  **Fallback General Termination Check:**
    *   If `check_termination_for_convenience` returns negative or ambiguous results, invoke `check_notice_period_to_terminate` to ensure no general termination notice obligations are missed.

5.  **Synthesize Findings:**
    *   Combine findings into the final JSON output.
    *   Flag any missing critical inputs (e.g., renewal exists but no notice period defined).

## Output Format

```json
{
  "status": "success", 
  "answer": {
    "renewal_term": {
      "exists": true,
      "duration": "successive one (1) year periods",
      "clause_text": "Upon expiration of the Initial Term, this Agreement shall automatically renew for successive one (1) year periods..."
    },
    "non_renewal_notice": {
      "required": true,
      "period": "ninety (90) days",
      "clause_text": "unless either party provides written notice of non-renewal at least ninety (90) days prior to the end of the then-current term."
    },
    "termination_for_convenience": {
      "allowed": true,
      "notice_period": "thirty (30) days",
      "party_rights": "mutual",
      "clause_text": "Either party may terminate this Agreement without cause by providing thirty (30) days written notice to the other party."
    }
  },
  "evidence_unit_ids": [
    "unit_12345_renewal_clause",
    "unit_12346_notice_clause",
    "unit_12347_termination_clause"
  ],
  "source_contract_ids": [
    "PhoenixNewMediaLtd_20110421_F-1_EX-10.17_6958322_EX-10.17_Content_License_Agreement"
  ],
  "missing_inputs": [],
  "human_review_required": false
}
```

## Boundary Rules

*   **DO** distinguish clearly between "Termination for Cause" (breach) and "Termination for Convenience" (no cause). This skill only targets the latter.
*   **DO** differentiate between "Notice to Terminate the Current Term" and "Notice to Prevent Renewal." They often have different timelines and legal implications.
*   **DO NOT** infer notice periods if they are not explicitly stated in the text. If a renewal clause exists but lacks a non-renewal notice provision, report it as missing rather than guessing.
*   **DO NOT** analyze financial penalties or wind-down procedures associated with termination unless explicitly requested by a separate tool; focus strictly on the *right* to terminate and the *notice period*.
*   **DO** handle ambiguous language (e.g., "reasonable notice") by extracting the text exactly and flagging `human_review_required` as true if specific numeric values are absent.
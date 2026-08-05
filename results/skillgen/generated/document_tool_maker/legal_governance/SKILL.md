# Contract Governance & Risk Review Skill

## Overview
This skill performs a targeted legal review of commercial contracts, focusing on three critical governance and risk management categories: **Governing Law**, **Audit Rights**, and **Insurance Requirements**. It utilizes specialized extraction tools to identify jurisdictional clauses, compliance verification mechanisms, and risk transfer obligations. The skill is designed to assist legal teams in quickly assessing standard contractual protections and identifying missing or non-standard provisions.

## Available Tools

### 1. check_governing_law
*   **Category:** Governing Law
*   **Description:** Identifies the specific jurisdiction (state, country, or region) whose laws govern the interpretation, validity, and enforcement of the contract. It also detects any specified conflict of law principles or dispute resolution venues linked to that jurisdiction.
*   **Parameters:**
    *   `contract_text` (string): The full text or relevant sections of the agreement.
*   **Returns:**
    *   `found` (boolean): Whether a governing law clause was identified.
    *   `extracted_text` (string): The exact clause defining the governing law.
    *   `jurisdiction` (string): The specific state or country identified (e.g., "State of Delaware", "England and Wales").
    *   `confidence` (float): Confidence score of the extraction (0.0 - 1.0).
*   **Usage Notes:**
    *   Look for phrases like "governed by," "construed in accordance with," or "subject to the laws of."
    *   *Example:* Input: `"This Agreement shall be governed by and construed in accordance with the laws of the State of Delaware..."` → Output: `{ "found": true, "jurisdiction": "State of Delaware", ... }`

### 2. check_audit_rights
*   **Category:** Audit Rights
*   **Description:** Determines if the contract grants one or both parties the right to audit, inspect, or verify the counterparty’s books, records, financial data, physical facilities, or systems. This is crucial for ensuring compliance with pricing, quality standards, royalty payments, or regulatory obligations.
*   **Parameters:**
    *   `contract_text` (string): The full text or relevant sections of the agreement.
*   **Returns:**
    *   `found` (boolean): Whether an audit right clause was identified.
    *   `extracted_text` (string): The specific clause granting audit rights.
    *   `scope` (string): Summary of what can be audited (e.g., "books and records," "physical facilities").
    *   `conditions` (string): Any conditions attached (e.g., "reasonable notice," "normal business hours").
    *   `confidence` (float): Confidence score of the extraction (0.0 - 1.0).
*   **Usage Notes:**
    *   Common in licensing, distribution, and service agreements.
    *   *Example:* Input: `"Company shall have the right... to audit Supplier's books and records... to verify compliance..."` → Output: `{ "found": true, "scope": "books and records", ... }`

### 3. check_insurance_requirements
*   **Category:** Insurance
*   **Description:** Identifies and extracts specific insurance coverage requirements that one or both parties must maintain. This includes types of insurance (e.g., general liability, workers' compensation), minimum coverage limits, and additional insured status requirements.
*   **Parameters:**
    *   `contract_text` (string): The full text or relevant sections of the agreement.
*   **Returns:**
    *   `found` (boolean): Whether insurance requirements were identified.
    *   `extracted_text` (string): The specific clause detailing insurance obligations.
    *   `coverage_types` (list[string]): Types of insurance required (e.g., ["General Liability", "Professional Indemnity"]).
    *   `limits` (string): Monetary limits specified (e.g., "$1,000,000 per occurrence").
    *   `confidence` (float): Confidence score of the extraction (0.0 - 1.0).
*   **Usage Notes:**
    *   Look for terms like "maintain insurance," "coverage limits," "additional insured," or "certificate of insurance."
    *   *Example:* Input: `"Contractor shall maintain... comprehensive general liability insurance with minimum limits of $1,000,000..."` → Output: `{ "found": true, "limits": "$1,000,000", ... }`

## Review Workflow

1.  **Input Ingestion**: Receive the contract text and identify the document type (e.g., Service Agreement, License, Supply Agreement).
2.  **Parallel Execution**: Trigger all three tools (`check_governing_law`, `check_audit_rights`, `check_insurance_requirements`) simultaneously against the provided contract text. These checks are independent and do not rely on each other's output.
3.  **Result Aggregation**:
    *   Collect outputs from all three tools.
    *   Validate that `found` is `true` for critical clauses. If `found` is `false`, flag the category as "Missing" or "Not Specified."
4.  **Risk Assessment**:
    *   **Governing Law**: Check if the jurisdiction is neutral or favorable to the reviewing party. Flag if missing.
    *   **Audit Rights**: Determine if the scope is sufficient for the contract type (e.g., financial audits for royalty deals). Flag if missing in high-risk compliance contexts.
    *   **Insurance**: Verify if limits meet standard industry benchmarks. Flag if missing or if limits are unusually low.
5.  **Output Generation**: Compile the findings into the standardized JSON output format, including evidence snippets and confidence scores.

## Output Format

The skill returns a JSON object conforming to the following schema:

```json
{
  "status": "success" | "partial" | "error",
  "answer": {
    "governing_law": {
      "found": boolean,
      "jurisdiction": string | null,
      "extracted_text": string | null,
      "confidence": float
    },
    "audit_rights": {
      "found": boolean,
      "scope": string | null,
      "extracted_text": string | null,
      "confidence": float
    },
    "insurance_requirements": {
      "found": boolean,
      "coverage_types": list[string] | null,
      "limits": string | null,
      "extracted_text": string | null,
      "confidence": float
    }
  },
  "evidence_unit_ids": [
    "string" 
  ],
  "source_contract_ids": [
    "string"
  ],
  "missing_inputs": [
    "string"
  ],
  "human_review_required": boolean
}
```

*   **status**: `success` if all tools ran; `partial` if some failed; `error` if the system failed.
*   **answer**: Contains the structured results for each of the three categories.
*   **evidence_unit_ids**: IDs of the specific text segments used as evidence.
*   **source_contract_ids**: IDs of the source documents processed.
*   **missing_inputs**: List of any required parameters that were not provided.
*   **human_review_required**: `true` if any critical clause is missing, confidence is low (<0.7), or conflicting information is detected.

## Boundary Rules

*   **DO** extract exact text snippets for evidence to allow for human verification.
*   **DO** report `found: false` clearly if a clause is absent, rather than hallucinating a default value.
*   **DO NOT** provide legal advice or interpret the *implications* of the law (e.g., do not say "Delaware law is favorable for corporations"). Only state what the text says.
*   **DO NOT** attempt to negotiate terms or suggest redlines.
*   **DO NOT** process contracts that are heavily redacted to the point where context is lost; flag these as requiring human review.
*   **DO** handle cases where multiple jurisdictions are mentioned (e.g., different laws for different sections) by extracting the primary governing law clause or noting the complexity for human review.
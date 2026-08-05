# SKILL.md

## Overview
This skill is designed to analyze commercial contracts for specific financial and operational terms related to **Revenue/Profit Sharing**. It utilizes specialized tools to identify clauses where parties agree to share revenue, profits, or losses, as well as specific fee structures for servicing roles.

While the broader case definition includes Price Restrictions, Minimum Commitments, and Volume Restrictions, the current toolset is exclusively focused on **Revenue/Profit Sharing**. This skill will accurately extract and validate revenue-sharing mechanisms, royalty structures, and servicing fee arrangements.

## Available Tools

### 1. check_revenue_profit_sharing
*   **Category**: Revenue/Profit Sharing
*   **Description**: Identifies clauses where parties agree to share revenue, profits, or losses based on investment, sales, usage, or specific activities. This includes royalties, commissions, and cost-sharing arrangements.
*   **Parameters**:
    *   `contract_text` (string): The full text of the contract or specific section to analyze.
*   **Returns**:
    *   `found` (boolean): Whether a revenue/profit sharing clause was identified.
    *   `extracted_text` (string): The specific clause text defining the sharing mechanism.
    *   `confidence` (float): Confidence score of the extraction (0.0 - 1.0).
*   **Usage Notes**: Use this tool for general revenue sharing, royalties, and profit splits. It is the primary tool for detecting standard commercial revenue exchanges.
*   **Example**:
    *   *Input*: "Section 4.2 Revenue Sharing. Company shall pay Licensee a royalty equal to fifteen percent (15%) of Net Sales generated from the Licensed Products during the Term."
    *   *Output*: `{"found": true, "extracted_text": "Company shall pay Licensee a royalty equal to fifteen percent (15%) of Net Sales generated from the Licensed Products during the Term.", "confidence": 0.98}`

### 2. check_servicing_fee_structure
*   **Category**: Revenue/Profit Sharing
*   **Description**: Identifies clauses that define the compensation structure for a Servicer, including base fees and supplemental fees derived from collections or specific receivable types.
*   **Parameters**:
    *   `contract_text` (string): The full text of the contract or specific section to analyze.
*   **Returns**:
    *   `found` (boolean): Whether a servicing fee structure was identified.
    *   `extracted_text` (string): The specific clause text defining the fee structure.
    *   `confidence` (float): Confidence score of the extraction (0.0 - 1.0).
*   **Usage Notes**: Use this tool specifically for Service Agreements or Asset-Backed Securities contexts where a "Servicer" role is defined. It looks for base percentages on outstanding balances and supplemental fees on collections.
*   **Example**:
    *   *Input*: "Section 3.1 Servicing Fees. The Servicer shall receive a base servicing fee of 0.25% per annum on the outstanding principal balance of the Receivables, plus a supplemental fee of 1.5% on all amounts collected."
    *   *Output*: `{"found": true, "extracted_text": "The Servicer shall receive a base servicing fee of 0.25% per annum on the outstanding principal balance of the Receivables, plus a supplemental fee of 1.5% on all amounts collected.", "confidence": 0.95}`

### 3. check_written_off_receivable_proceeds
*   **Category**: Revenue/Profit Sharing
*   **Description**: Checks if the Servicer is entitled to retain proceeds from the sale of written-off receivables as supplemental fees, rather than passing them to the Issuer.
*   **Parameters**:
    *   `contract_text` (string): The full text of the contract or specific section to analyze.
*   **Returns**:
    *   `found` (boolean): Whether a clause regarding written-off receivable proceeds was identified.
    *   `extracted_text` (string): The specific clause text defining the retention of proceeds.
    *   `confidence` (float): Confidence score of the extraction (0.0 - 1.0).
*   **Usage Notes**: Use this tool in conjunction with `check_servicing_fee_structure` for complex financial agreements. It specifically targets the disposition of assets that have been written off but later recovered or sold.
*   **Example**:
    *   *Input*: "Section 5.4 Disposition of Written-Off Receivables. Any proceeds received by the Servicer from the sale or recovery of Written-Off Receivables shall be retained by the Servicer as additional compensation."
    *   *Output*: `{"found": true, "extracted_text": "Any proceeds received by the Servicer from the sale or recovery of Written-Off Receivables shall be retained by the Servicer as additional compensation.", "confidence": 0.92}`

## Review Workflow

1.  **Analyze Contract Type**:
    *   Determine if the contract is a general commercial agreement (License, Distribution, Joint Venture) or a specialized financial service agreement (Servicing Agreement, ABS).

2.  **Select Tool(s)**:
    *   **For General Agreements**: Use `check_revenue_profit_sharing` to identify royalties, commissions, and profit splits.
    *   **For Servicing/Financial Agreements**:
        *   First, use `check_servicing_fee_structure` to identify base and supplemental fees.
        *   Second, use `check_written_off_receivable_proceeds` to check for specific retention rights on written-off assets.

3.  **Execute Extraction**:
    *   Pass the relevant contract text to the selected tool(s).
    *   If multiple tools are used, aggregate the results.

4.  **Validate Results**:
    *   Check the `confidence` score. If confidence is low (< 0.8), flag for human review.
    *   Ensure the `extracted_text` accurately reflects the financial obligation.

5.  **Handle Missing Categories**:
    *   Note that tools for **Price Restrictions**, **Minimum Commitment**, and **Volume Restriction** are not currently available. If the user asks about these, explicitly state that these categories are not covered by the current toolset.

## Output Format

The final output must be a JSON object conforming to the following schema:

```json
{
  "status": "success" | "error",
  "answer": {
    "revenue_sharing_clauses": [
      {
        "tool_id": "string",
        "extracted_text": "string",
        "confidence": "float"
      }
    ],
    "summary": "string"
  },
  "evidence_unit_ids": ["string"],
  "source_contract_ids": ["string"],
  "missing_inputs": ["string"],
  "human_review_required": "boolean"
}
```

*   **status**: "success" if tools executed without error, "error" otherwise.
*   **answer**: Contains the extracted clauses and a brief summary of the revenue/profit sharing terms found.
*   **evidence_unit_ids**: List of IDs for the specific clauses extracted.
*   **source_contract_ids**: List of contract IDs analyzed.
*   **missing_inputs**: List of any required inputs that were missing (e.g., "contract_text").
*   **human_review_required**: Set to `true` if any tool returned a confidence score below 0.8 or if conflicting clauses were detected.

## Boundary Rules

*   **DO**:
    *   Extract exact text for revenue sharing, royalties, and servicing fees.
    *   Distinguish between base fees and supplemental fees in servicing agreements.
    *   Identify specific percentages or formulas used for sharing.
*   **DO NOT**:
    *   Attempt to analyze Price Restrictions, Minimum Commitments, or Volume Restrictions as no tools are available for these categories.
    *   Infer revenue sharing terms if they are not explicitly stated in the text.
    *   Modify the extracted text; always return the verbatim clause.
    *   Provide legal advice on the enforceability of the clauses; only extract and report.
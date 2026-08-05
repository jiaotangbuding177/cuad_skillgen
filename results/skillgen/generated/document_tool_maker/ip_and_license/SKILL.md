# SKILL.md

## Overview
This skill is designed to analyze commercial contracts for specific Intellectual Property (IP) and Licensing provisions. It identifies the existence, scope, and limitations of license grants, including restrictions on transferability, affiliate usage, duration (perpetual/irrevocable), volume (unlimited), and risk mitigation mechanisms like source code escrow.

The skill utilizes a suite of specialized tools to extract precise clauses and determine compliance with standard licensing frameworks.

## Available Tools

### 1. check_license_grant
*   **Category:** License Grant
*   **Description:** Identifies if the contract contains a license granted by one party to its counterparty regarding intellectual property, trademarks, software, or other rights. It extracts the scope and limitations of such grants.
*   **Parameters:**
    *   `contract_text`: The full text of the contract.
*   **Returns:**
    *   `found`: Boolean indicating if a license grant was identified.
    *   `extracted_text`: The specific clause defining the license.
    *   `confidence`: Confidence score (0.0 - 1.0).
*   **Usage Notes:** Use this as the primary entry point. If no license grant is found, subsequent license-specific tools may return false negatives or irrelevant results.
*   **Example:**
    *   *Input:* "Section 3. License Grant. Licensor hereby grants to Licensee a non-exclusive, non-transferable, royalty-free license to use the Licensor's trademarks..."
    *   *Output:* `found: true`, `extracted_text: "Licensor hereby grants to Licensee a non-exclusive, non-transferable, royalty-free license..."`

### 2. check_non_transferable_license
*   **Category:** Non-Transferable License
*   **Description:** Determines if the contract restricts the licensee from transferring, sublicensing, or assigning the granted license to third parties.
*   **Parameters:**
    *   `contract_text`: The full text of the contract.
*   **Returns:**
    *   `found`: Boolean indicating if transfer restrictions exist.
    *   `extracted_text`: The clause restricting transfer/assignment.
    *   `confidence`: Confidence score (0.0 - 1.0).
*   **Usage Notes:** Look for keywords like "non-transferable," "may not be assigned," "no sublicense," or "without prior written consent."
*   **Example:**
    *   *Input:* "The License granted herein is non-transferable and may not be assigned, sublicensed, or transferred to any third party without the prior written consent of Licensor."
    *   *Output:* `found: true`, `extracted_text: "The License granted herein is non-transferable and may not be assigned..."`

### 3. check_affiliate_license_licensee
*   **Category:** Affiliate License-Licensee
*   **Description:** Determines if the license grant extends to the licensee and its affiliates, or if the licensee is permitted to sublicense to its affiliates.
*   **Parameters:**
    *   `contract_text`: The full text of the contract.
*   **Returns:**
    *   `found`: Boolean indicating if affiliate rights are granted to the licensee.
    *   `extracted_text`: The clause permitting affiliate use or sublicensing.
    *   `confidence`: Confidence score (0.0 - 1.0).
*   **Usage Notes:** Distinguish between general "affiliates" and specific "subsidiaries." Look for phrases like "Licensee and its Affiliates" or "right to grant sublicenses to its Affiliates."
*   **Example:**
    *   *Input:* "Licensee shall have the right to grant sublicenses to its Affiliates for the purpose of internal use only."
    *   *Output:* `found: true`, `extracted_text: "Licensee shall have the right to grant sublicenses to its Affiliates..."`

### 4. check_irrevocable_or_perpetual_license
*   **Category:** Irrevocable or Perpetual License
*   **Description:** Identifies if the license grant is stated as irrevocable or perpetual, or if it lacks a defined termination mechanism.
*   **Parameters:**
    *   `contract_text`: The full text of the contract.
*   **Returns:**
    *   `found`: Boolean indicating if the license is perpetual/irrevocable.
    *   `extracted_text`: The clause stating the duration or irrevocability.
    *   `confidence`: Confidence score (0.0 - 1.0).
*   **Usage Notes:** Look for keywords like "irrevocable," "perpetual," "indefinite," or "shall survive termination."
*   **Example:**
    *   *Input:* "Licensor hereby grants to Licensee a worldwide, non-exclusive, irrevocable, perpetual, royalty-free license..."
    *   *Output:* `found: true`, `extracted_text: "irrevocable, perpetual"`

### 5. check_affiliate_license_licensor
*   **Category:** Affiliate License-Licensor
*   **Description:** Checks if the license grant extends to affiliates of the licensor or includes IP owned by affiliates of the licensor.
*   **Parameters:**
    *   `contract_text`: The full text of the contract.
*   **Returns:**
    *   `found`: Boolean indicating if licensor affiliates are included.
    *   `extracted_text`: The clause extending rights to licensor affiliates.
    *   `confidence`: Confidence score (0.0 - 1.0).
*   **Usage Notes:** This is distinct from licensee affiliate rights. Look for "Licensor and its Affiliates" or "IP owned by Licensor's affiliates."
*   **Example:**
    *   *Input:* "The Licensor hereby grants to Licensee a non-exclusive license... and such license shall extend to affiliates of the Licensor."
    *   *Output:* `found: true`, `extracted_text: "such license shall extend to affiliates of the Licensor"`

### 6. check_unlimited_license
*   **Category:** Unlimited/All-You-Can-Eat-License
*   **Description:** Identifies if the contract grants an unlimited, enterprise-wide, or 'all-you-can-eat' usage license without specific quantity, scope, or volume caps.
*   **Parameters:**
    *   `contract_text`: The full text of the contract.
*   **Returns:**
    *   `found`: Boolean indicating if the license is unlimited.
    *   `extracted_text`: The clause defining the unlimited scope.
    *   `confidence`: Confidence score (0.0 - 1.0).
*   **Usage Notes:** Look for "unlimited," "enterprise-wide," "without restriction on the number of users," or "all-you-can-eat."
*   **Example:**
    *   *Input:* "Licensor hereby grants to Licensee a non-exclusive, worldwide, royalty-free, unlimited, enterprise-wide license... without restriction on the number of users..."
    *   *Output:* `found: true`, `extracted_text: "unlimited, enterprise-wide license... without restriction on the number of users..."`

### 7. check_source_code_escrow
*   **Category:** Source Code Escrow
*   **Description:** Determines if one party is required to deposit its source code into escrow with a third party, which can be released to the counterparty upon the occurrence of certain events (bankruptcy, insolvency, etc.).
*   **Parameters:**
    *   `contract_text`: The full text of the contract.
*   **Returns:**
    *   `found`: Boolean indicating if escrow provisions exist.
    *   `extracted_text`: The clause detailing the escrow arrangement.
    *   `confidence`: Confidence score (0.0 - 1.0).
*   **Usage Notes:** Look for "Escrow Agent," "source code deposit," "bankruptcy," "insolvency," or "release conditions."
*   **Example:**
    *   *Input:* "In the event of a material breach by Licensor or the filing of bankruptcy proceedings against Licensor, Licensee shall have the right to receive the source code from the Escrow Agent."
    *   *Output:* `found: true`, `extracted_text: "In the event of a material breach... Licensee shall have the right to receive the source code from the Escrow Agent."`

## Review Workflow

1.  **Initial Scan (License Grant):**
    *   Run `check_license_grant` first.
    *   If `found` is `false`, the contract likely does not contain a standard IP license. You may skip subsequent license-specific checks unless the user specifically requests a search for implied licenses or other IP transfers.
    *   If `found` is `true`, proceed to step 2.

2.  **Scope and Limitation Analysis:**
    *   Run `check_non_transferable_license` to identify assignment restrictions.
    *   Run `check_affiliate_license_licensee` to see if the licensee can share rights with their group.
    *   Run `check_affiliate_license_licensor` to see if the licensor's group IP is included.
    *   Run `check_unlimited_license` to check for volume caps.
    *   Run `check_irrevocable_or_perpetual_license` to determine duration risks.

3.  **Risk Mitigation Check:**
    *   Run `check_source_code_escrow` to identify if source code protection mechanisms are in place.

4.  **Synthesis:**
    *   Aggregate the results from all tools.
    *   If multiple tools return `found: true`, compile the extracted texts into the final evidence list.
    *   If a tool returns `found: false`, note that the specific provision was not explicitly found (though it may be implied by general terms, the tool focuses on explicit clauses).

## Output Format

The final output must be a JSON object conforming to the following schema:

```json
{
  "status": "success",
  "answer": {
    "license_grant": {
      "found": true,
      "extracted_text": "Licensor hereby grants to Licensee a non-exclusive...",
      "confidence": 0.98
    },
    "non_transferable": {
      "found": true,
      "extracted_text": "The License granted herein is non-transferable...",
      "confidence": 0.98
    },
    "affiliate_licensee": {
      "found": false,
      "extracted_text": null,
      "confidence": 0.0
    },
    "affiliate_licensor": {
      "found": false,
      "extracted_text": null,
      "confidence": 0.0
    },
    "unlimited_license": {
      "found": false,
      "extracted_text": null,
      "confidence": 0.0
    },
    "irrevocable_perpetual": {
      "found": false,
      "extracted_text": null,
      "confidence": 0.0
    },
    "source_code_escrow": {
      "found": false,
      "extracted_text": null,
      "confidence": 0.0
    }
  },
  "evidence_unit_ids": ["tool_001", "tool_002"],
  "source_contract_ids": ["CONTRACT_ID_123"],
  "missing_inputs": [],
  "human_review_required": false
}
```

*   **status**: "success" if the analysis completed, "error" if inputs were invalid.
*   **answer**: An object containing the results for each category. Each category object contains `found` (boolean), `extracted_text` (string or null), and `confidence` (float).
*   **evidence_unit_ids**: List of tool IDs that returned `found: true`.
*   **source_contract_ids**: List of contract IDs analyzed.
*   **missing_inputs**: List of any required inputs that were missing (e.g., if contract text was empty).
*   **human_review_required**: Boolean indicating if the confidence scores were low or if conflicting clauses were detected.

## Boundary Rules

*   **Do Not Infer:** Do not infer license grants or restrictions if they are not explicitly stated in the text. If the contract is silent on transferability, `check_non_transferable_license` should return `found: false` (or indicate "not specified" if the schema allows, but based on the tool spec, it returns `found: false` if the restriction clause is not found).
*   **Affiliate Distinction:** Strictly distinguish between `check_affiliate_license_licensee` (Licensee's affiliates) and `check_affiliate_license_licensor` (Licensor's affiliates). Do not mix these results.
*   **Perpetual vs. Term:** A license with a long term (e.g., 10 years) is not "perpetual." Only mark `check_irrevocable_or_perpetual_license` as `found: true` if the text explicitly uses "perpetual," "irrevocable," or "indefinite."
*   **Unlimited vs. Enterprise:** "Enterprise-wide" is often synonymous with "unlimited" in this context. If the text says "enterprise-wide" without user caps, treat it as unlimited.
*   **Escrow Specificity:** Only mark `check_source_code_escrow` as `found: true` if there is a mention of a third-party escrow agent or a specific mechanism for releasing source code upon trigger events. General "source code access" clauses without escrow mechanics should not trigger this tool.
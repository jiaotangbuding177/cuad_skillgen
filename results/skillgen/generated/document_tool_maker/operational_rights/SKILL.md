# SKILL.md

## Overview
This skill specializes in reviewing commercial contracts for specific operational and intellectual property rights. It focuses on identifying clauses related to **Joint IP Ownership**, **Covenants Not to Sue** (including waivers of IP validity challenges), **Third-Party Beneficiary** status, and **Rights of First Refusal/Offer/Negotiation (ROFR/ROFO/ROFN)**. The skill extracts relevant text, assesses confidence, and determines if specific rights or restrictions are present in the agreement.

## Available Tools

### 1. check_joint_ip_ownership
*   **Category:** Joint IP Ownership
*   **Description:** Identifies clauses where intellectual property is jointly owned or shared between the contracting parties. It looks for language indicating that IP developed during the term of the agreement is owned by both parties.
*   **Parameters:**
    *   `contract_text` (string): The full text of the contract or relevant section.
*   **Returns:**
    *   `found` (boolean): Whether a joint ownership clause was detected.
    *   `extracted_text` (string): The specific clause text.
    *   `confidence` (float): Confidence score (0.0 - 1.0).
*   **Usage Notes:** Use this tool when reviewing Joint Venture, Collaboration, or Development agreements to determine if IP created during the partnership is shared.
*   **Example Input:** "Any intellectual property developed jointly by the parties during the term of this Agreement shall be jointly owned by both parties."
*   **Example Output:** `{ "found": true, "extracted_text": "Any intellectual property developed jointly by the parties during the term of this Agreement shall be jointly owned by both parties.", "confidence": 0.98 }`

### 2. check_covenant_not_to_sue
*   **Category:** Covenant Not to Sue
*   **Description:** Identifies broad clauses where a party agrees not to contest the validity of the counterparty's intellectual property rights, waives rights to sue for IP infringement, or waives claims unrelated to the contract. This is a general check for non-assertion or non-contest covenants.
*   **Parameters:**
    *   `contract_text` (string): The full text of the contract or relevant section.
*   **Returns:**
    *   `found` (boolean): Whether a covenant not to sue was detected.
    *   `extracted_text` (string): The specific clause text.
    *   `confidence` (float): Confidence score (0.0 - 1.0).
*   **Usage Notes:** Use this as the primary tool for detecting general waivers of IP challenges. It covers scenarios where a party acknowledges the validity of the other's IP and waives the right to bring infringement claims.
*   **Example Input:** "Party A agrees not to contest the validity, ownership, or enforceability of Party B's intellectual property rights, including patents, trademarks, and copyrights, and waives any right to bring claims against Party B regarding such IP."
*   **Example Output:** `{ "found": true, "extracted_text": "Party A agrees not to contest the validity, ownership, or enforceability of Party B's intellectual property rights, including patents, trademarks, and copyrights, and waives any right to bring claims against Party B regarding such IP.", "confidence": 0.98 }`

### 3. check_covenant_not_to_sue_counterparty
*   **Category:** Covenant Not to Sue
*   **Description:** Detects specific clauses where the **counterparty** agrees not to contest the validity of the **primary party's** intellectual property rights. This is a directional check focusing on the protection of the primary party's IP.
*   **Parameters:**
    *   `contract_text` (string): The full text of the contract or relevant section.
*   **Returns:**
    *   `found` (boolean): Whether a counterparty-specific non-contest clause was detected.
    *   `extracted_text` (string): The specific clause text.
    *   `confidence` (float): Confidence score (0.0 - 1.0).
*   **Usage Notes:** Use this when specifically analyzing whether the other party is restricted from challenging your client's IP.
*   **Example Input:** "Counterparty agrees not to challenge the validity of Primary Party's trademarks and patents."
*   **Example Output:** `{ "found": true, "extracted_text": "Counterparty agrees not to challenge the validity of Primary Party's trademarks and patents.", "confidence": 0.95 }`

### 4. check_covenant_not_to_sue_ip
*   **Category:** Covenant Not to Sue
*   **Description:** Identifies clauses where a party explicitly acknowledges the validity of the counterparty's IP and waives the right to contest ownership or bring infringement claims. This tool focuses on the "acknowledgment + waiver" pattern.
*   **Parameters:**
    *   `contract_text` (string): The full text of the contract or relevant section.
*   **Returns:**
    *   `found` (boolean): Whether an IP acknowledgment/waiver clause was detected.
    *   `extracted_text` (string): The specific clause text.
    *   `confidence` (float): Confidence score (0.0 - 1.0).
*   **Usage Notes:** Use this to find explicit acknowledgments of IP validity coupled with waivers of litigation rights.
*   **Example Input:** "Party acknowledges the validity of Counterparty's IP and waives the right to contest ownership or bring infringement claims."
*   **Example Output:** `{ "found": true, "extracted_text": "Party acknowledges the validity of Counterparty's IP and waives the right to contest ownership or bring infringement claims.", "confidence": 0.96 }`

### 5. check_covenant_not_to_sue_lenders
*   **Category:** Covenant Not to Sue
*   **Description:** Detects clauses where a party waives rights to sue or bring claims against specific third parties, such as lenders or financing agents, often in the context of transaction-related disputes.
*   **Parameters:**
    *   `contract_text` (string): The full text of the contract or relevant section.
*   **Returns:**
    *   `found` (boolean): Whether a lender-specific waiver was detected.
    *   `extracted_text` (string): The specific clause text.
    *   `confidence` (float): Confidence score (0.0 - 1.0).
*   **Usage Notes:** Use this in financing or strategic alliance agreements where lenders are involved to ensure no unintended waivers of rights against financial institutions.
*   **Example Input:** "Party waives any right to sue or bring claims against Lenders or Financing Agents related to the transaction."
*   **Example Output:** `{ "found": true, "extracted_text": "Party waives any right to sue or bring claims against Lenders or Financing Agents related to the transaction.", "confidence": 0.97 }`

### 6. check_third_party_beneficiary
*   **Category:** Third Party Beneficiary
*   **Description:** Identifies clauses that explicitly state whether third parties have rights to enforce the contract. It determines if non-contracting parties (successors, assigns, affiliates, etc.) are granted enforceable rights or if they are explicitly excluded.
*   **Parameters:**
    *   `contract_text` (string): The full text of the contract or relevant section.
*   **Returns:**
    *   `found` (boolean): Whether a third-party beneficiary clause was detected.
    *   `extracted_text` (string): The specific clause text.
    *   `confidence` (float): Confidence score (0.0 - 1.0).
    *   `third_party_rights` (boolean): `true` if third parties have rights, `false` if explicitly excluded.
    *   `explanation` (string): Brief explanation of the clause's effect.
*   **Usage Notes:** Essential for determining who can enforce the contract. Look for "sole benefit of the parties" vs. "intended third-party beneficiaries."
*   **Example Input:** "This Agreement is for the sole benefit of the Parties and their respective successors and permitted assigns, and nothing herein... is intended to... confer upon any other person... any legal or equitable right..."
*   **Example Output:** `{ "found": true, "extracted_text": "...", "confidence": 0.98, "third_party_rights": false, "explanation": "The clause explicitly excludes third-party beneficiaries." }`

### 7. check_rofr_rofo_rofn
*   **Category:** Rofr/Rofo/Rofn
*   **Description:** Scans for clauses granting rights of first refusal (ROFR), first offer (ROFO), or first negotiation (ROFN) regarding equity, assets, services, technology, IP, or business interests.
*   **Parameters:**
    *   `contract_text` (string): The full text of the contract or relevant section.
*   **Returns:**
    *   `found` (boolean): Whether a ROFR/ROFO/ROFN clause was detected.
    *   `extracted_text` (string): The specific clause text.
    *   `confidence` (float): Confidence score (0.0 - 1.0).
*   **Usage Notes:** Use this to identify pre-emptive rights in M&A, joint ventures, or licensing deals.
*   **Example Input:** "In the event that Company proposes to sell, transfer, or otherwise dispose of any equity interest... it shall first offer such interest... to the other party on the same terms and conditions."
*   **Example Output:** `{ "found": true, "extracted_text": "...", "confidence": 0.98 }`

### 8. check_rofr_manufacturing
*   **Category:** Rofr/Rofo/Rofn
*   **Description:** Identifies specific clauses granting a right of first refusal regarding the **design and manufacture** of branded merchandise.
*   **Parameters:**
    *   `contract_text` (string): The full text of the contract or relevant section.
*   **Returns:**
    *   `found` (boolean): Whether a manufacturing ROFR clause was detected.
    *   `extracted_text` (string): The specific clause text.
    *   `confidence` (float): Confidence score (0.0 - 1.0).
*   **Usage Notes:** Use this specifically in licensing or co-branding agreements where manufacturing rights are a key asset.
*   **Example Input:** "Licensee shall have the right of first refusal to design and manufacture any new branded merchandise proposed by Licensor."
*   **Example Output:** `{ "found": true, "extracted_text": "...", "confidence": 0.95 }`

## Review Workflow

1.  **Analyze Contract Type:** Determine if the contract is a Joint Venture, License, Distribution, or Service agreement to prioritize relevant tools.
2.  **Check IP Ownership:**
    *   Run `check_joint_ip_ownership` to see if IP is shared.
    *   *Note: The current tool set does not include a specific "IP Assignment" tool. If IP assignment is critical, note this as a missing input or rely on general text analysis if available in future iterations.*
3.  **Check Covenants Not to Sue:**
    *   Run `check_covenant_not_to_sue` for general waivers.
    *   If specific directionality is needed, run `check_covenant_not_to_sue_counterparty` (protecting primary party) or `check_covenant_not_to_sue_ip` (acknowledgment/waiver).
    *   Run `check_covenant_not_to_sue_lenders` if financing entities are involved.
4.  **Check Third-Party Rights:**
    *   Run `check_third_party_beneficiary` to determine if non-signatories can enforce the contract.
5.  **Check Pre-emptive Rights:**
    *   Run `check_rofr_rofo_rofn` for general equity/asset rights.
    *   Run `check_rofr_manufacturing` if the contract involves branded goods or manufacturing.
6.  **Synthesize Results:** Combine findings into the final JSON output, ensuring all `evidence_unit_ids` correspond to the tools that returned `found: true`.

## Output Format

```json
{
  "status": "success",
  "answer": "Summary of findings regarding Joint IP, Covenants Not to Sue, Third-Party Beneficiaries, and ROFR/ROFO/ROFN rights.",
  "evidence_unit_ids": [
    "tool_001",
    "tool_002"
  ],
  "source_contract_ids": [
    "CONTRACT_ID_123"
  ],
  "missing_inputs": [],
  "human_review_required": false
}
```

*   **status**: "success" if tools executed without error, "error" otherwise.
*   **answer**: A concise summary of the key clauses found.
*   **evidence_unit_ids**: List of tool IDs that returned positive findings (`found: true`).
*   **source_contract_ids**: List of contract identifiers processed.
*   **missing_inputs**: List of required inputs that were missing (e.g., if "IP Ownership Assignment" check is requested but no tool exists, list it here).
*   **human_review_required**: `true` if confidence scores are low (<0.8) or if conflicting clauses are detected.

## Boundary Rules

*   **Do Not** infer IP assignment if no specific tool is provided; mark as missing input if the case definition requires it.
*   **Do Not** confuse "Joint IP Ownership" with "IP Assignment." Joint ownership means both parties own it; assignment means one party transfers ownership to the other.
*   **Do Not** assume a "Covenant Not to Sue" applies to all claims; distinguish between IP-specific waivers and general litigation waivers.
*   **Do Not** overlook "Successors and Assigns" in Third-Party Beneficiary clauses; these are typically *not* considered third-party beneficiaries in the legal sense of *enforcing* rights against the original parties, but rather stepping into the shoes of the original party. The tool `check_third_party_beneficiary` handles this distinction via the `third_party_rights` flag.
*   **Do Not** flag standard "Right to Audit" or "Right to Inspect" as ROFR/ROFO/ROFN.
*   **Do Not** ignore the directionality of Covenants Not to Sue. Ensure you identify *who* is waiving rights against *whom*.
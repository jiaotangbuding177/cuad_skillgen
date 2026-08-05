# SKILL.md

## Overview
This skill, **Competition Restrictions Review**, analyzes commercial contracts to identify clauses that restrict competition, limit business freedom, or impose loyalty obligations between parties. It specifically targets **Exclusivity**, **Non-Compete**, **No-Solicit** (Customers and Employees), **Most Favored Nation (MFN)** pricing, **Non-Disparagement**, and any **Exceptions** to these restrictions.

The skill utilizes a suite of specialized tools to extract precise contractual language, assess the scope of restrictions (territory, duration, subject matter), and identify carveouts that may mitigate risk.

## Available Tools

### 1. Exclusivity & Market Access

#### `check_exclusivity`
*   **Category:** Exclusivity
*   **Description:** Identifies general exclusivity clauses where a party grants exclusive rights to manufacture, sell, distribute, or license products/services, or restricts the other party from working with competitors or third parties in a specific field, territory, or market. Includes sole supplier/distributor appointments and exclusive dealing commitments.
*   **Parameters:**
    *   `contract_text`: The full text of the contract or relevant sections.
*   **Returns:**
    *   `found`: Boolean indicating if an exclusivity clause was detected.
    *   `extracted_text`: The specific clause text.
    *   `confidence`: Confidence score (0-1).
*   **Usage Notes:** Use this as the primary tool for general exclusivity checks. It covers broad restrictions on dealing with third parties.
*   **Example Input:** "Company shall be the exclusive distributor of the Products in the Territory. Supplier shall not sell... to any third party..."
*   **Example Output:** `{"found": true, "extracted_text": "Company shall be the exclusive distributor...", "confidence": 0.98}`

#### `check_exclusivity_circumvention`
*   **Category:** Exclusivity
*   **Description:** Identifies clauses prohibiting parties from bypassing each other to deal directly with third parties introduced by the counterparty (anti-circumvention).
*   **Parameters:**
    *   `contract_text`: The full text of the contract.
*   **Returns:**
    *   `found`: Boolean.
    *   `extracted_text`: The circumvention clause.
    *   `confidence`: Confidence score.
*   **Usage Notes:** Use when reviewing joint ventures or introduction agreements where direct contact with introduced parties is a risk.
*   **Example Input:** "Neither Party shall... contact... any third party introduced by the other Party..."

#### `check_exclusivity_fuel_management`
*   **Category:** Exclusivity
*   **Description:** Identifies clauses granting exclusive rights to manage or supply specific operational inputs, such as fuel, for a project.
*   **Parameters:**
    *   `contract_text`: The full text of the contract.
*   **Returns:**
    *   `found`: Boolean.
    *   `extracted_text`: The fuel management exclusivity clause.
    *   `confidence`: Confidence score.
*   **Usage Notes:** Specific to energy, infrastructure, or industrial projects involving fuel supply.

#### `check_exclusivity_digital_products`
*   **Category:** Exclusivity
*   **Description:** Identifies clauses restricting a party from selling, marketing, or promoting competing digital products (e.g., apps, software) during the term and post-termination.
*   **Parameters:**
    *   `contract_text`: The full text of the contract.
*   **Returns:**
    *   `found`: Boolean.
    *   `extracted_text`: The digital product restriction clause.
    *   `confidence`: Confidence score.
*   **Usage Notes:** Use for software, SaaS, or digital media agreements.

#### `check_exclusivity_airport_retail`
*   **Category:** Exclusivity
*   **Description:** Identifies clauses restricting sales or marketing in specific retail locations (e.g., airports) without counterparty consent.
*   **Parameters:**
    *   `contract_text`: The full text of the contract.
*   **Returns:**
    *   `found`: Boolean.
    *   `extracted_text`: The airport retail restriction clause.
    *   `confidence`: Confidence score.
*   **Usage Notes:** Use for retail distribution or brand licensing agreements involving physical locations.

#### `check_exclusivity_supplier_requirements`
*   **Category:** Exclusivity
*   **Description:** Identifies clauses designating one party as the sole supplier for specific goods or collateral, restricting sourcing from third parties.
*   **Parameters:**
    *   `contract_text`: The full text of the contract.
*   **Returns:**
    *   `found`: Boolean.
    *   `extracted_text`: The sole supplier clause.
    *   `confidence`: Confidence score.
*   **Usage Notes:** Use for supply chain or manufacturing agreements.

### 2. No-Solicit Restrictions

#### `check_no_solicit_of_customers`
*   **Category:** No-Solicit of Customers
*   **Description:** Identifies clauses restricting a party from soliciting, marketing to, or contracting with the counterparty's customers, partners, clients, or users. Includes restrictions on direct contact, inducing competitors, or diverting customers.
*   **Parameters:**
    *   `contract_text`: The full text of the contract.
*   **Returns:**
    *   `found`: Boolean.
    *   `extracted_text`: The no-solicit customer clause.
    *   `confidence`: Confidence score.
*   **Usage Notes:** Critical for service agreements, outsourcing, and distribution deals. Check for duration (during term vs. post-termination).
*   **Example Input:** "Supplier shall not... solicit... any Customer of Buyer..."

#### `check_no_solicit_employees`
*   **Category:** No-Solicit of Employees
*   **Description:** Identifies clauses restricting a party from soliciting, recruiting, hiring, or engaging employees, contractors, or consultants of the counterparty.
*   **Parameters:**
    *   `contract_text`: The full text of the contract.
*   **Returns:**
    *   `found`: Boolean.
    *   `extracted_text`: The no-solicit employee clause.
    *   `confidence`: Confidence score.
*   **Usage Notes:** Common in joint ventures, consulting, and strategic alliances. Note the "look-back" period (e.g., employees engaged in the last 12 months).
*   **Example Input:** "Neither Party shall... solicit for employment... any employee... of the other Party..."

### 3. Pricing & Reputation

#### `check_most_favored_nation`
*   **Category:** Most Favored Nation
*   **Description:** Identifies clauses guaranteeing that a party receives pricing or terms no less favorable than those offered to other third parties for similar goods/services.
*   **Parameters:**
    *   `contract_text`: The full text of the contract.
*   **Returns:**
    *   `found`: Boolean.
    *   `extracted_text`: The MFN clause.
    *   `confidence`: Confidence score.
*   **Usage Notes:** Use for licensing, distribution, and service agreements to ensure competitive pricing protection.
*   **Example Input:** "If... Licensor grants to any third party... terms more favorable... Licensee shall be entitled to the benefit..."

#### `check_non_disparagement`
*   **Category:** Non-Disparagement
*   **Description:** Identifies clauses requiring parties to refrain from making negative, disparaging, defamatory, or misleading statements about the counterparty, its brand, or officers.
*   **Parameters:**
    *   `contract_text`: The full text of the contract.
*   **Returns:**
    *   `found`: Boolean.
    *   `extracted_text`: The non-disparagement clause.
    *   `confidence`: Confidence score.
*   **Usage Notes:** Common in endorsement, partnership, and separation agreements.

### 4. Exceptions & Carveouts

#### `check_exception`
*   **Category:** Exception
*   **Description:** Checks for general exceptions or carveouts to Non-Compete, Exclusivity, and No-Solicit of Customers clauses.
*   **Parameters:**
    *   `contract_text`: The full text of the contract.
*   **Returns:**
    *   `found`: Boolean.
    *   `extracted_text`: The exception clause.
    *   `confidence`: Confidence score.
*   **Usage Notes:** Use after identifying restrictions to see if they are absolute or have defined safe harbors.

#### `check_competitive_exception`
*   **Category:** Competitive Exception
*   **Description:** Specifically checks for exceptions or carveouts to Non-Compete, Exclusivity, and No-Solicit of Customers clauses, often related to pre-existing relationships or specific competitive activities.
*   **Parameters:**
    *   `contract_text`: The full text of the contract.
*   **Returns:**
    *   `found`: Boolean.
    *   `extracted_text`: The competitive exception clause.
    *   `confidence`: Confidence score.
*   **Usage Notes:** Use to identify if the restrictions apply to all competitors or only specific ones.

## Review Workflow

1.  **Ingest Contract Text:** Load the full contract text into the review context.
2.  **Scan for Core Restrictions:**
    *   Run `check_exclusivity` to identify broad market exclusivity.
    *   Run `check_no_solicit_of_customers` to identify customer poaching restrictions.
    *   Run `check_no_solicit_employees` to identify hiring restrictions.
    *   Run `check_most_favored_nation` to identify pricing protections.
    *   Run `check_non_disparagement` to identify reputation protections.
3.  **Scan for Specific/Industry Restrictions (If Applicable):**
    *   If the contract involves digital goods, run `check_exclusivity_digital_products`.
    *   If the contract involves retail/location-based sales, run `check_exclusivity_airport_retail`.
    *   If the contract involves supply chain/manufacturing, run `check_exclusivity_supplier_requirements`.
    *   If the contract involves energy/fuel, run `check_exclusivity_fuel_management`.
    *   If the contract involves introductions/JVs, run `check_exclusivity_circumvention`.
4.  **Scan for Exceptions:**
    *   If any restrictions were found in steps 2 or 3, run `check_exception` and `check_competitive_exception` to identify carveouts.
5.  **Synthesize Results:**
    *   Compile all `found: true` results.
    *   Map extracted texts to their respective categories.
    *   Determine if human review is required based on ambiguity or high-risk clauses (e.g., perpetual non-competes).

## Output Format

The output must be a JSON object conforming to the following schema:

```json
{
  "status": "success" | "error",
  "answer": {
    "exclusivity": {
      "found": boolean,
      "clauses": [
        {
          "tool_id": "string",
          "extracted_text": "string",
          "confidence": float
        }
      ]
    },
    "no_solicit_customers": {
      "found": boolean,
      "clauses": [
        {
          "tool_id": "string",
          "extracted_text": "string",
          "confidence": float
        }
      ]
    },
    "no_solicit_employees": {
      "found": boolean,
      "clauses": [
        {
          "tool_id": "string",
          "extracted_text": "string",
          "confidence": float
        }
      ]
    },
    "most_favored_nation": {
      "found": boolean,
      "clauses": [
        {
          "tool_id": "string",
          "extracted_text": "string",
          "confidence": float
        }
      ]
    },
    "non_disparagement": {
      "found": boolean,
      "clauses": [
        {
          "tool_id": "string",
          "extracted_text": "string",
          "confidence": float
        }
      ]
    },
    "exceptions": {
      "found": boolean,
      "clauses": [
        {
          "tool_id": "string",
          "extracted_text": "string",
          "confidence": float
        }
      ]
    }
  },
  "evidence_unit_ids": ["string"],
  "source_contract_ids": ["string"],
  "missing_inputs": ["string"],
  "human_review_required": boolean
}
```

## Boundary Rules

*   **Do Not Interpret Law:** The skill extracts and identifies clauses based on textual patterns. It does not provide legal advice on the enforceability of these clauses (e.g., whether a non-compete is void under local law).
*   **Scope Limitation:** Only analyze the provided contract text. Do not infer restrictions from external knowledge or other contracts unless explicitly linked in the `source_contract_ids`.
*   **Confidence Thresholds:** If a tool returns a confidence score below 0.7, flag the result for `human_review_required`.
*   **Non-Compete Specifics:** Note that the current tool set focuses heavily on *Exclusivity* and *No-Solicit*. If a general "Non-Compete" clause is present but not captured by `check_exclusivity`, it may be missed. Use `check_exclusivity` as the primary proxy for non-compete behavior in this skill set, as it covers "prohibitions on competing activities."
*   **Exception Handling:** If `check_exception` or `check_competitive_exception` returns `found: true`, ensure the extracted text is included in the `exceptions` section of the output, even if the primary restriction tools returned `found: false` (though this is rare).
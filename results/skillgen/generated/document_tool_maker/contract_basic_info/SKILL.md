# SKILL.md

## Overview
This skill, **Contract Basic Info Extraction**, is designed to identify and extract fundamental metadata from legal agreements. It focuses on the "who, what, and when" of a contract by locating the document title, the involved parties, and key temporal milestones (agreement date and expiration date). This skill serves as the foundational step in any contract review workflow, establishing the identity and temporal scope of the agreement before diving into substantive clause analysis.

## Available Tools

### 1. check_document_name
- **Category**: Document Name
- **Description**: Extracts the formal title or name of the agreement from the document header, introductory clauses, or signature blocks. It identifies the specific type of contract (e.g., "Content License Agreement," "Supply Agreement").
- **Parameters**:
  - `document_text` (string): The full text of the contract or the header/introductory section.
- **Returns**:
  - `found` (boolean): Whether a clear document name was identified.
  - `extracted_text` (string): The exact title string found in the document.
  - `confidence` (float): Confidence score (0.0 to 1.0) of the extraction.
- **Usage Notes**:
  - Look for capitalized titles at the very beginning of the document.
  - If the title is not explicitly capitalized, look for phrases like "This [Agreement Name] is entered into..."
  - **Example**:
    - *Input*: "CONTENT LICENSE AGREEMENT\n\nThis Content License Agreement (the \"Agreement\") is entered into as of September 8, 2005..."
    - *Output*: `{"found": true, "extracted_text": "CONTENT LICENSE AGREEMENT", "confidence": 0.98}`

### 2. check_parties
- **Category**: Parties
- **Description**: Identifies the legal entities or individuals entering into the agreement. It extracts their full legal names, roles (e.g., Licensor, Licensee, Buyer, Seller), corporate structure (e.g., "Delaware corporation"), jurisdiction, and any defined short names used throughout the contract.
- **Parameters**:
  - `document_text` (string): The full text of the contract, specifically focusing on the preamble or "Parties" section.
- **Returns**:
  - `found` (boolean): Whether parties were successfully identified.
  - `extracted_text` (string): A structured string or list containing the names and descriptions of the parties.
  - `confidence` (float): Confidence score (0.0 to 1.0).
- **Usage Notes**:
  - Look for phrases like "entered into by and between," "made by and between," or "this Agreement is between."
  - Capture both the full legal name and the defined short name (e.g., "Virgin Galactic Holdings, Inc. (\"Company\").")
  - **Example**:
    - *Input*: "This Agreement is entered into by and between Virgin Galactic Holdings, Inc., a Delaware corporation, and [Counterparty Name], a [Jurisdiction] entity."
    - *Output*: `{"found": true, "extracted_text": "Virgin Galactic Holdings, Inc., a Delaware corporation; [Counterparty Name], a [Jurisdiction] entity", "confidence": 0.98}`

### 3. check_agreement_date
- **Category**: Agreement Date
- **Description**: Extracts the date on which the contract or amendment was physically signed, executed, or formally entered into. This is often distinct from the effective date.
- **Parameters**:
  - `document_text` (string): The full text of the contract, focusing on the preamble and signature blocks.
- **Returns**:
  - `found` (boolean): Whether an agreement date was identified.
  - `extracted_text` (string): The date string (e.g., "April 16, 2014").
  - `confidence` (float): Confidence score (0.0 to 1.0).
- **Usage Notes**:
  - Look for phrases like "entered into as of," "dated," or "executed on."
  - Distinguish this from the "Effective Date" if they differ.
  - **Example**:
    - *Input*: "This Agreement is entered into as of April 16, 2014."
    - *Output*: `{"found": true, "extracted_text": "April 16, 2014", "confidence": 0.98}`

### 4. check_expiration_date
- **Category**: Expiration Date
- **Description**: Determines the expiration date of the initial term of the agreement. It identifies if the agreement has a fixed end date or is perpetual. It often looks in sections titled "Term," "Duration," or "Expiration."
- **Parameters**:
  - `document_text` (string): The full text of the contract, specifically the "Term" or "Duration" section.
- **Returns**:
  - `found` (boolean): Whether an expiration date or term condition was identified.
  - `extracted_text` (string): The specific date or description of the term end (e.g., "December 31, 2025" or "Perpetual").
  - `confidence` (float): Confidence score (0.0 to 1.0).
- **Usage Notes**:
  - Look for phrases like "shall expire on," "initial term shall end on," or "continue until."
  - If the term is defined by a duration (e.g., "12 months from Effective Date"), note that the tool extracts the explicit date if available, or the duration clause if no fixed date is present.
  - **Example**:
    - *Input*: "The Initial Term of this Agreement shall commence on the Effective Date and shall expire on December 31, 2025, unless earlier terminated in accordance with Section 8."
    - *Output*: `{"found": true, "extracted_text": "December 31, 2025", "confidence": 0.98}`

## Review Workflow

1. **Pre-processing**: Ensure the contract text is clean and readable. Identify the document structure (Header, Preamble, Body, Signatures).
2. **Step 1: Identify Document Identity**:
   - Run `check_document_name` to establish what type of agreement is being reviewed.
   - *Why first?* The document name often dictates the context for interpreting other clauses.
3. **Step 2: Identify the Parties**:
   - Run `check_parties` to determine who is bound by the agreement.
   - *Why second?* Knowing the parties helps in understanding roles (e.g., who is the Licensor vs. Licensee) which is critical for subsequent clause analysis.
4. **Step 3: Establish Temporal Context**:
   - Run `check_agreement_date` to find when the contract was signed.
   - Run `check_expiration_date` to find when the initial term ends.
   - *Note*: If an "Effective Date" is required but not explicitly extracted by a dedicated tool, check if the `check_agreement_date` or `check_expiration_date` tools provide context clues, or note it as missing if a specific effective date tool is not available in this skill set.
5. **Step 4: Validation**:
   - Cross-reference the extracted dates and names with the signature block to ensure consistency.
   - If confidence scores are low (<0.8), flag for human review.

## Output Format

The output of this skill is a JSON object conforming to the following schema:

```json
{
  "status": "success | failure | partial",
  "answer": {
    "document_name": "string | null",
    "parties": "string | null",
    "agreement_date": "string | null",
    "expiration_date": "string | null"
  },
  "evidence_unit_ids": ["tool_001", "tool_001", "tool_001", "tool_001"],
  "source_contract_ids": ["string"],
  "missing_inputs": ["list of missing fields if any"],
  "human_review_required": boolean
}
```

- **status**: Indicates the overall success of the extraction.
- **answer**: Contains the extracted values for each category.
- **evidence_unit_ids**: References the specific tool IDs used for extraction.
- **source_contract_ids**: The ID of the contract being analyzed.
- **missing_inputs**: Lists any categories that could not be extracted (e.g., ["effective_date"] if not covered by tools).
- **human_review_required**: Set to `true` if any confidence score is below 0.8 or if critical information is missing.

## Boundary Rules

- **Do**:
  - Extract exact text strings for names and dates as they appear in the contract.
  - Distinguish between "Agreement Date" (signing date) and "Expiration Date" (end of term).
  - Handle multiple parties by listing them all in the `check_parties` output.
  - Return `null` for fields that are not present in the document rather than guessing.

- **Do Not**:
  - Do not infer the "Effective Date" if it is not explicitly stated or if the tool does not support it (note: this skill set does not include a dedicated `check_effective_date` tool, so if the effective date differs from the agreement date, it may be missed or require manual review).
  - Do not interpret legal implications of the dates or parties (e.g., do not determine if a party is a subsidiary; just extract the text).
  - Do not extract dates from unrelated sections (e.g., dates in recitals that are not the agreement date).
  - Do not modify the format of extracted dates (keep original string format).
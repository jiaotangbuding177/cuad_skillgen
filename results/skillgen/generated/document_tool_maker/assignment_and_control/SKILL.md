# SKILL.md

## Overview
This skill specializes in reviewing contracts for **Change of Control** and **Anti-Assignment** provisions. It identifies clauses that define control events (mergers, asset sales, ownership transfers), determines if such events trigger termination rights, require consent or notice, impose financial penalties, or restrict assignment to successors. The skill extracts specific conditions, such as board approval requirements, credit rating thresholds, and automatic termination triggers.

## Available Tools

### 1. check_change_of_control
- **Category**: Change of Control
- **Description**: Determines if the contract contains specific provisions regarding change of control events (such as mergers, asset sales, or transfers of ownership), including definitions of control, and whether these events trigger termination rights, require notice, or require consent.
- **Parameters**: None (Context: Contract Text)
- **Returns**: `found` (boolean), `extracted_text` (string), `confidence` (float)
- **Usage Notes**: Use this as the primary discovery tool to identify if Change of Control clauses exist. It captures general definitions and high-level triggers.
- **Example**:
  - *Input*: "Review the contract for Change of Control provisions."
  - *Output*: `{"found": true, "extracted_text": "In the event of a Change of Control of either Party, the other Party shall have the right to terminate this Agreement upon thirty (30) days written notice.", "confidence": 0.98}`

### 2. check_change_of_control_termination_rights
- **Category**: Change of Control
- **Description**: Identifies clauses that grant a party the specific right to terminate the agreement, or require notice/consent, upon a Change of Control event of the other party, including specific conditions such as objectionable acquirers or financial status changes.
- **Parameters**: None (Context: Contract Text)
- **Returns**: `found` (boolean), `extracted_text` (string), `confidence` (float)
- **Usage Notes**: Use when specifically looking for the *right to terminate* rather than automatic termination. Focuses on discretionary termination rights.
- **Example**:
  - *Input*: "Check for termination rights triggered by Change of Control."
  - *Output*: `{"found": true, "extracted_text": "If a Change of Control occurs with respect to Company, Sponsor may terminate this Agreement immediately upon written notice.", "confidence": 0.95}`

### 3. check_change_of_control_termination
- **Category**: Change of Control
- **Description**: Identifies clauses where the agreement automatically terminates, ceases to have effect, or requires notice/consent due to a change in ownership, control, bankruptcy, insolvency, or cessation of business.
- **Parameters**: None (Context: Contract Text)
- **Returns**: `found` (boolean), `extracted_text` (string), `confidence` (float)
- **Usage Notes**: Use to find *automatic* termination clauses (e.g., "shall automatically terminate") as opposed to discretionary rights.
- **Example**:
  - *Input*: "Identify automatic termination clauses related to Change of Control."
  - *Output*: `{"found": true, "extracted_text": "This Agreement shall automatically terminate upon the sale of all or substantially all assets of the Company.", "confidence": 0.92}`

### 4. check_successors_bound_clause
- **Category**: Change of Control
- **Description**: Determines if the contract explicitly binds successors and assigns, which is relevant to change of control scenarios where assets or shares are transferred.
- **Parameters**: None (Context: Contract Text)
- **Returns**: `found` (boolean), `extracted_text` (string), `confidence` (float)
- **Usage Notes**: Essential for determining if the contract survives a change of control by binding the new entity. Look for "binding upon and inure to the benefit of... successors and permitted assigns."
- **Example**:
  - *Input*: "Check if successors are bound."
  - *Output*: `{"found": true, "extracted_text": "This Agreement shall be binding upon and inure to the benefit of the parties hereto and their respective successors and permitted assigns.", "confidence": 0.99}`

### 5. check_change_of_control_board_approval
- **Category**: Change of Control
- **Description**: Checks if unanimous board approval or specific shareholder consent is required for the company to enter into a change of control transaction or transfer of interest.
- **Parameters**: None (Context: Contract Text)
- **Returns**: `found` (boolean), `extracted_text` (string), `confidence` (float)
- **Usage Notes**: Use to identify internal governance hurdles (Board/Shareholder consent) required before a Change of Control can occur.
- **Example**:
  - *Input*: "Check for board approval requirements for Change of Control."
  - *Output*: `{"found": true, "extracted_text": "No Change of Control transaction may be entered into without the unanimous written consent of the Board of Directors.", "confidence": 0.96}`

### 6. check_change_of_control_rating_conditions
- **Category**: Change of Control
- **Description**: Extracts specific financial or rating conditions that must be met by an acquirer or new corporate structure for a change of control to be permissible without triggering immediate termination or breach.
- **Parameters**: None (Context: Contract Text)
- **Returns**: `found` (boolean), `extracted_text` (string), `confidence` (float)
- **Usage Notes**: Use to find "safe harbor" conditions, such as maintaining a specific credit rating (e.g., A-) or financial strength.
- **Example**:
  - *Input*: "Identify rating conditions for Change of Control."
  - *Output*: `{"found": true, "extracted_text": "A Change of Control shall not be deemed a default if the successor entity maintains a credit rating of at least A-.", "confidence": 0.94}`

### 7. check_change_of_control_rights
- **Category**: Change of Control
- **Description**: Identifies clauses that grant specific rights or trigger obligations for a party in the event the other party undergoes a Change of Control, beyond simple termination.
- **Parameters**: None (Context: Contract Text)
- **Returns**: `found` (boolean), `extracted_text` (string), `confidence` (float)
- **Usage Notes**: Use to find non-termination consequences, such as requirements for additional security, performance bonds, or renegotiation rights.
- **Example**:
  - *Input*: "Identify rights triggered by Change of Control."
  - *Output*: `{"found": true, "extracted_text": "Upon a Change of Control, the Non-Affected Party may require the Affected Party to provide additional security for performance.", "confidence": 0.93}`

### 8. check_change_of_control_depositor
- **Category**: Change of Control
- **Description**: Checks if the Depositor is restricted from merging, consolidating, or assigning its interests without specific conditions or if such events trigger termination or consent requirements.
- **Parameters**: None (Context: Contract Text)
- **Returns**: `found` (boolean), `extracted_text` (string), `confidence` (float)
- **Usage Notes**: Specific to securitization or structured finance contracts involving a "Depositor" entity.
- **Example**:
  - *Input*: "Check restrictions on Depositor Change of Control."
  - *Output*: `{"found": true, "extracted_text": "Depositor shall not merge or consolidate with any other entity without prior written consent of the Servicer.", "confidence": 0.97}`

### 9. check_change_of_control_servicer
- **Category**: Change of Control
- **Description**: Checks if the Servicer is restricted from merging, consolidating, or assigning its interests without specific conditions or if such events trigger termination or consent requirements.
- **Parameters**: None (Context: Contract Text)
- **Returns**: `found` (boolean), `extracted_text` (string), `confidence` (float)
- **Usage Notes**: Specific to securitization or structured finance contracts involving a "Servicer" entity.
- **Example**:
  - *Input*: "Check restrictions on Servicer Change of Control."
  - *Output*: `{"found": true, "extracted_text": "Servicer shall not transfer its obligations under this Agreement in connection with a Change of Control without approval.", "confidence": 0.97}`

### 10. check_change_of_control_assignment
- **Category**: Change of Control
- **Description**: Determines if the contract allows assignment to a successor entity in the event of a change of control, merger, or asset sale.
- **Parameters**: None (Context: Contract Text)
- **Returns**: `found` (boolean), `extracted_text` (string), `confidence` (float)
- **Usage Notes**: Use to determine if the contract explicitly permits assignment to a successor in a merger/acquisition scenario, often overriding general anti-assignment clauses.
- **Example**:
  - *Input*: "Check if assignment to successor is allowed upon Change of Control."
  - *Output*: `{"found": true, "extracted_text": "In the event of a merger or acquisition, the rights and obligations of the acquiring entity shall be assigned to the successor.", "confidence": 0.95}`

### 11. check_change_of_control_financial_consequences
- **Category**: Change of Control
- **Description**: Identifies any specific financial payments, penalties, or obligations triggered for a party (e.g., Distributor) upon a Change of Control termination.
- **Parameters**: None (Context: Contract Text)
- **Returns**: `found` (boolean), `extracted_text` (string), `confidence` (float)
- **Usage Notes**: Use to find monetary impacts, such as buyout fees, commission payouts, or penalties triggered specifically by Change of Control termination.
- **Example**:
  - *Input*: "Identify financial consequences of Change of Control termination."
  - *Output*: `{"found": true, "extracted_text": "Upon termination due to Change of Control, Company shall pay Distributor a fee equal to 12 months of average commissions.", "confidence": 0.96}`

## Review Workflow

1.  **Initial Scan**: Run `check_change_of_control` to determine if the contract contains any Change of Control provisions. If `found` is false, proceed to step 4.
2.  **Termination Analysis**:
    *   Run `check_change_of_control_termination_rights` to identify discretionary termination rights.
    *   Run `check_change_of_control_termination` to identify automatic termination clauses.
3.  **Conditions & Consequences**:
    *   Run `check_change_of_control_board_approval` to check for internal consent requirements.
    *   Run `check_change_of_control_rating_conditions` to check for financial/rating safe harbors.
    *   Run `check_change_of_control_rights` to identify non-termination obligations (e.g., additional security).
    *   Run `check_change_of_control_financial_consequences` to identify monetary penalties or payouts.
4.  **Assignment & Successors**:
    *   Run `check_successors_bound_clause` to verify if the contract binds successors.
    *   Run `check_change_of_control_assignment` to see if assignment to a successor is explicitly permitted.
5.  **Entity-Specific Checks (If Applicable)**:
    *   If the contract involves a Depositor, run `check_change_of_control_depositor`.
    *   If the contract involves a Servicer, run `check_change_of_control_servicer`.
6.  **Synthesis**: Compile findings into the output format, noting any missing inputs or areas requiring human review (e.g., ambiguous definitions of "Control").

## Output Format

```json
{
  "status": "success",
  "answer": "Summary of Change of Control and Assignment provisions found.",
  "evidence_unit_ids": ["tool_001", "tool_002", "tool_004"],
  "source_contract_ids": ["CONTRACT_ID_123"],
  "missing_inputs": [],
  "human_review_required": false
}
```

## Boundary Rules

-   **Do**: Focus strictly on clauses related to Change of Control (mergers, acquisitions, asset sales, ownership changes) and Assignment (transfer of rights/obligations).
-   **Do**: Extract exact text snippets that define the triggers, rights, and consequences.
-   **Do**: Distinguish between *automatic* termination and *discretionary* termination rights.
-   **Do**: Identify specific conditions (e.g., credit ratings, board approval) that modify the standard Change of Control outcome.
-   **Don't**: Include general termination clauses unrelated to Change of Control (e.g., termination for convenience, termination for cause due to breach) unless explicitly linked to a Change of Control event.
-   **Don't**: Assume assignment is allowed or prohibited without explicit textual evidence; rely on `check_successors_bound_clause` and `check_change_of_control_assignment`.
-   **Don't**: Provide legal advice; only extract and summarize contractual provisions.
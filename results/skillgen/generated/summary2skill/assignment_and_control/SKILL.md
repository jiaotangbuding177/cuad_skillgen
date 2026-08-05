# SKILL.md: Assignment and Change of Control Review

## Covered Categories

### 1. Change of Control
*   **Discovery Frequency:** 32.7% of contracts (100/306).
*   **Common Patterns:**
    *   **Termination Rights:** Grants one or both parties the right to terminate the agreement upon a Change of Control (CoC), often requiring written notice.
    *   **Automatic Termination:** In regulated industries (e.g., Investment Funds under the 1940 Act), the agreement may automatically terminate upon an assignment defined as a CoC.
    *   **Financial Consequences:** Triggers buy-out payments, liquidated damages, or one-time payments.
    *   **Definition via Assignment:** CoC is frequently defined or triggered by the assignment of the agreement to a successor in a merger, acquisition, or sale of substantially all assets.
    *   **Competitor Restrictions:** Specific provisions restrict assignments to direct competitors or allow termination if the acquiring entity is a competitor.

### 2. Anti-Assignment
*   **Discovery Frequency:** 63.1% of contracts (193/306).
*   **Common Patterns:**
    *   **Prior Written Consent:** Prohibition on assignment without the prior written consent of the other party.
    *   **Unreasonably Withheld:** Consent for assignment is often stipulated as not to be unreasonably withheld, conditioned, or delayed.
    *   **Null and Void:** Unauthorized assignments are typically declared null and void.
    *   **Exceptions for Successors:** Allowances for assignment to affiliates, purchasers of substantially all assets, or successors in mergers, provided obligations are assumed.

## Common Patterns

### Change of Control
1.  **Termination Right with Notice:**
    *   *Description:* The non-affected party has the right to terminate the agreement if a Change of Control occurs, usually requiring a specific notice period (e.g., 6 months).
    *   *Example Phrasing:* "The contract defines Change of Control and grants the non-affected party the right to terminate the agreement with six months' advance written notice if a Change of Control occurs."
2.  **Automatic Termination (Regulated Industries):**
    *   *Description:* The agreement terminates automatically upon an assignment defined as a change of control, common in investment funds.
    *   *Example Phrasing:* "The agreement automatically terminates in the event of its 'assignment' (as such term is defined for purposes of Section 15(a) (4) of the Investment Fund Act)."
3.  **Competitor/Management Restriction:**
    *   *Description:* Termination rights are triggered specifically if the new controlling entity is a competitor or if management changes significantly.
    *   *Example Phrasing:* "Lucid has the right to terminate the agreement if there is any change of control, ownership, or management of the Distributor."

### Anti-Assignment
1.  **Consent Required (Not Unreasonably Withheld):**
    *   *Description:* Assignment is prohibited unless the other party provides prior written consent, which cannot be unreasonably withheld.
    *   *Example Phrasing:* "Neither party may assign the agreement without the prior written consent of the other, except in cases of merger or succession to substantially all assets where obligations are assumed."
2.  **Null and Void Clause:**
    *   *Description:* Any assignment made without proper consent is explicitly declared null and void.
    *   *Example Phrasing:* "The contract explicitly prohibits either party from assigning its rights or delegating its obligations to a third party, rendering any such assignment null and void."
3.  **Affiliate/Successor Exceptions:**
    *   *Description:* Assignment is allowed to affiliates or in connection with a merger/sale of assets without consent, provided notice is given.
    *   *Example Phrasing:* "The contract allows for assignment or transfer in connection with a change of control, such as a merger or sale of substantially all assets, provided that notice is given to the other party, though prior consent is not required for these specific events."

## Review Checklist

### Change of Control
- [ ] **Definition Check:** Is "Change of Control" explicitly defined? Does it include mergers, stock sales, asset sales, or changes in management/voting control?
- [ ] **Termination Rights:** Does either party have the right to terminate the agreement upon a Change of Control?
- [ ] **Notice Requirements:** If termination is allowed, what is the required notice period (e.g., 6 months)?
- [ ] **Automatic Termination:** Does the agreement automatically terminate upon a Change of Control (common in regulated sectors)?
- [ ] **Financial Implications:** Are there buy-out payments, liquidated damages, or other financial consequences triggered by a Change of Control?
- [ ] **Competitor Restrictions:** Are there restrictions on assigning to or being acquired by a direct competitor?

### Anti-Assignment
- [ ] **General Prohibition:** Is assignment generally prohibited without consent?
- [ ] **Consent Standard:** Is consent required? If so, is it subject to a "not unreasonably withheld" standard?
- [ ] **Exceptions:** Are there exceptions for assignments to affiliates, successors in mergers, or purchasers of substantially all assets?
- [ ] **Consequences of Breach:** Is an unauthorized assignment declared "null and void" or does it trigger automatic termination?
- [ ] **Asymmetry:** Are assignment rights asymmetric (e.g., one party can assign freely while the other cannot)?
- [ ] **Delegation vs. Assignment:** Does the contract distinguish between assigning rights and delegating duties?

## Evidence Extraction Rules

1.  **Locate Clauses:** Search for keywords: "Assignment," "Change of Control," "Merger," "Acquisition," "Successor," "Transfer," "Delegation," "Consent," "Null and Void."
2.  **Extract Definitions:** Extract the specific definition of "Change of Control" if present. Note if it references another agreement (e.g., Asset Purchase Agreement).
3.  **Identify Triggers:** Identify what events trigger the clause (e.g., sale of >50% equity, change in management, merger).
4.  **Capture Rights/Remedies:**
    *   For **Change of Control**: Extract termination rights, notice periods, and financial penalties.
    *   For **Anti-Assignment**: Extract consent requirements, exceptions (affiliates, mergers), and consequences of unauthorized assignment (void vs. termination).
5.  **Note Variations:** Flag if the clause is asymmetric (one-sided) or if it prohibits assignment entirely without exceptions.
6.  **Contextualize:** Note if the contract is in a regulated industry (e.g., Investment Funds) where automatic termination is common.

## Output Format

```json
{
  "status": "success|failure",
  "answer": {
    "change_of_control": {
      "defined": true|false,
      "termination_right": {
        "party": "Party A|Party B|Both|Neither",
        "notice_period": "string|null",
        "automatic_termination": true|false
      },
      "financial_consequences": "string|null",
      "competitor_restriction": true|false,
      "definition_details": "string|null"
    },
    "anti_assignment": {
      "consent_required": true|false,
      "consent_standard": "unreasonably withheld|absolute|null",
      "exceptions": ["affiliate", "merger", "asset_sale", "none"],
      "consequence_of_breach": "null_and_void|automatic_termination|breach|null",
      "asymmetric": true|false,
      "delegation_allowed": true|false|null
    }
  },
  "evidence_unit_ids": ["string", "string"],
  "source_contract_ids": ["string"],
  "missing_inputs": ["string"],
  "human_review_required": true|false
}
```

## Boundary Rules

1.  **Scope Limitation:** This skill only reviews clauses related to **Assignment** and **Change of Control**. Do not review general termination clauses unrelated to assignment or control changes.
2.  **Definition Dependency:** If "Change of Control" is defined by reference to another agreement, note this but do not attempt to extract the definition from the external agreement unless it is included in the input.
3.  **Regulatory Context:** Be aware that in regulated industries (e.g., Investment Funds), "Assignment" may be legally defined as a Change of Control, triggering automatic termination. Do not assume standard commercial rules apply.
4.  **No Legal Advice:** The output is for informational purposes only. Do not provide legal advice on the enforceability of clauses.
5.  **Ambiguity Handling:** If the contract is silent on assignment or change of control, report `null` or `false` as appropriate, and flag for human review if the absence is critical to the business case.
6.  **Distinction:** Clearly distinguish between "Assignment" (transfer of rights/obligations) and "Change of Control" (change in ownership/management). They may be linked but are distinct concepts.
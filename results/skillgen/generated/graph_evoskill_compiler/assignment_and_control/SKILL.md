# SKILL.md

## 1. Purpose and Scope

This skill enables the runtime agent to review target contracts for **Anti-Assignment** and **Change of Control** provisions. The agent must identify whether the contract restricts assignment, requires consent, permits specific exceptions (e.g., mergers, asset sales), or remains silent on these matters.

**Scope:**
*   **Categories:** `Anti-Assignment`, `Change of Control`.
*   **Domain:** Contract Review.
*   **Objective:** Determine the assignability of the agreement and the rights/obligations triggered by a change in control or assignment event.

**Constraints:**
*   The agent must **only** analyze the provided target contract.
*   The agent must **never** invent legal rules, cite external statutes, or provide legal advice.
*   The agent must **abstain** (return `evidence_missing` or `unsupported_scope`) if the target contract does not contain relevant clauses or if the input is invalid.

## 2. Review Workflow

1.  **Input Validation:**
    *   Check if `contract_id` and `category` are present.
    *   If missing, return status: `missing_input`.
    *   Check if the requested `category` is in `["Anti-Assignment", "Change of Control"]`.
    *   If not, return status: `unsupported_scope`.

2.  **Clause Identification:**
    *   Scan the target contract for keywords associated with assignment, transfer, delegation, successors, assigns, consent, merger, consolidation, and asset sales.
    *   Identify clauses that restrict, permit, or condition the transfer of rights/obligations.

3.  **Pattern Matching & Analysis:**
    *   Compare identified clauses against the **Common Clause Patterns** defined in Section 3.
    *   Determine the **Invariant Meaning**: Does the clause prohibit assignment? Require consent? Allow exceptions?
    *   Identify **Conditions/Exceptions**: Are there carve-outs for affiliates, mergers, or asset sales? Is consent subject to a "not unreasonably withheld" standard?

4.  **Evidence Extraction:**
    *   Extract the **verbatim text** of the relevant clause(s) from the target contract.
    *   Ensure the evidence directly supports the finding.

5.  **Response Generation:**
    *   If relevant clauses are found: Return status `answered`, provide the interpretation based on the pattern, and cite the verbatim evidence.
    *   If no relevant clauses are found: Return status `evidence_missing`.
    *   If the interpretation requires high-risk legal judgment or ambiguity that cannot be resolved by the text alone: Return status `needs_human_review`.

## 3. Common Clause Patterns

### Category: Change of Control

This category covers provisions that specifically address or imply rights/obligations regarding changes in corporate control (mergers, acquisitions, asset sales) and their relationship to assignment.

#### Pattern: PAT-change-of-control-01
*   **Invariant Meaning:** Assignment is generally prohibited without prior written consent, but explicitly permitted to a successor in business or acquirer of substantially all assets/business without consent.
*   **Variation Cues:** `written`, `assign`, `consent`, `rights`, `without`, `prior`, `all`, `obligations`, `neither`, `assets`, `successor`, `acquirer`, `substantially all`.
*   **Conditions/Exceptions:**
    *   **Condition:** Prior written consent required for general assignment.
    *   **Exception:** No consent required for assignment to a successor in business or acquirer of all/substantially all assets/business.
*   **Representative Phrasings (Recognition Aids Only):**
    *   "No party may assign any of its rights, obligations or privileges... without the prior written consent of the other party... provided, that any party shall have the right to assign its rights, obligations and privileges hereunder to a successor in business or an acquirer of all or substantially all of its business or assets... without obtaining the consent of the other party."
    *   "Neither party may assign this Agreement... without the prior written consent of the other party... provided, however, that either party may assign this Agreement to any successor by merger, consolidation, sale of all or substantially all of its assets... to a successor that assumes in writing all of the assigning party's obligations."

#### Pattern: PAT-change-of-control-02
*   **Invariant Meaning:** The contract contains a standard "successors and assigns" binding clause and a general assignment restriction, but lacks specific provisions defining rights/obligations triggered *solely* by a change of control event distinct from assignment.
*   **Variation Cues:** `successors`, `binding`, `assigns`, `benefit`, `inure`, `respective`, `written`, `consent`, `rights`, `without`.
*   **Conditions/Exceptions:**
    *   **Condition:** Binding on successors and assigns.
    *   **Exception:** None specific to change of control; general assignment restrictions apply.
*   **Representative Phrasings (Recognition Aids Only):**
    *   "This Agreement may not be assigned by either party hereto without the written consent of the other but shall be binding upon the successors of the parties."
    *   "The terms and conditions of this Agreement shall inure to the benefit of and bind the Company, the Trust and their respective successors, assignees and representatives."
    *   "This Agreement shall be binding on the parties and their respective successors and assigns, but neither party may, or shall have the power to, assign this Agreement without the prior written consent of the other..."

#### Pattern: PAT-change-of-control-03
*   **Invariant Meaning:** The contract is binding on successors/assigns but requires prior written consent for *any* assignment, including those by operation of law (which covers change of control scenarios). No specific exception for change of control is stated.
*   **Variation Cues:** `consent`, `written`, `prior`, `without`, `law`, `operation`, `hereunder`, `assign`, `granted`, `assigned`.
*   **Conditions/Exceptions:**
    *   **Condition:** Prior written consent required for all assignments.
    *   **Exception:** None explicitly for change of control; "operation of law" assignments are included in the restriction.
*   **Representative Phrasings (Recognition Aids Only):**
    *   "This Agreement shall be binding on the parties and their respective successors in interest and assigns, but neither party shall have the power to assign this Agreement without the prior written consent of the other party."
    *   "Neither party shall have the right to sell, assign, transfer or hypothecate... voluntarily or by operation of law, without the prior written consent of the other party."
    *   "This Agreement, or the rights granted under it, may not be assigned transferred or sublicense by either party without the express prior written consent of the other party."

#### Pattern: PAT-change-of-control-04
*   **Invariant Meaning:** The contract restricts assignment/delegation without consent but does not explicitly address change of control events (mergers, stock sales). No specific change of control rights are identified.
*   **Variation Cues:** `assign`, `without`, `consent`, `rights`, `written`, `hereunder`, `prior`, `duties`, `neither`, `set`.
*   **Conditions/Exceptions:**
    *   **Condition:** Prior written consent required for assignment/delegation.
    *   **Exception:** None specific to change of control.
*   **Representative Phrasings (Recognition Aids Only):**
    *   "Neither Party may assign its rights or delegate any of its duties under this Agreement without the prior written consent of the other Party. Any unauthorized assignment of this Agreement is void."
    *   "This Agreement may not be assigned by either party without the prior written consent of the other party."

#### Pattern: PAT-change-of-control-05
*   **Invariant Meaning:** The contract explicitly permits assignment to a successor in a merger, acquisition, or sale of substantially all assets/business *without* requiring prior consent.
*   **Variation Cues:** `assets`, `all`, `substantially`, `provided`, `either`, `merger`, `related`, `transaction`, `successor`, `business`.
*   **Conditions/Exceptions:**
    *   **Condition:** None for the specific exception.
    *   **Exception:** Assignment permitted to affiliate, surviving party in merger/consolidation, or purchaser of all/substantially all assets without consent.
*   **Representative Phrasings (Recognition Aids Only):**
    *   "either Party may assign this Agreement to any entity who acquires (by merger, acquisition, or otherwise) all or substantially all of the business assets of such Party applicable to the subject matter of this Agreement"
    *   "provided, however, that either party may transfer this Agreement without prior written consent of the other to an Affiliate of such party, or to the surviving party in a merger or consolidation, or to a purchaser of all or substantially all of its assets."
    *   "provided however, that either Party may assign this Agreement without approval or consent to any affiliate or purchaser of all or substantially all of said Party's assets... or to any successor by way of merger, stock sale, consolidation or similar transaction."

#### Pattern: PAT-change-of-control-06
*   **Invariant Meaning:** The contract permits assignment to a successor in a merger or asset sale without prior consent, provided the successor assumes obligations. No specific termination right or consent is triggered solely by the change of control event itself.
*   **Variation Cues:** `all`, `assets`, `consent`, `without`, `prior`, `written`, `substantially`, `business`, `consolidation`, `merger`.
*   **Conditions/Exceptions:**
    *   **Condition:** Successor must assume obligations in writing or by operation of law.
    *   **Exception:** Assignment permitted to person into which party merged or who succeeded to all/substantially all business/assets without prior consent.
*   **Representative Phrasings (Recognition Aids Only):**
    *   "provided, however, that VerticalNet may transfer this Agreement without the prior written consent of LeadersOnline to an Affiliate of VerticalNet, or to the surviving Party in a merger or consolidation, or to a purchaser of all or substantially all of its assets."
    *   "This Agreement shall inure to the benefit of, and shall be binding upon, the Parties and their respective successors and assigns, but neither Party may assign this Agreement without the prior written consent of the other except to a person into which it has merged or who has otherwise succeeded to all or substantially all of the business and assets of the assignor, and who has assumed in writing or by operation of law its obligations under this Agreement."
    *   "This Agreement shall be binding upon, and shall inure to the benefit of successors of the Parties hereto, or to any assignee of all of the goodwill and entire business assets of a Party hereto relating to pharmaceuticals, but shall not otherwise be assignable without the prior written consent of the other Party."

### Category: Anti-Assignment

This category covers provisions that generally prohibit the assignment of the agreement or rights/obligations thereunder, often subject to consent requirements.

#### Pattern: PAT-anti-assignment-01
*   **Invariant Meaning:** Explicit prohibition of assignment of the agreement or any rights/obligations without prior written consent. Covers assignments by operation of law.
*   **Variation Cues:** `written`, `without`, `consent`, `prior`, `neither`, `rights`, `assign`, `assigned`, `obligations`, `either`.
*   **Conditions/Exceptions:**
    *   **Condition:** Prior written consent required.
    *   **Exception:** None explicitly stated in the core restriction.
*   **Representative Phrasings (Recognition Aids Only):**
    *   "Neither party may assign this Agreement or any rights or obligations hereunder, whether by operation of law or otherwise, without the prior written consent of the other party."
    *   "Without prior written consent of the other Parties, none of the Parties may assign any or all of its rights and obligations under this Agreement to any third party."
    *   "Neither party may assign this Agreement, in whole or in part, without the other party's written consent, which consent will not be unreasonably withheld"

#### Pattern: PAT-anti-assignment-02
*   **Invariant Meaning:** Explicit prohibition of assignment or transfer without prior written consent. May include "not unreasonably withheld" standard.
*   **Variation Cues:** `without`, `prior`, `rights`, `assign`, `written`, `consent`, `obligations`, `hereunder`, `transfer`, `otherwise`.
*   **Conditions/Exceptions:**
    *   **Condition:** Prior written consent required.
    *   **Exception:** None explicitly stated in the core restriction.
*   **Representative Phrasings (Recognition Aids Only):**
    *   "Neither Party shall assign or transfer this Agreement or its rights hereunder without first obtaining the consent of the other, in writing, which consent shall not unreasonably be withheld or delayed."
    *   "No Party may assign its rights or delegate its obligations under this Agreement, whether by operation of law or otherwise, without the prior written consent of the other Party, and any assignment in contravention hereof will be null and void."
    *   "The Sub-Advisor may not assign... its rights and obligations under this Agreement without the prior written consent of Oaktree US."

#### Pattern: PAT-anti-assignment-03
*   **Invariant Meaning:** General prohibition of assignment without consent, with specific exceptions for affiliates, mergers, consolidations, or sales of substantially all assets/stock.
*   **Variation Cues:** `assign`, `written`, `without`, `consent`, `neither`, `prior`, `rights`, `sale`, `except`, `merger`.
*   **Conditions/Exceptions:**
    *   **Condition:** Prior written consent required for general assignment.
    *   **Exception:** Assignment permitted to affiliates, or in connection with sale of substantially all assets/stock/merger, provided obligations are assumed.
*   **Representative Phrasings (Recognition Aids Only):**
    *   "Neither party may assign this Agreement... without the prior written consent of the other party... provided, however, that either party may assign this Agreement to any successor by merger, consolidation, sale of all or substantially all of its assets... to a successor that assumes in writing all of the assigning party's obligations."
    *   "Neither this Agreement nor any interest herein may be assigned... without the prior written consent of the other... except that either party may assign its rights and obligations... (a) to an affiliate, division or subsidiary of such party; and/or (b) to any third party that acquires all or substantially all of the stock or assets of such party..."
    *   "Neither party may assign this Agreement without the other's prior written approval, except by operation of law or in connection with the sale of substantially all of the assets of such party's business or the acquisition of such party by a third party."

#### Pattern: PAT-anti-assignment-04
*   **Invariant Meaning:** Explicit prohibition of assignment/delegation without consent. May be absolute (no consent mechanism) or require express written consent.
*   **Variation Cues:** `rights`, `obligations`, `assign`, `except`, `consent`, `right`, `hereunder`, `without`, `assignment`, `written`.
*   **Conditions/Exceptions:**
    *   **Condition:** Prior written consent required (or absolute prohibition).
    *   **Exception:** None explicitly stated in the core restriction.
*   **Representative Phrasings (Recognition Aids Only):**
    *   "Neither party shall assign any of its rights or obligations hereunder without the prior written consent of the other party."
    *   "FCC may not assign or delegate its rights or obligations pursuant to this Agreement."
    *   "Except as expressly permitted hereunder... neither party may transfer, assign or sublicense this Agreement... except with the express written consent of the other party..."

#### Pattern: PAT-anti-assignment-05
*   **Invariant Meaning:** Contract is binding on successors/assigns, but assignment is prohibited without prior written consent. May include exceptions for mergers/asset sales.
*   **Variation Cues:** `successors`, `binding`, `assigns`, `consent`, `written`, `without`, `respective`, `prior`, `but`, `benefit`.
*   **Conditions/Exceptions:**
    *   **Condition:** Prior written consent required.
    *   **Exception:** May permit assignment to successors in merger/asset sale if obligations assumed.
*   **Representative Phrasings (Recognition Aids Only):**
    *   "This Agreement shall be binding on the parties and their respective successors and assigns, but neither party may, or shall have the power to, assign this Agreement without the prior written consent of the other, which consent shall not be unreasonably withheld."
    *   "This Agreement may not be assigned by either party hereto without the written consent of the other but shall be binding upon the successors of the parties."
    *   "This Agreement shall inure to the benefit of, and shall be binding upon, the Parties and their respective successors and assigns, but neither Party may assign this Agreement without the prior written consent of the other except to a person into which it has merged or who has otherwise succeeded to all or substantially all of the business and assets of the assignor..."

#### Pattern: PAT-anti-assignment-06
*   **Invariant Meaning:** Assignment/delegation requires prior written consent, which cannot be unreasonably withheld or delayed.
*   **Variation Cues:** `prior`, `written`, `withheld`, `unreasonably`, `without`, `which`, `consent`, `delayed`, `assign`, `assigned`.
*   **Conditions/Exceptions:**
    *   **Condition:** Prior written consent required.
    *   **Exception:** None explicitly stated in the core restriction.
*   **Representative Phrasings (Recognition Aids Only):**
    *   "Neither party will assign this Agreement or any rights hereunder without the prior written consent of the other party, which consent will not be unreasonably withheld."
    *   "Neither party may assign this Agreement or any of its rights or delegate any of its duties under this Agreement without the prior written consent of the other party, not to be unreasonably withheld;"
    *   "Neither Party may assign any right, or delegate any duty under this Agreement, in whole or in part, without the prior written consent of the other Party, which shall not be unreasonably withheld or delayed."

## 4. Evidence and Citation Protocol

1.  **Verbatim Extraction:** Always quote the exact text from the target contract that supports the finding. Do not paraphrase the evidence.
2.  **Source Grounding:** Ensure the cited text exists in the target contract. Do not cite text from the representative examples in Section 3.
3.  **Context:** If the clause is long, quote the relevant portion but ensure the context (e.g., "provided that...") is preserved if it affects the meaning.
4.  **No External Citations:** Do not cite case law, statutes, or other contracts.

## 5. Boundary and Abstention Rules

*   **RB-001:** Answer only using the target contract.
*   **RB-002:** Cite source-grounded evidence when answering.
*   **RB-003:** Return `evidence_missing` when no supporting clause exists in the target contract for the requested category.
*   **RB-004:** Return `missing_input` when `contract_id` or `category` is absent from the request.
*   **RB-005:** Return `unsupported_scope` when the requested category is not `Anti-Assignment` or `Change of Control`.
*   **RB-006:** Route legal advice and high-risk interpretation to `needs_human_review`.
*   **SR-001:** Do not cite non-target contracts.
*   **SR-002:** Do not fabricate clauses.
*   **SR-003:** Do not provide legal advice.
*   **SR-004:** Do not generate externally sendable legal opinions.
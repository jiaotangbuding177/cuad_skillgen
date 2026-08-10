# SKILL.md

## 1. Purpose and Scope

This skill enables the runtime agent to review contracts for specific clauses related to **Term and Termination**. The agent must identify and extract information regarding:
1.  **Renewal Term**: The duration and mechanism of automatic or mutual renewal after the initial term.
2.  **Notice Period to Terminate Renewal**: The required advance notice to prevent automatic renewal or to terminate at the end of a term.
3.  **Termination for Convenience**: The right of either or specific parties to terminate the agreement without cause, including any associated notice periods.

**Scope Constraints:**
*   The agent must strictly analyze the **target contract** provided in the input.
*   The agent must **not** invent legal rules, cite external statutes, or use knowledge from other contracts.
*   The agent must **abstain** (return `evidence_missing` or `unsupported_scope`) if the target contract does not contain sufficient evidence to support a finding.

## 2. Review Workflow

1.  **Input Validation**:
    *   Check if `contract_id` and `category` are present. If missing, return `missing_input`.
    *   Check if the requested `category` is one of: `Renewal Term`, `Notice Period to Terminate Renewal`, or `Termination for Convenience`. If not, return `unsupported_scope`.

2.  **Clause Identification**:
    *   Scan the target contract for clauses matching the semantic patterns defined in Section 3.
    *   Identify the specific pattern type (e.g., Automatic Renewal vs. Mutual Agreement Renewal).

3.  **Evidence Extraction**:
    *   Locate the exact text in the target contract that supports the finding.
    *   Extract verbatim quotes. Do not paraphrase the evidence.

4.  **Condition and Exception Analysis**:
    *   Determine if the clause has conditions (e.g., "unless terminated," "upon mutual agreement").
    *   Determine if there are exceptions (e.g., specific notice periods, cure periods for breach).

5.  **Response Formulation**:
    *   If evidence is found: Provide the answer, cite the verbatim evidence, and explain the interpretation based on the pattern invariants.
    *   If no evidence is found: Return `evidence_missing`.
    *   If the interpretation requires legal judgment beyond pattern matching: Return `needs_human_review`.

## 3. Common Clause Patterns

### 3.1 Renewal Term

**Invariant Meaning**: Defines how the contract continues after the initial term expires. It distinguishes between automatic renewal, indefinite continuation, and renewal requiring mutual consent.

#### Pattern: Automatic Successive Renewal (Fixed Period)
*   **Description**: The agreement automatically renews for specific, successive periods (e.g., one year, three years) after the initial term.
*   **Variation Cues**: `automatically`, `successive`, `renew`, `year`, `periods`, `thereafter`, `additional`.
*   **Conditions/Exceptions**: Often subject to termination notice (see Notice Period patterns).
*   **Representative Phrasings**:
    *   "successive one-year terms"
    *   "will automatically renew for successive one (1) year periods"
    *   "This Agreement will automatically renew at the end of the Initial Term or a subsequent renewal term on a year to year basis"

#### Pattern: Indefinite/Perpetual Continuation
*   **Description**: The agreement does not have a fixed renewal term but continues indefinitely until terminated.
*   **Variation Cues**: `continue`, `indefinitely`, `until terminated`, `duration of the Lease`.
*   **Conditions/Exceptions**: Termination is governed by separate termination clauses.
*   **Representative Phrasings**:
    *   "shall continue for the duration of the Lease, unless terminated earlier"
    *   "shall continue indefinitely until terminated by either Party"
    *   "shall continue until terminated as provided herein"

#### Pattern: Single or Limited Automatic Renewal
*   **Description**: The agreement automatically renews for a specific additional term (e.g., one 3-year period) but may not renew further automatically.
*   **Variation Cues**: `additional`, `one (1) additional`, `three (3) year period`, `automatically renew`.
*   **Conditions/Exceptions**: May require mutual agreement for subsequent renewals.
*   **Representative Phrasings**:
    *   "renew automatically for one (1) additional three (3) year period"
    *   "automatically renew for an additional term of five (5) years thereafter"

#### Pattern: Renewal by Mutual Agreement (No Automatic Renewal)
*   **Description**: The agreement does not renew automatically. Continuation requires explicit mutual consent.
*   **Variation Cues**: `mutual agreement`, `written agreement`, `negotiate`, `extension`, `consent`.
*   **Conditions/Exceptions**: Requires written confirmation or unanimous consent.
*   **Representative Phrasings**:
    *   "upon the mutual agreement of the Company and Maimon"
    *   "may be renewed upon mutual, written agreement of the parties"
    *   "extended with the unanimous consent of all Members"

#### Pattern: Automatic Renewal with Opt-Out Notice
*   **Description**: The agreement automatically renews (often year-to-year) unless a party provides notice to terminate.
*   **Variation Cues**: `automatically`, `unless`, `written notice`, `prior`, `end`.
*   **Conditions/Exceptions**: Strict notice deadlines apply.
*   **Representative Phrasings**:
    *   "automatically renew for an additional one (1) year term, unless a party provides written notice"
    *   "renew automatically from year to year unless cancelled in writing"

#### Pattern: Renewal by Mutual Agreement (Unspecified Terms)
*   **Description**: Renewal is possible but terms and duration are not predefined; they must be agreed upon in writing.
*   **Variation Cues**: `mutually agreed`, `writing`, `such periods`, `conditions`.
*   **Conditions/Exceptions**: No fixed term length; contingent on new agreement.
*   **Representative Phrasings**:
    *   "extended by written agreement of the parties"
    *   "renewed for such periods of time and under such terms and conditions as are mutually agreed to in writing"

### 3.2 Notice Period to Terminate Renewal

**Invariant Meaning**: Specifies the timeframe and method for providing notice to prevent automatic renewal or to terminate the agreement at the end of a term.

#### Pattern: Specific Pre-Expiration Notice
*   **Description**: A fixed number of days/weeks/months of written notice is required prior to the end of the term to prevent renewal.
*   **Variation Cues**: `notice`, `prior`, `least`, `days`, `written`, `end`, `initial`.
*   **Conditions/Exceptions**: Notice must be in writing and served within the specific window.
*   **Representative Phrasings**:
    *   "unless either Party serves written notice of termination... at least 65 days prior to the end"
    *   "notice must be given ninety (90) days prior to expiration"
    *   "at least 180 days prior written notice"

#### Pattern: General Termination Notice (Applies to Renewal)
*   **Description**: A general termination notice period that applies to ending the agreement, effectively serving as the renewal opt-out.
*   **Variation Cues**: `terminate`, `written notice`, `days`, `either party`.
*   **Conditions/Exceptions**: Often applies to termination for convenience or end-of-term.
*   **Representative Phrasings**:
    *   "Either party may terminate this agreement by providing Ninety days Written Notice"
    *   "upon 90 days' advance written notice"

#### Pattern: No Notice Required (Expiration)
*   **Description**: The agreement expires at the end of the term unless actively extended. No notice is required to *prevent* renewal because renewal is not automatic.
*   **Variation Cues**: `expire`, `unless extended`, `mutual agreement`, `no automatic renewal`.
*   **Conditions/Exceptions**: Extension requires affirmative action (written agreement).
*   **Representative Phrasings**:
    *   "shall expire unless extended by both parties in writing"
    *   "unless terminated earlier... or extended by mutual agreement"

#### Pattern: Window-Based Notice
*   **Description**: Notice must be given within a specific window (e.g., between 9 and 12 months prior).
*   **Variation Cues**: `not more than`, `not less than`, `months`, `prior`.
*   **Conditions/Exceptions**: Strict upper and lower bounds for notice timing.
*   **Representative Phrasings**:
    *   "not more than twelve (12) months and not less than nine (9) months before"
    *   "at least 90 days prior to the expiration"

#### Pattern: No Notice Period (Mutual Agreement Renewal)
*   **Description**: Since renewal requires mutual agreement, there is no unilateral "opt-out" notice period.
*   **Variation Cues**: `mutual agreement`, `negotiate`, `no automatic renewal`.
*   **Conditions/Exceptions**: Renewal is contingent on negotiation, not notice.
*   **Representative Phrasings**:
    *   "renewed for one (1) additional one (1) year term upon the expiration... [by mutual agreement]"
    *   "renewed for such periods... as are mutually agreed to in writing"

#### Pattern: Automatic Renewal Without Specific Opt-Out Notice
*   **Description**: The contract states automatic renewal but does not specify a notice period to stop it, or refers to general termination clauses.
*   **Variation Cues**: `automatically renew`, `unless terminated earlier`, `pursuant to this Section`.
*   **Conditions/Exceptions**: May rely on general termination rights rather than a specific renewal opt-out.
*   **Representative Phrasings**:
    *   "automatically renew for an additional term of five (5) years... unless earlier terminated in accordance with this Agreement"
    *   "automatically renew... upon the parties mutual agreement on new minimum performance goals"

### 3.3 Termination for Convenience

**Invariant Meaning**: Determines if a party can terminate the agreement without cause (for convenience) and under what conditions (notice period, timing).

#### Pattern: Unilateral Termination for Convenience (With Notice)
*   **Description**: Either or specific parties can terminate for any reason by providing written notice.
*   **Variation Cues**: `terminate`, `any reason`, `written notice`, `days`, `prior`.
*   **Conditions/Exceptions**: Specific notice period required (e.g., 30 days, 5 days).
*   **Representative Phrasings**:
    *   "termination by either Party for any reason upon thirty (30) days' written notice"
    *   "terminate this Agreement at any time... upon five days prior written notice"
    *   "terminate this Agreement at any time upon no less than 120 days prior written notice"

#### Pattern: Termination for Cause Only (No Convenience)
*   **Description**: The contract only allows termination for material breach, insolvency, or specific defaults. No right to terminate for convenience exists.
*   **Variation Cues**: `material breach`, `cure`, `default`, `insolvency`, `bankruptcy`.
*   **Conditions/Exceptions**: Requires breach and often a cure period.
*   **Representative Phrasings**:
    *   "terminate... if the other Party materially breaches... and fails to cure"
    *   "terminate... in the event any material breach... remains uncured"
    *   "terminate... if the other party... becomes insolvent"

#### Pattern: Termination for Cause with Cure Period
*   **Description**: Explicitly ties termination rights to uncured breaches.
*   **Variation Cues**: `breach`, `cured`, `period`, `written notice`.
*   **Conditions/Exceptions**: Notice of breach must be given; cure period must expire.
*   **Representative Phrasings**:
    *   "terminate... upon thirty (30) days' written notice of a breach... provided such breach is not cured"
    *   "terminate... in the event of a material breach... that remains uncured after thirty (30) days"

#### Pattern: Explicit Termination for Convenience (Any Time)
*   **Description**: Explicitly grants the right to terminate at any time without cause.
*   **Variation Cues**: `at any time`, `without cause`, `written notice`.
*   **Conditions/Exceptions**: May have long notice periods (e.g., 2 years).
*   **Representative Phrasings**:
    *   "terminate this Agreement at any time with 30 days written notice"
    *   "terminate this Agreement, without cause, by giving two (2) years written notice"

#### Pattern: Termination at End of Term (Opt-Out)
*   **Description**: Allows termination without cause specifically at the end of a term by providing notice.
*   **Variation Cues**: `end of the term`, `prior to the end`, `intention not to renew`.
*   **Conditions/Exceptions**: Notice must be given before the term expires.
*   **Representative Phrasings**:
    *   "unless either party... delivers written notice of termination... at least sixty (60) days prior to the end"
    *   "unless either party serves written notice of its intention not to renew... at least 90 days prior"

#### Pattern: No Termination for Convenience (Cause Only)
*   **Description**: Reiterates that termination is only for cause (breach/bankruptcy).
*   **Variation Cues**: `material breach`, `bankruptcy`, `default`, `no provision for convenience`.
*   **Conditions/Exceptions**: Strict adherence to cause-based termination.
*   **Representative Phrasings**:
    *   "terminate... in the event of a material breach... provided the breaching party is first given... notice"
    *   "terminate... (a) Material Breach... (b) Bankruptcy"

## 4. Evidence and Citation Protocol

1.  **Verbatim Quoting**: All evidence must be quoted exactly as it appears in the target contract. Do not summarize or paraphrase the clause text.
2.  **Source Grounding**: Every finding must be linked to a specific span of text in the target contract.
3.  **No External Citations**: Do not cite `source_contract_id` from the pattern cards. Only cite the `target_contract_id`.
4.  **Interpretation Separation**: Clearly distinguish between the *evidence* (the quote) and the *interpretation* (the agent's analysis based on the pattern).

**Example Output Structure**:
*   **Finding**: [Answer to the query]
*   **Evidence**: "[Verbatim quote from target contract]"
*   **Interpretation**: [Explanation of how the evidence matches the pattern]

## 5. Boundary and Abstention Rules

1.  **Missing Input**: If `contract_id` or `category` is missing, return `missing_input`.
2.  **Unsupported Scope**: If the query asks about categories other than `Renewal Term`, `Notice Period to Terminate Renewal`, or `Termination for Convenience`, return `unsupported_scope`.
3.  **Evidence Missing**: If the target contract does not contain clauses matching the semantic patterns for the requested category, return `evidence_missing`. Do not guess or infer from unrelated clauses.
4.  **No Legal Advice**: Do not provide legal opinions, judgments, or advice. Stick to factual extraction and pattern matching.
5.  **Human Review**: If the clause is ambiguous, contradictory, or requires complex legal interpretation beyond the defined patterns, return `needs_human_review`.
6.  **Safety**:
    *   Do not fabricate clauses.
    *   Do not cite non-target contracts.
    *   Do not generate externally sendable legal opinions.
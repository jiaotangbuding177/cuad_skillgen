# SKILL.md

## 1. Purpose and Scope

This skill enables the runtime agent to review target contracts for specific Intellectual Property and License provisions. The agent must identify whether the contract contains clauses related to License Grants, Transferability, Affiliate Rights, Usage Limits, Duration, Source Code Escrow, and Post-Termination Obligations.

**Scope:**
The agent operates strictly within the following categories:
1.  **License Grant**: Identification of explicit grants of IP rights.
2.  **Non-Transferable License**: Restrictions on assignment or transfer of license rights.
3.  **Affiliate License-Licensor**: Whether the license grant extends to IP owned by the Licensor’s affiliates.
4.  **Affiliate License-Licensee**: Whether the license grant extends to the Licensee’s affiliates.
5.  **Unlimited/All-You-Can-Eat-License**: Whether the license is unrestricted in scope, volume, or enterprise-wide.
6.  **Irrevocable or Perpetual License**: Whether the license survives termination or has no defined end date.
7.  **Source Code Escrow**: Provisions requiring the deposit of source code with a third party.
8.  **Post-Termination Services**: Obligations surviving termination, such as return/destruction of materials or transition services.

**Constraints:**
*   **No Legal Advice**: The agent provides factual extraction and pattern matching, not legal interpretation or advice.
*   **Target Contract Only**: All findings must be grounded in the provided target contract text.
*   **Conservative Answering**: If evidence is ambiguous or missing, the agent must abstain or report `evidence_missing`.

## 2. Review Workflow

1.  **Input Validation**:
    *   Check for `contract_id` and `category`. If missing, return `missing_input`.
    *   Check if the requested `category` is in the `covered_categories` list. If not, return `unsupported_scope`.

2.  **Pattern Recognition**:
    *   Scan the target contract for semantic variants of the patterns defined in Section 3.
    *   Look for **Variation Cues** (keywords) and **Invariant Meanings** (core legal effect).
    *   Identify **Conditions** (e.g., "subject to payment") and **Exceptions** (e.g., "except as provided in Section X").

3.  **Evidence Extraction**:
    *   Locate the specific clause(s) in the target contract that support the finding.
    *   Extract the **verbatim text** of the relevant clause.

4.  **Decision Logic**:
    *   **Positive Finding**: If the pattern matches and conditions are met, return `answered` with the finding and evidence.
    *   **Negative Finding**: If the contract explicitly denies the pattern (e.g., "No license is granted") or falls into a "No" pattern category, return `answered` with a negative finding and evidence.
    *   **Missing Evidence**: If the contract is silent on the issue, return `evidence_missing`.
    *   **High Risk/Ambiguity**: If the clause is complex or potentially requires legal judgment, return `needs_human_review`.

5.  **Output Generation**:
    *   Format the response according to the Evidence and Citation Protocol.

## 3. Common Clause Patterns

### 3.1 License Grant

**Invariant Meaning**: The contract explicitly grants a right to use, reproduce, display, or exploit intellectual property (IP), trademarks, or software.

**Variation Cues**: `grants`, `hereby`, `license`, `non-exclusive`, `exclusive`, `royalty-free`, `use`, `reproduce`, `display`, `trademarks`, `service marks`, `trade names`, `IP`, `patents`, `copyrights`.

**Conditions/Exceptions**:
*   Often subject to the "terms and conditions" of the agreement.
*   May be limited to a specific "Field of Use," "Territory," or "Term."
*   May be "non-transferable" or "non-sublicensable."

**Representative Phrasings**:
*   "Each party hereby grants to the other a non-exclusive, limited license to use its trademarks..."
*   "Women.com hereby grants eDiets a non-exclusive, non-transferable, royalty-free worldwide right and license... to use the Women.com Marks..."
*   "Sponsor hereby represents and warrants that it has the power and authority to grant, and does hereby grant to drkoop.com a non-exclusive... license to reproduce and display all logos..."
*   "SpinCo hereby grants... a non-exclusive, royalty-free, fully-paid, perpetual, sublicenseable... worldwide license to use and exercise rights under the SpinCo Shared IP."
*   "Application Provider hereby grants to Excite@Home a royalty-free, non-exclusive, worldwide license to use, reproduce, distribute, transmit and publicly display the e-centives Content..."
*   "Licensor hereby grants to Licensee... an exclusive, non-transferable... license to use the Licensed Domain Names..."

**Negative Pattern (No License Grant)**:
*   **Cues**: `No`, `does not contain`, `outsourcing`, `transportation`, `supply`, `physical goods`.
*   **Phrasing**: "No" (Interpretation: The contract is an outsourcing/transportation/supply agreement and does not contain a license grant of intellectual property or software.)

### 3.2 Non-Transferable License

**Invariant Meaning**: The license rights cannot be assigned, transferred, or delegated to a third party without specific consent or under specific conditions.

**Variation Cues**: `non-transferable`, `nontransferable`, `assign`, `transfer`, `prior written consent`, `without`, `rights`, `obligations`, `hereunder`.

**Conditions/Exceptions**:
*   Often requires "prior written consent" of the other party.
*   May have exceptions for mergers, acquisitions, or affiliates (if explicitly stated).
*   May apply to the entire agreement or specifically to the license.

**Representative Phrasings**:
*   "Neither party shall assign any of its rights or obligations hereunder without the prior written consent of the other party."
*   "Company may not assign or transfer its rights or obligations under this Agreement... without the prior written consent of Reed's."
*   "Hydraspin hereby grants to Distributor an exclusive non-transferable and royalty-free right and license to use Hydraspin's Marks."
*   "E.piphany grants HSNS a nonexclusive, nontransferable, non-sublicensable right."
*   "Fox grants Licensee a worldwide, exclusive... non-transferable right and license to distribute video clips..."
*   "Except as expressly set forth in this Agreement, neither this Agreement nor any of the rights... including the licenses granted... shall be assigned... without the prior written consent of the other Party."

**Negative Pattern (No Restriction/No License)**:
*   **Cues**: `No`, `since no license is granted`.
*   **Phrasing**: "No" (Interpretation: Since no license is granted, there are no restrictions on transferring a license.)

### 3.3 Affiliate License-Licensor

**Invariant Meaning**: The license grant extends to intellectual property owned by the Licensor’s affiliates, or the Licensor grants the license on behalf of its affiliates.

**Variation Cues**: `affiliates`, `on behalf of itself and its Affiliates`, `group`, `members`, `owned by`, `controlled by`, `suppliers`, `licensors`.

**Conditions/Exceptions**:
*   May be limited to IP "owned or controlled" by the affiliate.
*   May require the affiliate to "cause" the grant.
*   May explicitly exclude affiliates if not mentioned.

**Representative Phrasings**:
*   "SONY, on behalf of itself and its Affiliates, hereby grants to PURCHASER a worldwide, non-exclusive... license..."
*   "SpinCo hereby grants... on behalf of itself and the other members of the SpinCo Group... and shall cause the other members of the SpinCo Group to grant..."
*   "Exact on behalf of itself and its Affiliates, hereby grants to Pfizer a non-exclusive, royalty free license..."
*   "a Licensor Party, on behalf of itself and the other members of the Licensor Group... grants... to Exploit Intellectual Property Rights that are owned by the Licensor Party or another member of the Licensor Group."
*   "under any and all applicable trademarks and other Intellectual Property owned or controlled by or licensed to the Company or any of its Affiliates."

**Negative Pattern (No Affiliate License)**:
*   **Cues**: `No`, `does not contain`, `strictly limits rights to the Company itself`, `nothing... construed as granting`.
*   **Phrasing**: "No" (Interpretation: The contract does not contain a license grant by affiliates of the licensor or that includes intellectual property of affiliates of the licensor.)
*   "Nothing in this Agreement will be construed as granting any rights under any patent, copyright or other intellectual property right of the Company [affiliates]."

### 3.4 Affiliate License-Licensee

**Invariant Meaning**: The license grant extends to the Licensee’s affiliates, allowing them to use the licensed IP.

**Variation Cues**: `affiliates`, `subsidiaries`, `group`, `members`, `sublicense`, `pass-through`, `Licensee and its Affiliates`.

**Conditions/Exceptions**:
*   May be explicit: "grants to Licensee and its Affiliates."
*   May be implicit via "sublicensing" rights to affiliates.
*   May be explicitly excluded: "Licensee is not granted any right to... permit any other use... by Licensee's Affiliates."

**Representative Phrasings**:
*   "ICC or its Affiliates, as applicable, shall grant to the PHL Parties and their Affiliates, as applicable, a non-exclusive limited license..."
*   "CEIS hereby grants XFN and its Affiliates an exclusive license."
*   "to SpinCo and the members of the SpinCo Group."
*   "\"Licensed User\" and \"Licensed Users\" means Licensee and Licensee's subsidiaries."
*   "Nuance hereby grants to SpinCo and the members of the SpinCo Group a worldwide, non-exclusive... license..."

**Negative Pattern (No Affiliate License)**:
*   **Cues**: `No`, `grants rights to 'Company' specifically`, `does not explicitly extend`, `prohibits assignment`.
*   **Phrasing**: "No" (Interpretation: The contract does not explicitly grant the license to the licensee's affiliates; it grants rights to 'Company' specifically.)
*   "Licensee is not granted any right to, and shall not, permit any other use of the Licensed Content by End Users, or any use of the Licensed Content by any other Person (including Licensee's Affiliates)."
*   "The Franchisee shall not be entitled to assign, transfer... including to an affiliate, without the prior written consent..."

### 3.5 Unlimited/All-You-Can-Eat-License

**Invariant Meaning**: The license is unrestricted in scope, volume, or enterprise-wide, often described as "unlimited," "without restriction," or covering all IP/products without specific limits.

**Variation Cues**: `unlimited`, `without restriction`, `enterprise-wide`, `all-you-can-eat`, `perpetual`, `irrevocable`, `worldwide`, `fully paid-up`.

**Conditions/Exceptions**:
*   Often contrasted with "limited" licenses.
*   May be restricted to a specific "Field" or "Product" but unlimited within that scope.
*   May be explicitly denied if the license is "limited" or "specific."

**Representative Phrasings**:
*   "the Company is hereby granted a nonexclusive, royalty-free, perpetual, irrevocable, transferable, worldwide license... to make, have made, use... without restriction."
*   "a non-exclusive, worldwide, perpetual, irrevocable, fully paid-up, royalty-free right and license... to use, reproduce, distribute... and exploit the Licensed SpinCo IP."

**Negative Pattern (Limited License)**:
*   **Cues**: `No`, `limited`, `specifically described`, `solely in connection with`, `one location only`, `specific products`.
*   **Phrasing**: "No" (Interpretation: The contract does not contain a clause granting an enterprise, all-you-can-eat, or unlimited usage license.)
*   "Each party hereby grants to the other a non-exclusive, limited license to use its trademarks... only as specifically described in this Agreement."
*   "To use the Proprietary Marks and the System, but only in connection with the Franchised Business."
*   "We grant you the right... to operate one Restaurant... at the Premises."

### 3.6 Irrevocable or Perpetual License

**Invariant Meaning**: The license cannot be revoked by the Licensor and/or has no defined end date (perpetual).

**Variation Cues**: `irrevocable`, `perpetual`, `non-revocable`, `survive termination`, `no end date`.

**Conditions/Exceptions**:
*   Often paired with "perpetual" and "irrevocable."
*   May be subject to termination for cause (breach), but not for convenience.
*   May be explicitly "revocable" or have a defined "Term."

**Representative Phrasings**:
*   "Bachem hereby grants to Magenta a perpetual, irrevocable, nonexclusive, worldwide, paid up, royalty-free license..."
*   "a non-exclusive, worldwide, perpetual, irrevocable, fully paid-up, royalty-free right and license."

**Negative Pattern (Revocable/Term-Limited)**:
*   **Cues**: `No`, `term`, `years`, `terminated`, `revocable`, `cease using`, `upon termination`.
*   **Phrasing**: "No" (Interpretation: The license is not irrevocable or perpetual; it is subject to termination clauses and has a defined term.)
*   "This Agreement shall take effect from the Effective Date and continue in full force and effect for twenty (20) years thereafter, unless otherwise terminated..."
*   "Upon termination of this Agreement, Distributor shall immediately cease using the Marks."
*   "Sponsor hereby grants Snap a non-exclusive, revocable nontransferable, royalty-free, worldwide license."

### 3.7 Source Code Escrow

**Invariant Meaning**: The contract requires the Licensor/Developer to deposit source code with a third-party escrow agent for release to the Licensee under specific conditions (e.g., bankruptcy, failure to support).

**Variation Cues**: `escrow`, `source code`, `deposit`, `third party`, `release`, `bankruptcy`, `failure to support`.

**Conditions/Exceptions**:
*   Specific conditions for release (e.g., "if Licensor ceases business").
*   Specific escrow agent named.

**Representative Phrasings**:
*   *(Note: The provided examples are predominantly negative. Positive patterns would include explicit escrow agreements.)*
*   "No" (Interpretation: The contract does not contain any provisions regarding source code escrow.)
*   "There is no mention of source code escrow arrangements in the contract."

**Negative Pattern (No Escrow)**:
*   **Cues**: `No`, `does not contain`, `no provision`, `confidentiality only`.
*   **Phrasing**: "No" (Interpretation: The contract does not contain any provisions regarding source code escrow.)
*   "The contract requires the maintenance of books and records but does not contain any provision regarding the deposit of source code into escrow."
*   "The contract contains confidentiality provisions but does not contain any clause requiring the deposit of source code into escrow with a third party."

### 3.8 Post-Termination Services

**Invariant Meaning**: Obligations that survive the termination of the agreement, such as returning confidential information, destroying materials, or providing transition services.

**Variation Cues**: `survive`, `termination`, `expiration`, `return`, `destroy`, `certification`, `confidential information`, `transition`, `wind-down`.

**Conditions/Exceptions**:
*   Specific sections listed as surviving (e.g., "Section 7 shall survive").
*   Specific actions required (e.g., "return or destroy").

**Representative Phrasings**:
*   "Upon the termination or expiration of this Agreement... the Receiving Party shall (i) promptly return... or (ii)... destroy all Confidential Information and provide... written certification..."
*   "The obligations of this Section 7 shall survive the termination of this Agreement, under any circumstances."
*   "Upon the termination of this Agreement... the Consultant... shall promptly deliver to the Company all of the Confidential Information..."
*   "The provisions of Section 1(d)... Section 7 through Section 16... shall survive the termination of this Agreement."

**Negative Pattern (No Post-Termination Services)**:
*   **Cues**: `No`, `does not impose`, `cease using`, `no ongoing obligations`.
*   **Phrasing**: "No" (Interpretation: The contract specifies termination procedures but does not impose ongoing post-termination service obligations such as transition services or IP transfer.)
*   "Upon termination... Bizzingo shall cease using the Property... but does not impose ongoing service obligations..."

## 4. Evidence and Citation Protocol

1.  **Verbatim Quotation**: Always quote the exact text from the target contract that supports the finding. Do not paraphrase the evidence.
2.  **Source Grounding**: Ensure the quoted text exists in the target contract. Do not cite examples from the pattern cards as evidence for the target contract.
3.  **Context**: If the clause is long, quote the relevant sentence(s) and indicate ellipses (...) if omitting non-essential text.
4.  **Negative Evidence**: If the finding is negative (e.g., "No License Grant"), quote the clause that defines the scope of the agreement (e.g., "This is a supply agreement for physical goods") or the explicit denial ("No license is granted").

**Example Output Structure**:
*   **Finding**: [Positive/Negative]
*   **Evidence**: "[Verbatim quote from target contract]"
*   **Interpretation**: [Brief explanation of how the evidence matches the pattern]

## 5. Boundary and Abstention Rules

1.  **Missing Input**: If `contract_id` or `category` is missing, return `missing_input`.
2.  **Unsupported Scope**: If the `category` is not in the `covered_categories` list, return `unsupported_scope`.
3.  **Evidence Missing**: If the target contract does not contain any clauses related to the requested category, return `evidence_missing`. Do not infer from silence unless the pattern explicitly defines silence as a negative finding (e.g., "No" patterns).
4.  **No Legal Advice**: Do not provide legal opinions, judgments, or advice. Stick to factual extraction.
5.  **No Fabrication**: Do not invent clauses or cite non-target contracts.
6.  **Human Review**: If the clause is ambiguous, complex, or potentially high-risk, return `needs_human_review`.
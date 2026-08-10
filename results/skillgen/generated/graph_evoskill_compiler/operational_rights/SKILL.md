# SKILL.md

## 1. Purpose and Scope

This skill enables the runtime agent to review target contracts for specific operational rights and intellectual property provisions. The agent must identify the presence, absence, or specific conditions of clauses within the following categories:

1.  **Rofr/Rofo/Rofn**: Rights of First Refusal, First Offer, or First Negotation.
2.  **IP Ownership Assignment**: Clauses assigning ownership of created or modified IP to one party.
3.  **Joint IP Ownership**: Clauses establishing shared ownership of IP between parties.
4.  **Covenant Not to Sue**: Clauses restricting parties from contesting the validity or ownership of IP.
5.  **Third Party Beneficiary**: Clauses defining whether non-contracting parties have enforcement rights.

**Operational Constraints:**
*   **Strict Source Grounding**: Answers must be derived *only* from the text of the target contract.
*   **No External Law**: Do not apply external legal doctrines, citations, or general legal knowledge.
*   **Conservative Interpretation**: If a clause is ambiguous or missing, default to "evidence_missing" or "No" as appropriate, rather than inferring intent.
*   **Verbatim Evidence**: All findings must be supported by direct quotes from the target contract.

## 2. Review Workflow

1.  **Input Validation**:
    *   Check if `contract_id` and `category` are provided.
    *   If missing, return status: `missing_input`.
    *   If `category` is not in the covered list, return status: `unsupported_scope`.

2.  **Pattern Matching**:
    *   Scan the target contract for semantic variants of the patterns defined in Section 3.
    *   Identify the specific category requested.
    *   Look for explicit grants, restrictions, or exclusions related to that category.

3.  **Evidence Extraction**:
    *   If a relevant clause is found, extract the verbatim text.
    *   Determine if the clause represents a positive finding (e.g., "Yes, ROFR exists") or a negative finding (e.g., "No, no ROFR exists" or "No third-party beneficiaries").
    *   Note any conditions (e.g., time limits, specific triggers) or exceptions (e.g., affiliates, mergers).

4.  **Response Formulation**:
    *   **If evidence exists**: State the finding clearly, quote the evidence, and explain the invariant meaning based on the pattern definitions.
    *   **If no evidence exists**: Return status: `evidence_missing` with a statement that the contract does not contain clauses addressing the specific category.
    *   **If high-risk/ambiguous**: Return status: `needs_human_review`.

5.  **Safety Check**:
    *   Ensure no legal advice is given.
    *   Ensure no clauses from other contracts are cited.
    *   Ensure the response does not resemble a formal legal opinion.

## 3. Common Clause Patterns

### 3.1 Rofr/Rofo/Rofn

**Invariant Meaning**: Clauses granting a party the priority right to purchase, lease, or negotiate for assets, equity, or interests before the other party can sell to a third party.

**Variation Cues**: `right`, `offer`, `first`, `refusal`, `negotiation`, `purchase`, `sell`, `shares`, `interest`, `notice`, `period`.

**Conditions/Exceptions**:
*   **Conditions**: Often triggered by a specific event (e.g., receipt of a bona fide third-party offer, expiry of a lock-up period).
*   **Exceptions**: May exclude transfers to affiliates, mergers, or internal reorganizations.

**Representative Phrasings**:
*   *Positive (ROFR)*: "BP shall then have an optional prior right... to purchase for the stated consideration on the same terms and conditions the interest which Company proposes to sell."
*   *Positive (ROFR with Notice)*: "Licensee shall have the right and a first opportunity to purchase... on the Terms and Conditions set forth in the Offering Notice... within ninety (90) days."
*   *Negative (No ROFR)*: "The contract does not contain any clauses granting a right of first refusal, right of first offer, or right of first negotiation."
*   *Negative (Assignment Restriction Only)*: "This Agreement may not be assigned... without the prior written consent... [but does not grant a right of first refusal]."
*   *Negative (No Exclusivity)*: "Otherwise there is no exclusivity expressed or implied by either Party."

### 3.2 IP Ownership Assignment

**Invariant Meaning**: Clauses that transfer or assign the title, right, and interest in intellectual property (created, modified, or pre-existing) from one party to another.

**Variation Cues**: `assign`, `transfer`, `sole and exclusive property`, `work product`, `modifications`, `enhancements`, `derivative works`, `retain`, `ownership`.

**Conditions/Exceptions**:
*   **Conditions**: Often applies specifically to "Work Product," "modifications," or "jointly created" items.
*   **Exceptions**: Pre-existing IP usually remains with the original owner; licenses may be granted instead of assignment.

**Representative Phrasings**:
*   *Positive (Assignment of Work Product)*: "Turpin does hereby assign and transfer to the Company... all right, title, and interest that Turpin may have in and to the Work Product."
*   *Positive (Assignment of Modifications)*: "All changes, modifications and enhancements... shall be owned by Changepoint."
*   *Negative (Retention of Ownership)*: "Sponsor retains all right, title and interest in and to the Sponsor Web Site... and other Sponsor Brand Features."
*   *Negative (No Assignment)*: "The contract does not contain specific provisions assigning ownership of intellectual property created by one party to the other."
*   *Negative (License Only)*: "The contract grants licenses to use existing IP but does not assign ownership of newly created IP."

### 3.3 Joint IP Ownership

**Invariant Meaning**: Clauses establishing that two or more parties share ownership rights in specific intellectual property, typically created jointly.

**Variation Cues**: `jointly owned`, `shared`, `co-created`, `joint inventions`, `equally owned`, `user data`.

**Conditions/Exceptions**:
*   **Conditions**: Usually limited to IP created through the specific collaboration or joint efforts.
*   **Exceptions**: Pre-existing IP remains separate; sole ownership may be retained for specific deliverables.

**Representative Phrasings**:
*   *Positive (Joint Ownership)*: "Copyright Materials that are jointly created by the Parties shall be jointly owned."
*   *Positive (Joint Inventions)*: "All Joint Inventions shall be owned jointly by Theravance and GSK."
*   *Negative (Sole Ownership)*: "The intellectual property of the project belongs to Party A."
*   *Negative (No Joint Ownership)*: "The contract does not provide for joint or shared ownership of intellectual property between the parties."
*   *Negative (Separate Rights)*: "Each party shall exclusively own its respective trademarks... and will not have any claim or right to the other party's Intellectual Property."

### 3.4 Covenant Not to Sue

**Invariant Meaning**: Clauses where a party agrees not to challenge, contest, or sue regarding the validity, ownership, or infringement of the other party's intellectual property.

**Variation Cues**: `contest`, `challenge`, `validity`, `ownership`, `covenant`, `not to sue`, `assist`, `register`, `confusingly similar`.

**Conditions/Exceptions**:
*   **Conditions**: Often applies during and after the term of the agreement.
*   **Exceptions**: May not apply to third-party IP or unrelated claims.

**Representative Phrasings**:
*   *Positive (No Contest)*: "VerticalNet shall not now or in the future contest the validity of PaperExchange's Intellectual Property."
*   *Positive (No Challenge)*: "Licensee agrees and covenants that it shall not challenge, contest, or take any actions inconsistent with Licensor's exclusive rights of ownership."
*   *Positive (No Registration)*: "At no time... shall either party challenge... or attempt to register any trademarks... confusingly similar to those of the other party."
*   *Negative (No Covenant)*: "The contract does not contain a covenant not to sue regarding intellectual property validity or unrelated claims."
*   *Negative (Warranty Only)*: "Supplier represents and warrants... Supplier is not infringing... [but does not contain a covenant restricting contesting validity]."

### 3.5 Third Party Beneficiary

**Invariant Meaning**: Clauses defining whether parties outside the contract (non-signatories) have the right to enforce terms or benefit from the agreement.

**Variation Cues**: `third party`, `beneficiary`, `enforce`, `rights`, `remedies`, `successors`, `assigns`, `solely for the benefit`.

**Conditions/Exceptions**:
*   **Conditions**: Rights may extend to "successors and permitted assigns."
*   **Exceptions**: Explicit exclusions of specific entities (e.g., "Borrowers are not third-party beneficiaries").

**Representative Phrasings**:
*   *Negative (No Third Party)*: "This Agreement is solely for the benefit of the parties hereto and is not enforceable by any other persons."
*   *Negative (Explicit Exclusion)*: "Nothing in this Agreement... is intended to confer any rights or remedies... on any persons other than the parties to it."
*   *Negative (Standard Boilerplate)*: "This Agreement will be binding on, and will inure to the benefit of, the parties and their respective successors and assigns, and shall not confer any rights or remedies on any other Persons."
*   *Positive (Specific Beneficiary)*: [Rare in this dataset, but look for explicit naming of a third party with enforcement rights.]
*   *Negative (No Identification)*: "The contract does not identify any non-contracting party as a beneficiary with enforcement rights."

## 4. Evidence and Citation Protocol

1.  **Verbatim Quoting**: Always quote the exact text from the target contract that supports the finding. Do not paraphrase the evidence.
2.  **Contextualization**: Briefly explain how the quoted text maps to the pattern definition (e.g., "This clause assigns ownership of modifications, satisfying the IP Ownership Assignment pattern.").
3.  **No External Citations**: Never cite case law, statutes, or other contracts.
4.  **Handling "No" Findings**: If the contract explicitly states the absence of a right (e.g., "No third-party beneficiaries"), quote that exclusionary language as evidence for the "No" finding. If the contract is silent, state that no supporting clause was found.

## 5. Boundary and Abstention Rules

1.  **Missing Input**: If `contract_id` or `category` is missing, return `missing_input`.
2.  **Unsupported Scope**: If the requested category is not one of the five defined above, return `unsupported_scope`.
3.  **Evidence Missing**: If the target contract does not contain any clauses matching the semantic patterns for the requested category, return `evidence_missing`. Do not infer the presence of rights based on general contract principles.
4.  **No Legal Advice**: Do not interpret the legal enforceability, validity, or implications of the clauses beyond their literal text. Do not advise the user on whether a clause is "good" or "bad."
5.  **Human Review**: If the clause is highly ambiguous, contradictory, or involves complex conditional logic that cannot be definitively resolved by the pattern definitions, return `needs_human_review`.
6.  **Strict Source Adherence**: Only use the text provided in the target contract. Do not use the "representative examples" from the pattern cards as evidence for the target contract.
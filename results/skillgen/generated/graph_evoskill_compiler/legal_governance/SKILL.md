# SKILL.md

## 1. Purpose and Scope

This skill enables the runtime agent to review target contracts for specific legal governance and risk management clauses. The agent must identify, extract, and interpret provisions related to **Governing Law**, **Audit Rights**, and **Insurance**.

The agent operates under strict evidentiary constraints:
*   **Source Grounding:** All findings must be derived exclusively from the text of the target contract.
*   **No External Law:** The agent must not invent legal rules, cite external statutes, or provide legal advice.
*   **Conservative Interpretation:** If a clause is ambiguous or absent, the agent must abstain or report missing evidence rather than guessing.

## 2. Review Workflow

1.  **Input Validation:**
    *   Check if `contract_id` and `category` are provided.
    *   If missing, return status: `missing_input`.
    *   If `category` is not in `["Governing Law", "Audit Rights", "Insurance"]`, return status: `unsupported_scope`.

2.  **Pattern Matching:**
    *   Scan the target contract text for semantic variants of the patterns defined in Section 3.
    *   Identify the specific jurisdiction, rights granted, or insurance requirements.

3.  **Evidence Extraction:**
    *   Locate the exact verbatim text supporting the finding.
    *   Verify that the evidence exists within the target contract (Rule SR-002).

4.  **Interpretation & Output:**
    *   If evidence is found: Extract the clause, interpret its invariant meaning based on the pattern definitions, and return status: `answered`.
    *   If no relevant clause is found: Return status: `evidence_missing`.
    *   If the interpretation requires high-risk legal judgment: Return status: `needs_human_review`.

## 3. Common Clause Patterns

### Governing Law

**Invariant Meaning:**
Identifies the specific jurisdiction's laws that govern the interpretation, construction, and enforcement of the agreement. It often includes exclusions for conflict-of-law principles.

**Variation Cues:**
*   Keywords: `governed`, `construed`, `laws`, `state`, `accordance`, `without`, `principles`, `conflict`, `law`, `regard`, `interpreted`, `enforced`.
*   Structural cues: "This Agreement shall be governed by...", "construed in accordance with...", "without regard to conflict of laws...".

**Conditions & Exceptions:**
*   **Condition:** The clause must explicitly name a jurisdiction (e.g., State of New York, Province of British Columbia, People's Republic of China).
*   **Exception:** Look for exclusions such as "without application of conflict of laws principles," "excluding the choice of law rules," or "without regard to its conflicts of law provisions."

**Representative Phrasings (Recognition Aids Only):**
*   "This Agreement shall be governed by and construed in accordance with the laws of the State of New York, without application of conflict of laws principles."
*   "This Agreement will be governed and construed in accordance with the laws of the State of New York without giving effect to conflict of laws principles."
*   "This Agreement shall be governed by, construed, and enforced in accordance with the laws of the State of Delaware, without regard to choice of law principles that would require the application of the laws of any other jurisdiction."
*   "This Agreement shall be governed by and interpreted under the laws of the Commonwealth of Pennsylvania without regard to its conflicts of law provisions."
*   "This Agreement shall be deemed to have been entered into in the State of New Jersey, and shall be construed and interpreted in accordance with the laws of that State applicable to agreements made and to be performed in the State of New Jersey."
*   "In accordance with the Law of the People's Republic of China on Joint Ventures Using Chinese and Foreign Investment... and other relevant Chinese laws and regulations"
*   "governed by the laws of the State of California except that body of law dealing with conflicts of law."
*   "THIS AGREEMENT SHALL BE GOVERNED BY AND CONSTRUED IN ACCORDANCE WITH THE INTERNAL LAWS OF THE STATE OF NEW YORK... WITHOUT REGARD TO THE CONFLICTS OF LAW PRINCIPLES..."

### Audit Rights

**Invariant Meaning:**
Determines whether a party has the explicit right to inspect, examine, or audit the other party's books, records, accounts, or physical locations to verify compliance or payments.

**Variation Cues:**
*   **Positive Indicators:** `audit`, `examine`, `inspect`, `books`, `records`, `accounts`, `verify`, `compliance`, `normal business hours`, `reasonable notice`.
*   **Negative/Null Indicators:** Clauses discussing `entire agreement`, `indemnification`, `confidentiality`, `reimbursement`, or `general cooperation` do **not** constitute audit rights unless they explicitly grant inspection privileges.

**Conditions & Exceptions:**
*   **Condition:** The clause must explicitly grant the right to access records or premises. Mere obligations to provide reports or financial statements (e.g., "provide most recent financial statements") are not audit rights unless coupled with an inspection/audit mechanism.
*   **Exception:** Distinguish between "right to audit" and "obligation to provide information." If the text only says "Party A shall provide reports," it is **not** an audit right. If it says "Party B may examine Party A's books," it **is** an audit right.

**Representative Phrasings (Recognition Aids Only):**
*   *Positive (Audit Right Exists):*
    *   "Customer grants to Cisco and its independent accountants the right to examine Customer's books, records and accounts during Customer's normal business hours to verify compliance with this Agreement."
    *   "Upon reasonable notice to Distributor, Distributor shall make such books and records available to Developer... to audit the payments being made by Distributor hereunder."
    *   "The Servicer shall maintain appropriate books of account and records... which books of account and records shall be accessible for inspection by the Owner at any time during normal business hours."
*   *Negative (No Audit Right):*
    *   "This writing constitutes the entire agreement between the parties hereto..." (Entire Agreement clause does not grant audit rights).
    *   "The reports will contain sufficient information to permit Provider to verify payments hereunder." (Reporting obligation, not audit right).
    *   "Reseller agrees to provide McDATA with its... most recent financial statements..." (Provision of documents, not audit right).
    *   "Each Party shall treat as confidential... all Confidential Information..." (Confidentiality clause, not audit right).

### Insurance

**Invariant Meaning:**
Identifies obligations for one or both parties to maintain specific types of insurance coverage (e.g., General Liability, Workers' Compensation) and often specifies minimum limits and additional insured requirements.

**Variation Cues:**
*   **Positive Indicators:** `maintain`, `insurance`, `coverage`, `liability`, `general`, `commercial`, `workers' compensation`, `additional insured`, `limits`, `per occurrence`, `aggregate`.
*   **Negative/Null Indicators:** Clauses discussing `indemnification`, `hold harmless`, `entire agreement`, or `expenses` do **not** constitute insurance requirements unless they explicitly mandate the purchase/maintenance of insurance policies.

**Conditions & Exceptions:**
*   **Condition:** The clause must explicitly require the maintenance of insurance policies. Indemnification clauses ("indemnify, defend, and hold harmless") are distinct from insurance requirements.
*   **Exception:** Look for specific policy types (General Liability, Umbrella, Media Liability) and monetary limits. If the clause only mentions "indemnify," it is **not** an insurance clause.

**Representative Phrasings (Recognition Aids Only):**
*   *Positive (Insurance Required):*
    *   "HDS agrees to provide and maintain at its own expense, the following insurance coverages: A. Commercial General Liability coverage... B. Umbrella / Excess Liability coverage... C. Media Liability insurance..."
    *   "NETGEAR, at its expense, agrees to maintain insurance coverage to protect against its liabilities... This insurance will include (a) worker's compensation insurance, (b) comprehensive general liability insurance... and (c) automobile liability insurance."
    *   "Each party shall maintain insurance, including comprehensive or commercial general liability and products liability insurance... with limits not less than the following: (a) each occurrence, one million dollars..."
*   *Negative (No Insurance Requirement):*
    *   "HSNS agrees to indemnify, defend and hold harmless E.piphany... against any and all claims..." (Indemnification only, no insurance mandate).
    *   "Reseller agrees to defend, indemnify, and hold McDATA harmless..." (Indemnification only).
    *   "This Agreement is solely for the benefit of the parties hereto..." (No insurance mandate).
    *   "Except as expressly provided for in this Agreement, each party shall bear its own expenses..." (Expense allocation, not insurance).

## 4. Evidence and Citation Protocol

1.  **Verbatim Quoting:**
    *   When a finding is made, quote the exact text from the target contract.
    *   Do not paraphrase the evidence.
    *   Example: `"This Agreement shall be governed by and construed in accordance with the laws of the State of New York..."`

2.  **Source Verification:**
    *   Ensure the quoted text appears in the target contract provided in the input.
    *   Do not cite `source_contract_id` from the pattern cards (e.g., `WebmdHealthCorp_...`). These are training examples only.

3.  **Interpretation Separation:**
    *   Clearly separate the **Evidence** (the quote) from the **Interpretation** (the agent's analysis of what the quote means in the context of the category).
    *   Interpretation must be conservative. If the text says "governed by NY law," do not infer "NY courts have jurisdiction" unless the text also explicitly states jurisdiction/venue.

## 5. Boundary and Abstention Rules

1.  **Missing Input:**
    *   If `contract_id` is null or `category` is not provided, return `missing_input`.

2.  **Unsupported Scope:**
    *   If the requested category is not `Governing Law`, `Audit Rights`, or `Insurance`, return `unsupported_scope`.

3.  **Evidence Missing:**
    *   If the target contract does not contain a clause matching the invariant meaning of the requested category, return `evidence_missing`.
    *   *Example:* If asked for "Audit Rights" and the contract only has an "Entire Agreement" clause, return `evidence_missing` for Audit Rights. Do not hallucinate an audit right from the entire agreement clause.

4.  **No Legal Advice:**
    *   Do not provide opinions on the enforceability, fairness, or legal sufficiency of the clauses.
    *   Do not suggest changes to the contract.
    *   If the clause is complex or ambiguous, return `needs_human_review`.

5.  **No External Citations:**
    *   Do not cite laws, regulations, or case law not present in the target contract text.
    *   Do not use the `representative_examples` from Section 3 as evidence for the target contract. They are for pattern recognition only.
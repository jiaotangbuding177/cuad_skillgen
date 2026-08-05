# SKILL.md: Contract Review Skill Compiler

## Covered Categories
- **Governing Law**: 221 evidence atoms (KA-0001 to KA-0221)
- **Audit Rights**: 234 evidence atoms (KA-0002 to KA-0234)
- **Insurance**: 225 evidence atoms (KA-0003 to KA-0225)

## Evidence-Based Review Rules

### Governing Law
1.  **Identify Explicit Choice of Law Clauses**: Look for standard phrasing such as "governed by and construed in accordance with the laws of" or "interpreted under the laws of" to determine the applicable jurisdiction [KA-0001, KA-0007, KA-0012, KA-0015, KA-0018, KA-0025, KA-0028, KA-0031, KA-0034, KA-0037, KA-0040, KA-0043, KA-0052, KA-0055, KA-0058, KA-0063, KA-0067, KA-0070, KA-0073, KA-0091, KA-0094, KA-0097].
2.  **Verify Specific Jurisdiction**: Ensure the clause explicitly names the state, province, or country (e.g., California, Delaware, New York, Texas, Pennsylvania, Nevada, British Columbia, Israel, Kazakhstan, Iowa, Georgia, Massachusetts, Oklahoma, Florida, New Jersey) [KA-0001, KA-0004, KA-0007, KA-0012, KA-0015, KA-0018, KA-0025, KA-0028, KA-0031, KA-0034, KA-0037, KA-0040, KA-0043, KA-0052, KA-0055, KA-0058, KA-0063, KA-0067, KA-0070, KA-0073, KA-0078, KA-0091, KA-0094, KA-0097, KA-0100].
3.  **Check for Conflict of Law Exclusions**: Look for language excluding "choice or conflict of law principles" to ensure the chosen law applies regardless of other legal connections [KA-0031].
4.  **Identify Joint Venture Formation Laws**: For joint ventures, check if the agreement specifies the laws under which the venture is formed, which may differ from general governing law [KA-0078].

### Audit Rights
1.  **Verify Existence of Audit Clause**: Confirm if the contract explicitly grants the right to audit books, records, or facilities. If no such clause exists, flag as missing [KA-0092, KA-0134].
2.  **Identify Audit Scope**: Determine if the audit right covers financial records (books of account, sales figures), physical facilities (manufacturing sites, quality systems), or compliance (FCPA, anti-corruption) [KA-0002, KA-0008, KA-0029, KA-0035, KA-0041, KA-0059, KA-0061, KA-0079, KA-0095, KA-0098, KA-0116, KA-0140, KA-0143, KA-0161, KA-0164, KA-0167, KA-0178, KA-0214, KA-0228, KA-0231, KA-0240, KA-0258, KA-0259].
3.  **Check Frequency and Notice Requirements**: Look for limitations on how often audits can occur (e.g., "once every twelve months," "no more frequently than once per year") and required advance notice periods (e.g., "reasonable advance notice," "ten days written notice," "thirty days prior written notice") [KA-0002, KA-0029, KA-0035, KA-0041, KA-0061, KA-0098, KA-0231, KA-0240, KA-0258].
4.  **Identify Auditor Qualifications**: Check if the contract specifies who can perform the audit (e.g., "independent CPA," "third party auditor," "authorized representatives") [KA-0002, KA-0008, KA-0041, KA-0059, KA-0116, KA-0161, KA-0167, KA-0258].
5.  **Assess Cost Allocation**: Determine if the auditing party bears the cost ("at its own expense") or if costs are shared/reimbursed [KA-0041, KA-0164, KA-0228].

### Insurance
1.  **Verify Existence of Insurance Requirement**: Confirm if the contract mandates insurance coverage. If no requirement exists, flag as missing [KA-0003, KA-0069, KA-0093, KA-0135, KA-0150, KA-0209, KA-0229].
2.  **Identify Required Coverage Types**: Look for specific insurance types such as Commercial General Liability, Product Liability, Errors and Omissions, Fidelity/Electronic Crime, Property Insurance, Cargo Liability, or Workers' Compensation [KA-0017, KA-0030, KA-0036, KA-0045, KA-0062, KA-0065, KA-0072, KA-0096, KA-0099, KA-0120, KA-0144, KA-0162, KA-0194, KA-0200, KA-0215, KA-0220, KA-0232, KA-0235].
3.  **Check Minimum Coverage Limits**: Identify specific monetary limits required (e.g., "$1,000,000," "$5,000,000," "AU$10 million") [KA-0017, KA-0065, KA-0120, KA-0194, KA-0215, KA-0232].
4.  **Verify Additional Insured Status**: Check if the counterparty must be named as an "additional insured" on the policy [KA-0099, KA-0215, KA-0235].
5.  **Assess Carrier Requirements**: Look for requirements regarding the insurer's reputation or rating (e.g., "reputable insurer," "duly licensed") [KA-0062, KA-0120, KA-0232].

## Review Checklist

### Governing Law
- [ ] Does the contract contain an explicit governing law clause? [KA-0001, KA-0012]
- [ ] Is the specific jurisdiction (State/Country) clearly identified? [KA-0001, KA-0004, KA-0012]
- [ ] Are conflict of law principles excluded? [KA-0031]
- [ ] For joint ventures, is the formation law specified? [KA-0078]

### Audit Rights
- [ ] Is there an explicit audit right granted to either or both parties? [KA-0002, KA-0092]
- [ ] Is the scope of the audit defined (financial, physical, compliance)? [KA-0029, KA-0035, KA-0140]
- [ ] Are there frequency limits (e.g., annual)? [KA-0002, KA-0041]
- [ ] Is advance notice required? [KA-0029, KA-0098]
- [ ] Is the type of auditor specified (e.g., CPA)? [KA-0002, KA-0041]
- [ ] Who bears the cost of the audit? [KA-0164, KA-0228]

### Insurance
- [ ] Is there an explicit insurance requirement? [KA-0017, KA-0003]
- [ ] Are specific coverage types listed (e.g., General Liability, Product Liability)? [KA-0036, KA-0096]
- [ ] Are minimum coverage limits specified? [KA-0017, KA-0065]
- [ ] Is the counterparty named as an additional insured? [KA-0099, KA-0215]
- [ ] Are carrier ratings or reputations specified? [KA-0062, KA-0120]

## Output Format
JSON:
```json
{
  "status": "success|error",
  "answer": "Summary of findings based on evidence",
  "evidence_unit_ids": ["KA-XXXX", "KA-YYYY"],
  "source_contract_ids": ["ContractID_1", "ContractID_2"],
  "missing_inputs": ["category", "contract_id"],
  "human_review_required": true|false
}
```

## Boundary Rules
- **[RB-001]**: Answer only using the target contract. Do not infer rules from external knowledge.
- **[RB-002]**: Cite source-grounded evidence when answering. Every claim must reference a KA ID.
- **[RB-003]**: Return `evidence_missing` when no supporting clause exists for a specific category (e.g., no audit clause found [KA-0092, KA-0134]).
- **[RB-004]**: Return `missing_input` when `contract_id` or `category` is absent from the request.
- **[RB-005]**: Return `unsupported_scope` when the question is outside covered_categories (Governing Law, Audit Rights, Insurance).
- **[RB-006]**: Route legal advice and high-risk interpretation to human review.
- **[SR-001]**: Do not cite non-target contracts. Only use KAs linked to the provided evidence index.
- **[SR-002]**: Do not fabricate clauses. If a clause pattern is not in the evidence index, do not include it.
- **[SR-003]**: Do not provide legal advice. Provide factual extraction and pattern matching only.
- **[SR-004]**: Do not generate externally sendable legal opinions.
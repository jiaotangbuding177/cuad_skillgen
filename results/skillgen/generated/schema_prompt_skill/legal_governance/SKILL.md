# SKILL.md

## Covered Categories

### Governing Law
- **Description**: Which state/country's law governs the interpretation of the contract?
- **Answer Format**: Name of a US State / non-US Province, Country

### Audit Rights
- **Description**: Does a party have the right to audit the books, records, or physical locations of the counterparty to ensure compliance with the contract?
- **Answer Format**: Yes/No

### Insurance
- **Description**: Is there a requirement for insurance that must be maintained by one party for the benefit of the counterparty?
- **Answer Format**: Yes/No

## Review Checklist

### Governing Law
- [ ] Locate the "Governing Law" clause (often titled "Governing Law," "Applicable Law," or "Choice of Law")
- [ ] Identify the specific jurisdiction named (e.g., "State of New York," "State of Delaware," "laws of England," "laws of the State of Israel")
- [ ] Note any exceptions or carve-outs (e.g., "without regard to principles of conflicts of laws")
- [ ] If no explicit governing law clause exists, check for jurisdiction/venue clauses that may imply governing law

### Audit Rights
- [ ] Search for keywords: "audit," "inspect," "books and records," "examination," "review"
- [ ] Determine if the audit right is unilateral (one party only) or mutual
- [ ] Check for scope limitations (e.g., "during normal business hours," "upon reasonable notice," "once per year")
- [ ] Look for audit rights related to: financial records, compliance, quality control, manufacturing facilities
- [ ] Note if audit rights are tied to royalty/revenue verification or general compliance

### Insurance
- [ ] Search for keywords: "insurance," "insure," "coverage," "policy"
- [ ] Determine if insurance is required to be maintained (mandatory) versus merely offered as a benefit
- [ ] Check if the insurance is for the benefit of the counterparty (e.g., named as additional insured)
- [ ] Look for specific insurance types: general liability, professional liability, workers' compensation, property insurance
- [ ] Distinguish between employee benefits (e.g., health insurance) and liability insurance for the counterparty's protection

## Evidence Extraction Rules

### Governing Law
- **Location**: Typically found in the final sections of the contract (e.g., Section 10, Section 22, Section 15.6)
- **Pattern**: "This Agreement shall be governed by and construed in accordance with the laws of [Jurisdiction]"
- **Example**: "This Agreement has been made in the State of California and shall be governed by and construed in accordance with the laws thereof" → Extract: "California"
- **Example**: "This Agreement is governed by and construed in accordance with English law" → Extract: "England"
- **Example**: "This Agreement shall be governed by and construed in accordance with the laws of the State of Israel" → Extract: "Israel"

### Audit Rights
- **Location**: Often in sections titled "Reports and Audit Rights," "Books and Records," "Audits," or "Inspection"
- **Pattern**: Look for explicit language granting the right to audit, inspect, or examine records
- **Example**: "Todos shall have the right to have an inspection and audit of all the relevant accounting and sales books and records" → Extract: "Yes"
- **Example**: "NeuroBo may, at its cost and expense, inspect Dong-A's manufacturing facilities" → Extract: "Yes"
- **Example**: "D2 may audit such records by engaging an independent public audit firm" → Extract: "Yes"
- **Note**: If no audit clause exists, answer "No"

### Insurance
- **Location**: Often in sections titled "Insurance," "Insurances," or "Indemnification"
- **Pattern**: Look for language requiring a party to "maintain," "carry," or "procure" insurance
- **Example**: "Each party shall carry appropriate and commercially reasonable amounts of insurance adequate for the activities detailed in this Agreement" → Extract: "Yes"
- **Example**: "The Executive is entitled to membership of a Group income protection plan and life assurance cover" → This is an employee benefit, not insurance for counterparty benefit → Extract: "No"
- **Note**: Distinguish between insurance as an employee benefit versus insurance required to protect the counterparty

## Output Format

```json
{
  "status": "answered",
  "answer": "California",
  "evidence_unit_ids": ["HOLIDAYRVSUPERSTORESINC_04_15_2002-EX-10.13-ENDORSEMENT_AGREEMENT"],
  "source_contract_ids": ["HOLIDAYRVSUPERSTORESINC_04_15_2002-EX-10.13-ENDORSEMENT_AGREEMENT"],
  "missing_inputs": [],
  "human_review_required": false
}
```

## Boundary Rules

1. **Answer only using the target contract**: All answers must be derived exclusively from the contract document provided. Do not use external knowledge or assumptions.

2. **Cite source-grounded evidence when answering**: Every answer must reference specific clauses, sections, or language from the contract. Include the evidence_unit_ids pointing to the exact contract document.

3. **Return evidence_missing when no supporting clause exists**: If the contract does not contain a clause addressing the category, return status "evidence_missing" with an empty answer.

4. **Return missing_input when contract_id or category is absent**: If the required inputs (contract_id or category) are not provided, return status "missing_input" and list the missing inputs.

5. **Return unsupported_scope when the question is outside covered_categories**: If asked about a category not listed in the covered categories, return status "unsupported_scope".

6. **Route legal advice and high-risk interpretation to human review**: If the question requires legal interpretation, judgment calls, or involves high-risk determinations, set human_review_required to true.

### Safety Requirements
- **Do not cite non-target contracts**: Only reference the contract(s) specified in the input.
- **Do not fabricate clauses**: If a clause doesn't exist, do not invent it. Return evidence_missing.
- **Do not provide legal advice**: Do not offer opinions on legal strategy, enforceability, or recommendations.
- **Do not generate externally sendable legal opinions**: The output is for internal review purposes only.
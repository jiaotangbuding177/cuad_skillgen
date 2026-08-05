# SKILL.md - Legal Governance Contract Review Skill

## Covered Categories

### Governing Law
- **Discovery frequency**: 67.6% of contracts (207 out of 306)
- **Common patterns**: Most contracts specify a U.S. state law (Delaware, New York, California, Texas, Florida most common); international contracts often choose a specific country's law; many exclude conflict of laws principles; some specify exclusive jurisdiction in addition to governing law.

### Audit Rights
- **Discovery frequency**: 36.3% of contracts (111 out of 306)
- **Common patterns**: Audits typically conducted by independent CPA or third-party auditor; frequency limited to once per year; conducted during normal business hours upon reasonable notice; often limited to financial records related to payments or royalties.

### Insurance
- **Discovery frequency**: 26.5% of contracts (81 out of 306)
- **Common patterns**: Minimum coverage amounts specified (often $1M-$2M); requirement to name counterparty as additional insured; includes commercial general liability, product liability, workers' compensation; evidence of insurance required upon request.

## Common Patterns

### Governing Law
1. **U.S. State Law Selection**: Most common pattern. Example: "This Agreement shall be governed by and construed in accordance with the laws of the State of [Delaware/New York/California/Texas/Florida]."
2. **International Law Selection**: Contracts involving parties from different countries. Example: "This Agreement shall be governed by the laws of [England/Japan/Israel/China/Hong Kong/Ontario]."
3. **Exclusive Jurisdiction + Governing Law**: Specifies both governing law and exclusive venue. Example: "This Agreement is governed by the laws of the State of New York, with exclusive jurisdiction in New York, New York."

### Audit Rights
1. **Financial Record Audit**: Right to audit books/records related to payments, royalties, or financial obligations. Example: "[Party] has the right to audit [Counterparty]'s books and records related to payments under this agreement."
2. **Quality/Compliance Audit**: Right to inspect facilities, premises, or manufacturing operations. Example: "[Party] has the right to inspect [Counterparty]'s premises, books, and records related to the [Program/Product]."
3. **Mutual Audit Rights**: Both parties have reciprocal audit rights. Example: "Each party has the right to audit the other party's books and records related to this agreement."

### Insurance
1. **Standard Liability Coverage**: Requires commercial general liability and product liability insurance with minimum limits. Example: "[Party] must maintain commercial general liability insurance with minimum limits of $1,000,000 per occurrence and $2,000,000 aggregate."
2. **Additional Insured Requirement**: Requires naming counterparty as additional insured. Example: "[Party] shall name [Counterparty] as an additional insured on its insurance policies."
3. **Evidence of Insurance**: Requires providing certificate of insurance upon request. Example: "[Party] shall provide [Counterparty] with a certificate of insurance evidencing such coverage upon request."

## Review Checklist

### Governing Law
- [ ] Does the contract specify a governing law (state or country)?
- [ ] Is the governing law clearly stated in a single clause?
- [ ] Does the contract also specify exclusive jurisdiction or venue?
- [ ] Does the contract exclude conflict of laws principles?
- [ ] Is the governing law appropriate for the parties' locations and the contract's subject matter?

### Audit Rights
- [ ] Does any party have audit rights over the other?
- [ ] What is the scope of the audit (financial records, facilities, operations)?
- [ ] Is the audit frequency specified (e.g., once per year)?
- [ ] Who conducts the audit (independent accountant, third-party auditor)?
- [ ] Are there notice requirements and time restrictions (e.g., normal business hours)?
- [ ] Are there cost-bearing provisions (e.g., audited party pays if underpayment exceeds threshold)?

### Insurance
- [ ] Does the contract require insurance to be maintained?
- [ ] What types of insurance are required (CGL, product liability, workers' comp, errors & omissions)?
- [ ] Are minimum coverage amounts specified?
- [ ] Is the counterparty required to be named as an additional insured?
- [ ] Is evidence of insurance required to be provided?
- [ ] Are there any exceptions (e.g., "Producer has no insurance requirement")?

## Evidence Extraction Rules

### Governing Law
- **Location**: Typically found in a "Governing Law" or "Choice of Law" section, often near the end of the contract.
- **Keywords**: "governed by", "governing law", "choice of law", "laws of", "jurisdiction", "venue", "conflict of laws".
- **Extraction**: Capture the full sentence or clause specifying the governing law. Note if jurisdiction/venue is also specified. Record any exclusion of conflict of laws principles.

### Audit Rights
- **Location**: Often in a dedicated "Audit Rights" or "Inspection" section, or within "Records" or "Compliance" clauses.
- **Keywords**: "audit", "inspect", "examine", "books and records", "financial records", "premises", "facilities", "independent accountant", "third-party auditor".
- **Extraction**: Capture the full clause describing the audit right. Note the scope (financial, quality, compliance), frequency, notice requirements, who conducts the audit, and any cost-bearing provisions.

### Insurance
- **Location**: Typically in an "Insurance" section, or within "Indemnification" or "General Provisions".
- **Keywords**: "insurance", "coverage", "additional insured", "certificate of insurance", "commercial general liability", "product liability", "workers' compensation", "errors and omissions".
- **Extraction**: Capture the full insurance clause. Note types of insurance required, minimum coverage amounts, additional insured requirements, and evidence of insurance requirements.

## Output Format

```json
{
  "status": "complete" | "incomplete" | "error",
  "answer": "Summary of findings for each category, or error message.",
  "evidence_unit_ids": ["list of evidence unit IDs supporting the answer"],
  "source_contract_ids": ["list of contract IDs where evidence was found"],
  "missing_inputs": ["list of required inputs that were not provided"],
  "human_review_required": true | false
}
```

## Boundary Rules

### What the skill SHOULD do:
- **Extract and summarize** governing law, audit rights, and insurance provisions from contracts.
- **Identify patterns** based on the aggregated knowledge (e.g., common state laws, typical audit frequency, standard insurance amounts).
- **Flag missing or ambiguous provisions** for human review.
- **Provide clear, structured output** in the specified JSON format.
- **Use evidence extraction rules** to locate and capture relevant clauses.

### What the skill should NOT do:
- **Do not interpret or advise** on the legal sufficiency or enforceability of provisions.
- **Do not assume** a provision exists if not explicitly stated (e.g., do not infer governing law from jurisdiction alone unless clearly linked).
- **Do not modify or rewrite** contract language.
- **Do not make judgments** about which governing law is "better" or which insurance amount is "adequate."
- **Do not handle categories outside** Governing Law, Audit Rights, and Insurance.
- **Do not generate legal opinions** or recommendations.
- **Do not ignore explicit exceptions** (e.g., "Producer has no insurance requirement" should be reported as found).
# SKILL.md - Operational Rights Review

## Covered Categories

### Rofr/Rofo/Rofn
**Description:** Is there a clause granting one party a right of first refusal, right of first offer or right of first negotiation to purchase, license, market, or distribute equity interest, technology, assets, products or services?
**Answer Format:** Yes/No

### IP Ownership Assignment
**Description:** Does intellectual property created by one party become the property of the counterparty, either per the terms of the contract or upon the occurrence of certain events?
**Answer Format:** Yes/No

### Joint IP Ownership
**Description:** Is there any clause providing for joint or shared ownership of intellectual property between the parties to the contract?
**Answer Format:** Yes/No

### Covenant Not to Sue
**Description:** Is a party restricted from contesting the validity of the counterparty's ownership of intellectual property or otherwise bringing a claim against the counterparty for matters unrelated to the contract?
**Answer Format:** Yes/No

### Third Party Beneficiary
**Description:** Is there a non-contracting party who is a beneficiary to some or all of the clauses in the contract and therefore can enforce its rights against a contracting party?
**Answer Format:** Yes/No

## Review Checklist

### Rofr/Rofo/Rofn
- [ ] Look for explicit language using terms "right of first refusal," "right of first offer," "right of first negotiation," "ROFR," "ROFO," or "ROFN"
- [ ] Check for clauses granting a party the first opportunity to purchase, license, market, or distribute specific assets, equity, technology, or services before the offering party can negotiate with third parties
- [ ] Examine sections related to exclusivity, purchase options, or preferential rights to acquire interests
- [ ] Review any "first opportunity" or "first right" language in marketing, distribution, or licensing contexts

### IP Ownership Assignment
- [ ] Identify clauses stating that IP created by one party "shall be owned by" or "shall become the property of" the counterparty
- [ ] Look for "work made for hire" designations or assignment language transferring IP rights
- [ ] Check for provisions requiring one party to assign all rights, title, and interest in inventions or developments to the other party
- [ ] Examine sections titled "Proprietary Rights," "Ownership," or "Intellectual Property"

### Joint IP Ownership
- [ ] Search for language indicating IP is "jointly owned," "co-owned," or shared between parties in specified percentages
- [ ] Look for provisions describing "joint inventions" or "jointly developed" intellectual property
- [ ] Check for clauses establishing co-ownership rights with specific shares (e.g., 50/50)
- [ ] Examine sections addressing ownership of "Joint IP," "Collaboration IP," or "Joint Inventions"

### Covenant Not to Sue
- [ ] Identify clauses restricting a party from challenging or contesting the validity of the counterparty's IP ownership
- [ ] Look for non-assertion covenants or agreements not to bring claims against the counterparty
- [ ] Check for provisions prohibiting actions that would "adversely affect" the counterparty's IP rights
- [ ] Examine sections on "Non-Assertion," "Covenant Not to Sue," or restrictions on challenging trademarks/patents

### Third Party Beneficiary
- [ ] Search for explicit "third party beneficiary" language or clauses stating that non-signatories may enforce contract terms
- [ ] Look for provisions identifying specific third parties (e.g., lenders, agents, affiliates) as beneficiaries
- [ ] Check for clauses stating that certain parties "shall be deemed a third-party beneficiary" with enforcement rights
- [ ] Examine sections on "Successors and Assigns" or "No Third Party Beneficiaries" for explicit statements

## Evidence Extraction Rules

### Locating Evidence
1. **Section Headers:** Focus on sections titled "Licenses; Proprietary Rights," "Intellectual Property," "Ownership," "Grants," "Exclusivity," "Covenants," and "General Provisions"
2. **Definition Sections:** Check definitions for terms like "Inventions," "Intellectual Property," "Know-How," "Patents," and "Confidential Information"
3. **Recitals:** Review "WHEREAS" clauses for statements about IP ownership intentions and relationship structure
4. **Exhibits and Schedules:** Examine attachments that may list IP, licensed technology, or specify ownership arrangements

### Extraction Methodology
- Extract the exact clause text containing the relevant provision
- Note the section number and title where the clause appears
- Identify which parties are involved in the IP/rights arrangement
- Document any conditions, exceptions, or limitations on the rights granted

### Key Patterns from Contracts
- **ROFR/ROFO/ROFN:** Look for explicit "right of first refusal" language in exclusivity or marketing sections (e.g., Xpresspa/Calm Agreement Section 3.03)
- **IP Assignment:** Look for "assigns all of its right title and interest" language (e.g., Cytodyn/Vyera Agreement Section 2.2(b))
- **Joint IP:** Look for "jointly to the parties in equal shares" or "co-ownership" language (e.g., Kiromic/Molipharma Agreement Section 6)
- **Covenant Not to Sue:** Look for restrictions on challenging marks or IP validity (e.g., Xpresspa/Calm Agreement Section 9.04)
- **Third Party Beneficiary:** Look for explicit "third-party beneficiary" designation (e.g., CURO Servicing Agreement Section 21)

## Output Format

```json
{
  "status": "answered",
  "answer": "Yes/No",
  "evidence_unit_ids": ["contract_id:section_number"],
  "source_contract_ids": ["contract_id"],
  "missing_inputs": [],
  "human_review_required": false
}
```

### Status Values
- **answered:** Sufficient evidence found to answer the question
- **evidence_missing:** No supporting clause exists in the contract
- **missing_input:** Contract_id or category is absent from the request
- **unsupported_scope:** The question falls outside covered categories
- **needs_human_review:** Legal advice or high-risk interpretation required

## Boundary Rules

### Answering Rules
1. **Answer only using the target contract** - Do not reference or cite provisions from non-target contracts
2. **Cite source-grounded evidence** - When answering "Yes," provide specific section references and clause text
3. **Return evidence_missing** - When no supporting clause exists in the contract for the category
4. **Return missing_input** - When contract_id or category is absent from the request
5. **Return unsupported_scope** - When the question is outside the five covered categories

### Safety Requirements
1. **Do not cite non-target contracts** - Only use evidence from the contract being reviewed
2. **Do not fabricate clauses** - If no clause exists, return evidence_missing
3. **Do not provide legal advice** - Do not interpret legal implications or advise on legal strategy
4. **Do not generate externally sendable legal opinions** - Output is for internal review purposes only
5. **Route to human review** - Set `human_review_required: true` when the question involves:
   - Legal advice or interpretation of ambiguous clauses
   - High-risk determinations that could have significant legal consequences
   - Questions requiring analysis of applicable law or jurisdiction
   - Assessment of whether a clause is enforceable or valid
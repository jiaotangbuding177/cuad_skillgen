# SKILL.md - Competition Restrictions Review

## Covered Categories

### Most Favored Nation
- **Description**: Identifies clauses requiring that if a third party receives better terms on licensing or sale of technology/goods/services, the buyer under this contract shall be entitled to those better terms.
- **Answer Format**: Yes/No

### Non-Compete
- **Description**: Identifies restrictions on a party's ability to compete with the counterparty or operate in a certain geography, business, or technology sector.
- **Answer Format**: Yes/No

### Exclusivity
- **Description**: Identifies exclusive dealing commitments, including requirements to procure all "requirements" from one party, prohibitions on licensing/selling to third parties, or prohibitions on collaborating with other parties.
- **Answer Format**: Yes/No

### No-Solicit of Customers
- **Description**: Identifies restrictions on contracting or soliciting customers or partners of the counterparty.
- **Answer Format**: Yes/No

### Competitive Restriction Exception
- **Description**: Identifies exceptions or carveouts to Non-Compete, Exclusivity, and No-Solicit of Customers clauses.
- **Answer Format**: Yes/No

### No-Solicit of Employees
- **Description**: Identifies restrictions on soliciting or hiring employees and/or contractors from the counterparty.
- **Answer Format**: Yes/No

### Non-Disparagement
- **Description**: Identifies requirements not to disparage the counterparty.
- **Answer Format**: Yes/No

## Review Checklist

### Most Favored Nation
- [ ] Does the contract contain language requiring that if a third party receives better terms, the buyer is entitled to those same better terms?
- [ ] Look for phrases like "most favored nation," "most favorable treatment," "better terms," or "shall be entitled to those better terms"

### Non-Compete
- [ ] Does the contract restrict a party from competing with the counterparty?
- [ ] Does the contract restrict operating in a certain geography, business sector, or technology field?
- [ ] Look for "standstill provisions," "non-compete," "restrictions on competition," or prohibitions on engaging in similar business

### Exclusivity
- [ ] Does the contract require a party to procure all "requirements" from one party?
- [ ] Does the contract prohibit licensing or selling technology/goods/services to third parties?
- [ ] Does the contract prohibit collaborating or working with other parties?
- [ ] Look for "exclusive," "sole provider," "shall not grant any third party," or "shall not enter into an agreement with"

### No-Solicit of Customers
- [ ] Does the contract restrict a party from soliciting customers or partners of the counterparty?
- [ ] Does this restriction apply during the contract, after the contract ends, or both?
- [ ] Look for "solicit," "solicitation of customers," or restrictions on contacting counterparty's customers

### Competitive Restriction Exception
- [ ] Are there exceptions or carveouts to Non-Compete, Exclusivity, or No-Solicit of Customers clauses?
- [ ] Look for "notwithstanding," "provided that," "except," "shall not prohibit," or "nothing in this Agreement shall prevent"

### No-Solicit of Employees
- [ ] Does the contract restrict soliciting or hiring employees and/or contractors from the counterparty?
- [ ] Does this restriction apply during the contract, after the contract ends, or both?
- [ ] Look for "solicit employees," "hire employees," "no-solicit of employees," or restrictions on recruiting counterparty personnel

### Non-Disparagement
- [ ] Does the contract require a party not to disparage the counterparty?
- [ ] Look for "non-disparagement," "shall not disparage," "shall not make negative statements," or "mutual non-disparagement"

## Evidence Extraction Rules

### Locating Evidence
1. **Search for section headings**: Look for sections titled "Standstill Provisions," "Restrictions on Competition," "Non-Compete," "Exclusivity," "Non-Disparagement," "Mutual Non-Disparagement," or "Competitive Restrictions"
2. **Search for defined terms**: Look for definitions of "Standstill Period," "Exclusive Category," "Non-Compete," or similar terms
3. **Search for key phrases**: "shall not," "prohibited from," "restricted from," "agree not to," "covenants and agrees"
4. **Search for exceptions**: "provided that," "notwithstanding," "except," "shall not prohibit," "nothing in this Agreement shall prevent"

### Extraction Patterns from Contracts

**Non-Compete/Standstill (HC2HOLDINGS Agreement - Section 3)**:
- Look for explicit "Standstill Provisions" sections listing prohibited activities
- Evidence: "none of the MG Capital Parties nor any of their Affiliates and Associates will... engage in a 'solicitation' of 'proxies'... form, join or in any way participate in any 'group'... seek or submit... nomination(s) in furtherance of a 'contested solicitation'"

**Exclusivity (EmbarkCom Agreement - Section 2.6)**:
- Look for "Exclusive Sponsorship" or "Exclusive Category" sections
- Evidence: "Snap will not grant any third party any right to sponsor any products or services in the Exclusive Category"

**Exclusivity (LeadersOnline Agreement - Section 12.2)**:
- Look for "Parallel Agreement" or non-compete with specific competitors
- Evidence: "VerticalNet agrees that during the term of this Agreement, it shall not enter into an agreement with Futurestep, Inc."

**Non-Disparagement (HC2HOLDINGS Agreement - Section 6)**:
- Look for "Mutual Non-Disparagement" sections
- Evidence: "neither Party nor any of its subsidiaries... shall in any way... publicly disparage, impugn, make ad hominem attacks on or otherwise defame or slander"

**Most Favored Nation (SENMIAOTECHNOLOGY Agreement - Section 3.2.17)**:
- Look for "most favorable treatment" or "most favored nation" language
- Evidence: "Party B guarantees that the Driver User will enjoy the most favorable treatment... In case that the price and other substantive terms offered by Party B to such entity are more favorable than those enjoyed by the Driver User... the Driver User and Party B shall amend the provisions"

**No-Solicit of Customers (Pizza Fusion Agreement - Section 1.2.2)**:
- Look for restrictions on soliciting customers outside designated areas
- Evidence: "You agree not to: (a) advertise or market the services of your Franchised Business outside of the Delivery/Catering and Advertising Area; and/or (b) engage in direct solicitation of customers outside of the Delivery/Catering and Advertising Area"

**Competitive Restriction Exception (HC2HOLDINGS Agreement - Section 3(b))**:
- Look for "Notwithstanding the foregoing" or exception clauses
- Evidence: "nothing in this Agreement shall prohibit or restrict the MG Capital Parties from: (A) communicating privately with the Board... (B) communicating privately with stockholders... (C) taking any action necessary to comply with any law"

**No-Solicit of Employees (Pizza Fusion Agreement - Section 17)**:
- Look for sections titled "Restrictions on Competition" or similar
- Evidence: Check Section 17 of the Pizza Fusion Agreement for employee solicitation restrictions

## Output Format

```json
{
  "status": "answered",
  "answer": "Yes/No",
  "evidence_unit_ids": ["contract_id-section_number"],
  "source_contract_ids": ["contract_id"],
  "missing_inputs": [],
  "human_review_required": false
}
```

### Status Values
- **answered**: Sufficient evidence found to answer the question
- **evidence_missing**: No supporting clause exists in the contract
- **missing_input**: Contract_id or category is absent from the input
- **unsupported_scope**: The question is outside the covered categories
- **needs_human_review**: Legal advice or high-risk interpretation required

## Boundary Rules

1. **Answer only using the target contract**: Do not reference or cite clauses from non-target contracts
2. **Cite source-grounded evidence**: When answering "Yes," provide specific section references and quote relevant language
3. **Return evidence_missing**: When no supporting clause exists in the contract, return status "evidence_missing" with answer "No"
4. **Return missing_input**: When contract_id or category is absent, return status "missing_input"
5. **Return unsupported_scope**: When the question is outside covered_categories, return status "unsupported_scope"
6. **Route to human review**: For legal advice or high-risk interpretation, set human_review_required to true

### Safety Requirements
- Do not cite non-target contracts
- Do not fabricate clauses or evidence
- Do not provide legal advice or legal opinions
- Do not generate externally sendable legal opinions
- Do not interpret ambiguous clauses beyond what is explicitly stated
- When in doubt about interpretation, flag for human review
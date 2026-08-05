# SKILL.md - Liability and Indemnity Review

## Covered Categories

### Uncapped Liability
- **Description**: Determines whether a party's liability is uncapped upon breach of its obligation in the contract. This also includes uncapped liability for a particular type of breach such as IP infringement or breach of confidentiality obligation.
- **Answer Format**: Yes/No

### Cap on Liability
- **Description**: Determines whether the contract includes a cap on liability upon breach of a party's obligation. This includes time limitations for the counterparty to bring claims or maximum amount for recovery.
- **Answer Format**: Yes/No

### Liquidated Damages
- **Description**: Determines whether the contract contains a clause that would award either party liquidated damages for breach or a fee upon termination of a contract (termination fee).
- **Answer Format**: Yes/No

### Warranty Duration
- **Description**: Determines the duration of any warranty against defects or errors in technology, products, or services provided under the contract.
- **Answer Format**: Number of months or years

## Review Checklist

### Uncapped Liability
- [ ] Check for any clause that explicitly states liability is "uncapped" or "without limit"
- [ ] Look for clauses that exclude liability caps for specific types of breaches (e.g., IP infringement, breach of confidentiality, gross negligence, willful misconduct)
- [ ] Identify if the contract states "no limitation of liability" for certain obligations
- [ ] Check indemnification clauses that may be uncapped

### Cap on Liability
- [ ] Look for a "Limitation of Liability" section that specifies a maximum monetary amount
- [ ] Check for time limitations on bringing claims (statute of limitations modifications)
- [ ] Identify any caps expressed as a multiple of fees paid (e.g., "liability shall not exceed the fees paid")
- [ ] Look for fixed dollar amount caps (e.g., "$15,000,000")
- [ ] Check if the cap applies to "direct damages" only

### Liquidated Damages
- [ ] Look for clauses explicitly titled "Liquidated Damages"
- [ ] Check for termination fees or early termination penalties
- [ ] Identify clauses that specify a predetermined amount of damages for breach
- [ ] Look for language stating the amount is a "reasonable estimate of damages" and not a "penalty"

### Warranty Duration
- [ ] Check for warranty sections that specify a time period (e.g., "90 days," "1 year")
- [ ] Look for warranty periods in both general warranty clauses and specific product/service warranties
- [ ] Identify any warranty periods for bug fixes or defect corrections
- [ ] Check for warranty duration in maintenance or support sections

## Evidence Extraction Rules

### Locating Evidence
1. **Liability Clauses**: Search for sections titled "Limitation of Liability," "Liability," "Indemnification," or "Damages"
2. **Warranty Clauses**: Search for sections titled "Warranty," "Representations and Warranties," or "Product Warranty"
3. **Liquidated Damages**: Search for "Liquidated Damages," "Termination Fee," "Specific Performance," or "Damages"
4. **Caps**: Look for specific dollar amounts or formulas (e.g., "not exceed $X," "limited to fees paid")

### Extraction Patterns
- **Uncapped Liability**: Look for exceptions to liability caps (e.g., "notwithstanding the foregoing, liability for...shall not be limited")
- **Cap on Liability**: Extract the specific cap amount or formula (e.g., "liability shall not exceed $15,000,000" or "the sum total of payments made")
- **Liquidated Damages**: Extract the specific amount or calculation method (e.g., "an amount equal to the lesser of...")
- **Warranty Duration**: Extract the specific time period (e.g., "90 days," "1 year," "warranty period")

### Evidence Unit ID Format
- Use the contract name and section number (e.g., "SUNTRONCORP_05_17_2006-EX-10.22-MAINTENANCE_AGREEMENT_Section4")
- For contracts without numbered sections, use the page number or paragraph identifier

## Output Format

```json
{
  "status": "answered",
  "answer": "Yes/No or specific duration",
  "evidence_unit_ids": ["ContractName_SectionNumber"],
  "source_contract_ids": ["ContractName"],
  "missing_inputs": [],
  "human_review_required": false
}
```

## Boundary Rules

### Answering Rules
1. **Answer only using the target contract**: Base all answers solely on the content of the contract being reviewed. Do not reference other contracts or external sources.
2. **Cite source-grounded evidence**: When answering, provide specific evidence unit IDs that reference the exact location in the contract where the supporting clause is found.
3. **Return evidence_missing when no supporting clause exists**: If the contract does not contain any clause relevant to the category, set status to "evidence_missing" and provide an empty answer.
4. **Return missing_input when contract_id or category is absent**: If the contract ID or category is not provided, set status to "missing_input" and list the missing inputs.
5. **Return unsupported_scope when the question is outside covered_categories**: If the question does not fall within the four covered categories (Uncapped Liability, Cap on Liability, Liquidated Damages, Warranty Duration), set status to "unsupported_scope".

### Safety Requirements
1. **Do not cite non-target contracts**: Only reference the specific contract being reviewed. Do not bring in clauses from other contracts.
2. **Do not fabricate clauses**: Only report what is actually present in the contract. Do not invent or assume clauses that do not exist.
3. **Do not provide legal advice**: State what the contract says without offering legal opinions or recommendations. Use neutral language.
4. **Do not generate externally sendable legal opinions**: The output should be factual observations about the contract, not legal conclusions that could be used as legal advice.
5. **Route legal advice and high-risk interpretation to human review**: If the question requires legal interpretation or involves high-risk scenarios (e.g., ambiguous clauses, conflicting provisions), set "human_review_required" to true.

### Status Definitions
- **answered**: The contract contains sufficient information to answer the question
- **evidence_missing**: The contract does not contain any clause relevant to the category
- **missing_input**: Required input (contract_id or category) is not provided
- **unsupported_scope**: The question falls outside the covered categories
- **needs_human_review**: The question requires legal interpretation or involves high-risk scenarios
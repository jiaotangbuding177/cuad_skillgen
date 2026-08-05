# SKILL.md

## Contract Basic Info Extraction

## Covered Categories

| Category | Description | Answer Format |
|----------|-------------|---------------|
| Document Name | The name of the contract as stated in the title or header | Contract Name |
| Parties | The two or more parties who signed the contract | Entity or individual names |
| Agreement Date | The date of the contract | Date (mm/dd/yyyy) |
| Effective Date | The date when the contract is effective | Date (mm/dd/yyyy) |
| Expiration Date | On what date will the contract's initial term expire? | Date (mm/dd/yyyy) / Perpetual |

## Review Checklist

### Document Name
- [ ] Locate the contract title in the opening paragraph or header (e.g., "ONLINE HOSTING AGREEMENT", "SPONSORSHIP AGREEMENT", "LICENSE, DEVELOPMENT AND COMMERCIALIZATION AGREEMENT")
- [ ] Check for any amendment or addendum titles that may modify the original agreement
- [ ] Verify the document name matches the contract identifier provided

### Parties
- [ ] Identify all named parties in the opening recital paragraph (typically begins with "This Agreement is entered into by and between")
- [ ] Note each party's full legal name, state of incorporation/organization, and principal place of business
- [ ] Check for defined terms used throughout the contract (e.g., "Array", "Ono", "Licensor", "Licensee")
- [ ] Verify signature blocks for all parties at the end of the document

### Agreement Date
- [ ] Locate the date in the opening paragraph (e.g., "as of the 1st day of June, 1999")
- [ ] Check for date in the signature block (e.g., "IN WITNESS WHEREOF, the parties hereto have executed this Agreement as of June 30, 1999")
- [ ] Note if the agreement date differs from the effective date

### Effective Date
- [ ] Identify the effective date clause (e.g., "effective as of the 1st day of June, 1999")
- [ ] Check for explicit "Effective Date" definition in the definitions section
- [ ] Note if the effective date is the same as the agreement date or different

### Expiration Date
- [ ] Locate the Term section of the contract (typically Section titled "Term" or "Duration")
- [ ] Identify the initial term length (e.g., "12 months", "20 years", "through March 31, 2004")
- [ ] Calculate the expiration date from the effective date if not explicitly stated
- [ ] Check for perpetual or indefinite terms (e.g., "endure indefinitely unless terminated")
- [ ] Note any renewal or extension provisions

## Evidence Extraction Rules

### Locating Evidence
1. **Document Name**: Extract from the first line or header of the contract document. Look for bold, capitalized, or centered text at the top of the first page.

2. **Parties**: Extract from the opening recital paragraph. Pattern: "This Agreement is entered into by and between [Party A], a [jurisdiction] [entity type], and [Party B], a [jurisdiction] [entity type]."

3. **Agreement Date**: Extract from:
   - Opening paragraph (e.g., "as of the 11th day of March, 1999")
   - Signature block date (e.g., "IN WITNESS WHEREOF, the parties have executed this Agreement as of June 30, 1999")
   - Date in the preamble

4. **Effective Date**: Extract from:
   - Explicit "Effective Date" definition in definitions section
   - Opening paragraph stating "effective as of"
   - Term section describing when the term begins

5. **Expiration Date**: Extract from:
   - Term section (e.g., "shall continue for a period of 12 months")
   - Explicit expiration date (e.g., "shall expire on December 31, 2021")
   - Language indicating perpetual duration (e.g., "endure indefinitely")
   - Calculate from effective date + initial term length if not explicitly stated

### Citation Format
- Cite the specific section or paragraph where evidence is found
- Use the contract identifier provided in the case definition
- Quote relevant text directly

## Output Format

```json
{
  "status": "answered",
  "answer": "Contract Name: ONLINE HOSTING AGREEMENT\nParties: Diplomat Direct Marketing Corporation and Tadeo E-Commerce Corp.\nAgreement Date: 06/30/1999\nEffective Date: 06/01/1999\nExpiration Date: 06/01/2000",
  "evidence_unit_ids": ["DYNTEKINC_07_30_1999-EX-10-ONLINE_HOSTING_AGREEMENT"],
  "source_contract_ids": ["DYNTEKINC_07_30_1999-EX-10-ONLINE_HOSTING_AGREEMENT"],
  "missing_inputs": [],
  "human_review_required": false
}
```

## Boundary Rules

### Answering Rules
- **Answer only using the target contract**: Do not reference or cite information from non-target contracts
- **Cite source-grounded evidence**: Every answer must be supported by specific text from the contract
- **Return evidence_missing**: When no supporting clause exists for a requested category
- **Return missing_input**: When contract_id or category is absent from the request
- **Return unsupported_scope**: When the question falls outside the covered categories
- **Route to human review**: For legal advice, high-risk interpretation, or ambiguous contract language

### Safety Requirements
- **Do not cite non-target contracts**: Only use the contract(s) specified in the case definition
- **Do not fabricate clauses**: Never invent contract terms or provisions
- **Do not provide legal advice**: State what the contract says, not what it should say or what legal effect it has
- **Do not generate externally sendable legal opinions**: Output is for internal review purposes only

### Status Values
| Status | When to Use |
|--------|-------------|
| `answered` | All requested information found and extracted |
| `evidence_missing` | No supporting clause exists for a requested category |
| `missing_input` | Contract_id or category is absent from the request |
| `unsupported_scope` | Question falls outside covered categories |
| `needs_human_review` | Ambiguous language, legal interpretation required, or high-risk determination |
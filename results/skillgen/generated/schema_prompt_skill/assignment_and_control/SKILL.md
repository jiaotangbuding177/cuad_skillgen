# SKILL.md - Assignment and Control Review

## Covered Categories

### Change of Control
**Description:** Determines whether one party has the right to terminate or if consent/notice is required from the counterparty when a party undergoes a change of control (e.g., merger, stock sale, transfer of all/substantially all assets, assignment by operation of law).

**Answer Format:** Yes/No

### Anti-Assignment
**Description:** Determines whether consent or notice is required from a party if the contract is assigned to a third party.

**Answer Format:** Yes/No

## Review Checklist

### Change of Control
- [ ] Does the contract contain a provision granting a party the right to terminate upon the other party's change of control?
- [ ] Does the contract require consent or notice from the counterparty before a change of control can occur?
- [ ] Look for clauses specifically mentioning "change of control," "merger," "sale of assets," "change in ownership," or "change in management"
- [ ] Check termination sections for change-of-control-related termination rights
- [ ] Review assignment clauses for change-of-control provisions (some contracts treat mergers/acquisitions differently from other assignments)

### Anti-Assignment
- [ ] Does the contract require consent from the other party before assignment to a third party?
- [ ] Does the contract require notice (but not consent) before assignment?
- [ ] Are there exceptions for assignments to affiliates or successors by merger?
- [ ] Look for clauses containing "assignment," "transfer," "delegate," or "novation"
- [ ] Check if consent cannot be unreasonably withheld or delayed

## Evidence Extraction Rules

### Locating Relevant Clauses
1. **Primary locations for Change of Control provisions:**
   - Termination sections (often labeled "Termination" or "Term")
   - Assignment sections
   - Sections titled "Change of Control" specifically
   - Look for phrases like "change of control," "change in ownership," "merger," "sale of substantially all assets"

2. **Primary locations for Anti-Assignment provisions:**
   - Sections titled "Assignment," "Assignment and Delegation," or "Successors and Assigns"
   - General provisions sections (often Section 12 or similar)
   - Look for phrases like "shall not assign," "prior written consent," "may not transfer"

### Extraction Patterns from Provided Contracts

**Pattern 1: Change of Control as Termination Right**
- Look for: "may terminate this agreement... if there is any change of control, ownership or management"
- Example from LUCIDINC Distributor Agreement: "Lucid may terminate this agreement by giving the Distributor Written Notice if there is any change of control, ownership or management of the Distributor."
- This indicates: **Yes** - one party has termination rights upon change of control

**Pattern 2: Change of Control as Consent/Notice Requirement**
- Look for: "consent will not be unreasonably withheld" combined with change of control language
- Example from MTITECHNOLOGYCORP Reseller Agreement: "McDATA may assign this Agreement to any entity controlled by, controlling, or under common control with McDATA or to any successor by merger... without consent of Reseller."
- This indicates: **No** - no consent/notice required for certain change of control events

**Pattern 3: Anti-Assignment with Consent Requirement**
- Look for: "Neither party will assign this Agreement... without the prior written consent of the other party"
- Example from MTITECHNOLOGYCORP: "Neither party will assign this Agreement or any rights hereunder without the prior written consent of the other party, which consent will not be unreasonably withheld."
- This indicates: **Yes** - consent required for assignment

**Pattern 4: Anti-Assignment with Exceptions**
- Look for: exceptions for mergers, affiliate assignments, or asset sales
- Example from Columbia Laboratories Amendment: "each party may assign or transfer this Agreement without such consent to any Affiliate or to any successor by merger... or upon a sale or other transfer of all or substantially all of such party's assets"
- This indicates: **Yes** - consent required generally, but with exceptions

**Pattern 5: No Assignment Clause**
- Look for: "No Joint Venturer shall be authorized... to sell, or transfer, an interest in the Joint Venture"
- Example from ACCELERATEDTECHNOLOGIES Joint Venture Agreement: "No Joint Venturer shall be authorized or empowered to... sell, or transfer, an interest in the Joint Venture... without the consent of the other Joint Venturer."
- This indicates: **Yes** - consent required

**Pattern 6: Personal Rights / Non-Assignment**
- Look for: "rights granted Company hereunder are personal to it"
- Example from MOSSIMOINC Endorsement Agreement: "The rights granted Company hereunder are personal to it... shall not without the prior written consent of Licensor be transferred or assigned to any other party."
- This indicates: **Yes** - consent required

### Evidence Unit ID Format
Use the contract identifier and section reference, e.g.:
- `LUCIDINC_04_15_2011-EX-10.9-DISTRIBUTOR_AGREEMENT:Section16B`
- `MTITECHNOLOGYCORP_11_16_2004-EX-10.102-Reseller_Agreement_Premier_Addendum:Section12.5`

## Output Format

```json
{
  "status": "answered",
  "answer": "Yes/No",
  "evidence_unit_ids": ["contract_id:section_reference"],
  "source_contract_ids": ["contract_id"],
  "missing_inputs": [],
  "human_review_required": false
}
```

## Boundary Rules

### Answering Rules
1. **Answer only using the target contract** - Do not reference or cite provisions from non-target contracts
2. **Cite source-grounded evidence** - Every answer must reference specific contract language with section numbers
3. **Return evidence_missing** when no supporting clause exists in the contract for the category being reviewed
4. **Return missing_input** when:
   - No contract_id is provided
   - No category is specified
   - The contract document is empty or unreadable
5. **Return unsupported_scope** when the question falls outside the defined covered categories (Change of Control and Anti-Assignment)

### Safety Requirements
1. **Do not cite non-target contracts** - Only use the contract(s) explicitly provided for review
2. **Do not fabricate clauses** - If a provision doesn't exist in the contract, state evidence_missing
3. **Do not provide legal advice** - State factual findings from the contract text only; do not interpret legal consequences or recommend courses of action
4. **Do not generate externally sendable legal opinions** - Output is for internal review purposes only

### Human Review Triggers
Set `human_review_required: true` when:
- The contract language is ambiguous or contradictory regarding assignment/change of control
- The contract uses unusual or non-standard definitions that could affect interpretation
- Multiple provisions conflict with each other
- The question involves legal interpretation beyond simple yes/no extraction
- The contract references external documents not provided for review
- The assignment clause contains complex conditions or exceptions that require legal judgment
# SKILL.md - Term and Termination Review

## Covered Categories

### Renewal Term
**Description:** What is the renewal term after the initial term expires? This includes automatic extensions and unilateral extensions with prior notice.
**Answer Format:** [Successive] number of years/months / Perpetual

### Notice Period to Terminate Renewal
**Description:** What is the notice period required to terminate renewal?
**Answer Format:** Number of days/months/year(s)

### Termination for Convenience
**Description:** Can a party terminate this contract without cause (solely by giving a notice and allowing a waiting period to expire)?
**Answer Format:** Yes/No

## Review Checklist

### Renewal Term
- [ ] Locate the "Term" or "Duration" section of the contract
- [ ] Identify the initial term length
- [ ] Check for automatic renewal clauses (e.g., "shall automatically renew," "shall continue on a year to year basis")
- [ ] Check for unilateral extension options with prior notice
- [ ] Determine if renewal is perpetual or for a fixed successive period
- [ ] Note any conditions that must be met for renewal to occur

### Notice Period to Terminate Renewal
- [ ] Find the termination or renewal notice clause
- [ ] Identify the specific notice period required to prevent automatic renewal
- [ ] Look for phrases like "unless either party gives written notice to terminate at least [X] prior to the end of the term"
- [ ] Determine if the notice period is measured in days, months, or years
- [ ] Note if different notice periods apply to different parties

### Termination for Convenience
- [ ] Search for "termination for convenience," "termination without cause," or similar language
- [ ] Check if either party can terminate by simply giving notice without needing to show breach
- [ ] Look for clauses allowing termination "for any reason" or "at any time"
- [ ] Identify any waiting period required after notice before termination takes effect
- [ ] Note if this right is available to one or both parties

## Evidence Extraction Rules

### Locating Relevant Clauses
1. **Term Section:** Look for sections titled "Term," "Duration," "Term of Agreement," or similar. These typically contain renewal and termination provisions.
2. **Termination Section:** Check for "Termination," "Cancellation," or "Term and Termination" sections.
3. **Renewal Language:** Search for keywords: "renew," "extend," "continue," "year to year," "automatically," "perpetual."
4. **Notice Language:** Search for keywords: "notice," "prior written notice," "days prior," "months prior."

### Extraction Patterns from Contracts
- **Automatic Renewal Pattern:** "This Agreement shall automatically renew for consecutive [period] terms at the end of each [period] unless either party gives at least [X] prior written notice of non-renewal."
- **Year-to-Year Pattern:** "This Agreement shall continue on a year to year basis until terminated by either party by giving written notice at least [X] prior to the end of the then current term."
- **Fixed Renewal Pattern:** "The Initial Term shall automatically be extended for an additional period of [X] unless either party provides written notification of termination at least [X] days prior to end of such period."

### Evidence Unit ID Format
Use the contract name and paragraph/section number (e.g., "BNLFINANCIALCORP_03_30_2007-EX-10.8-OUTSOURCING_AGREEMENT:15.B")

## Output Format

```json
{
  "status": "answered",
  "answer": "string",
  "evidence_unit_ids": ["string"],
  "source_contract_ids": ["string"],
  "missing_inputs": [],
  "human_review_required": false
}
```

**Status Options:**
- `answered`: Successfully found evidence and can provide answer
- `evidence_missing`: No supporting clause exists in the contract
- `missing_input`: Contract_id or category is absent from input
- `unsupported_scope`: Question is outside covered categories
- `needs_human_review`: Legal advice or high-risk interpretation required

## Boundary Rules

### Answering Rules
1. **Answer only using the target contract** - Do not reference or cite non-target contracts
2. **Cite source-grounded evidence** - Every answer must reference specific contract clauses
3. **Return `evidence_missing`** when no supporting clause exists in the contract
4. **Return `missing_input`** when contract_id or category is absent from the input
5. **Return `unsupported_scope`** when the question is outside the three covered categories

### Safety Requirements
1. **Do not cite non-target contracts** - Only use the contract document provided
2. **Do not fabricate clauses** - If evidence doesn't exist, return `evidence_missing`
3. **Do not provide legal advice** - State what the contract says, not what it should say
4. **Do not generate externally sendable legal opinions** - Output is for internal review only
5. **Route to human review** when the question requires legal interpretation or involves high-risk scenarios

### Human Review Triggers
Set `human_review_required: true` when:
- The contract language is ambiguous or contradictory
- The question involves legal advice or interpretation of complex terms
- Multiple reasonable interpretations exist
- The answer could have significant legal or financial consequences
- The contract references external documents not provided
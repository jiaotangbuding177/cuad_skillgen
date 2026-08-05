# SKILL.md - Revenue and Commercial Terms Review

## Covered Categories

### Revenue/Profit Sharing
**Description:** Determine whether one party is required to share revenue or profit with the counterparty for any technology, goods, or services.
**Answer Format:** Yes/No

### Price Restrictions
**Description:** Determine whether there is a restriction on the ability of a party to raise or reduce prices of technology, goods, or services provided.
**Answer Format:** Yes/No

### Minimum Commitment
**Description:** Determine whether there is a minimum order size or minimum amount or units per-time period that one party must buy from the counterparty under the contract.
**Answer Format:** Yes/No

### Volume Restriction
**Description:** Determine whether there is a fee increase or consent requirement, etc. if one party's use of the product/services exceeds certain threshold.
**Answer Format:** Yes/No

## Review Checklist

### Revenue/Profit Sharing
- [ ] Check for explicit revenue sharing percentages or formulas (e.g., "X% of Net Sales", "X% of Gross Receipts")
- [ ] Look for royalty payment structures tied to sales or revenue
- [ ] Identify profit-sharing arrangements or margin splits between parties
- [ ] Check for milestone payments, bonuses, or other contingent payments based on revenue/profit
- [ ] Look for "bounty fees," "commission fees," or similar per-transaction revenue sharing
- [ ] Check for guaranteed minimum royalty payments that function as revenue sharing

### Price Restrictions
- [ ] Check for clauses that fix prices or establish pricing formulas
- [ ] Look for "most favored nation" clauses or price matching requirements
- [ ] Identify restrictions on unilateral price changes (e.g., requiring mutual agreement)
- [ ] Check for price approval rights by one party over the other
- [ ] Look for restrictions on discounts, rebates, or promotional pricing
- [ ] Identify any caps or floors on pricing

### Minimum Commitment
- [ ] Check for minimum purchase quantities or volumes (e.g., "minimum order of X units")
- [ ] Look for minimum revenue guarantees or guaranteed payments
- [ ] Identify minimum advertising or marketing spend commitments
- [ ] Check for minimum number of sales representatives or detailing requirements
- [ ] Look for minimum impression guarantees or delivery commitments
- [ ] Identify minimum performance thresholds (e.g., "at least X details per quarter")

### Volume Restriction
- [ ] Check for tiered pricing that changes based on volume thresholds
- [ ] Look for consent requirements when exceeding certain volumes
- [ ] Identify fee increases triggered by volume thresholds
- [ ] Check for capacity limitations or caps on usage
- [ ] Look for volume-based discount structures that change pricing
- [ ] Identify any penalties or additional costs for exceeding thresholds

## Evidence Extraction Rules

### Locating Evidence
1. **Revenue/Profit Sharing:** Search for sections titled "Royalties," "Revenue Share," "Compensation," "Fees," "Payments," or "Financial Provisions." Look for percentage-based payment structures tied to sales, revenue, or profits.

2. **Price Restrictions:** Search for sections titled "Price," "Pricing," "Fees," "Payment Terms," or "Financial Provisions." Look for language about price changes, approvals needed, or restrictions on modifying prices.

3. **Minimum Commitment:** Search for sections titled "Minimum Commitment," "Guarantee," "Minimum Order," "Forecast," "Obligations," or "Performance Requirements." Look for specific numerical minimums or guaranteed amounts.

4. **Volume Restriction:** Search for sections titled "Volume," "Threshold," "Tier," "Overages," or "Additional Fees." Look for language about what happens when volumes exceed certain levels.

### Extraction Patterns
- Look for defined terms like "Net Sales," "Gross Receipts," "Available Margin," "Royalty," "Guaranteed Minimum Royalty"
- Identify specific percentages (e.g., "10% of Net Sales," "50% of Gross Margin")
- Look for dollar amounts tied to minimums or thresholds
- Check exhibits, schedules, and appendices for detailed pricing or volume information
- Note any redacted or confidential treatment amounts as evidence of the existence of terms

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
- **missing_input:** Contract_id or category is absent from the input
- **unsupported_scope:** The question falls outside the covered categories
- **needs_human_review:** Legal advice or high-risk interpretation required

## Boundary Rules

### Answering Rules
1. **Answer only using the target contract** - Do not reference or cite contracts not provided in the input
2. **Cite source-grounded evidence** - When answering "Yes," provide specific section references and quote relevant language
3. **Return evidence_missing** - When no supporting clause exists in the contract for the category
4. **Return missing_input** - When contract_id or category is absent from the input
5. **Return unsupported_scope** - When the question is outside the four covered categories
6. **Route to human review** - For legal advice, high-risk interpretation, or ambiguous situations requiring legal judgment

### Safety Requirements
1. **Do not cite non-target contracts** - Only use evidence from the contract(s) provided
2. **Do not fabricate clauses** - Only reference language that actually exists in the provided contracts
3. **Do not provide legal advice** - Do not interpret legal consequences or provide recommendations
4. **Do not generate externally sendable legal opinions** - Output is for internal review purposes only
5. **Do not speculate** - If evidence is unclear or missing, return evidence_missing rather than guessing

### Evidence Unit ID Format
Use the format: `contract_id:section_number` (e.g., `GluMobileInc_20070319_S-1A_EX-10.09:7` for Section 7 of the Glu Mobile contract)
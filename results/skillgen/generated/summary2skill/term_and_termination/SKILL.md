# SKILL.md - Term and Termination Review

## Covered Categories

### Renewal Term
- **Discovery frequency**: 31% of contracts (95/306)
- **Common patterns**: Automatic renewal for fixed periods, perpetual/indefinite terms, conditional renewals based on performance thresholds, and unilateral extension rights

### Notice Period to Terminate Renewal
- **Discovery frequency**: 17% of contracts (53/306)
- **Common patterns**: Written notice required 30-90 days before term end, notice periods ranging from 30 days to 1 year, and notice of non-renewal to prevent automatic extension

### Termination for Convenience
- **Discovery frequency**: 25% of contracts (78/306)
- **Common patterns**: Either party may terminate without cause with written notice (30-90 days common), termination available after initial term, and some contracts allow termination at any time

## Common Patterns

### Renewal Term
1. **Automatic renewal for successive fixed terms**: "The agreement automatically renews for successive one-year terms unless a party gives notice of non-renewal at least 30 days before expiration."
2. **Perpetual/indefinite term**: Agreement continues indefinitely until terminated by either party with notice.
3. **Conditional renewal**: Renewal contingent on meeting performance thresholds (e.g., net sales, minimum payments) or mutual written agreement.

### Notice Period to Terminate Renewal
1. **Standard notice periods (30-90 days)**: "Either party must give at least 60 days' written notice before the end of the current term to prevent automatic renewal."
2. **Extended notice periods (120+ days)**: "Either party must give at least six months' written notice prior to the end of the then-current term to terminate the renewal."
3. **Written notice requirement**: Notice of non-renewal must be in writing and delivered within specified timeframe.

### Termination for Convenience
1. **Standard termination for convenience**: "Either party may terminate the agreement without cause by providing at least 90 days' prior written notice."
2. **Termination after initial term**: Termination for convenience available only after a minimum initial term has elapsed.
3. **Unilateral termination right**: Only one party (e.g., franchisor, Bank of America) has the right to terminate for convenience.

## Review Checklist

### Renewal Term
- [ ] Does the contract specify an automatic renewal mechanism?
- [ ] Is renewal conditional on performance metrics or mutual agreement?
- [ ] Is there a perpetual/indefinite term with no fixed renewal?
- [ ] Does either party have unilateral extension rights?

### Notice Period to Terminate Renewal
- [ ] What is the notice period required to prevent automatic renewal?
- [ ] Is written notice required?
- [ ] Is the notice period reasonable (typically 30-90 days)?
- [ ] Does the notice period apply to both parties equally?

### Termination for Convenience
- [ ] Can either party terminate without cause?
- [ ] What is the notice period for termination for convenience?
- [ ] Is termination for convenience available immediately or after an initial term?
- [ ] Are there any penalties or fees for termination for convenience?

## Evidence Extraction Rules

### Renewal Term
- **Locate**: Search for "renew", "extend", "perpetual", "automatic", "successive", "term"
- **Extract**: The specific renewal mechanism (automatic, conditional, perpetual), duration of renewal term, and any conditions for renewal
- **Example**: "The agreement automatically renews for successive one-year terms unless a party gives notice of non-renewal at least 30 days before expiration."

### Notice Period to Terminate Renewal
- **Locate**: Search for "notice", "non-renewal", "termination", "days", "written notice"
- **Extract**: The exact number of days required for notice, whether written notice is required, and to whom notice must be given
- **Example**: "Either party must give at least 60 days' written notice before the end of the current term to prevent automatic renewal."

### Termination for Convenience
- **Locate**: Search for "terminate without cause", "termination for convenience", "without cause", "any reason", "at any time"
- **Extract**: Which parties have the right, notice period required, any restrictions (e.g., after initial term), and any penalties
- **Example**: "Either party may terminate the agreement without cause by providing at least 90 days' prior written notice."

## Output Format

```json
{
  "status": "complete" | "incomplete" | "needs_review",
  "answer": "Summary of findings for each category",
  "evidence_unit_ids": ["id1", "id2", ...],
  "source_contract_ids": ["contract1", "contract2", ...],
  "missing_inputs": ["Renewal Term", "Notice Period to Terminate Renewal", "Termination for Convenience"],
  "human_review_required": true | false
}
```

## Boundary Rules

### What the skill SHOULD do:
- Identify and extract renewal terms, notice periods, and termination for convenience clauses
- Flag contracts with unusual or extreme notice periods (e.g., >180 days)
- Note when termination for convenience is unilateral (only one party)
- Identify conditional renewals that depend on performance metrics
- Highlight perpetual/indefinite terms that may require special attention

### What the skill SHOULD NOT do:
- Evaluate the fairness or reasonableness of terms (e.g., whether 30 days is "too short")
- Provide legal advice or recommend specific actions
- Interpret ambiguous language without flagging for human review
- Assess whether performance thresholds are achievable
- Determine if a notice period is "adequate" under applicable law
- Make judgments about termination penalties or fees (flag for human review)
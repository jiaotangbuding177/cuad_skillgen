# SKILL.md - Contract Review: Term and Termination

## Overview

This skill enables you to systematically review contracts to extract key information about contract duration, renewal mechanisms, and termination rights. Specifically, it focuses on three critical categories: Renewal Term, Notice Period to Terminate Renewal, and Termination for Convenience. These provisions determine how long a contract lasts, how it can be extended or ended, and whether a party can walk away without cause.

## Review Steps

### Step 1: Locate the Term and Termination Section

First, find the section of the contract that addresses term, duration, and termination. Common section titles include:
- "Term"
- "Term of Agreement"
- "Duration"
- "Term and Termination"
- "Effective Date and Term"

**What to look for:** Scan the table of contents or section headings. In the provided contracts, these provisions appear in sections like "15. TERM" (BNLFINANCIALCORP), "2. TERM OF AGREEMENT" (IMAGEWARESYSTEMSINC), "10. TERM AND TERMINATION" (EdietsComInc), and "7. TERM OF THE AGREEMENT AND TERMINATION" (DataCallTechnologies).

### Step 2: Identify the Initial Term

Determine the length of the initial term before any renewal provisions apply.

**What to look for:** Look for language like "initial term," "Initial Term," or "first year." Note the specific duration stated.

**Examples from contracts:**
- "The initial term ('Initial Term') of this Agreement shall be for one year commencing on the 1st day of May, 2006" (BNLFINANCIALCORP)
- "XIMAGE's obligations hereunder shall become effective upon the 'Effective Date' and, unless sooner terminated as provided herein, shall remain in full force and effect for at least one year thereafter" (IMAGEWARESYSTEMSINC)
- "shall remain effective for two (2) years from and after the Effective Date (the 'Initial Term')" (EdietsComInc)
- "the term of this letter Agreement shall continue for twenty-four (24) months with the effective date" (DataCallTechnologies)

### Step 3: Determine the Renewal Term

Identify what happens after the initial term expires. Look for automatic renewal, perpetual continuation, or the need for affirmative action to renew.

**What to look for:** Keywords include "automatically renew," "year to year basis," "Extended Term," "Renewal Terms," "successive terms," "perpetual," or "unless either party gives notice."

**Answer Format:** [Successive] number of years/months / Perpetual

**Examples from contracts:**
- "Unless either party gives written notice to terminate this Agreement at least six (6) months prior to the end of said Initial Term, this Agreement shall continue on a year to year basis ('Extended Term(s)')" → **1 year** (BNLFINANCIALCORP)
- "This Agreement shall automatically renew for consecutive one (1) year terms at XIMAGE's then prevailing rates at the end of each one (1) year term" → **1 year** (IMAGEWARESYSTEMSINC)
- "This agreement shall automatically renew for additional successive terms of twelve (12) months each at the end of the Initial Term ('Renewal Terms')" → **12 months** (EdietsComInc)
- "The Initial Term shall automatically be extended for an additional period of half a year unless either party provides the other party with written notification of termination" → **6 months** (DataCallTechnologies)

### Step 4: Identify the Notice Period to Terminate Renewal

Find the notice period required to prevent automatic renewal or to terminate at the end of a term.

**What to look for:** Look for phrases like "written notice," "prior written notice," "days prior to," "months prior to" in conjunction with termination or non-renewal.

**Answer Format:** Number of days/months/year(s)

**Examples from contracts:**
- "at least six (6) months prior to the end of said Initial Term" → **6 months** (BNLFINANCIALCORP)
- "unless either party gives at least sixty (60) days prior written notice of the non-renewal of this Agreement" → **60 days** (IMAGEWARESYSTEMSINC)
- "unless either party notifies the other in writing at least sixty (60) days prior to the end of the Initial Term" → **60 days** (EdietsComInc)
- "unless either party provides the other party with written notification of termination of the letter Agreement at least 60 days prior to end of such period" → **60 days** (DataCallTechnologies)

### Step 5: Determine Termination for Convenience

Check whether either party can terminate the contract without cause (i.e., without needing to show a breach or other fault).

**What to look for:** Look for language like "terminate without cause," "termination for convenience," "at will," "solely by giving notice," or "without cause." If the contract only allows termination for cause (breach, insolvency, etc.), then the answer is "No."

**Answer Format:** Yes/No

**Examples from contracts:**
- BNLFINANCIALCORP: Section 15(B) allows either party to terminate by giving six months' notice at the end of any Extended Term. This is effectively termination for convenience with notice. → **Yes** (but only at term end)
- IMAGEWARESYSTEMSINC: Section 2 allows non-renewal by giving 60 days' notice, but Section 13 only allows termination for cause (breach, non-payment, bankruptcy). No general termination for convenience. → **No**
- EdietsComInc: Section 10.1 allows either party to prevent renewal by giving 60 days' notice, but Section 10.2 only allows termination for material breach. No general termination for convenience. → **No**
- DataCallTechnologies: Section 7.2 only allows termination for material breach. No termination for convenience. → **No**

**Important nuance:** Some contracts allow termination for convenience only at the end of a term (by not renewing), but not mid-term. Distinguish between "non-renewal" (which is essentially termination for convenience at term end) and "termination for convenience" (which allows mid-term cancellation without cause).

## Output Format

For each contract reviewed, produce a structured output as follows:

```markdown
## Contract Review: [Contract Name]

### Renewal Term
- **Answer:** [Successive] [number] [years/months] / Perpetual
- **Evidence:** [Quote the relevant clause]
- **Notes:** [Any additional context, e.g., "Automatic renewal unless notice given"]

### Notice Period to Terminate Renewal
- **Answer:** [Number] [days/months/year(s)]
- **Evidence:** [Quote the relevant clause]
- **Notes:** [e.g., "Notice must be in writing and sent by certified mail"]

### Termination for Convenience
- **Answer:** Yes / No
- **Evidence:** [Quote the relevant clause or explain absence]
- **Notes:** [e.g., "Only at end of term by not renewing" or "No termination for convenience clause exists"]
```

## Common Patterns and Pitfalls

1. **Automatic vs. Perpetual:** "Automatic renewal" means the contract continues for successive fixed terms. "Perpetual" means it continues indefinitely until terminated. Distinguish carefully.

2. **Notice Period Timing:** Notice periods are often tied to the end of the current term. For example, "at least 6 months prior to the end of the then current Extended Term" means you must give notice well before the term ends.

3. **Termination for Convenience vs. For Cause:** Many contracts only allow termination for cause (breach, bankruptcy, non-payment). If no "without cause" or "for convenience" clause exists, the answer is "No."

4. **Non-Renewal vs. Termination:** Non-renewal (letting the contract expire) is different from mid-term termination. Some contracts allow non-renewal without cause but do not allow mid-term termination without cause.

5. **Survival Clauses:** Check if certain obligations (confidentiality, indemnification) survive termination. This does not affect the termination analysis but is important context.
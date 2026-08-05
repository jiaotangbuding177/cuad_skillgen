# SKILL.md: Liability and Indemnity Contract Review

## Overview

This skill enables you to systematically review contracts for key liability and indemnity provisions. You will analyze contracts to determine whether liability is capped or uncapped, whether liquidated damages or termination fees exist, and the duration of any warranty periods. The skill covers four specific categories: Uncapped Liability, Cap on Liability, Liquidated Damages, and Warranty Duration.

## Review Steps

### Step 1: Identify All Liability-Related Clauses

Scan the contract for the following sections:
- **Limitation of Liability** or **Limitation of Liability** clauses
- **Indemnification** or **Indemnity** clauses
- **Warranty** clauses (especially duration of warranties)
- **Liquidated Damages** clauses
- **Damages** or **Remedies** clauses
- **Termination Fees** provisions
- Any sections titled **Cap on Liability**, **Liability Cap**, or similar

### Step 2: Analyze Uncapped Liability

**What to look for:**
- Any statement that liability is "unlimited" or "uncapped"
- Indemnification provisions that do not reference a cap
- IP infringement indemnification clauses that explicitly state liability is not capped
- Breach of confidentiality obligations that are excluded from liability caps
- Fraud, gross negligence, or willful misconduct exclusions from liability caps
- Any provision stating "notwithstanding anything to the contrary" that creates uncapped liability

**Patterns from contracts:**
- In the **Co-Hosting Agreement** (Beyond.com), Section 10 states: "EXCEPT FOR CLAIMS UNDER SECTION 9 HEREOF, THE LIABILITY OF A PARTY TO THE OTHER FOR DIRECT DAMAGES SHALL NOT EXCEED FIFTEEN MILLION DOLLARS." This creates a cap, but Section 9 (indemnification) is excluded from the cap, meaning indemnification claims are uncapped.
- In the **Outsourcing Agreement** (OasysMobile), Section 11 states: "IN NO EVENT SHALL E.PIPHANY'S LIABILITY HEREUNDER EXCEED THE SUM TOTAL OF PAYMENTS MADE BY HSNS UNDER THE INITIAL TERM OF THIS AGREEMENT." This is a cap, but check if any exceptions exist.

**Answer Format:** Yes/No
- Answer "Yes" if any party's liability is uncapped for any type of breach
- Answer "No" if all liability is capped (including indemnification)

### Step 3: Analyze Cap on Liability

**What to look for:**
- A specific monetary cap on liability (e.g., "liability shall not exceed $X")
- A cap based on fees paid (e.g., "liability shall not exceed the fees paid in the preceding 12 months")
- A multiplier of fees (e.g., "liability shall not exceed 3x the fees paid")
- Time limitations for bringing claims (statute of limitations shortening)
- Exclusions from the cap (e.g., "except for indemnification obligations")
- Any provision that limits the types of damages recoverable

**Patterns from contracts:**
- **Co-Hosting Agreement** (Beyond.com): Section 10 caps liability at $15,000,000 for direct damages, but excludes indemnification claims under Section 9.
- **Outsourcing Agreement** (Paratek): Section 13.4 contains a limitation of liability clause. Look for specific monetary caps or fee-based caps.
- **Supply Agreement** (Bellicum): Check for liability caps in the limitation of liability section.

**Answer Format:** Yes/No
- Answer "Yes" if there is any cap on liability (monetary cap, fee-based cap, or time limitation)
- Answer "No" if there is no cap at all

### Step 4: Analyze Liquidated Damages

**What to look for:**
- A clause that specifies a fixed amount of damages for breach
- Language such as "liquidated damages," "agreed damages," or "fixed damages"
- Termination fees or early termination penalties
- Clauses that state damages are "impracticable or extremely difficult to ascertain"
- Provisions stating the amount is a "reasonable estimate" of damages
- Any formula for calculating damages that is predetermined

**Patterns from contracts:**
- **Maintenance Agreement** (SuntronCorp): Section 4 explicitly states: "an amount equal to the lesser of (i) the full amount of each Required Capital Contribution that has not been made by the Investor and (ii) the then-outstanding balance of the Obligations, represents a reasonable estimate of the damages... and (b) such lesser amount will be the full, agreed and liquidated damages resulting from the occurrence of any Maintenance Event of Default hereunder."
- **Co-Hosting Agreement** (Beyond.com): Exhibit A, Part 2 defines "Liquidated Damages Amount" as a formula based on fees paid and revenue targets.
- **Endorsement Agreement** (Teardrop Golf): Section 16 states past due payments "shall bear interest at a rate of two percent (2%) per month OR the maximum rate permissible by law, whichever is less" - this is an interest penalty, not liquidated damages.

**Answer Format:** Yes/No
- Answer "Yes" if there is a liquidated damages clause or termination fee
- Answer "No" if there is no such provision

### Step 5: Analyze Warranty Duration

**What to look for:**
- Express warranty periods stated in months or years
- Language such as "warrants for a period of X months/years"
- Warranty periods for technology, products, or services
- Distinguish between different warranty types (e.g., software warranty vs. services warranty)
- Look for the longest warranty period if multiple warranties exist

**Patterns from contracts:**
- **Application Development Agreement** (ClickstreamCorp): Section 8(a) states "the Application will be free from programming errors and defects in workmanship and materials" during the "Support Period." Exhibit A, Section E states: "90 days warranty (bugfixing) support is included."
- **Outsourcing Agreement** (OasysMobile): Section 4.1 states: "E.piphany warrants that for a period of one (1) year from Effective Date, the Application as used within the scope of this Agreement will perform substantially in accordance with the functions described in the Documentation."
- **Supply Agreement** (Bellicum): Check for warranty duration in the warranty section.

**Answer Format:** Number of months or years
- State the specific duration (e.g., "90 days," "1 year," "2 years")
- If multiple warranties exist, state the longest applicable warranty period
- If no warranty period is specified, state "Not specified"

## Output Format

For each contract reviewed, provide the following structured output:

```markdown
## Contract Review: [Contract Name]

### Uncapped Liability
- **Answer:** [Yes/No]
- **Evidence:** [Quote or describe the relevant clause(s)]
- **Analysis:** [Brief explanation of why this answer was chosen]

### Cap on Liability
- **Answer:** [Yes/No]
- **Evidence:** [Quote or describe the relevant clause(s)]
- **Analysis:** [Brief explanation of why this answer was chosen, including the cap amount if applicable]

### Liquidated Damages
- **Answer:** [Yes/No]
- **Evidence:** [Quote or describe the relevant clause(s)]
- **Analysis:** [Brief explanation of why this answer was chosen]

### Warranty Duration
- **Answer:** [Number of months or years, or "Not specified"]
- **Evidence:** [Quote or describe the relevant clause(s)]
- **Analysis:** [Brief explanation of why this answer was chosen]
```

## Key Considerations

1. **Indemnification clauses often create uncapped liability** - Even if there is a general liability cap, indemnification provisions are frequently excluded from that cap, creating uncapped liability for certain types of claims.

2. **IP infringement indemnification is commonly uncapped** - Many contracts explicitly state that liability for IP infringement is not subject to the general liability cap.

3. **Breach of confidentiality obligations** - These are also commonly excluded from liability caps.

4. **Liquidated damages must be distinguished from penalties** - Look for language indicating the amount is a "reasonable estimate" of damages, not a penalty.

5. **Warranty duration may vary by product/service type** - Software warranties are often 90 days to 1 year, while services warranties may be shorter.

6. **Termination fees** - These are considered liquidated damages for the purpose of this review.

7. **Time limitations on claims** - A clause that limits the time period for bringing claims (e.g., "no action may be brought more than 2 years after the cause of action accrues") constitutes a cap on liability.
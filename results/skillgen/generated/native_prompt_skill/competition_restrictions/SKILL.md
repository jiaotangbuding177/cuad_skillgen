# SKILL.md - Competition Restrictions Contract Review

## Overview

This skill enables systematic identification and analysis of competition-related restrictions in commercial contracts. It covers seven distinct categories of competitive restrictions: Most Favored Nation clauses, Non-Compete provisions, Exclusivity arrangements, No-Solicit of Customers, Competitive Restriction Exceptions, No-Solicit of Employees, and Non-Disparagement clauses.

The skill is designed for reviewing a wide range of contract types including franchise agreements, cooperation agreements, development agreements, co-branding agreements, endorsement agreements, outsourcing agreements, and collaboration agreements.

## Review Steps

### Step 1: Initial Contract Assessment
1. Identify the contract type and parties involved
2. Determine the primary business relationship (franchisor/franchisee, licensor/licensee, service provider/client, strategic partner)
3. Note the contract duration and any post-termination obligations
4. Scan for sections titled "Restrictions," "Non-Compete," "Exclusivity," "Standstill," or similar

### Step 2: Most Favored Nation Analysis
1. Search for language granting the buyer rights to better terms offered to third parties
2. Look for phrases like "most favored nation," "most favorable," "better terms," "more favorable terms"
3. Check pricing and commercial terms sections
4. Examine any "most favored customer" or "most favored licensee" provisions

### Step 3: Non-Compete Analysis
1. Search for restrictions on competing with the counterparty
2. Look for language about operating in certain geographies, businesses, or technology sectors
3. Check for "standstill" provisions that limit competitive activities
4. Examine post-termination restrictions on competitive activities

### Step 4: Exclusivity Analysis
1. Search for exclusive dealing commitments
2. Look for requirements to procure all "requirements" from one party
3. Check for prohibitions on licensing or selling to third parties
4. Examine restrictions on collaborating with other parties
5. Note whether exclusivity applies during the contract, after termination, or both

### Step 5: No-Solicit of Customers Analysis
1. Search for restrictions on contracting with or soliciting customers/partners
2. Look for limitations on advertising or marketing to certain areas
3. Check for restrictions on direct solicitation of customers
4. Note whether restrictions apply during the contract, after termination, or both

### Step 6: Competitive Restriction Exception Analysis
1. Identify any exceptions or carveouts to non-compete, exclusivity, or no-solicit provisions
2. Look for language like "provided that," "notwithstanding," "except," "carveout"
3. Check for specific exclusions for certain activities, geographies, or time periods
4. Note any "permitted activities" sections

### Step 7: No-Solicit of Employees Analysis
1. Search for restrictions on soliciting or hiring employees/contractors
2. Look for language about "solicit," "hire," "recruit," "induce to leave"
3. Check whether restrictions apply to employees, contractors, or both
4. Note whether restrictions apply during the contract, after termination, or both

### Step 8: Non-Disparagement Analysis
1. Search for requirements not to disparage the counterparty
2. Look for language about "disparage," "defame," "impugn," "negative statements"
3. Check for exceptions (e.g., legal proceedings, regulatory requirements)
4. Note the duration of non-disparagement obligations

## What to Look For in Contracts

### Most Favored Nation Patterns
- **Direct MFN clauses**: "If Party B offers more favorable terms to any third party, Party A shall be entitled to those better terms"
- **Most favorable treatment**: "Party B guarantees that the Driver User will enjoy the most favorable treatment" (as seen in the iDreamSky/Didi collaboration agreement)
- **Pricing parity**: Requirements that pricing to one party be no less favorable than pricing to others

### Non-Compete Patterns
- **Standstill provisions**: Restrictions on acquiring securities, soliciting proxies, making proposals (as seen in the HC2 Holdings cooperation agreement)
- **Geographic restrictions**: Limitations on operating in certain areas
- **Business sector restrictions**: Prohibitions on competing in specific industries or technology fields
- **Post-termination restrictions**: Continued non-compete obligations after contract ends
- **Examples from contracts**:
  - HC2 Agreement: "none of the MG Capital Parties...will...seek or submit...nomination(s) in furtherance of a 'contested solicitation'"
  - Pizza Fusion Agreement: Section 17 "Restrictions on Competition"
  - Dassault/PlanetCAD Agreement: "PlanetCAD shall not market any services to Customers without the prior written approval of Dassault Systemes"

### Exclusivity Patterns
- **Exclusive dealing**: Requirements to purchase all needs from one supplier
- **Exclusive sponsorship**: "Snap will not grant any third party any right to sponsor any products or services in the Exclusive Category" (as seen in the Snap/United Airlines co-branding agreement)
- **Exclusive provider**: Appointment as "exclusive provider of Care Management Services" (as seen in the Sykes/HPS outsourcing agreement)
- **Exclusive endorsement rights**: "the exclusive right to utilize Ogle's name in connection with the advertisement, promotion and sale of the Teardrop Putter" (as seen in the endorsement agreement)
- **Preemptive rights**: "Party A shall have a preemptive right to carry out mobile game services with Party B" (as seen in the iDreamSky/Telecom agreement)
- **Exclusive category restrictions**: Limitations on granting rights to third parties in defined categories

### No-Solicit of Customers Patterns
- **Geographic solicitation limits**: Restrictions on advertising or soliciting outside defined areas
- **Direct solicitation prohibitions**: "You agree not to...engage in direct solicitation of customers outside of the Delivery/Catering and Advertising Area" (as seen in the Pizza Fusion franchise agreement)
- **Customer solicitation restrictions**: Limitations on marketing to customers of the counterparty
- **Post-termination customer restrictions**: Continued limitations after contract ends

### Competitive Restriction Exception Patterns
- **Permitted activities exceptions**: "Nothing in this Agreement shall prohibit or restrict the MG Capital Parties from: (A) communicating privately with the Board" (as seen in the HC2 Agreement)
- **Fiduciary duty exceptions**: "nothing in this Agreement shall be deemed to restrict in any way the ability of...directors...from exercising any of his rights, powers and privileges as directors"
- **Legal compliance exceptions**: "taking any action necessary to comply with any law, rule or regulation"
- **Independent development exceptions**: "PlanetCAD may market new functions and services...provided PlanetCAD obtained the contact information...from an independent source"
- **Non-exclusivity statements**: "This Agreement is not an exclusive services agreement" (as seen in the Dassault/PlanetCAD Agreement)

### No-Solicit of Employees Patterns
- **Direct hiring restrictions**: Prohibitions on hiring employees from the counterparty
- **Solicitation prohibitions**: Restrictions on inducing employees to leave
- **Contractor restrictions**: Limitations on soliciting or hiring contractors
- **Duration**: Whether restrictions apply during contract, after termination, or both
- **Note**: None of the provided contracts contained explicit employee non-solicit provisions, but these are common in commercial agreements

### Non-Disparagement Patterns
- **Mutual non-disparagement**: "Each of the Parties covenants and agrees that...neither Party...shall...publicly disparage, impugn, make ad hominem attacks on or otherwise defame or slander" (as seen in the HC2 Agreement)
- **Scope of prohibition**: Covers written, oral, electronic communications
- **Covered persons**: Extends to subsidiaries, affiliates, officers, directors, employees
- **Exceptions**: Legal proceedings, fiduciary duties, legal process compliance
- **Duration**: Often tied to the contract term or standstill period

## Output Format

For each contract reviewed, provide results in the following format:

```json
{
  "contract_id": "[Contract identifier]",
  "review_date": "[Date]",
  "categories": {
    "most_favored_nation": {
      "present": true/false,
      "details": "[Description of clause found, including section reference]",
      "text": "[Relevant excerpt from contract]"
    },
    "non_compete": {
      "present": true/false,
      "details": "[Description of non-compete provisions]",
      "text": "[Relevant excerpt]"
    },
    "exclusivity": {
      "present": true/false,
      "details": "[Description of exclusive dealing or exclusivity provisions]",
      "text": "[Relevant excerpt]"
    },
    "no_solicit_customers": {
      "present": true/false,
      "details": "[Description of customer solicitation restrictions]",
      "text": "[Relevant excerpt]"
    },
    "competitive_restriction_exception": {
      "present": true/false,
      "details": "[Description of exceptions or carveouts]",
      "text": "[Relevant excerpt]"
    },
    "no_solicit_employees": {
      "present": true/false,
      "details": "[Description of employee solicitation restrictions]",
      "text": "[Relevant excerpt]"
    },
    "non_disparagement": {
      "present": true/false,
      "details": "[Description of non-disparagement provisions]",
      "text": "[Relevant excerpt]"
    }
  },
  "summary": "[Brief overall assessment of competition restrictions in the contract]"
}
```

### Example Output

```json
{
  "contract_id": "HC2HOLDINGS,INC_05_14_2020-EX-10.1-COOPERATION_AGREEMENT",
  "review_date": "2024-01-15",
  "categories": {
    "most_favored_nation": {
      "present": false,
      "details": "No most favored nation clause found",
      "text": ""
    },
    "non_compete": {
      "present": true,
      "details": "Section 3 (Standstill Provisions) contains extensive restrictions on competitive activities including limitations on acquiring securities, soliciting proxies, making proposals, and engaging in contested solicitations",
      "text": "The MG Capital Parties hereby agree that during the Standstill Period, none of the MG Capital Parties...will...seek or submit...nomination(s) in furtherance of a 'contested solicitation' for the appointment, election or removal of directors"
    },
    "exclusivity": {
      "present": true,
      "details": "Section 3 contains exclusive dealing provisions requiring the MG Capital Parties to vote in favor of Board-nominated directors and against removal of directors",
      "text": "they shall vote all shares of Common Stock...in favor of all directors nominated by the Board for election and against the removal of any member of the Board"
    },
    "no_solicit_customers": {
      "present": false,
      "details": "No customer solicitation restrictions found",
      "text": ""
    },
    "competitive_restriction_exception": {
      "present": true,
      "details": "Section 3(b) provides exceptions for private communications with the Board, private communications with stockholders, legal compliance, and fiduciary duties of directors",
      "text": "nothing in this Agreement shall prohibit or restrict the MG Capital Parties from: (A) communicating privately with the Board... (B) communicating privately with stockholders... (C) taking any action necessary to comply with any law"
    },
    "no_solicit_employees": {
      "present": false,
      "details": "No employee solicitation restrictions found",
      "text": ""
    },
    "non_disparagement": {
      "present": true,
      "details": "Section 6 (Mutual Non-Disparagement) contains mutual non-disparagement obligations during the Standstill Period",
      "text": "neither Party...shall in any way...publicly disparage, impugn, make ad hominem attacks on or otherwise defame or slander...the other Party"
    }
  },
  "summary": "This cooperation agreement contains significant standstill/non-compete provisions, exclusive voting arrangements, and mutual non-disparagement obligations, with exceptions for private communications and fiduciary duties"
}
```
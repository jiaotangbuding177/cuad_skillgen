# SKILL.md - Legal Governance Contract Review

## Overview

This skill enables systematic review of contracts to identify and extract key governance provisions related to governing law, audit rights, and insurance requirements. The skill focuses on three specific categories that are fundamental to understanding the legal framework and risk allocation in any contractual relationship.

## Review Categories and What to Look For

### 1. Governing Law

**What to Look For:**
- A dedicated "Governing Law" clause (often a separate section near the end of the contract)
- Language such as "governed by," "construed in accordance with," or "interpreted under"
- References to specific state or country laws
- May include choice of venue or jurisdiction provisions

**Common Patterns Observed in Contracts:**
- **US State Law:** "This Agreement shall be governed by and construed in accordance with the laws of the State of [State Name]" (e.g., New York, Delaware, California)
- **Non-US Law:** "governed by the laws of [Country]" (e.g., England, Israel, Australia)
- **With or without conflicts of law provisions:** Some contracts include "without regard to principles of conflicts of laws" while others omit this
- **Combined with jurisdiction clauses:** Often paired with exclusive jurisdiction in specific courts

**Examples from Provided Contracts:**
- "This Agreement has been made in the State of California and shall be governed by and construed in accordance with the laws thereof" (Holiday RV/AGI Endorsement Agreement)
- "This Agreement is governed by and construed in accordance with English law" (WPP Service Agreement)
- "This Agreement shall be governed by and construed in accordance with the laws of the State of Israel" (Todos Medical Marketing Agreement)
- "The laws of the State of New York (without giving effect to its conflicts of law principles) govern all matters arising out of or relating to this Agreement" (NeuroBo Manufacturing Agreement)

### 2. Audit Rights

**What to Look For:**
- Explicit language granting a party the right to audit books, records, or physical locations
- Terms like "audit," "inspection," "books and records," "examine"
- Conditions for audit (notice period, frequency, scope)
- Who bears the cost of audit

**Common Patterns Observed in Contracts:**
- **Financial/royalty audits:** Right to audit accounting records related to payments, royalties, or sales
- **Quality/compliance inspections:** Right to inspect manufacturing facilities or processes
- **Notice requirements:** Typically 5-30 days' written notice
- **Frequency limitations:** Often limited to once per calendar year
- **Cost allocation:** Usually at the requesting party's expense, unless material discrepancy found

**Examples from Provided Contracts:**
- **Yes - Financial Audit:** "Todos shall have the right to have an inspection and audit of all the relevant accounting and sales books and records of Reseller conducted by an independent auditor... Any such audit shall be upon five (5) days prior written notice" (Todos Medical Marketing Agreement)
- **Yes - Quality Inspection:** "Todos shall have the right to conduct periodic on-site inspections to ensure the quality control of the cancer screening processes" (Todos Medical Marketing Agreement)
- **Yes - Manufacturing Inspection:** "NeuroBo may, at its cost and expense, inspect Dong-A's manufacturing facilities where the Licensed Products are manufactured" (NeuroBo Manufacturing Agreement)
- **Yes - Royalty Audit:** "IntriCon must make all such records available for inspection, copying and audit by an independent auditor... Audits will be limited to one audit in any calendar year" (IntriCon/Dynamic Hearing Strategic Alliance Agreement)
- **No - No audit provisions found:** Holiday RV/AGI Endorsement Agreement, WPP Service Agreement, Allison Transmission Cooperation Agreement

### 3. Insurance

**What to Look For:**
- Explicit requirement for one party to maintain insurance for the benefit of the other
- Terms like "insurance," "maintain insurance," "shall carry insurance"
- Types of insurance mentioned (liability, property, professional, D&O)
- Coverage amounts or limits
- Whether insurance is for the benefit of the counterparty

**Common Patterns Observed in Contracts:**
- **General liability insurance:** Required for activities under the agreement
- **Directors and officers insurance:** For executive protection
- **Employee benefits insurance:** Health, life, disability coverage for employees
- **Professional indemnity:** For professional services
- **"Commercially reasonable amounts":** Sometimes specified without exact limits

**Examples from Provided Contracts:**
- **Yes - General Insurance:** "Each party shall carry appropriate and commercially reasonable amounts of insurance adequate for the activities detailed in this Agreement, as well as sufficient levels of all legally mandated insurance, if any" (Todos Medical Marketing Agreement)
- **Yes - Employee Benefits Insurance:** "The Executive is entitled to membership of a Group income protection plan and life assurance cover, which will be paid for by the Company" and "The Executive is entitled to the benefit of any indemnity in the Company's articles of association and may also entitled to the benefit of cover under such directors and officers liability insurance policy as may be maintained by the Company from time to time" (WPP Service Agreement)
- **No - No insurance provisions found:** Holiday RV/AGI Endorsement Agreement, NeuroBo Manufacturing Agreement, Allison Transmission Cooperation Agreement, IntriCon/Dynamic Hearing Strategic Alliance Agreement

## Review Steps

### Step 1: Locate Governing Law Provisions
1. Scan the contract for a section titled "Governing Law," "Applicable Law," or similar
2. If no dedicated section exists, check the "General" or "Miscellaneous" section
3. Look for language indicating which jurisdiction's laws apply
4. Note whether conflicts of law principles are excluded
5. Record the governing law in the specified format (US State or non-US Province, Country)

### Step 2: Identify Audit Rights
1. Search for "audit," "inspect," "examine," "books and records," "accounting records"
2. Look in sections about:
   - Payment/reporting obligations
   - Quality control
   - Compliance verification
   - Royalty calculations
3. Determine if the audit right is:
   - Financial (books, records, accounts)
   - Physical (facilities, premises)
   - Quality/compliance (processes, procedures)
4. Note any conditions (notice, frequency, cost allocation)
5. Record as "Yes" if any audit right exists, "No" if none found

### Step 3: Identify Insurance Requirements
1. Search for "insurance," "indemnity," "cover," "policy"
2. Look in sections about:
   - Insurance (dedicated section)
   - Indemnification
   - Employee benefits
   - Liability
3. Determine if insurance is:
   - For the benefit of the counterparty (named as additional insured)
   - Required to be maintained by one party
   - For employee/director protection
4. Note types and amounts of insurance required
5. Record as "Yes" if any insurance requirement exists for counterparty benefit, "No" if none found

## Output Format

For each contract reviewed, provide results in the following format:

```yaml
contract_id: [Contract Name/Identifier]
governing_law: [Name of US State / non-US Province, Country]
audit_rights: [Yes/No]
insurance: [Yes/No]
```

### Examples:

```yaml
contract_id: HOLIDAYRVSUPERSTORESINC_04_15_2002-EX-10.13-ENDORSEMENT_AGREEMENT
governing_law: California, United States
audit_rights: No
insurance: No
```

```yaml
contract_id: WPPPLC_04_30_2020-EX-4.28-SERVICE_AGREEMENT
governing_law: England, United Kingdom
audit_rights: No
insurance: Yes
```

```yaml
contract_id: TodosMedicalLtd_20190328_20-F_EX-4.10_Marketing_Agreement
governing_law: Israel
audit_rights: Yes
insurance: Yes
```

```yaml
contract_id: NeuroboPharmaceuticalsInc_20190903_S-4_EX-10.36_Manufacturing_Agreement
governing_law: New York, United States
audit_rights: Yes
insurance: No
```

## Important Notes

- **Governing Law:** If the contract specifies both a governing law and a separate jurisdiction for dispute resolution, report the governing law as stated. If only jurisdiction is specified without explicit governing law, note the jurisdiction as the governing law.
- **Audit Rights:** Only count explicit contractual audit rights. General rights to "inspect" or "examine" that are clearly audit-related should be included. Routine reporting obligations without audit rights should not be counted.
- **Insurance:** Only count insurance requirements that are explicitly stated in the contract. General indemnification clauses without specific insurance requirements should not be counted. Employee benefit insurance (health, life, disability) provided by an employer to its own employees should be counted as "Yes" if it benefits the counterparty (e.g., key person insurance, D&O insurance).
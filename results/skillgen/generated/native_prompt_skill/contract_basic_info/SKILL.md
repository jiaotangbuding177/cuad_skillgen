# SKILL.md - Contract Basic Information Review

## Overview

This skill enables the extraction of fundamental identifying information from contracts and agreements. It focuses on capturing the core metadata that establishes what the document is, who is involved, when it was created, and when it takes effect or expires. This foundational information is essential for contract management, portfolio analysis, and legal record-keeping.

## Review Steps

### Step 1: Identify the Document Name
1. Scan the document title at the top of the first page
2. Look for headings such as "AGREEMENT," "CONTRACT," "AMENDMENT," or "LICENSE"
3. Note any document identifiers (e.g., "Contract No. 076C/01")
4. For amendments, include both the amendment number and the original agreement name

### Step 2: Identify the Parties
1. Locate the introductory paragraph that typically begins with "This Agreement is entered into..."
2. Look for phrases like "by and between," "entered into by and between," or "made and entered into by and between"
3. Identify each party's full legal name and jurisdiction of incorporation (e.g., "a Delaware corporation")
4. Note any "d/b/a" (doing business as) designations

### Step 3: Identify the Agreement Date
1. Look for the date in the introductory paragraph or immediately after the parties' identification
2. Common phrases: "entered into as of the ___ day of ___, 20__" or "dated as of"
3. Check the signature block date if no date appears in the preamble
4. Format as mm/dd/yyyy

### Step 4: Identify the Effective Date
1. Look for explicit "Effective Date" definitions in the preamble or definitions section
2. Common phrases: "effective as of," "Effective Date," "this Agreement shall be effective"
3. If the effective date is the same as the agreement date, note that
4. Format as mm/dd/yyyy

### Step 5: Identify the Expiration Date
1. Look for "Term" sections that specify the initial term duration
2. Common phrases: "shall continue for a period of," "initial term of," "shall expire on"
3. Calculate the expiration date based on the effective date plus the stated term
4. If no expiration is specified, note as "Perpetual"
5. Format as mm/dd/yyyy or "Perpetual"

## What to Look For in Contracts

### Document Name Patterns
- **Standard Agreements**: "Online Hosting Agreement," "Sponsorship Agreement," "Supply Agreement"
- **Amendments**: "Amendment No. 2 to [Original Agreement Name]"
- **Licenses**: "License and Maintenance Agreement," "Licensing and Web Site Hosting Agreement"
- **Franchise Agreements**: "Franchise Agreement"
- **Distributor Agreements**: "Distributor Agreement"

### Party Identification Patterns
- **Full Legal Name**: "Diplomat Direct Marketing Corporation, a Delaware corporation"
- **Abbreviated Name**: Often defined in parentheses: "('Diplomat')"
- **Multiple Parties**: "by and between Array BioPharma Inc. ... and Ono Pharmaceutical Co., Ltd."
- **D/B/A Designations**: "EWSD 1, LLC, d/b/a/ SHI FARMS"

### Date Location Patterns
- **Preamble**: Most common location for agreement date
- **Definitions Section**: "Effective Date" often defined in Article 1
- **Signature Block**: Sometimes contains the execution date
- **Recitals**: May reference "of even date herewith"

### Term Duration Patterns
- **Fixed Term**: "12 months," "20 years," "through March 31, 2004"
- **Perpetual**: "enduring in perpetuity" or "shall endure indefinitely"
- **Renewal Terms**: "renew automatically for successive terms"
- **Conditional Expiration**: "until terminated as provided for elsewhere"

## Output Format

For each contract reviewed, provide the following structured output:

```json
{
  "Document Name": "[Full contract title as it appears in the document]",
  "Parties": "[Party 1 Name] and [Party 2 Name]",
  "Agreement Date": "[mm/dd/yyyy]",
  "Effective Date": "[mm/dd/yyyy]",
  "Expiration Date": "[mm/dd/yyyy] or Perpetual"
}
```

### Example Outputs

**Example 1 - Online Hosting Agreement:**
```json
{
  "Document Name": "Online Hosting Agreement",
  "Parties": "Diplomat Direct Marketing Corporation and Tadeo E-Commerce Corp.",
  "Agreement Date": "06/30/1999",
  "Effective Date": "06/01/1999",
  "Expiration Date": "06/01/2000"
}
```

**Example 2 - Sponsorship Agreement:**
```json
{
  "Document Name": "Sponsorship Agreement",
  "Parties": "drkoop.com, inc. and Vitamin Shoppe Industries, Inc.",
  "Agreement Date": "03/11/1999",
  "Effective Date": "03/11/1999",
  "Expiration Date": "Perpetual"
}
```

**Example 3 - License and Maintenance Agreement:**
```json
{
  "Document Name": "License and Maintenance Agreement (Telkom Contract No. 076C/01)",
  "Parties": "Systems Applications Products (Africa) (Pty) Limited and Telkom South Africa Limited",
  "Agreement Date": "01/30/2003",
  "Effective Date": "01/30/2003",
  "Expiration Date": "Perpetual"
}
```

## Common Pitfalls and Edge Cases

1. **Multiple Dates**: When the agreement date and effective date differ, capture both separately
2. **Undefined Terms**: If "Effective Date" is not explicitly defined, use the agreement date
3. **Amendments**: For amendments, the document name should reflect it's an amendment, but the parties and dates should be from the amendment document itself
4. **Redacted Information**: Some contracts may have redacted party names or dates - note what is available
5. **Conditional Effective Dates**: Some agreements have effective dates tied to conditions (e.g., "upon execution by both parties")
6. **Perpetual vs. Indefinite**: "Perpetual" means no end date; "indefinite" may still have termination provisions
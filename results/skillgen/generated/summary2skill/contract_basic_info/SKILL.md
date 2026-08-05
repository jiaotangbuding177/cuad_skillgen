# SKILL.md

## Covered Categories

### Document Name
- **Discovery frequency**: 100% of contracts (306/306)
- **Common patterns**: Clear title in header or first paragraph; includes type of agreement (e.g., "Agency Agreement", "Supply Agreement", "Collaboration Agreement"); amendments and schedules reference original agreement

### Parties
- **Discovery frequency**: 100% of contracts (306/306)
- **Common patterns**: Identified in opening paragraph with legal names and jurisdictions; includes addresses and defined terms (e.g., "Company", "Agent"); parties are typically companies or individuals with legal form (Inc., LLC, Ltd.)

### Agreement Date
- **Discovery frequency**: 95.1% of contracts (291/306)
- **Common patterns**: Found in opening paragraph or signature block; labeled as "dated as of", "entered into on", or "made as of"; format varies

### Effective Date
- **Discovery frequency**: 91.2% of contracts (279/306)
- **Common patterns**: Often same as agreement date or a specified date; explicitly stated in opening paragraph or definition section; may be contingent on conditions (e.g., "the date a fully executed copy is received")

### Expiration Date
- **Discovery frequency**: 81.7% of contracts (250/306)
- **Common patterns**: Specified as fixed term (e.g., "one year", "five years") from effective date; some have automatic renewal unless terminated; termination may be tied to completion of project or event

## Common Patterns

### Document Name
1. **Standard title in header**: "The contract is titled '[TYPE] AGREEMENT'." (e.g., "CO-BRANDING AND ADVERTISING AGREEMENT", "Services Agreement", "Joint Venture Agreement")
2. **Amendment/Schedule reference**: "The document is Amendment #[N] to the [Original Agreement] between [Parties]." (e.g., "Amendment #3 to the Manufacturing Agreement between ADMA BioManufacturing, LLC and Sanofi Pasteur S.A.")
3. **Embedded in larger header**: "EXHIBIT [NUMBER] [TYPE] AGREEMENT" (e.g., "EXHIBIT 10.26 MICOA AGENCY AGREEMENT")

### Parties
1. **Standard opening paragraph**: "The parties are [Party A] and [Party B]." (e.g., "The parties are I-ESCROW, INC. and 2THEMART.COM, INC.")
2. **Multiple entities on one side**: "The parties are [Party A] and [Party B] (including [Subsidiaries])." (e.g., "the Marathon Parties" includes several entities)
3. **Redacted/placeholder parties**: "The parties are [Provider (redacted)] and [Recipient (Telcostar Pte, Ltd. and Ability Computer & Software Industries Ltd)]."

### Agreement Date
1. **Explicit date in opening**: "The agreement is made as of [Date]." (e.g., "The agreement is made as of June 21, 1999.")
2. **Date in signature block**: "The agreement was entered into on [Date]." (e.g., "The agreement was entered into on October 1, 2019.")
3. **Blank/placeholder date**: "The agreement date is blank in the contract, indicated by underscores." (e.g., "___ __, 2000", "____ day of ________, 19____")

### Effective Date
1. **Same as agreement date**: "The effective date is [Date]." (e.g., "The effective date is June 21, 1999.")
2. **Different specified date**: "The effective date is [Date]." (e.g., "The effective date is November 1, 2019.")
3. **Defined by reference to event**: "The [Event] shall commence on [Date]." (e.g., "The Joint Venture shall commence on March 1, 2003.")

### Expiration Date
1. **Fixed term from effective date**: "The initial term is [N] [years/months] from the Effective Date, so it expires on [Date]." (e.g., "The initial term is one year from the Effective Date, so it expires on February 5, 2021.")
2. **Specific calendar date**: "The agreement terminates on [Date], unless terminated earlier." (e.g., "The agreement terminates on December 31, 2020, unless terminated earlier.")
3. **Tied to event/anniversary**: "The initial term expires [N] [years/months] after the [Event]." (e.g., "The initial term expires one year after the Launch Date")

## Review Checklist

### Document Name
- [ ] Is the document name clearly stated in the header or first paragraph?
- [ ] Does the name include the type of agreement (e.g., "Agreement", "Amendment", "Addendum")?
- [ ] If it's an amendment or schedule, does it reference the original agreement?

### Parties
- [ ] Are all parties identified with their full legal names?
- [ ] Are the parties' legal forms (Inc., LLC, Ltd., etc.) included?
- [ ] Are there any redacted or placeholder parties that need clarification?
- [ ] Are there multiple entities on one side that need to be listed?

### Agreement Date
- [ ] Is the agreement date explicitly stated?
- [ ] Is the date in the opening paragraph or signature block?
- [ ] If the date is blank or placeholder, is this noted?

### Effective Date
- [ ] Is the effective date explicitly stated?
- [ ] Is it the same as the agreement date or different?
- [ ] Is it contingent on any conditions (e.g., "date a fully executed copy is received")?
- [ ] If defined by reference to another event, is that event specified?

### Expiration Date
- [ ] Is the expiration date or term length specified?
- [ ] Is it a fixed term from the effective date or a specific calendar date?
- [ ] Are there automatic renewal provisions?
- [ ] Is termination tied to completion of a project or event?
- [ ] If no fixed expiration, is the contract perpetual or indefinite?

## Evidence Extraction Rules

### Document Name
- **Location**: Header, first paragraph, or title section of the document
- **Extraction method**: Look for the first line or heading that identifies the document type. For amendments/schedules, also extract the reference to the original agreement.
- **Evidence format**: "The contract is titled '[EXACT TITLE]'." or "The document is [Amendment/Schedule] #[N] to the [Original Agreement] between [Parties]."

### Parties
- **Location**: Opening paragraph, typically after "THIS [AGREEMENT TYPE] is made and entered into by and between"
- **Extraction method**: Identify all named parties. Note any redactions or placeholders. For multiple entities on one side, list all.
- **Evidence format**: "The parties are [Party A] and [Party B]." or "The parties are [Party A] and [Party B] (including [Subsidiaries])."

### Agreement Date
- **Location**: Opening paragraph (e.g., "dated as of", "made this", "entered into as of") or signature block
- **Extraction method**: Find the date associated with the agreement's execution. Note if blank or placeholder.
- **Evidence format**: "The agreement is made as of [Date]." or "The agreement was entered into on [Date]."

### Effective Date
- **Location**: Opening paragraph, definition section, or specific clause (e.g., "Effective Date" definition)
- **Extraction method**: Find the date when the contract becomes effective. Note if same as agreement date or different. If contingent on conditions, describe the condition.
- **Evidence format**: "The effective date is [Date]." or "The effective date is [Date], contingent on [Condition]."

### Expiration Date
- **Location**: Term section, expiration clause, or definition of "Term"
- **Extraction method**: Find the initial term length or specific expiration date. Note automatic renewal provisions. If no fixed expiration, note "perpetual" or "indefinite."
- **Evidence format**: "The initial term is [N] [years/months] from the Effective Date, so it expires on [Date]." or "The agreement terminates on [Date], unless terminated earlier."

## Output Format

```json
{
  "status": "complete" | "incomplete" | "error",
  "answer": {
    "Document Name": "string",
    "Parties": ["string", "string"],
    "Agreement Date": "string (YYYY-MM-DD format or description)",
    "Effective Date": "string (YYYY-MM-DD format or description)",
    "Expiration Date": "string (YYYY-MM-DD format or description)"
  },
  "evidence_unit_ids": ["string"],
  "source_contract_ids": ["string"],
  "missing_inputs": ["string"],
  "human_review_required": false
}
```

## Boundary Rules

### What the skill SHOULD do:
1. **Extract only the five specified categories**: Document Name, Parties, Agreement Date, Effective Date, Expiration Date
2. **Use exact language from the contract** when possible, especially for Document Name and Parties
3. **Note any blanks, placeholders, or redactions** in dates or parties
4. **Calculate expiration dates** when the contract specifies a term length from the effective date (e.g., "one year from Effective Date")
5. **Identify automatic renewal provisions** and note them in the expiration date description
6. **Handle amendments and schedules** by extracting their specific information while noting the reference to the original agreement

### What the skill should NOT do:
1. **Do not extract information beyond the five specified categories** (e.g., do not extract governing law, jurisdiction, payment terms, etc.)
2. **Do not interpret or infer missing information** - if a date is blank, state it's blank; if parties are redacted, state they are redacted
3. **Do not calculate dates based on assumptions** - if the effective date is not specified, do not assume it's the same as the agreement date
4. **Do not modify or standardize party names** - use the exact names as they appear in the contract
5. **Do not extract multiple dates** for the same category unless explicitly required (e.g., if there are multiple signature dates, note the earliest or as specified)
6. **Do not provide legal advice or interpretation** - simply extract the factual information as presented in the contract
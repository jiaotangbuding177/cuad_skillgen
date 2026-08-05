## Covered Categories
- Document Name (30 evidence atoms)
- Parties (30 evidence atoms)
- Agreement Date (30 evidence atoms)
- Effective Date (30 evidence atoms)
- Expiration Date (30 evidence atoms)

## Evidence-Based Review Rules

### Document Name
- Identify the contract type by extracting the explicit title from the header or preamble, such as "Co-Branding and Advertising Agreement" [KA-0001], "Services Agreement" [KA-0007], or "Joint Venture Agreement" [KA-0014].
- Recognize amendment documents by identifying titles that reference the original agreement, such as "Amendment #3 to the Manufacturing Agreement" [KA-0019] or "Amendment n° 01 to the Global Maintenance Agreement" [KA-0144].
- Detect specific industry agreement types including "Agency Agreement" [KA-0025, KA-0033], "Reseller Agreement" [KA-0050], "Outsourcing Agreement" [KA-0056], and "Manufacturing and Supply Agreement" [KA-0108].
- Identify license-related documents such as "Joint Content License Agreement" [KA-0089], "Form of Trademark License Agreement" [KA-0120], and "Sponsored Research and License Agreement" [KA-0132].

### Parties
- Extract all contracting entities, including primary parties like "I-ESCROW, INC." [KA-0002] and "2THEMART.COM, INC." [KA-0003], or international entities like "TELCOSTAR PTE, LTD." [KA-0009] and "Ability Computer & Software Industries Ltd" [KA-0010].
- Identify defined party roles such as "Company" [KA-0026], "Agent" [KA-0029], "Lessor" [KA-0034], and "Contractor" [KA-0058].
- Capture groups of parties referenced via schedules, such as "the persons and entities listed on Schedule A (collectively, the 'ValueAct Group')" [KA-0040].
- Ensure all signatories are captured, including multiple related entities in joint filings, such as "HPS INVESTMENT PARTNERS, LLC" [KA-0063] and its affiliates [KA-0064-KA-0067].

### Agreement Date
- Locate the date the agreement was made or signed, often found in the preamble, such as "June 21, 1999" [KA-0004] or "October 1, 2019" [KA-0011].
- Distinguish between the signing date and the effective date if they differ, noting dates like "December 21, 2017" for amendments [KA-0022] or "May 25, 1999" for execution [KA-0047].
- Identify template agreements where the date is left blank, such as "made this _____ day of ________, 19____" [KA-0238].

### Effective Date
- Extract the explicitly defined "Effective Date," which may match the agreement date [KA-0005, KA-0094] or be a distinct future/past date [KA-0012, KA-0106].
- Identify conditional effective dates, such as "upon receipt of a fully executed copy" [KA-0087] or "on the date of its signature by both Parties" [KA-0148].
- Note when the effective date is defined by reference to another event or document, such as "commence on the 1st of March, 2003" [KA-0017] or "date first written above" [KA-0054, KA-0197].

### Expiration Date
- Identify fixed expiration dates for the initial term, such as "December 31, 2020" [KA-0013] or "February 28, 2004" [KA-0018].
- Calculate expiration based on term length if a specific end date is not explicitly stated but the start date and duration are provided, e.g., "two (2) year(s) commencing on the Effective Date" [KA-0055] or "ten (10) years commencing on the date of this Agreement" [KA-0240].
- Detect agreements with no fixed expiration, described as "perpetually thereafter" [KA-0341], "indefinite period" [KA-0430], or continuing until terminated [KA-0198, KA-0448].
- Identify expiration tied to other agreements, such as "remain in force for the term of the referenced GMA" [KA-0149] or "expires automatically when the related License and Supply Agreement... terminates" [KA-0192].

## Review Checklist

### Document Name
- [ ] Verify the document title matches the expected agreement type (e.g., Services, Agency, Manufacturing) [KA-0001, KA-0007, KA-0108].
- [ ] Confirm if the document is an original agreement or an amendment [KA-0019, KA-0144].

### Parties
- [ ] List all primary contracting parties with their full legal names [KA-0002, KA-0003, KA-0009].
- [ ] Identify any defined roles (e.g., Agent, Lessor, Company) and the entities assigned to them [KA-0026, KA-0029, KA-0034].
- [ ] Check for group parties defined by reference to schedules [KA-0040].

### Agreement Date
- [ ] Extract the date the agreement was signed/executed [KA-0004, KA-0011].
- [ ] Flag templates with missing dates [KA-0238].

### Effective Date
- [ ] Extract the specific "Effective Date" definition [KA-0005, KA-0012].
- [ ] Determine if the effective date is conditional (e.g., upon signature or receipt) [KA-0087, KA-0148].
- [ ] Verify if the effective date differs from the agreement date [KA-0012 vs KA-0011].

### Expiration Date
- [ ] Extract the fixed expiration date if available [KA-0013, KA-0018].
- [ ] Calculate the expiration date if defined by term length (e.g., X years from Effective Date) [KA-0055, KA-0240].
- [ ] Identify if the agreement is perpetual or indefinite [KA-0341, KA-0430].
- [ ] Check if expiration is tied to the termination of another agreement [KA-0149, KA-0192].

## Output Format
JSON: {status, answer, evidence_unit_ids, source_contract_ids, missing_inputs, human_review_required}

## Boundary Rules
- [RB-001] Answer only using the target contract.
- [RB-002] Cite source-grounded evidence when answering.
- [RB-003] Return evidence_missing when no supporting clause exists.
- [RB-004] Return missing_input when contract_id or category is absent.
- [RB-005] Return unsupported_scope when the question is outside covered_categories.
- [RB-006] Route legal advice and high-risk interpretation to human review.
- [SR-001] Do not cite non-target contracts.
- [SR-002] Do not fabricate clauses.
- [SR-003] Do not provide legal advice.
- [SR-004] Do not generate externally sendable legal opinions.
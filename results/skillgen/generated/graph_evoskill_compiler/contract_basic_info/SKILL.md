# SKILL.md

## 1. Purpose and Scope

This skill enables the runtime agent to extract specific metadata fields from legal contracts based on graph-derived clause patterns. The scope is strictly limited to the following categories:
*   **Document Name**: Identification of the agreement type (e.g., Strategic Alliance, Joint Venture).
*   **Parties**: Identification of the contracting entities.
*   **Agreement Date**: The date the contract was signed or executed.
*   **Effective Date**: The date the contract terms begin to apply.
*   **Expiration Date**: The date the initial term ends or the contract expires.

The agent must answer conservatively, relying solely on verbatim evidence from the target contract. No external legal knowledge, citations, or interpretations beyond the provided pattern cards are permitted.

## 2. Review Workflow

1.  **Input Validation**:
    *   Check if `contract_id` and `category` are provided.
    *   If missing, return status: `missing_input`.
    *   Check if the requested `category` is within `covered_categories` (Document Name, Parties, Agreement Date, Effective Date, Expiration Date).
    *   If outside scope, return status: `unsupported_scope`.

2.  **Pattern Matching**:
    *   Scan the target contract text for semantic variants of the patterns defined in Section 3.
    *   Identify the specific pattern ID that matches the context.
    *   Extract the relevant data point (Name, Party, Date).

3.  **Evidence Verification**:
    *   Locate the exact sentence or phrase in the target contract that supports the finding.
    *   Ensure the evidence is verbatim.
    *   Verify that the evidence does not contradict other clauses (e.g., an amendment overriding a date).

4.  **Response Construction**:
    *   If evidence is found: Return status `answered`, the extracted value, and the verbatim citation.
    *   If no supporting clause exists: Return status `evidence_missing`.
    *   If the interpretation requires legal judgment or high-risk analysis: Return status `needs_human_review`.

## 3. Common Clause Patterns

### Document Name

**Invariant Meaning**: The explicit title or designation of the agreement as stated in the header, title, or preamble.

**Variation Cues**:
*   *PAT-document-name-01*: services, sponsorship, outsourcing, endorsement, co-branding, intellectual, property, joint, cooperation, strategic.
*   *PAT-document-name-02*: license, development, co-branding, content, sponsorship, supply, commercialization, maintenance, outsourcing, manufacturing.
*   *PAT-document-name-03*: strategic, alliance, distributor, distributorship, intellectual, property, exhibit, erchonia, exclusive, corporation.
*   *PAT-document-name-04*: amendment, manufacturing, agency, collaboration, supply, first, development, corporation, nutrition, llc.
*   *PAT-document-name-05*: license, distributor, contract, transportation, media, cooperation, development, business, venture, joint.
*   *PAT-document-name-06*: agency, outsourcing, biopure, corporation, franchise, sponsorship, venture, joint.

**Conditions/Exceptions**: None.

**Representative Phrasings** (Recognition Aids Only):
*   "STRATEGIC ALLIANCE AGREEMENT"
*   "INTELLECTUAL PROPERTY AGREEMENT"
*   "JOINT VENTURE AGREEMENT"
*   "JOINT CONTENT LICENSE AGREEMENT"
*   "TRANSPORTATION AGREEMENT"
*   "ERCHONIA CORPORATION EXCLUSIVE DISTRIBUTOR AGREEMENT"
*   "Collaboration Agreement"
*   "AGENCY AGREEMENT"
*   "DISTRIBUTOR AGREEMENT"
*   "TRANSPORTATION CONTRACT"
*   "SPONSORSHIP AGREEMENT"

### Parties

**Invariant Meaning**: The legal entities (corporations, LLCs, individuals) entering into the agreement, often identified by their full legal name and jurisdiction of organization.

**Variation Cues**:
*   *PAT-parties-01*: inc, corporation, com, ltd, systems, delaware, international, nevada, pharmaceuticals, affiliates.
*   *PAT-parties-02*: corporation, delaware, inc, organized, laws, arconic, corio, licensee, licensor, rolled.
*   *PAT-parties-03*: inc, pharmaceuticals, corporation, georgia, amag, vaccines, dba, jvls, llc, ltd.
*   *PAT-parties-04*: llc, corporation, company, biomanufacturing, adma, sanofi, pasteur, alamogordo, federal, financial.
*   *PAT-parties-05*: liability, delaware, llc, company, limited, curo, owner, finance, receivables, management.
*   *PAT-parties-06*: corporation, delaware, nutrition, premier, spinco, cerence, inc, porex, clickstream, digital.

**Conditions/Exceptions**: None.

**Representative Phrasings** (Recognition Aids Only):
*   "RSL COM PrimeCall, Inc., a Delaware corporation (\"PrimeCall\")"
*   "DOVA PHARMACEUTICALS, INC."
*   "Bioeq IP AG"
*   "e.l.f. Beauty, Inc., a Delaware corporation (the \"Company\")"
*   "Commerce One, Inc., a Delaware corporation"
*   "CytoDyn Inc., a Delaware corporation (\"CytoDyn\")"
*   "CONVERGTV, INC., a Delaware Corporation"
*   "Equifax Inc., a Georgia corporation (\"Equifax\")"
*   "WPD Pharmaceuticals, (\"WPD\")"
*   "F. Hoffmann-La Roche Ltd"
*   "EDGE Communications Solutions, LLC"
*   "Stremick's Heritage Foods, LLC"
*   "Vyera Pharmaceuticals, LLC, a Delaware limited liability company (\"Vyera\")"
*   "National CineMedia, LLC, a Delaware limited liability company (\"NCM\")"
*   "S2K Financial LLC, a Delaware limited liability company (\"S2K\")"
*   "CERENCE INC., a Delaware corporation (\"SpinCo\")"
*   "Premier Nutrition Corporation"
*   "Digital Cinema Destinations Corp., a Delaware corporation (\"Network Affiliate\""

### Agreement Date

**Invariant Meaning**: The specific calendar date on which the parties signed or executed the document.

**Variation Cues**:
*   *PAT-agreement-date-01*: day, june, march, april, december, august, february, november, january, october.
*   *PAT-agreement-date-02*: day, october, november, february, january, december, march, april, july, entered.
*   *PAT-agreement-date-03*: day, dated, september, march, november, december, july, february, friday, january.
*   *PAT-agreement-date-04*: january, march, december, dated, september, october, april.
*   *PAT-agreement-date-05*: dated, november, april, june, october, day, august, july, february, january.
*   *PAT-agreement-date-06*: day, january, september, first, december, dated, april.

**Conditions/Exceptions**: None.

**Representative Phrasings** (Recognition Aids Only):
*   "12th day of November, 2019"
*   "28th day of March 2006"
*   "June 13, 2012"
*   "20t h day of November, 2018"
*   "October 30, 2019"
*   "9th day of October, 2001"
*   "12th day of November, 2018"
*   "dated March 15, 2000"
*   "December 10, 2015"
*   "December 19, 2019"
*   "September 27, 2018"
*   "Dated as of April 2, 2020"
*   "dated this  3rd day of November, 2010"
*   "29/3/18"
*   "April 15, 1994"
*   "this first (1st)  day of January, 1996"
*   "2nd day of September 1998"
*   "dated as of December 20, 2007"

### Effective Date

**Invariant Meaning**: The date on which the contractual obligations and terms begin to apply. This may be the same as the Agreement Date or a different date specified in the contract.

**Variation Cues**:
*   *PAT-effective-date-01*: effective, date, day, march, february, september, january, december, august, june.
*   *PAT-effective-date-02*: effective, date, december, hereof, july, dated, day, commence, signed, january.
*   *PAT-effective-date-03*: date, march, hereof, day, april, commence, term, commencing, dated, begin.
*   *PAT-effective-date-04*: effective, november, date, day, february, january, october, letter, july, made.
*   *PAT-effective-date-05*: date, effective, last, execute, which, sign, signed, term, begin, signatory.
*   *PAT-effective-date-06*: date, effective, november, above, first, written, day, become.

**Conditions/Exceptions**:
*   *PAT-effective-date-02*: May be conditional on signing or installation (e.g., "effective on the signing date").
*   *PAT-effective-date-06*: May refer to the date first written above.

**Representative Phrasings** (Recognition Aids Only):
*   "20t h day of December 2018 (the \"Effective Date\")"
*   "23rd day of September, 1997 (\"Effective Date\")"
*   "14th day of March, 2016"
*   "This JV Agreement shall become effective on the signing date"
*   "December 10, 1993"
*   "dated as of May 13, 2020"
*   "11th day of December, 2015"
*   "April 18, 2018"
*   "From January 30, 2012"
*   "12th day of November, 2019 (the \"Effective Date\")"
*   "4th day of February 2019 (\"Effective Date\")"
*   "January 1, 2007"
*   "September 30, 1998"
*   "The term of this Agreement (\"Term\") will begin on the date this Agreement is signed by the last signatory (\"Effective Date\")"
*   "the date on which the Parties sign and execute this Agreement"
*   "12th day of November, 2018 (the \"Effective Date\")"
*   "This Agreement shall become effective upon the date first written above"
*   "20t h day of November, 2018 (the \"Effective Date\")"

### Expiration Date

**Invariant Meaning**: The date on which the initial term of the agreement ends. This may be a fixed date, a duration from the effective date, or indefinite.

**Variation Cues**:
*   *PAT-expiration-date-01*: date, years, effective, term, five, initial, continue, period, year, ten.
*   *PAT-expiration-date-02*: december, term, terminated, unless, date, continue, effective, february, expire, initial.
*   *PAT-expiration-date-03*: terminated, continue, until, date, effective, effect, thereafter, pursuant, written, indefinitely.
*   *PAT-expiration-date-04*: years, period, continue, term, effect, date, effective, two, force, full.
*   *PAT-expiration-date-05*: effective, term, date, years, period, year, initial, commence, effect, continue.
*   *PAT-expiration-date-06*: date, effective, anniversary, term, initial, through, day, prior, mean, first.

**Conditions/Exceptions**:
*   *PAT-expiration-date-01*: May be defined as an anniversary of the Effective Date.
*   *PAT-expiration-date-02*: May be subject to earlier termination ("unless terminated earlier").
*   *PAT-expiration-date-03*: May be indefinite ("continue indefinitely") or until terminated per specific sections.
*   *PAT-expiration-date-04*: May be a minimum period.
*   *PAT-expiration-date-05*: May be defined as a period extending from the Effective Date.
*   *PAT-expiration-date-06*: May be defined as the day prior to an anniversary.

**Representative Phrasings** (Recognition Aids Only):
*   "end on the five (5) year anniversary of the Effective Date (the \"Initial Term\")"
*   "two (2) years after the date of this Agreement"
*   "This Agreement shall be for an initial term of five (5) years"
*   "expire on December 31, 2028"
*   "The term of this Agreement shall be one (1) year unless terminated earlier in accordance with the terms of this Agreement"
*   "concluding December 31, 1998"
*   "This Agreement shall continue until terminated as provided herein."
*   "this Agreement shall continue indefinitely"
*   "This Agreement shall commence on the Effective Date and shall continue until it is terminated in accordance with the provisions of Section 15 of this Agreement"
*   "The initial term of this Agreement shall commence on the Effective Date and shall continue for a period of five (5) years"
*   "continue for a minimum period of 12 months"
*   "the term of this Agreement shall be for a period of five (5) years, beginning on the Effective Date"
*   "This Agreement shall commence on the Effective Date and shall extend for a period of Five (5) years thereafter (\"Initial Term\")"
*   "shall continue for a term of three (3) years"
*   "this Agreement shall commence on the Effective Date and continue for a period of one (1) year (\"Term\")"
*   "the fifth (5t h) anniversary of the Effective Date"
*   "The term of this Agreement is twelve (12) months from the date hereof"
*   "Initial Term shall mean the Effective Date through the day prior to the fourth anniversary of the Effective Date"

## 4. Evidence and Citation Protocol

1.  **Verbatim Quoting**: All findings must be supported by a direct, verbatim quote from the target contract. Do not paraphrase.
2.  **Source Grounding**: The evidence must exist within the text of the target contract identified by `contract_id`.
3.  **No External Citations**: Do not cite other contracts, case law, or external documents.
4.  **Conservative Interpretation**: If a date is calculated (e.g., "5 years from Effective Date"), the agent must explicitly state the calculation logic and the resulting date, citing the clause that defines the duration and the clause that defines the start date.
5.  **Ambiguity Handling**: If multiple dates are present (e.g., Agreement Date vs. Effective Date), distinguish them clearly based on the category requested.

## 5. Boundary and Abstention Rules

1.  **Allowed Statuses**:
    *   `answered`: Valid finding with evidence.
    *   `evidence_missing`: No supporting clause found in the target contract.
    *   `missing_input`: Required input parameters (`contract_id`, `category`) are absent.
    *   `unsupported_scope`: The requested category is not in the covered list.
    *   `needs_human_review`: The query requires legal judgment or involves high-risk interpretation.

2.  **Hard Enforcement Rules**:
    *   **RB-001**: Answer only using the target contract.
    *   **RB-002**: Cite source-grounded evidence when answering.
    *   **RB-003**: Return `evidence_missing` when no supporting clause exists.
    *   **RB-004**: Return `missing_input` when `contract_id` or `category` is absent.
    *   **RB-005**: Return `unsupported_scope` when the question is outside covered categories.
    *   **RB-006**: Route legal advice and high-risk interpretation to human review.

3.  **Safety Requirements**:
    *   **SR-001**: Do not cite non-target contracts. Verify `source_contract_ids` match `target_contract_id`.
    *   **SR-002**: Do not fabricate clauses. Verify evidence spans exist in the target contract.
    *   **SR-003**: Do not provide legal advice. Detect and avoid legal judgment language in the answer.
    *   **SR-004**: Do not generate externally sendable legal opinions. Detect and avoid formal document patterns.

4.  **Abstention**:
    *   If the contract text is ambiguous or contradictory regarding the requested field, and no clear hierarchy of clauses is evident, return `needs_human_review`.
    *   If the pattern matches but the context suggests it is not the primary definition (e.g., a reference to a past agreement), return `evidence_missing` for the current contract's metadata.
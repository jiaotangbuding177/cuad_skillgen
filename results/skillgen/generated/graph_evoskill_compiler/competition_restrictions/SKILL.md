# SKILL.md

## 1. Purpose and Scope

This skill enables the runtime agent to review target contracts for specific competition-related restrictions and exceptions. The agent must identify clauses falling within the following **Covered Categories**:

*   **Competitive Restriction Exception**: Clauses that carve out exceptions to non-compete or exclusivity obligations.
*   **Non-Disparagement**: Clauses prohibiting negative public statements about the counterparty.
*   **Non-Compete**: Clauses restricting a party from competing with the other in specific geographies, sectors, or activities.
*   **Exclusivity**: Clauses granting exclusive rights to distribute, sell, or license products/services.
*   **No-Solicit of Customers**: Clauses restricting the solicitation of the counterparty’s customers.
*   **Most Favored Nation (MFN)**: Clauses guaranteeing terms equal to or better than those offered to third parties.
*   **No-Solicit of Employees**: Clauses restricting the solicitation or hiring of the counterparty’s employees.

**Scope Constraints:**
*   The agent must analyze **only** the provided target contract.
*   The agent must **not** invent legal rules, citations, or interpretations not grounded in the text.
*   The agent must **abstain** from answering if the target contract does not contain evidence supporting a finding for the requested category.

## 2. Review Workflow

1.  **Input Validation**:
    *   Check if `contract_id` and `category` are provided.
    *   If missing, return status: `missing_input`.
    *   Check if the requested `category` is within the **Covered Categories** listed in Section 1.
    *   If outside scope, return status: `unsupported_scope`.

2.  **Pattern Recognition**:
    *   Scan the target contract for semantic variants of the patterns defined in Section 3.
    *   Identify the **invariant meaning** of the clause (e.g., is it a restriction or an exception?).
    *   Note any **conditions** (e.g., "subject to," "provided that") or **exceptions** (e.g., "except as," "without consent").

3.  **Evidence Extraction**:
    *   Locate the verbatim text in the target contract that supports the finding.
    *   Ensure the evidence is from the **target contract only**. Do not use examples from the pattern cards as evidence.

4.  **Response Formulation**:
    *   If evidence is found: Return status `answered`, include the interpretation, and quote the verbatim evidence.
    *   If no evidence is found: Return status `evidence_missing`.
    *   If the clause is ambiguous or requires high-risk legal judgment: Return status `needs_human_review`.

## 3. Common Clause Patterns

### Competitive Restriction Exception

**Invariant Meaning**: These clauses explicitly allow a party to engage in activities that might otherwise be restricted by non-compete or exclusivity provisions. They often serve as carve-outs.

**Pattern 1: General Permission for Similar Services/Content**
*   **Meaning**: Allows a party to perform similar services or acquire them from third parties, or to develop competitive content.
*   **Variation Cues**: "similar", "services", "construed", "nothing", "content", "provide", "third", "acquiring", "itself", "performing".
*   **Conditions/Exceptions**: Often unconditional ("Nothing in this Agreement shall be construed...").
*   **Representative Phrasings**:
    *   "Nothing in this Agreement shall be construed to prevent the Recipient from itself performing or from acquiring services from other providers that are similar to or identical to the Services."
    *   "Nothing in this Agreement shall be construed as preventing Impresse or VerticalNet from developing other co-branded versions of their materials, data, information and content."
    *   "XFN and/or its Affiliates are entitled to publish or distribute content of any third party where such content is similar to or competitive with the Content."

**Pattern 2: Exception Subject to Specific Sections**
*   **Meaning**: Permits activity generally, except where specific non-compete sections apply.
*   **Variation Cues**: "set", "except", "preventing", "construed", "forth", "nothing", "site", "sections", "implementing", "links".
*   **Conditions/Exceptions**: "Except as set forth in Sections [X] and [Y]..."
*   **Representative Phrasings**:
    *   "Except as set forth in Sections 4.3 [Non-Competition] and 5.8 [Non-Competition], nothing in this Agreement shall be construed as preventing either party from developing other co-branded versions of its materials..."
    *   "Except as set forth in Sections 3.8 [LABORATORY PRODUCTS] and 5.8 [CO-BRANDED TRAINING AND EDUCATION SITE], nothing in this Agreement shall be construed as preventing Neoforma from implementing Neoforma Links on any other Site."

**Pattern 3: Consent-Based Exception**
*   **Meaning**: Restriction applies unless prior written consent is obtained.
*   **Variation Cues**: "consent", "prior", "express", "without", "written", "advance", "jrvs", "material", "seeking", "writing".
*   **Conditions/Exceptions**: Requires "express prior written consent" or consent based on "full disclosure".
*   **Representative Phrasings**:
    *   "without the express prior written consent of Calm."
    *   "unless JRVS consents thereto in writing in advance, based upon the Distributor's full disclosure of the material facts in seeking such consent."

**Pattern 4: Carve-Out for Specific Activities/Parties**
*   **Meaning**: Non-compete restrictions do not apply to specific types of activities (e.g., ads) or specific parties (e.g., affiliates).
*   **Variation Cues**: "however", "provided", "apply", "section", "restrictions", "non-competition", "features", "storefronts", "advertisements", "verticalnet".
*   **Conditions/Exceptions**: "provided, however, that this Section... shall not apply to..."
*   **Representative Phrasings**:
    *   "provided, however, that this Section 5.8.1 [Non-Competition] shall not apply to advertisements, Storefronts or similar features on VerticalNet's Sites."
    *   "provided, however, that DIALOG shall not be under any such restrictions in relation to services or products it provides to the Key Customer in the event the Key Customer terminates its agreement with ENERGOUS."
    *   "provided, however, the Parties hereby acknowledge that the restrictions set forth in this Section 2.3 shall not apply to any Affiliates of MMT (including Pfizer)"

**Pattern 5: Reservation of Rights to Sell Directly**
*   **Meaning**: Manufacturer reserves the right to sell to certain resellers despite exclusivity granted to a distributor.
*   **Variation Cues**: "who", "majority", "license", "outlets", "reserves", "products", "distributors", "both", "period", "procure".
*   **Conditions/Exceptions**: "The foregoing notwithstanding... reserves the right to sell... to customers other than distributors such as... resellers who procure Products at centralized locations..."
*   **Representative Phrasings**:
    *   "The foregoing notwithstanding, during the [*] and any subsequent period, NETGEAR reserves the right to sell or license Products in [*] to customers other than distributors such as, but not limited to resellers who procure Products at centralized locations for resale to end-use customers solely through their wholly or majority owned retail outlets..."

**Pattern 6: Unanimous Consent Waiver**
*   **Meaning**: Restriction can be waived by unanimous written consent of remaining participants.
*   **Variation Cues**: "participants", "remaining", "without", "unanimous", "consent", "written", "racing", "endorsement", "writing", "sponsor".
*   **Conditions/Exceptions**: "without the unanimous written consent of the remaining Participants."
*   **Representative Phrasings**:
    *   "without the unanimous written consent of the remaining Participants."
    *   "unless such endorsement activity is approved in writing by Racing and the Sponsor"

### Non-Disparagement

**Invariant Meaning**: Prohibits parties from making negative public statements about the counterparty, its business, or its representatives.

**Pattern 1: Absence of Clause**
*   **Meaning**: The contract does not contain a non-disparagement clause.
*   **Variation Cues**: None (Negative finding).
*   **Representative Phrasings**: "No" (Indicates absence in source data; agent must verify absence in target).

**Pattern 2: Mutual Non-Disparagement with Broad Scope**
*   **Meaning**: Both parties agree not to disparage each other, affiliates, employees, or business reputation. Often includes exceptions for litigation disclosures.
*   **Variation Cues**: "who", "disparage", "subsidiaries", "affiliates", "indirectly", "businesses", "slander", "media", "expected", "longer".
*   **Conditions/Exceptions**: "Subject to applicable law... during the Standstill Period... provided that... nothing in this Section shall prevent either Party from disclosing any facts... with respect to any such litigation."
*   **Representative Phrasings**:
    *   "Subject to applicable law, each of the Parties covenants and agrees that... neither Party... shall in any way... publicly disparage, impugn, make ad hominem attacks on or otherwise defame or slander... the other Party or such other Party's Representatives..."
    *   "Subject to applicable law, the Company... and each of the Marathon Parties... covenants and agrees that... neither it nor any of its respective Representatives... shall in any way publicly... criticize, disparage, call into disrepute or otherwise defame or slander the other Party..."

**Pattern 3: Non-Disparagement via Use of Marks/Domain Names**
*   **Meaning**: Prohibits using licensed marks or domains in a way that tarnishes or disparages the licensor.
*   **Variation Cues**: "licensor", "business", "adversely", "manner", "licensed", "licensee", "disparages", "reflects", "reputation", "use".
*   **Conditions/Exceptions**: "Licensee shall not knowingly... use the Licensed Domain Names in any manner that tarnishes, degrades, disparages or reflects adversely on Licensor..."
*   **Representative Phrasings**:
    *   "Licensee shall not knowingly (a) use the Licensed Domain Names in any manner that tarnishes, degrades, disparages or reflects adversely on Licensor or Licensor's business or reputation"
    *   "The Licensee shall not by any act or omission use the Licensed Mark in any manner that disparages or reflects adversely on Licensor or its business or reputation."

**Pattern 4: Investor/Company Mutual Non-Disparagement**
*   **Meaning**: Investors and Company agree not to make derogatory statements during the Standstill Period. Includes cure periods for breaches.
*   **Variation Cues**: "further", "disparage", "affiliates", "indirectly", "includes", "three", "declaration", "write", "verbalize", "following".
*   **Conditions/Exceptions**: "until the earlier of (i) the expiration of the Standstill Period or (ii) any material breach... (provided that the Company shall have three (3) business days... to remedy...)"
*   **Representative Phrasings**:
    *   "Each Investor agrees that... neither it nor any of its Affiliates or Associates will... publicly make... any remark... that might reasonably be construed to be derogatory or critical of... the Company..."
    *   "The Company hereby agrees that... neither it nor any of its Affiliates will... publicly make... any remark... that might reasonably be construed to be derogatory or critical of... the Investors..."

**Pattern 5: Confidentiality Only (No Explicit Non-Disparagement)**
*   **Meaning**: Contract contains confidentiality obligations but no explicit ban on negative public statements.
*   **Variation Cues**: "information", "confidential", "disclosing", "consent", "written", "without", "agrees", "proprietary", "agree", "right".
*   **Representative Phrasings**:
    *   "The parties agree that each will treat such information as confidential. Neither party shall have the right to disclose the Proprietary Information to any third party without the express written consent of the disclosing party."
    *   "Each Party agrees that the terms and conditions... shall be treated as the other's Confidential Information... no public reference... can be made without the prior written consent..."

**Pattern 6: Non-Disparagement via Use of Materials/Marks**
*   **Meaning**: Prohibits using licensed materials or marks in a disparaging manner or negative light.
*   **Variation Cues**: "light", "agrees", "manner", "otherwise", "portrays", "negative", "disparaging", "use", "connection", "marks".
*   **Representative Phrasings**:
    *   "Affiliate agrees not to use the Licensed Materials in any manner that is disparaging or that otherwise portrays Chase in a negative light."
    *   "In connection with such license each party agrees not to use the other party's Marks in any manner that is disparaging or that otherwise portrays such party in a negative light."

### Non-Compete

**Invariant Meaning**: Restricts a party from engaging in competitive activities, selling competing products, or operating in specific territories/fields.

**Pattern 1: Absence of Clause**
*   **Meaning**: No general non-compete clause exists.
*   **Representative Phrasings**: "No" (Indicates absence in source data).

**Pattern 2: Table of Contents Reference**
*   **Meaning**: Presence of a section titled "Non-Competition" or "Covenant Not to Compete" in the TOC indicates the clause exists elsewhere in the document.
*   **Variation Cues**: "compete", "covenant", "noncompetition", "section", "non-competition", "competition", "restrictions".
*   **Representative Phrasings**:
    *   "20.COVENANT NOT TO COMPETE."
    *   "Section 6.13 Noncompetition"
    *   "9.3 Non-Competition Agreement"

**Pattern 3: Restriction on Marketing/Selling Competitive Products**
*   **Meaning**: Distributor/Party cannot market, sell, or promote products competitive with the licensed products.
*   **Variation Cues**: "express", "nor", "promote", "consent", "products", "written", "sell", "prior", "without", "sale".
*   **Conditions/Exceptions**: Often requires "prior express written consent" for exceptions.
*   **Representative Phrasings**:
    *   "During the term of this agreement, Distributor shall not market, sell advertise or promote the sale or use of any product or device which is competitive with or substantially similar to the Products, without the prior express written consent of Erchonia..."
    *   "Throughout the Term and for a period of six (6) months after the expiration or termination of this Agreement, neither Calm nor any of its affiliates shall... sell, offer for sale, market or promote any digital meditation or digital sleep products... without the express prior written consent of XSPA."

**Pattern 4: Restriction on Developing/Commercializing Competitive Products**
*   **Meaning**: Party cannot develop, manufacture, or commercialize competitive products in the territory/field.
*   **Variation Cues**: "product", "during", "commercialize", "term", "territory", "royalty", "manufacture", "except", "competitive", "vyera".
*   **Conditions/Exceptions**: "Except as expressly required under this Agreement..."
*   **Representative Phrasings**:
    *   "Except as expressly required under this Agreement, Vyera hereby covenants not to Develop, Manufacture, Commercialize or otherwise exploit a Competitive Product in the Territory during the Royalty Term..."
    *   "During the Term, MMT shall not Commercialize in any manner any Competing Product in the Field in any country in the Territory"

**Pattern 5: Restriction on Advertising Competitors**
*   **Meaning**: Party cannot place advertisements for competitors on their sites.
*   **Variation Cues**: "competitor", "term", "advertisements", "during", "place", "paperexchange", "verticalnet", "pulp", "online", "paper".
*   **Representative Phrasings**:
    *   "During the Term, Neoforma shall not place any advertisements on a Neoforma Site for any VerticalNet Competitor."
    *   "During the Term, PaperExchange shall not place any advertisements on the PaperExchange Site from any Pulp and Paper Online Competitor."

**Pattern 6: Restriction on Selling Competing Products in Specific Jurisdictions**
*   **Meaning**: Party cannot sell competing products in a specific state/region without consent.
*   **Variation Cues**: "sell", "agrees", "written", "products", "without", "professional", "liability", "agency", "micoa", "competing".
*   **Conditions/Exceptions**: "without the written consent of MICOA."
*   **Representative Phrasings**:
    *   "Agency agrees not to sell any competing professional liability products in Nevada, without the written consent of MICOA."
    *   "Until expiration or earlier termination of the Agreement, DIALOG agrees that it and its Affiliates will not, without ENERGOUS' written approval, intentionally sell, distribute or work with any third party to develop products incorporating any Uncoupled Power Transfer Technology other than Licensed Products;"

### Exclusivity

**Invariant Meaning**: Grants a party the sole right to distribute, sell, or license products/services in a territory, excluding others (including the licensor).

**Pattern 1: Grant of Exclusive License/Right**
*   **Meaning**: Licensor grants exclusive right to market/distribute products in a territory.
*   **Variation Cues**: "exclusive", "grants", "products", "distribute", "territory", "sell", "right", "distributor", "hereby", "market".
*   **Conditions/Exceptions**: "Upon the terms and subject to the conditions of this Agreement..."
*   **Representative Phrasings**:
    *   "Upon the terms and subject to the conditions of this Agreement, Developer hereby grants to Distributor an exclusive, non-transferable fight and license to market and distribute the Products in the Territory."
    *   "Todos hereby grants the Reseller a non-sublicensable, non-transferable, exclusive right to distribute and sell the Products to Customers in the Territory"

**Pattern 2: Appointment as Exclusive Distributor**
*   **Meaning**: Explicit appointment of a party as the exclusive distributor.
*   **Variation Cues**: "exclusive", "distributor", "products", "territory", "appointment", "accepts", "appoints", "terms", "conditions", "hereby".
*   **Conditions/Exceptions**: "subject to the terms and conditions... including... satisfaction of the Performance Benchmarks."
*   **Representative Phrasings**:
    *   "Hydraspin hereby appoints Distributor, and Distributor hereby accepts appointment, as Hydraspin's exclusive distributor of the Products in the Territory during the term of this Agreement..."
    *   "ARGO agreed to appoint YEC as the exclusive distributor of its products in the Territory specified therein"

**Pattern 3: Explicit Non-Exclusivity**
*   **Meaning**: Clause explicitly states the relationship is **non-exclusive**. This is a negative finding for Exclusivity.
*   **Variation Cues**: "appoints", "products", "non-exclusive", "accepts", "authorized", "appointment", "terms", "hereby", "distributor", "territory".
*   **Representative Phrasings**:
    *   "Subject to the terms and conditions of this Agreement, Galaxy hereby appoints Telnet as a non-exclusive authorized reseller of the Products and Services..."
    *   "The Supplier appoints the Distributor as its non-exclusive distributor to distribute the Products in the Territory..."

**Pattern 4: Exclusive License to Commercialize**
*   **Meaning**: Exclusive license to use patents/know-how to commercialize products in a field/territory.
*   **Variation Cues**: "license", "exclusive", "field", "hereby", "grants", "territory", "grant", "products", "section", "patents".
*   **Representative Phrasings**:
    *   "Array hereby grants to Ono an exclusive license... under the Array Patents... to Commercialize the Products in the Field in the Ono Territory."
    *   "CytoDyn hereby grants to Vyera... an exclusive royalty-bearing license... solely to Commercialize... Licensed Products in the Field in the Territory."

**Pattern 5: Exclusive License to Use Content/Lists**
*   **Meaning**: Exclusive license to use, modify, or transmit specific content or product listings.
*   **Variation Cues**: "enhance", "transmit", "grants", "license", "verticalnet", "perform", "modify", "display", "reproduce", "use".
*   **Conditions/Exceptions**: "even as to VerticalNet" (excludes licensor).
*   **Representative Phrasings**:
    *   "VerticalNet hereby grants Neoforma an exclusive license, even as to VerticalNet, to use, modify, enhance, reproduce, display, perform and transmit the VerticalNet Medical Product Listings..."
    *   "PaperExchange hereby grants VerticalNet an exclusive license to use, modify, enhance, reproduce, display, perform and transmit the PaperExchange Content"

**Pattern 6: Conditional Exclusivity (Marketing Plan)**
*   **Meaning**: Exclusivity is granted contingent on meeting marketing requirements.
*   **Variation Cues**: "subject", "exhibit", "which", "conducting", "described", "appointed", "during", "between", "only", "one".
*   **Conditions/Exceptions**: "subject to Distributor conducting mutually agreed to marketing activities as described in the Marketing Plan..."
*   **Representative Phrasings**:
    *   "During the initial one year period beginning on the Amendment Date, Distributor shall be the only distributor appointed by NETGEAR in [*], subject to Distributor conducting mutually agreed to marketing activities as described in the Marketing Plan..."

### No-Solicit of Customers

**Invariant Meaning**: Restricts a party from soliciting or contacting the counterparty’s customers.

**Pattern 1: Absence of Clause**
*   **Meaning**: No specific clause restricting solicitation of customers.
*   **Representative Phrasings**: "No" (Indicates absence in source data).

**Pattern 2: Mutual Non-Solicitation with Joint Marketing Exception**
*   **Meaning**: Parties cannot solicit each other's customers, except for joint marketing efforts.
*   **Variation Cues**: "except", "above", "section", "indirectly", "agrees", "joint", "purolator", "referred", "directly", "efforts".
*   **Conditions/Exceptions**: "Except for the joint marketing efforts referred to in Section 3.1 (v) above..."
*   **Representative Phrasings**:
    *   "Except for the joint marketing efforts referred to in Section 3.1 (v) above, Purolator agrees not to directly or indirectly solicit next day or multiple day freight from existing sameday customers of Dynamex."
    *   "Except for the joint marketing efforts referred to in Section 3.1 (v) above, Dynamex agrees not to directly or indirectly solicit overnight freight from customers of Purolator."

**Pattern 3: Restriction on Marketing to Customers Without Approval**
*   **Meaning**: Party cannot market services to customers without prior written approval.
*   **Variation Cues**: "except", "provided", "restrictions", "approval", "period", "dassault", "during", "expressly", "one", "systemes".
*   **Conditions/Exceptions**: "except as expressly provided in this Agreement... without the prior written approval of Dassault Systemes."
*   **Representative Phrasings**:
    *   "During the Term of this Agreement, and for a period of one year thereafter, except as expressly provided in this Agreement, PlanetCAD shall not market any services to Customers without the prior written approval of Dassault Systemes."

**Pattern 4: Exclusivity Implied Non-Solicitation**
*   **Meaning**: Supplier agrees to deal exclusively through Distributor, effectively prohibiting direct solicitation of customers.
*   **Variation Cues**: "acting", "except", "which", "limitation", "distribution", "consent", "products", "indirectly", "hydraspin", "relation".
*   **Conditions/Exceptions**: "except pursuant to an agreement with the Distributor... without the prior written consent of the Distributor."
*   **Representative Phrasings**:
    *   "Hydraspin certifies, stipulates, and agrees that the Hydraspin will deal exclusively with and through the Distributor... Hydraspin will not in any way... (a) contact, approach or negotiate with any Customer outside of the Distributor..."

**Pattern 5: Restriction on Using Records to Solicit**
*   **Meaning**: Party cannot use business records to solicit policyholders for other products.
*   **Variation Cues**: "authorized", "except", "provided", "agency", "unless", "products", "affiliates", "section", "micoa", "placed".
*   **Conditions/Exceptions**: "Except as provided in Section D or unless authorized by the Agency..."
*   **Representative Phrasings**:
    *   "Except as provided in Section D or unless authorized by the Agency, MICOA or its affiliates shall not use its records of business placed by the Agency with MICOA to solicit individual policyholders for the sale of other lines of insurance..."

**Pattern 6: Right to Solicit Upon Termination**
*   **Meaning**: Grants a party the right to solicit customers if the agreement is terminated for default. This is an exception to standard non-solicitation.
*   **Variation Cues**: "subscribers", "right", "directly", "terminated", "client", "solicit", "contact", "pursuant", "another", "galaxy".
*   **Conditions/Exceptions**: "If this Agreement is terminated pursuant to section 10.2..."
*   **Representative Phrasings**:
    *   "If this Agreement is terminated pursuant to section 10.2, Galaxy shall have the right to contact Subscribers directly and solicit such Subscribers to become subscribers of Galaxy..."

### Most Favored Nation

**Invariant Meaning**: Guarantees that a party receives terms (price, benefits) equal to or better than those offered to third parties.

**Pattern 1: Absence of Clause**
*   **Meaning**: No MFN clause exists.
*   **Representative Phrasings**: "No" (Indicates absence in source data).

**Pattern 2: Fee Structure Without MFN**
*   **Meaning**: Fees are defined by exhibit/section, but no guarantee of best terms vs. third parties.
*   **Variation Cues**: "after", "service", "provided", "exhibit", "terminated", "when", "fee", "section", "described", "relating".
*   **Representative Phrasings**:
    *   "Diplomat will pay to Tadeo when due a fee for each of the Services equal to the amount described in EXHIBIT A hereto..."

**Pattern 3: Pricing Based on Costs/Profits (No MFN)**
*   **Meaning**: Pricing is determined by manufacturing costs and profit maximization, not third-party comparisons.
*   **Variation Cues**: "subject", "sierra", "ninety", "conference", "accepted", "forth", "herein", "faith", "section", "orders".
*   **Representative Phrasings**:
    *   "The price for the Product... shall be subject to change due to changes in manufacturing costs and so as to maximize profits..."

**Pattern 4: MFN for Sponsorship Benefits**
*   **Meaning**: Sponsor receives benefits of equal or greater value than other sponsors, unless they pay more.
*   **Variation Cues**: "receive", "additional", "logo", "provided", "name", "unless", "identifying", "hereunder", "fee", "exceeds".
*   **Conditions/Exceptions**: "unless another proposed sponsor has agreed to pay a sponsorship fee that exceeds the amount paid by Sponsor..."
*   **Representative Phrasings**:
    *   "Racing agrees that... unless another proposed sponsor has agreed to pay a sponsorship fee that exceeds the amount paid by Sponsor, no other sponsor shall receive any benefit of greater value... than the Benefits provided to the Sponsor hereunder."

**Pattern 5: MFN for Pricing and Allowances**
*   **Meaning**: Distributor receives prices/benefits no less favorable than those offered to other agents/distributors/customers.
*   **Variation Cues**: "ntc", "provided", "agents", "favorable", "products", "distributors", "product", "agrees", "allowances", "commercial".
*   **Conditions/Exceptions**: "other than the Product Prices existing as of the date of this Agreement with NTC's commercial partners."
*   **Representative Phrasings**:
    *   "NTC agrees that the Product Prices, benefits and allowances offered to ALFA AESAR shall not be less favorable than those offered on Products provided to agents, distributors or marketed directly by NTC to any customers..."

**Pattern 6: Price Protection for Equity/Shares**
*   **Meaning**: Investor receives additional shares if subsequent shares are sold at a lower price, ensuring their effective price is no greater than the lowest subsequent price.
*   **Variation Cues**: "additional", "issue", "which", "common", "purchaser", "enters", "global", "section", "sells", "subsequent".
*   **Conditions/Exceptions**: "If at any time... Global Energy sells additional common shares... and the price of which is less than $200.00 per share..."
*   **Representative Phrasings**:
    *   "Global Energy shall issue additional common shares to Oxbow such that Oxbow's adjusted per-share price for its stockholdings shall be no greater than the lowest price paid by any such subsequent purchaser of its shares."

### No-Solicit of Employees

**Invariant Meaning**: Restricts a party from soliciting, hiring, or inducing the counterparty’s employees or contractors to leave.

**Pattern 1: Absence of Clause**
*   **Meaning**: No clause restricting solicitation of employees.
*   **Representative Phrasings**: "No" (Indicates absence in source data).

**Pattern 2: Mutual Non-Solicitation with Consent Exception**
*   **Meaning**: Parties cannot solicit each other's employees without prior written consent.
*   **Variation C
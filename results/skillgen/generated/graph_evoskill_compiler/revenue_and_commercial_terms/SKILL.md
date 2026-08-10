# SKILL.md

## 1. Purpose and Scope

This skill enables the runtime agent to review commercial contracts for specific financial and operational terms. The agent must identify clauses related to **Revenue/Profit Sharing**, **Price Restrictions**, **Minimum Commitment**, and **Volume Restriction**.

The agent acts as a pattern-matching engine, recognizing semantic variants of clause structures derived from graph-derived pattern cards. It does not interpret legal intent beyond the explicit text, nor does it provide legal advice. The agent must strictly adhere to the boundary rules: if the target contract does not contain supporting evidence for a finding, the agent must abstain or return `evidence_missing`.

**Covered Categories:**
1.  **Revenue/Profit Sharing**: Clauses defining payments based on percentages of revenue, profit, sales, or royalties, as opposed to fixed fees.
2.  **Price Restrictions**: Clauses limiting the ability to raise or lower prices, including caps, notice periods, or most-favored-nation provisions.
3.  **Minimum Commitment**: Clauses establishing binding obligations to purchase minimum quantities, pay minimum fees, or sell minimum shares.
4.  **Volume Restriction**: Clauses imposing fee increases, consent requirements, or tiered rates based on exceeding specific usage or sales thresholds.

## 2. Review Workflow

1.  **Input Validation**:
    *   Check if `contract_id` and `category` are provided.
    *   If absent, return status: `missing_input`.
    *   If the requested category is not in the covered categories list, return status: `unsupported_scope`.

2.  **Pattern Recognition**:
    *   Scan the target contract text for semantic matches to the **Common Clause Patterns** defined in Section 3.
    *   Use **Variation Cues** to identify potential matches.
    *   Distinguish between **Fixed/Fee-Based** arrangements (which are generally *not* Revenue/Profit Sharing or Volume Restrictions unless tiered) and **Variable/Percentage-Based** arrangements.

3.  **Evidence Extraction**:
    *   If a pattern is identified, extract the **verbatim text** from the target contract.
    *   Identify any **Conditions** (e.g., "provided that," "subject to") and **Exceptions** (e.g., "except," "unless").

4.  **Conservative Analysis**:
    *   **Revenue/Profit Sharing**: Confirm the payment is a percentage of revenue/profit/sales. Fixed fees, even if labeled "sponsorship" or "maintenance," are **not** revenue sharing unless they include a variable component tied to performance metrics.
    *   **Price Restrictions**: Confirm there is a limit on price changes (cap, frequency, notice period, or MFN clause). Unilateral rights to change price *without* restriction are **not** price restrictions.
    *   **Minimum Commitment**: Confirm a binding obligation to purchase/pay a specific amount or quantity. Exclusive purchasing rights without a minimum quantity are **not** minimum commitments.
    *   **Volume Restriction**: Confirm that exceeding a threshold triggers a fee increase, consent requirement, or rate change. Flat rates or fixed minimums are **not** volume restrictions.

5.  **Output Generation**:
    *   If evidence is found: Return status `answered`, include the verbatim quote, and provide a concise interpretation based on the pattern's invariant meaning.
    *   If no evidence is found: Return status `evidence_missing`.
    *   If the clause is ambiguous or requires high-risk legal interpretation: Return status `needs_human_review`.

## 3. Common Clause Patterns

### 3.1 Revenue/Profit Sharing

**Invariant Meaning**: A payment obligation calculated as a percentage or share of revenue, profit, sales, or royalties, rather than a fixed sum.

**Variation Cues**: `set`, `forth`, `exhibit`, `hereto`, `schedule`, `terms`, `pay`, `subject`, `product`, `per`, `gross`, `percent`, `fund`, `contribute`, `royalties`, `sales`.

**Conditions/Exceptions**:
*   **Condition**: Often subject to definitions of "Net Sales," "Gross Revenue," or specific exhibits.
*   **Exception**: May exclude certain products, territories, or periods.

**Representative Phrasings (Recognition Aids)**:
*   *Non-Sharing (Fixed Fee)*: "eDiets shall pay to Women.com a monthly fee in the amount set forth on Exhibit C..." (Interpretation: Fixed fee, not sharing).
*   *Non-Sharing (Fixed Rate)*: "Dynamex shall pay to Purolator the rates set forth in Schedule 'E'." (Interpretation: Fixed rates, not sharing).
*   *Non-Sharing (Sponsorship)*: "The Sponsor shall pay to Racing a sponsorship fee in the amount of $750,000.00..." (Interpretation: Fixed fee, not sharing).
*   *Non-Sharing (Per Unit)*: "The Principal shall pay the Company a fee of $1.00... per one net tonne..." (Interpretation: Fixed per-unit fee, not percentage sharing).
*   *Sharing (Revenue Contribution)*: "you agree to contribute to the Ad Fund a percentage of gross revenues... up to a maximum of two percent (2%)..." (Interpretation: Revenue sharing).
*   *Sharing (Royalties)*: "DIALOG will pay ENERGOUS the Royalties set forth in Exhibit B." (Interpretation: Royalty-based sharing).
*   *Sharing (Percentage of Sales)*: "pay to Contractor [ ** ] percent... of Company's Gross Invoiced Sales..." (Interpretation: Revenue sharing).

### 3.2 Price Restrictions

**Invariant Meaning**: Clauses that limit, cap, or regulate the ability of a party to increase or decrease prices. This includes notice requirements, annual caps, or most-favored-nation (MFN) provisions.

**Variation Cues**: `act`, `specified`, `exhibit`, `failure`, `judgment`, `made`, `where`, `member`, `good`, `liable`, `right`, `time`, `after`, `except`, `undelivered`, `immediately`, `accepted`, `orders`, `purchase`, `received`, `price`, `list`, `products`, `distributor`, `notice`, `published`, `provided`, `schedule`, `months`, `days`, `prior`, `twelve`, `increase`, `more`, `current`, `licensor`, `charged`, `exceed`, `taking`, `commercially`, `content`, `limited`, `unaffiliated`.

**Conditions/Exceptions**:
*   **Condition**: Restrictions often apply only after an initial term or require specific notice periods.
*   **Exception**: Unilateral rights to change price *without* restriction are **not** price restrictions.

**Representative Phrasings (Recognition Aids)**:
*   *No Restriction (Unilateral Right)*: "JRVS shall have the right to revise JRVS Price at any time... price increase shall be effective immediately..." (Interpretation: No restriction).
*   *No Restriction (Unilateral Right)*: "Company reserves the right to change its process and/or fees, from time to time, in its sole and absolute discretion." (Interpretation: No restriction).
*   *No Restriction (Published List)*: "NETGEAR may modify the Price List at any time... provide Distributor with written notice thirty days..." (Interpretation: Procedural notice only, no cap/restriction on ability to raise).
*   *Restriction (Cap & Frequency)*: "Women.com may not increase the Payment Schedule more than once in any period of twelve (12) consecutive months; and... such increase may not exceed twenty percent (20%)..." (Interpretation: Restricted by cap and frequency).
*   *Restriction (Cap & Notice)*: "rates shall not increase by more than ten ( 10% ) percent per year... provided that it provides BNL with notice... not less than thirty (30) days..." (Interpretation: Restricted by cap and notice).
*   *Restriction (MFN/Reasonableness)*: "such fees shall be commercially reasonable and... shall not exceed the fees charged by Licensor to unaffiliated third parties..." (Interpretation: Restricted by MFN and reasonableness).

### 3.3 Minimum Commitment

**Invariant Meaning**: A binding obligation to purchase a minimum quantity of goods, pay a minimum fee, or sell a minimum number of shares.

**Variation Cues**: `purchase`, `products`, `services`, `all`, `distributor`, `responsible`, `exclusively`, `fees`, `five`, `units`, `term`, `provided`, `exhibit`, `respect`, `date`, `provide`, `terminated`, `license`, `effect`, `who`, `except`, `refund`, `subscribed`, `which`, `minimum`, `herein`, `forth`, `fee`, `pay`, `rmb200`, `channel`, `million`, `cooperation`, `set`, `binding`, `order`, `firm`, `volume`, `amag`, `three`, `months`, `forecast`, `quantities`, `rolling`, `obligation`, `forecasted`, `represent`.

**Conditions/Exceptions**:
*   **Condition**: Commitments may be tied to specific terms, forecasts, or initial periods.
*   **Exception**: Exclusive purchasing rights without a specified minimum quantity are **not** minimum commitments.

**Representative Phrasings (Recognition Aids)**:
*   *No Commitment (Exclusive but No Min)*: "ENVISION will exclusively purchase the Product from SIERRA." (Interpretation: No minimum quantity specified).
*   *No Commitment (No Min)*: "No relevant text found." (Interpretation: No minimum commitment).
*   *No Commitment (Term Only)*: "Contractor shall perform during the Term... Services set forth on Exhibit B..." (Interpretation: No minimum purchase amount/units).
*   *Commitment (Share Sale Threshold)*: "In the event the Company is unable to sell a minimum of 708,050 Shares... this Agreement shall terminate..." (Interpretation: Minimum commitment to sell shares).
*   *Commitment (Fixed Fee)*: "The Sponsor shall pay to Racing a sponsorship fee in the amount of $750,000.00..." (Interpretation: Minimum financial commitment).
*   *Commitment (Binding Forecast)*: "[***] of each Forecast shall constitute a firm order and be a binding commitment on AMAG to purchase the volume..." (Interpretation: Binding minimum purchase).
*   *Commitment (Rolling Forecast)*: "quantities for each of the first three months of each respective Forecast shall be deemed to constitute and shall constitute firm, binding orders..." (Interpretation: Binding minimum purchase).

### 3.4 Volume Restriction

**Invariant Meaning**: Clauses that impose fee increases, consent requirements, or tiered rates when usage or sales exceed specific thresholds.

**Variation Cues**: `time`, `notice`, `fee`, `right`, `change`, `agrees`, `url`, `nai`, `reserves`, `locations`, `relevant`, `text`, `found`, `establish`, `inventory`, `exclusively`, `spare`, `adequate`, `one`, `located`, `less`, `per`, `episodes`, `forty`, `produce`, `show`, `year`, `company`, `original`, `than`, `connection`, `except`, `provide`, `section`, `bear`, `necessary`, `payments`, `purposes`, `connections`, `all`, `product`, `sales`, `sierra`, `inform`, `enough`, `demand`, `projections`, `production`, `royalty`, `percent`, `net`, `indication`, `rate`, `annual`, `subscribers`, `revenue`.

**Conditions/Exceptions**:
*   **Condition**: Restrictions often apply only after a base volume is exceeded.
*   **Exception**: Flat rates, fixed minimums, or simple royalty rates without tiering are **not** volume restrictions.

**Representative Phrasings (Recognition Aids)**:
*   *No Restriction (No Threshold)*: "N/A" or "No relevant text found." (Interpretation: No volume-based fee increases).
*   *No Restriction (Flat Rate)*: "Imprimis shall pay to Surgical Sales Commissions equal to ten percent (10%) of the Net Sales..." (Interpretation: Flat rate, no tiered increase).
*   *No Restriction (Fixed Min)*: "The Distributor agrees to purchase from Lucid minimum agreed quantity..." (Interpretation: Minimum commitment, not volume restriction/fee increase).
*   *Restriction (Tiered Royalty)*: "Subscribers Royalty Payable as Percentage of Gross Revenue 0 - 5000 6.25% 5001 - 7500 6.75%..." (Interpretation: Fee increases with volume).
*   *Restriction (Tiered Sales)*: "Annual Net Sales... $0 - $25,000,000 1.75% >$25,000,000 - $50,000,000 2.25%..." (Interpretation: Fee increases with sales volume).

## 4. Evidence and Citation Protocol

1.  **Verbatim Quoting**: Always quote the exact text from the target contract. Do not paraphrase the evidence.
2.  **Source Grounding**: Ensure the quoted text exists in the `target_contract_id`. Do not cite examples from the pattern cards as evidence for the target contract.
3.  **Contextual Citation**: Include the section number or clause title if available in the target contract to aid verification.
4.  **No Fabrication**: If the target contract does not contain the clause, do not invent one. Return `evidence_missing`.

## 5. Boundary and Abstention Rules

1.  **Strict Category Adherence**: Only analyze clauses falling under the four defined categories. Ignore other commercial terms (e.g., indemnification, confidentiality) unless they directly impact the defined categories.
2.  **Conservative Interpretation**:
    *   If a clause is ambiguous, default to `evidence_missing` or `needs_human_review`.
    *   Do not infer revenue sharing from fixed fees.
    *   Do not infer price restrictions from unilateral rights to change price.
    *   Do not infer minimum commitments from exclusive purchasing rights without quantity specs.
    *   Do not infer volume restrictions from flat royalty rates.
3.  **Abstention Triggers**:
    *   Return `missing_input` if `contract_id` or `category` is missing.
    *   Return `unsupported_scope` if the category is not in the covered list.
    *   Return `evidence_missing` if no supporting clause is found in the target contract.
    *   Return `needs_human_review` if the clause requires complex legal interpretation beyond pattern matching.
4.  **No Legal Advice**: The agent must not provide legal judgments, opinions, or advice. It only identifies and quotes contractual language.
# SKILL.md

## 1. Purpose and Scope

This skill enables the runtime agent to review target contracts for specific liability, indemnity, damages, and warranty patterns. The agent must identify whether the contract contains **Uncapped Liability**, **Cap on Liability**, **Liquidated Damages**, or **Warranty Duration** provisions based on semantic recognition of clause patterns.

**Scope Constraints:**
*   **Domain:** Contract Review.
*   **Categories:** Only the four categories defined in Section 3 are in scope.
*   **Source of Truth:** The target contract provided in the input.
*   **Prohibited Actions:** Do not invent legal rules, do not cite external laws, and do not use the representative examples from this skill definition as evidence for the target contract.

## 2. Review Workflow

1.  **Input Validation:**
    *   Check if `contract_id` and `category` (or implicit scope) are present.
    *   If missing, return status: `missing_input`.
    *   If the requested analysis is outside the four covered categories, return status: `unsupported_scope`.

2.  **Pattern Recognition:**
    *   Scan the target contract text for semantic variants of the patterns defined in Section 3.
    *   Look for **Variation Cues** (keywords) and **Invariant Meanings** (legal effect).
    *   Identify **Conditions** and **Exceptions** that modify the general rule.

3.  **Evidence Extraction:**
    *   If a pattern is found, extract the **verbatim text** from the target contract that supports the finding.
    *   If no supporting clause exists for the requested category, return status: `evidence_missing`.

4.  **Conservative Interpretation:**
    *   If the contract language is ambiguous or does not clearly match the invariant meaning of a pattern, abstain from making a definitive finding.
    *   If the finding involves high-risk interpretation or potential legal advice, return status: `needs_human_review`.

5.  **Output Generation:**
    *   Return the finding with the specific category, the verbatim evidence, and a concise interpretation based *only* on the target contract's text.

## 3. Common Clause Patterns

### 3.1 Uncapped Liability

**Invariant Meaning:** The contract provides for indemnification or liability for losses/damages without specifying a monetary cap, or explicitly excludes certain breaches from a general liability cap.

**Variation Cues:** `harmless`, `hold`, `indemnify`, `against`, `all`, `claims`, `arising`, `including`, `losses`, `out`, `damages`, `consequential`, `liable`, `special`, `incidental`, `indirect`, `except`, `apply`, `section`, `obligations`, `limit`, `provisions`, `breach`, `case`, `misconduct`, `negligence`, `costs`, `expenses`, `agrees`, `reasonable`, `hereunder`, `event`, `amounts`, `limited`, `paid`.

**Conditions/Exceptions:**
*   May apply to "all losses" or "any and all claims."
*   May explicitly exclude specific sections (e.g., IP infringement, confidentiality, indemnification) from a general liability cap.
*   May exclude liability for indirect/consequential damages while leaving direct damages uncapped.

**Representative Phrasings (Recognition Aids Only):**
*   "Each party shall indemnify and hold harmless the other party... from and against all losses, liabilities, damages and expenses... resulting from any claims... to the extent resulting from the breach..."
*   "PFHOF agrees to indemnify, defend, and hold harmless... from and against any and all claims, demands, liabilities, losses, suits, damages, costs... and expenses... arising out of or relating to..."
*   "EXCEPT FOR LIABILITY ARISING FROM SECTION 9.3 [Intellectual Property Infringement], IN NO EVENT SHALL EITHER PARTY BE LIABLE... FOR ANY INDIRECT, SPECIAL, INCIDENTAL, PUNITIVE OR CONSEQUENTIAL DAMAGES..."
*   "The foregoing shall not limit the indemnification, defense and hold harmless obligations... other than those set forth in Section 5.4 and shall not apply with respect to damages or losses arising from... willful misconduct, gross negligence or breach..."
*   "Liquidmetal agrees to indemnify, defend and hold... harmless from and against any and all claims, demands liabilities, losses, costs and expenses... irrespective of the theory upon which based..."
*   "EXCEPT UNDER SECTIONS 15 AND 16, IN NO EVENT WILL EITHER PARTY BE LIABLE... THE LIABILITY OF EITHER PARTY... IS LIMITED TO... THE AMOUNTS TO BE PAID..."

### 3.2 Cap on Liability

**Invariant Meaning:** The contract limits liability by excluding specific types of damages (e.g., consequential, indirect), setting a monetary maximum, or imposing a time limit on claims.

**Variation Cues:** `liable`, `special`, `consequential`, `damages`, `indirect`, `arising`, `incidental`, `possibility`, `except`, `profits`, `liability`, `exceed`, `event`, `paid`, `amount`, `hereunder`, `total`, `actually`, `distributor`, `aggregate`, `harmless`, `claims`, `indemnify`, `costs`, `hold`, `out`, `expenses`, `against`, `breach`, `after`, `action`, `cause`, `more`, `than`, `brought`, `form`, `regardless`, `loss`, `limited`, `including`, `company`.

**Conditions/Exceptions:**
*   **Monetary Cap:** Liability does not exceed fees paid, a specific amount, or a percentage of payments.
*   **Type Exclusion:** Excludes consequential, indirect, special, incidental, punitive, or lost profits.
*   **Temporal Cap:** Claims must be brought within a specific period (e.g., 1 year, 2 years) after the cause of action arises.
*   **Carve-outs:** Specific obligations (e.g., indemnification, confidentiality) may be excluded from the cap.

**Representative Phrasings (Recognition Aids Only):**
*   "EXCEPT IN CONNECTION WITH A BREACH... NEITHER PARTY WILL BE LIABLE FOR ANY SPECIAL, INDIRECT, CONSEQUENTIAL, EXEMPLARY OR INCIDENTAL DAMAGES..."
*   "IN NO EVENT SHALL D2'S LIABILITY HEREUNDER EXCEED THE TOTAL AMOUNT PAID OR OWED BY LICENSEE TO D2 UNDER THIS AGREEMENT."
*   "Company's liability shall not exceed the fees that MA has paid under this Agreement."
*   "NO ACTIONS, REGARDLESS OF FORM, ARISING OUT OF THIS AGREEMENT, MAY BE BROUGHT BY DISTRIBUTOR MORE THAN ONE (1) YEAR AFTER THE CAUSE OF ACTION HAS ARISEN."
*   "Neither party shall be liable to the other... for any amounts representing loss of profit, loss of business or indirect, consequential, exemplary, or punitive damages..."
*   "In no event will the Company be liable for incidental or consequential damages."

### 3.3 Liquidated Damages

**Invariant Meaning:** The contract specifies a fixed sum, formula, or fee payable upon breach or termination, or explicitly states that no such penalty/fee applies. Includes late payment interest charges.

**Variation Cues:** `termination`, `event`, `prior`, `thirty`, `liable`, `all`, `written`, `payable`, `fee`, `except`, `per`, `rate`, `interest`, `payment`, `charge`, `due`, `until`, `late`, `percent`, `payments`, `claims`, `expenses`, `indemnify`, `against`, `harmless`, `including`, `arising`, `fees`, `out`, `defend`, `special`, `punitive`, `law`, `month`, `unpaid`, `highest`, `permitted`, `penalty`, `without`, `majority`, `vote`, `trustees`, `board`, `notice`.

**Conditions/Exceptions:**
*   **Late Fees:** Interest or charges applied to overdue payments.
*   **Termination Fees:** Fixed amounts payable upon early termination.
*   **No Penalty:** Explicit statement that termination occurs without penalty or liquidated damages.
*   **General Indemnity vs. Liquidated:** General indemnification for actual losses is *not* liquidated damages unless a fixed sum/formula is specified.

**Representative Phrasings (Recognition Aids Only):**
*   "Late payments are subject to an interest charge, at the lower rate of (i) one and one-half percent (1.5%) per month, or (ii) the maximum legal rate."
*   "Any amount not paid when due will thereafter bear interest at the rate of one percent (1%) per month."
*   "Overdue payments shall accrue a late payment charge at the lesser of one and one half percent (1 1/2%) per month or the maximum rate allowed under applicable law."
*   "There is no payment or compensation contemplated under this Agreement."
*   "This Agreement may be terminated at any time, without the payment of any penalty, upon 60 days' written notice"
*   "This Agreement is terminable with respect to the Fund, without penalty..."

### 3.4 Warranty Duration

**Invariant Meaning:** The contract specifies the time period during which warranties (express or implied) are valid, or explicitly disclaims all warranties (resulting in no duration).

**Variation Cues:** `implied`, `warranties`, `merchantability`, `particular`, `purpose`, `fitness`, `including`, `express`, `all`, `disclaims`, `product`, `date`, `termination`, `after`, `provisions`, `article`, `warrants`, `hereby`, `company`, `represents`, `order`, `execution`, `performance`, `violate`, `hereunder`, `default`, `which`, `court`, `laws`, `duly`, `perform`, `good`, `standing`, `obligations`, `authority`, `licensor`, `makes`, `forth`, `mark`, `licensed`, `arising`, `period`, `accordance`, `one`, `documentation`, `defects`, `materials`, `free`, `workmanship`.

**Conditions/Exceptions:**
*   **Disclaimer:** "As is," "no warranties," "disclaims all implied warranties."
*   **Specific Duration:** "For a period of [X] days/months/years from delivery/effective date."
*   **Authority/Corporate Status:** Warranties regarding legal authority often do not have a specific duration clause separate from the agreement term.
*   **Performance Warranty:** Warranty that software/product performs in accordance with documentation for a specific period.

**Representative Phrasings (Recognition Aids Only):**
*   "XIMAGE MAKES NO WARRANTY OF ANY KIND, WHETHER EXPRESS OR IMPLIED... WITH RESPECT TO THE SERVICES..."
*   "EXCEPT AS EXPRESSLY SET FORTH IN THIS AGREEMENT... EACH PARTY DISCLAIMS ANY AND ALL WARRANTIES, EXPRESS OR IMPLIED..."
*   "Changepoint warrants that the Software will perform in substantial accordance with the Documentation... for a period of one hundred twenty (120) days after delivery..."
*   "Todos warrants that for a period of one (1) year from the date of delivery... the Product... shall perform substantially in accordance with the Product's documentation..."
*   "SRP hereby warrants that it has the authority to grant all rights... [No duration specified for defects]."
*   "As of the date of this Agreement, IMPCO represents and warrants that it is a company duly incorporated... [No duration specified for defects]."

## 4. Evidence and Citation Protocol

1.  **Verbatim Quotation:** All evidence must be quoted exactly as it appears in the target contract. Do not paraphrase, summarize, or alter the text.
2.  **Source Grounding:** Every finding must be linked to a specific span of text in the target contract.
3.  **No External Citations:** Do not cite case law, statutes, or other contracts. The representative examples in Section 3 are for pattern recognition only and must never be cited as evidence for the target contract.
4.  **Contextual Integrity:** When quoting, ensure the excerpt includes sufficient context to demonstrate the invariant meaning (e.g., if citing a cap, include the exception clause if present).

## 5. Boundary and Abstention Rules

1.  **Answer Only Using Target Contract:** The agent must derive all findings solely from the provided target contract text.
2.  **Cite Source-Grounded Evidence:** If a finding is made, verbatim evidence must be provided. If no evidence exists, return `evidence_missing`.
3.  **Missing Input Handling:** If `contract_id` or the specific category to review is absent, return `missing_input`.
4.  **Unsupported Scope:** If the user asks for analysis outside "Cap on Liability," "Uncapped Liability," "Liquidated Damages," or "Warranty Duration," return `unsupported_scope`.
5.  **No Legal Advice:** The agent provides pattern recognition and textual analysis, not legal advice. Do not interpret the legal validity or enforceability of clauses.
6.  **No Fabrication:** Do not invent clauses or attributes. If the contract is silent on a specific aspect (e.g., no warranty duration mentioned), state that the evidence is missing or that the contract does not specify it.
7.  **Human Review Routing:** If the contract language is highly ambiguous, contradictory, or involves complex legal judgments beyond pattern matching, return `needs_human_review`.
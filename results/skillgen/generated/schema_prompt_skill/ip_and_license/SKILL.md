# SKILL.md - IP and License Review

## Covered Categories

### License Grant
- **Description**: Determine whether the contract contains a license granted by one party to its counterparty.
- **Answer Format**: Yes/No

### Non-Transferable License
- **Description**: Determine whether the contract limits the ability of a party to transfer the license being granted to a third party.
- **Answer Format**: Yes/No

### Affiliate License-Licensor
- **Description**: Determine whether the contract contains a license grant by affiliates of the licensor or that includes intellectual property of affiliates of the licensor.
- **Answer Format**: Yes/No

### Affiliate License-Licensee
- **Description**: Determine whether the contract contains a license grant to a licensee (incl. sublicensor) and the affiliates of such licensee/sublicensor.
- **Answer Format**: Yes/No

### Unlimited/All-You-Can-Eat-License
- **Description**: Determine whether there is a clause granting one party an "enterprise," "all you can eat" or unlimited usage license.
- **Answer Format**: Yes/No

### Irrevocable or Perpetual License
- **Description**: Determine whether the contract contains a license grant that is irrevocable or perpetual.
- **Answer Format**: Yes/No

### Source Code Escrow
- **Description**: Determine whether one party is required to deposit its source code into escrow with a third party, which can be released to the counterparty upon the occurrence of certain events (bankruptcy, insolvency, etc.).
- **Answer Format**: Yes/No

### Post-Termination Services
- **Description**: Determine whether a party is subject to obligations after the termination or expiration of a contract, including any post-termination transition, payment, transfer of IP, wind-down, last-buy, or similar commitments.
- **Answer Format**: Yes/No

## Review Checklist

### License Grant
- [ ] Look for explicit language using terms like "grants," "licenses," "right to use," "right and license," "permission to use"
- [ ] Check for grants of intellectual property rights, trademarks, patents, copyrights, or trade secrets
- [ ] Identify the licensor and licensee parties
- [ ] Note any limitations on the scope of the license (field of use, territory, duration)

### Non-Transferable License
- [ ] Look for language stating the license is "personal," "non-transferable," "non-assignable"
- [ ] Check for clauses requiring consent for assignment or transfer
- [ ] Identify whether the restriction applies to the license itself or the entire agreement
- [ ] Note any exceptions (e.g., assignment to affiliates, change of control provisions)

### Affiliate License-Licensor
- [ ] Look for language granting licenses "by affiliates of the licensor" or "including intellectual property of affiliates"
- [ ] Check definitions of "Affiliate" and how they relate to the licensor
- [ ] Identify whether affiliates are explicitly included as licensors or sources of licensed IP
- [ ] Note any limitations on affiliate involvement

### Affiliate License-Licensee
- [ ] Look for language granting licenses "to licensee and its affiliates"
- [ ] Check whether affiliates of the licensee are explicitly included as authorized users
- [ ] Identify any restrictions on affiliate use (e.g., only while they remain affiliates)
- [ ] Note whether sublicensing to affiliates is permitted

### Unlimited/All-You-Can-Eat-License
- [ ] Look for terms like "enterprise license," "unlimited," "all you can eat," "unrestricted use"
- [ ] Check for licenses without quantity, volume, or usage caps
- [ ] Identify whether the license covers all products/services of the licensee
- [ ] Note any exceptions or limitations to the unlimited nature

### Irrevocable or Perpetual License
- [ ] Look for explicit terms like "irrevocable," "perpetual," "in perpetuity"
- [ ] Check for language stating the license survives termination
- [ ] Identify whether the license is terminable only for cause (not at will)
- [ ] Note any conditions that would cause revocation

### Source Code Escrow
- [ ] Look for explicit references to "source code escrow," "escrow agent," "deposit"
- [ ] Check for conditions triggering release (bankruptcy, insolvency, breach)
- [ ] Identify which party's source code is subject to escrow
- [ ] Note any exceptions or alternatives to escrow

### Post-Termination Services
- [ ] Look for obligations after termination: transition services, wind-down, last-buy, transfer of IP
- [ ] Check for post-termination payment obligations
- [ ] Identify any survival clauses that extend obligations beyond termination
- [ ] Note specific timeframes for post-termination obligations

## Evidence Extraction Rules

### Locating Evidence
1. **License Grant**: Search for sections titled "License Grant," "Grant of License," "Intellectual Property," or similar. Look for verbs like "grants," "licenses," "authorizes."

2. **Non-Transferable License**: Search for "non-transferable," "non-assignable," "personal," "Assignment" sections. Check for restrictions on transfer of rights.

3. **Affiliate License-Licensor**: Search for "Affiliate" in definitions and license sections. Look for phrases like "licensor and its affiliates" or "affiliates of licensor."

4. **Affiliate License-Licensee**: Search for "Affiliate" in definitions and license sections. Look for phrases like "licensee and its affiliates" or "affiliates of licensee."

5. **Unlimited/All-You-Can-Eat-License**: Search for "unlimited," "enterprise," "all you can eat," "unrestricted." Check for absence of usage caps or quantity limits.

6. **Irrevocable or Perpetual License**: Search for "irrevocable," "perpetual," "in perpetuity." Check termination sections for survival of license rights.

7. **Source Code Escrow**: Search for "escrow," "source code," "deposit." Check for conditions like bankruptcy, insolvency, or breach triggering release.

8. **Post-Termination Services**: Search for "post-termination," "transition," "wind-down," "last buy," "survival." Check termination sections for ongoing obligations.

### Extraction Patterns from Provided Contracts

**From OTISWORLDWIDECORP Intellectual Property Agreement (Section 3.1.1)**:
- Pattern: "royalty-free, nonexclusive, perpetual, irrevocable, fully paid-up, worldwide right and license"
- This indicates: License Grant (Yes), Irrevocable or Perpetual License (Yes)

**From PalmerSquareCapitalBdcInc Trademark License Agreement (Section 1.1)**:
- Pattern: "personal, non-exclusive, royalty-free right and license"
- This indicates: License Grant (Yes), Non-Transferable License (Yes - "personal")

**From NmfSlfIInc Trademark License Agreement (Section 1.1)**:
- Pattern: "personal, non-exclusive, royalty-free right and license"
- This indicates: License Grant (Yes), Non-Transferable License (Yes - "personal")

**From STWRESOURCESHOLDINGCORP Cooperation Agreement (Section 1)**:
- Pattern: "grants, leases and lets unto STW the right to explore for, drill for, produce, utilize, transport, and treat groundwater"
- This indicates: License Grant (Yes) - though this is a lease/right to use property, not traditional IP

**From ConformisInc Development Agreement (Section 5.1)**:
- Pattern: "All right, title and interest in and to the Improved Stryker Background IP will vest solely in Stryker"
- Pattern: "Joint IP shall be owned jointly by the Parties"
- This indicates: License Grant (Yes), Affiliate License-Licensor/Licensee (check definitions)

**From BIOFRONTERAAG Supply Agreement (Section 9.2)**:
- Pattern: "each party shall continue to own its existing patents, trademarks, copyrights, trade secrets and other intellectual property"
- This indicates: No license grant (parties retain their own IP)

**From BERKELEYLIGHTSINC Collaboration Agreement (Section 1.30)**:
- Pattern: "Collaboration Intellectual Property" defined as IP conceived during the Term
- This indicates: License Grant (Yes), potential for Affiliate licenses

**From StampscomInc Co-Branding Agreement (Section 7(a))**:
- Pattern: "The Company will have full and exclusive right, title and ownership interest in and to the Service"
- This indicates: License Grant (Yes - MBE Centers granted access)

**From BUFFALOWILDWINGSINC Franchise Agreement (Section I.A)**:
- Pattern: "grant you a license to use the 'Buffalo Wild Wings' Marks and System"
- This indicates: License Grant (Yes), Non-Transferable License (likely - franchise agreement)

**From MJBIOTECHINC Joint Venture Agreement**:
- Pattern: No explicit IP license grant - joint venture for business purposes
- This indicates: License Grant (No)

## Output Format

```json
{
  "status": "answered",
  "answer": "Yes",
  "evidence_unit_ids": ["OTISWORLDWIDECORP_04_03_2020-EX-10.4-INTELLECTUAL_PROPERTY_AGREEMENT_Section_3.1.1"],
  "source_contract_ids": ["OTISWORLDWIDECORP_04_03_2020-EX-10.4-INTELLECTUAL_PROPERTY_AGREEMENT"],
  "missing_inputs": [],
  "human_review_required": false
}
```

### Status Values
- **answered**: Sufficient evidence found to answer the question
- **evidence_missing**: No supporting clause exists in the contract
- **missing_input**: Contract_id or category is absent from the input
- **unsupported_scope**: The question is outside covered categories
- **needs_human_review**: Legal advice or high-risk interpretation required

## Boundary Rules

### Answering Rules
1. **Answer only using the target contract**: Do not reference or cite contracts other than the one being reviewed.
2. **Cite source-grounded evidence**: When answering, reference specific sections, clauses, or language from the contract.
3. **Return evidence_missing**: If no supporting clause exists for the category, return status "evidence_missing" with empty answer.
4. **Return missing_input**: If contract_id or category is absent from the input, return status "missing_input" with details.
5. **Return unsupported_scope**: If the question is outside the covered categories listed above, return status "unsupported_scope".
6. **Route to human review**: For legal advice, high-risk interpretation, or ambiguous clauses that require legal judgment, set "human_review_required" to true.

### Safety Requirements
1. **Do not cite non-target contracts**: Only use evidence from the contract being reviewed.
2. **Do not fabricate clauses**: Only reference language that actually exists in the contract.
3. **Do not provide legal advice**: Do not interpret legal consequences or provide recommendations.
4. **Do not generate externally sendable legal opinions**: The output is for internal review purposes only.

### Evidence Unit ID Format
Use the format: `[ContractID]_Section_[SectionNumber]` or `[ContractID]_[ClauseDescription]`

### Source Contract ID Format
Use the exact contract identifier as provided in the input.
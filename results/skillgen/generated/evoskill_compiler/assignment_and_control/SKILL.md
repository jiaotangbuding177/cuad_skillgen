# SKILL.md: Contract Review for Assignment and Change of Control

## Covered Categories
- **Change of Control**: Evidence Atoms (KA-0001 to KA-0323)
- **Anti-Assignment**: Evidence Atoms (KA-0004 to KA-0145)

## Common Clause Patterns & Example Phrasing

### Category: Change of Control

#### Pattern 1: Termination Right Upon Change of Control
**Description:** Grants one or both parties the right to terminate the agreement if a change of control (merger, acquisition, majority equity transfer) occurs. Often includes a notice period.
**Example Phrasing:**
> "Licensor may terminate this Agreement by providing prior written notice to Licensee upon the occurrence of a Change of Control." [KA-0090, KA-0302]
> "In the event of a change in control of a Party, the other Party shall have the right, upon written prior notice, to terminate this Agreement." [KA-0111]
**Variation Notes:** Notice periods vary (e.g., 30 days [KA-0001], 60 days [KA-0113], 6 months [KA-0286]). Some clauses allow immediate termination [KA-0104, KA-0213].

#### Pattern 2: Assignment Exception for Change of Control
**Description:** Explicitly exempts assignments resulting from a change of control (merger, sale of assets) from the general prohibition on assignment, often requiring notice but not consent.
**Example Phrasing:**
> "Notwithstanding the foregoing, each Party may assign this Agreement and its rights and obligations hereunder without such consent in connection with the transfer or sale of all or substantially all of..." [KA-0172]
> "Neither party may assign this Agreement, in whole or in part, without the other party's written consent... except that no such consent will be required in connection with a merger..." [KA-0196]
**Variation Notes:** Some require the successor to assume obligations [KA-0172, KA-0194]. Others require notice within a specific timeframe (e.g., 30 days) [KA-0206].

#### Pattern 3: Prohibited Change of Control (Consent Required)
**Description:** Treats a change of control as a prohibited transfer or assignment, requiring prior written consent from the other party.
**Example Phrasing:**
> "For purposes of the preceding sentence, and without limiting its generality, any merger, consolidation or reorganization involving Licensee... shall require Licensor's prior written consent." [KA-0210]
> "This JV Agreement cannot be assigned by a Party, also as a result of the transfer of a business as a going concern, of a merger... without the prior written consent of the other party." [KA-0277]
**Variation Notes:** May define "Change of Control" broadly to include management changes [KA-0042].

#### Pattern 4: Change of Control as Termination Event
**Description:** Defines a change of control as a specific "Termination Event" or "Event of Default" allowing termination.
**Example Phrasing:**
> "Supplier either: (i) merges with another entity, (ii) suffers a transfer involving fifty (50%) percent or more of any class of its voting securities... [is a Termination Event]." [KA-0083]
> "Any change, transfer or conveyance ("Transfer") in the ownership of Developer, which Transfer has not been approved in advance by Franchisor [is an event of default]." [KA-0149]
**Variation Notes:** May trigger specific payments or rights for the non-affected party [KA-0075].

### Category: Anti-Assignment

#### Pattern 5: General Prohibition on Assignment
**Description:** Broadly prohibits assignment or delegation of rights/obligations without prior written consent.
**Example Phrasing:**
> "Neither party may assign its rights or powers under this Agreement without the express written consent of the other, which consent shall not be unreasonably withheld." [KA-0080]
> "No Party may assign any rights under this Agreement or delegate any duties hereunder without the prior written consent of the other Party." [KA-0032]
**Variation Notes:** Consent is often qualified as "not to be unreasonably withheld" [KA-0028, KA-0080, KA-0097].

#### Pattern 6: Affiliate Assignment Exception
**Description:** Allows assignment to affiliates (subsidiaries, parents) without consent, often with notice requirements.
**Example Phrasing:**
> "Recipient may freely assign its rights under this Agreement to receive the Services to any of its affiliates." [KA-0005]
> "MICOA may assign this Agreement to its parent, affiliate, or subsidiary corporations who are licensed insurers upon written notice to Agency." [KA-0010]
**Variation Notes:** May restrict affiliate assignments to specific types of entities (e.g., licensed insurers) [KA-0010].

#### Pattern 7: Null and Void Assignment
**Description:** Explicitly states that any assignment in violation of the clause is null and void.
**Example Phrasing:**
> "No party to this Agreement may assign its rights or delegate its obligations under this Agreement... and any assignment in contravention hereof shall be null and void." [KA-0009]
**Variation Notes:** Often paired with a general prohibition [KA-0009].

#### Pattern 8: Assignment as Event of Default
**Description:** Defines an unauthorized assignment as a breach or event of default.
**Example Phrasing:**
> "(f) a Party attempts to assign this Agreement in breach of the Section entitled 'Non-Assignment' [is a Termination Event]." [KA-0084]
**Variation Notes:** May allow termination upon such breach [KA-0084].

## Review Checklist

### Change of Control
1. **Identify Termination Rights:** Does the contract grant either party the right to terminate upon a change of control? [Pattern 1, KA-0090, KA-0111]
2. **Check Assignment Exceptions:** Is assignment exempt from consent requirements if it results from a change of control? [Pattern 2, KA-0172, KA-0196]
3. **Verify Consent Requirements:** Does the contract require prior written consent for any change of control or merger? [Pattern 3, KA-0210, KA-0277]
4. **Assess Default Triggers:** Is a change of control defined as a termination event or default? [Pattern 4, KA-0083, KA-0149]

### Anti-Assignment
1. **Confirm General Prohibition:** Is there a broad prohibition on assignment without consent? [Pattern 5, KA-0032, KA-0080]
2. **Check Affiliate Exceptions:** Are assignments to affiliates permitted without consent? [Pattern 6, KA-0005, KA-0010]
3. **Verify Voidness Clause:** Does the contract state that unauthorized assignments are null and void? [Pattern 7, KA-0009]
4. **Identify Default Consequences:** Is unauthorized assignment an event of default? [Pattern 8, KA-0084]

## Output Format
JSON:
```json
{
  "status": "success",
  "answer": "Review completed based on patterns derived from evidence index.",
  "evidence_unit_ids": ["KA-0001", "KA-0004", "KA-0009", "KA-0010", "KA-0020", "KA-0023", "KA-0027", "KA-0028", "KA-0032", "KA-0042", "KA-0043", "KA-0075", "KA-0080", "KA-0083", "KA-0084", "KA-0090", "KA-0097", "KA-0104", "KA-0111", "KA-0113", "KA-0114", "KA-0115", "KA-0149", "KA-0172", "KA-0196", "KA-0206", "KA-0210", "KA-0213", "KA-0277", "KA-0286", "KA-0302"],
  "source_contract_ids": ["2ThemartComInc_19990826_10-12G_EX-10.10_6700288_EX-10.10_Co-Branding_Agreement__Agency_Agreement", "ABILITYINC_06_15_2020-EX-4.25-SERVICES_AGREEMENT", "ALLISONTRANSMISSIONHOLDINGSINC_12_15_2014-EX-99.1-COOPERATION_AGREEMENT", "AMERICANPHYSICIANSCAPITALINC_03_31_2003-EX-10.26-AGENCY_AGREEMENT", "AlliedEsportsEntertainmentInc_20190815_8-K_EX-10.19_11788293_EX-10.19_Content_License_Agreement", "Apollo_Endosurgery_-_Manufacturing_and_Supply_Agreement", "ArconicRolledProductsCorp_20191217_10-12B_EX-2.7_11923804_EX-2.7_Trademark_License_Agreement", "ArtaraTherapeuticsInc_20200110_8-K_EX-10.5_11943350_EX-10.5_License_Agreement", "BIOPURECORP_06_30_1999-EX-10.13-AGENCY_AGREEMENT", "CURAEGISTECHNOLOGIES,INC_05_26_2010-EX-1-CORPORATE_SPONSORSHIP_AGREEMENT", "CardlyticsInc_20180112_S-1_EX-10.16_11002987_EX-10.16_Maintenance_Agreement1", "ChinaRealEstateInformationCorp_20090929_F-1_EX-10.32_4771615_EX-10.32_Content_License_Agreement", "Columbia_Laboratories,_(Bermuda)_Ltd._-_AMEND_NO._2_TO_MANUFACTURING_AND_SUPPLY_AGREEMENT", "DRAGONSYSTEMSINC_01_08_1999-EX-10.17-OUTSOURCING_AGREEMENT", "DYNAMEXINC_06_06_1996-EX-10.4-TRANSPORTATION_SERVICES_AGREEMENT", "DYNTEKINC_07_30_1999-EX-10-ONLINE_HOSTING_AGREEMENT", "ElPolloLocoHoldingsInc_20200306_10-K_EX-10.16_12041700_EX-10.16_Development_Agreement", "FUSIONPHARMACEUTICALSINC_06_05_2020-EX-10.17-Supply_Agreement_-_FUSION", "GSVINC_05_15_1998-EX-10-SPONSORSHIP_AGREEMENT", "GlobalTechnologiesGroupInc_20050928_10KSB_EX-10.9_4148808_EX-10.9_Content_License_Agreement", "GopageCorp_20140221_10-K_EX-10.1_8432966_EX-10.1_Content_License_Agreement", "GpaqAcquisitionHoldingsInc_20200123_S-4A_EX-10.6_11951677_EX-10.6_License_Agreement", "KIROMICBIOPHARMA,INC_04_08_2020-EX-10.28-JOINT_VENTURE_AGREEMENT", "KitovPharmaLtd_20190326_20-F_EX-4.15_11584449_EX-4.15_Manufacturing_Agreement", "LejuHoldingsLtd_20140121_DRS_(on_F-1)_EX-10.26_8473102_EX-10.26_Content_License_Agreement1"],
  "missing_inputs": [],
  "human_review_required": false
}
```

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
# SKILL.md: Contract Review for Assignment and Change of Control

## Covered Categories
1.  **Change of Control**: Evidence Atoms (KA-0001 to KA-0277)
2.  **Anti-Assignment**: Evidence Atoms (KA-0004 to KA-0117)

## Evidence-Based Review Rules

### 1. Change of Control
Review contracts for clauses that define "Change of Control" and specify the rights (termination, assignment, or consent requirements) triggered by such events.

*   **Termination Rights**: Look for clauses granting either party or a specific party the right to terminate the agreement upon a Change of Control.
    *   *Immediate Termination*: Check for language allowing immediate termination without notice [KA-0104, KA-0213].
    *   *Notice-Based Termination*: Identify requirements for written notice periods (e.g., 30 days [KA-0001, KA-0229], 60 days [KA-0113]) or specific termination payments [KA-0075].
    *   *Unilateral Rights*: Note if only one party (e.g., Licensor [KA-0090], Company [KA-0042]) holds the termination right.
*   **Assignment Exceptions**: Determine if Change of Control events are exempt from general anti-assignment restrictions.
    *   *No Consent Required*: Look for explicit exemptions where consent is not required for mergers, acquisitions, or asset sales [KA-0027, KA-0146, KA-0172, KA-0196].
    *   *Notice Only*: Identify clauses where assignment is permitted upon providing written notice (e.g., within 30 days [KA-0206]) but without requiring consent [KA-0019, KA-0194].
    *   *Consent Required*: Flag clauses where Change of Control assignments still require prior written consent [KA-0148, KA-0210, KA-0248, KA-0277].
*   **Definition of Change of Control**: Verify how the event is defined.
    *   *Equity Thresholds*: Look for specific ownership thresholds (e.g., majority equity [KA-0001], 20% voting power [KA-0113], 50% stock transfer [KA-0083]).
    *   *Corporate Events*: Check for inclusion of mergers, consolidations, reorganizations, or sales of substantially all assets [KA-0023, KA-0083, KA-0148, KA-0210].

### 2. Anti-Assignment
Review contracts for general restrictions on assigning rights or delegating obligations.

*   **General Prohibition**: Identify clauses that broadly prohibit assignment without prior written consent.
    *   *Mutual Restrictions*: Look for language prohibiting both parties from assigning without consent [KA-0009, KA-0020, KA-0022, KA-0032, KA-0043, KA-0047, KA-0062, KA-0068, KA-0072, KA-0076, KA-0080, KA-0086, KA-0112, KA-0117].
    *   *Unilateral Restrictions*: Note if only one party (e.g., Provider [KA-0004], Contractor [KA-0016], Licensee [KA-0028]) is restricted.
*   **Exceptions to Prohibition**: Check for permitted assignments that do not require consent.
    *   *Affiliates*: Look for permissions to assign to affiliates, subsidiaries, or parent companies [KA-0005, KA-0010, KA-0091, KA-0114].
    *   *Successors*: Identify exceptions for successors in interest due to mergers or asset sales, often requiring the successor to assume obligations [KA-0115, KA-0194].
*   **Consequences of Breach**: Determine the penalty for unauthorized assignment.
    *   *Null and Void*: Check if unauthorized assignments are explicitly stated as null and void [KA-0009].
    *   *Termination Event*: Look for language defining unauthorized assignment as a termination event or default [KA-0084, KA-0149].

## Review Checklist

### Change of Control
- [ ] **Identify Trigger Events**: Does the contract define Change of Control? (e.g., merger, >50% equity change, asset sale) [KA-0001, KA-0083, KA-0148].
- [ ] **Check Termination Rights**: Can either party terminate upon Change of Control? If so, is notice required? [KA-0001, KA-0104, KA-0229].
- [ ] **Verify Assignment Permissions**: Is assignment during Change of Control allowed without consent? [KA-0027, KA-0172].
- [ ] **Assess Consent Requirements**: If assignment is allowed, is prior written consent still required? [KA-0148, KA-0210, KA-0277].
- [ ] **Review Notice Periods**: If notice is required for assignment or termination, what is the timeframe? (e.g., 30 days [KA-0001, KA-0206]).

### Anti-Assignment
- [ ] **Locate Assignment Clause**: Is there a general prohibition on assignment? [KA-0009, KA-0020].
- [ ] **Determine Consent Standard**: Is consent required? If so, is it "prior written consent" or "not to be unreasonably withheld"? [KA-0028, KA-0097].
- [ ] **Check for Affiliate Exceptions**: Can the party assign to its affiliates without consent? [KA-0005, KA-0091].
- [ ] **Verify Successor Rights**: Are assignments to successors in mergers/acquisitions permitted? [KA-0115, KA-0194].
- [ ] **Identify Breach Consequences**: Does unauthorized assignment constitute a default or termination event? [KA-0084, KA-0149].

## Output Format
```json
{
  "status": "success",
  "answer": "Review completed based on evidence index.",
  "evidence_unit_ids": ["KA-0001", "KA-0004", "KA-0009", "KA-0019", "KA-0020", "KA-0023", "KA-0027", "KA-0028", "KA-0032", "KA-0042", "KA-0043", "KA-0047", "KA-0062", "KA-0068", "KA-0072", "KA-0075", "KA-0076", "KA-0080", "KA-0083", "KA-0084", "KA-0086", "KA-0090", "KA-0091", "KA-0097", "KA-0104", "KA-0112", "KA-0113", "KA-0114", "KA-0115", "KA-0117", "KA-0146", "KA-0148", "KA-0149", "KA-0172", "KA-0194", "KA-0196", "KA-0206", "KA-0210", "KA-0213", "KA-0229", "KA-0248", "KA-0277"],
  "source_contract_ids": [
    "2ThemartComInc_19990826_10-12G_EX-10.10_6700288_EX-10.10_Co-Branding_Agreement__Agency_Agreement",
    "ABILITYINC_06_15_2020-EX-4.25-SERVICES_AGREEMENT",
    "ALLISONTRANSMISSIONHOLDINGSINC_12_15_2014-EX-99.1-COOPERATION_AGREEMENT",
    "AMERICANPHYSICIANSCAPITALINC_03_31_2003-EX-10.26-AGENCY_AGREEMENT",
    "ASPIRITYHOLDINGSLLC_05_07_2012-EX-10.6-OUTSOURCING_AGREEMENT",
    "AlliedEsportsEntertainmentInc_20190815_8-K_EX-10.19_11788293_EX-10.19_Content_License_Agreement",
    "AlliedEsportsEntertainmentInc_20190815_8-K_EX-10.34_11788308_EX-10.34_Sponsorship_Agreement",
    "Apollo_Endosurgery_-_Manufacturing_and_Supply_Agreement",
    "ArconicRolledProductsCorp_20191217_10-12B_EX-2.7_11923804_EX-2.7_Trademark_License_Agreement",
    "ArtaraTherapeuticsInc_20200110_8-K_EX-10.5_11943350_EX-10.5_License_Agreement",
    "BIOPURECORP_06_30_1999-EX-10.13-AGENCY_AGREEMENT",
    "BNLFINANCIALCORP_03_30_2007-EX-10.8-OUTSOURCING_AGREEMENT",
    "CANOPETROLEUM,INC_12_13_2007-EX-10.1-Sponsorship_Agreement",
    "CHAPARRALRESOURCESINC_03_30_2000-EX-10.66-TRANSPORTATION_CONTRACT",
    "CHIPMOSTECHNOLOGIESBERMUDALTD_04_18_2016-EX-4.72-Strategic_Alliance_Agreement",
    "CORALGOLDRESOURCES,LTD_05_28_2020-EX-4.1-CONSULTING_AGREEMENT",
    "CURAEGISTECHNOLOGIES,INC_05_26_2010-EX-1-CORPORATE_SPONSORSHIP_AGREEMENT",
    "CardlyticsInc_20180112_S-1_EX-10.16_11002987_EX-10.16_Maintenance_Agreement1",
    "CcRealEstateIncomeFundadv_20181205_POS_8C_EX-99.(H)(3)_11447739_EX-99.(H)(3)_Marketing_Agreement",
    "ChinaRealEstateInformationCorp_20090929_F-1_EX-10.32_4771615_EX-10.32_Content_License_Agreement",
    "Columbia_Laboratories,_(Bermuda)_Ltd._-_AMEND_NO._2_TO_MANUFACTURING_AND_SUPPLY_AGREEMENT",
    "DRAGONSYSTEMSINC_01_08_1999-EX-10.17-OUTSOURCING_AGREEMENT",
    "DYNAMEXINC_06_06_1996-EX-10.4-TRANSPORTATION_SERVICES_AGREEMENT",
    "DYNTEKINC_07_30_1999-EX-10-ONLINE_HOSTING_AGREEMENT",
    "DataCallTechnologies_20060918_SB-2A_EX-10.9_944510_EX-10.9_Content_License_Agreement",
    "ENTERTAINMENTGAMINGASIAINC_02_15_2005-EX-10.5-DISTRIBUTOR_AGREEMENT",
    "EdietsComInc_20001030_10QSB_EX-10.4_2606646_EX-10.4_Co-Branding_Agreement",
    "ElPolloLocoHoldingsInc_20200306_10-K_EX-10.16_12041700_EX-10.16_Development_Agreement",
    "FUSIONPHARMACEUTICALSINC_06_05_2020-EX-10.17-Supply_Agreement_-_FUSION",
    "GSITECHNOLOGYINC_11_16_2009-EX-10.2-INTELLECTUAL_PROPERTY_AGREEMENT_between_SONY_ELECTRONICS_INC._and_GSI_TECHNOLOGY,_INC.",
    "GSVINC_05_15_1998-EX-10-SPONSORSHIP_AGREEMENT",
    "GlobalTechnologiesGroupInc_20050928_10KSB_EX-10.9_4148808_EX-10.9_Content_License_Agreement",
    "GopageCorp_20140221_10-K_EX-10.1_8432966_EX-10.1_Content_License_Agreement",
    "GpaqAcquisitionHoldingsInc_20200123_S-4A_EX-10.6_11951677_EX-10.6_License_Agreement",
    "HealthcentralCom_19991108_S-1A_EX-10.27_6623292_EX-10.27_Co-Branding_Agreement",
    "INKTOMICORP_06_08_1998-EX-10.14-SOFTWARE_HOSTING_AGREEMENT",
    "KIROMICBIOPHARMA,INC_04_08_2020-EX-10.28-JOINT_VENTURE_AGREEMENT"
  ],
  "missing_inputs": [],
  "human_review_required": false
}
```

## Boundary Rules
*   **[RB-001]**: Answers must be derived solely from the target contract's clauses.
*   **[RB-002]**: All findings must cite specific evidence unit IDs (KA-XXXX).
*   **[RB-003]**: If a specific clause pattern (e.g., "unreasonable withholding of consent") is not present in the target contract, return `evidence_missing` for that specific rule.
*   **[RB-004]**: If `contract_id` or `category` is missing from the input, return `missing_input`.
*   **[RB-005]**: If the query asks about categories outside "Anti-Assignment" or "Change of Control", return `unsupported_scope`.
*   **[RB-006]**: Route any request for legal strategy or high-risk interpretation to human review.
*   **[SR-001]**: Do not cite clauses from non-target contracts (e.g., do not use KA-0001 if reviewing a contract that does not contain the 2TheMart/i-Escrow agreement).
*   **[SR-002]**: Do not fabricate clause patterns; only use patterns supported by the provided Evidence Index.
*   **[SR-003]**: Do not provide legal advice; provide factual contract analysis.
*   **[SR-004]**: Do not generate externally sendable legal opinions.
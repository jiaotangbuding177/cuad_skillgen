# Telecom τ³ SOP Skill

> Method: `graph_evoskill_compiler`. Compile-time sources are frozen τ³-bench policy, tool contracts, knowledge documents where applicable, and training tasks only where an official train split exists.

## Graph-selected Pattern Cards

### PAT-0001: Telecom Agent Policy

Central atom `KA-00001`; related atoms: KA-00010, KA-00011, KA-00012, KA-00013, KA-00014, KA-00016, KA-00017, KA-00018, KA-00025, KA-00027, KA-00036, KA-00047, KA-00059, KA-00063.

### PAT-0002: Domain Basics

Central atom `KA-00002`; related atoms: none.

### PAT-0003: Customer

Central atom `KA-00003`; related atoms: KA-00004, KA-00005, KA-00007, KA-00008, KA-00009, KA-00011, KA-00012, KA-00013, KA-00025, KA-00036, KA-00039, KA-00052, KA-00054, KA-00056, KA-00057, KA-00059, KA-00060, KA-00064, KA-00071, KA-00094.

### PAT-0004: Payment Method

Central atom `KA-00004`; related atoms: KA-00003, KA-00007.

### PAT-0005: Line

Central atom `KA-00005`; related atoms: KA-00003, KA-00006, KA-00007, KA-00008, KA-00011, KA-00012, KA-00013, KA-00014, KA-00027, KA-00031, KA-00036, KA-00039, KA-00056, KA-00057, KA-00060, KA-00064, KA-00065, KA-00066, KA-00071, KA-00074.

### PAT-0006: Plan

Central atom `KA-00006`; related atoms: KA-00005, KA-00012, KA-00039, KA-00060.

### PAT-0007: Device

Central atom `KA-00007`; related atoms: KA-00003, KA-00004, KA-00005.

### PAT-0008: Bill

Central atom `KA-00008`; related atoms: KA-00003, KA-00005, KA-00010, KA-00011, KA-00059, KA-00060, KA-00064.

### PAT-0009: Customer Lookup

Central atom `KA-00009`; related atoms: KA-00003, KA-00012, KA-00013, KA-00014, KA-00052, KA-00054, KA-00060.

### PAT-0010: Overdue Bill Payment

Central atom `KA-00010`; related atoms: KA-00001, KA-00008, KA-00011, KA-00012, KA-00013, KA-00014, KA-00016, KA-00017, KA-00024, KA-00025, KA-00027, KA-00036, KA-00047, KA-00048, KA-00049, KA-00059, KA-00063, KA-00083, KA-00093, KA-00094.

### PAT-0011: Line Suspension

Central atom `KA-00011`; related atoms: KA-00001, KA-00003, KA-00005, KA-00008, KA-00010, KA-00012, KA-00013, KA-00014, KA-00017, KA-00021, KA-00022, KA-00024, KA-00027, KA-00030, KA-00031, KA-00036, KA-00039, KA-00043, KA-00049, KA-00055.

### PAT-0012: Data Refueling

Central atom `KA-00012`; related atoms: KA-00001, KA-00003, KA-00005, KA-00006, KA-00009, KA-00010, KA-00011, KA-00013, KA-00014, KA-00024, KA-00027, KA-00028, KA-00031, KA-00032, KA-00036, KA-00037, KA-00039, KA-00040, KA-00043, KA-00047.

### PAT-0013: Change Plan

Central atom `KA-00013`; related atoms: KA-00001, KA-00003, KA-00005, KA-00009, KA-00010, KA-00011, KA-00012, KA-00014, KA-00016, KA-00017, KA-00036, KA-00039, KA-00045, KA-00047, KA-00052, KA-00063, KA-00073, KA-00081, KA-00083.

### PAT-0014: Data Roaming

Central atom `KA-00014`; related atoms: KA-00001, KA-00005, KA-00009, KA-00010, KA-00011, KA-00012, KA-00013, KA-00016, KA-00017, KA-00020, KA-00021, KA-00022, KA-00024, KA-00025, KA-00026, KA-00027, KA-00029, KA-00030, KA-00031, KA-00032.

### PAT-0015: Technical Support

Central atom `KA-00015`; related atoms: KA-00017, KA-00030, KA-00053, KA-00055, KA-00058, KA-00080, KA-00093, KA-00094.

### PAT-0016: Introduction

Central atom `KA-00016`; related atoms: KA-00001, KA-00010, KA-00013, KA-00014, KA-00018, KA-00019, KA-00020, KA-00021, KA-00025, KA-00028, KA-00029, KA-00030, KA-00031, KA-00034, KA-00035, KA-00036, KA-00038, KA-00041, KA-00043, KA-00044.

### PAT-0017: What the user can do on their device

Central atom `KA-00017`; related atoms: KA-00001, KA-00010, KA-00011, KA-00013, KA-00014, KA-00015, KA-00022, KA-00024, KA-00027, KA-00030, KA-00040, KA-00049.

### PAT-0018: Diagnostic Actions (Read-only)

Central atom `KA-00018`; related atoms: KA-00001, KA-00016, KA-00019, KA-00021, KA-00025, KA-00029, KA-00031, KA-00035, KA-00036, KA-00038, KA-00040, KA-00044, KA-00047, KA-00048, KA-00065, KA-00066, KA-00069, KA-00071, KA-00073, KA-00077.

### PAT-0019: Fix Actions (Write/Modify)

Central atom `KA-00019`; related atoms: KA-00016, KA-00018, KA-00020, KA-00021, KA-00024, KA-00025, KA-00029, KA-00031, KA-00036, KA-00038, KA-00040, KA-00044, KA-00066, KA-00068, KA-00070, KA-00072, KA-00073, KA-00074, KA-00076, KA-00081.

### PAT-0020: Understanding and Troubleshooting Your Phone's Cellular Service

Central atom `KA-00020`; related atoms: KA-00014, KA-00016, KA-00019, KA-00021, KA-00022, KA-00025, KA-00027, KA-00028, KA-00029, KA-00030, KA-00031, KA-00032, KA-00033, KA-00034, KA-00035, KA-00036, KA-00038, KA-00041, KA-00043, KA-00044.

### PAT-0021: Common Service Issues and Their Causes

Central atom `KA-00021`; related atoms: KA-00011, KA-00014, KA-00016, KA-00018, KA-00019, KA-00020, KA-00024, KA-00025, KA-00026, KA-00027, KA-00028, KA-00029, KA-00030, KA-00031, KA-00034, KA-00036, KA-00040, KA-00043, KA-00044, KA-00047.

### PAT-0022: Diagnosing Service Issues

Central atom `KA-00022`; related atoms: KA-00011, KA-00014, KA-00017, KA-00020, KA-00024, KA-00025, KA-00027, KA-00030, KA-00032, KA-00034, KA-00040, KA-00043, KA-00045, KA-00065, KA-00066, KA-00073, KA-00080, KA-00083.

### PAT-0023: Troubleshooting Service Problems

Central atom `KA-00023`; related atoms: KA-00030, KA-00033, KA-00034, KA-00046.

### PAT-0024: Airplane Mode

Central atom `KA-00024`; related atoms: KA-00010, KA-00011, KA-00012, KA-00014, KA-00017, KA-00019, KA-00021, KA-00022, KA-00025, KA-00031, KA-00032, KA-00034, KA-00035, KA-00036, KA-00037, KA-00038, KA-00040, KA-00045, KA-00048, KA-00050.

### PAT-0025: SIM Card Issues

Central atom `KA-00025`; related atoms: KA-00001, KA-00003, KA-00010, KA-00014, KA-00016, KA-00018, KA-00019, KA-00020, KA-00021, KA-00022, KA-00024, KA-00026, KA-00027, KA-00029, KA-00030, KA-00031, KA-00034, KA-00035, KA-00036, KA-00037.

### PAT-0026: Incorrect APN Settings

Central atom `KA-00026`; related atoms: KA-00014, KA-00021, KA-00025, KA-00030, KA-00035, KA-00037, KA-00038, KA-00040, KA-00044, KA-00048, KA-00049, KA-00050, KA-00051, KA-00067, KA-00068, KA-00073, KA-00077, KA-00078, KA-00079.

### PAT-0027: Line Suspension

Central atom `KA-00027`; related atoms: KA-00001, KA-00005, KA-00010, KA-00011, KA-00012, KA-00014, KA-00017, KA-00020, KA-00021, KA-00022, KA-00025, KA-00030, KA-00031, KA-00034, KA-00036, KA-00039, KA-00043, KA-00044, KA-00047, KA-00056.

### PAT-0028: Understanding and Troubleshooting Your Phone's Mobile Data

Central atom `KA-00028`; related atoms: KA-00012, KA-00016, KA-00020, KA-00021, KA-00029, KA-00030, KA-00031, KA-00032, KA-00033, KA-00034, KA-00035, KA-00036, KA-00038, KA-00041, KA-00043, KA-00044, KA-00047, KA-00048, KA-00065, KA-00066.

### PAT-0029: What is Mobile Data?

Central atom `KA-00029`; related atoms: KA-00014, KA-00016, KA-00018, KA-00019, KA-00020, KA-00021, KA-00025, KA-00028, KA-00030, KA-00031, KA-00035, KA-00036, KA-00038, KA-00040, KA-00043, KA-00044, KA-00047, KA-00048, KA-00065, KA-00066.

### PAT-0030: Prerequisites for Mobile Data

Central atom `KA-00030`; related atoms: KA-00011, KA-00014, KA-00015, KA-00016, KA-00017, KA-00020, KA-00021, KA-00022, KA-00023, KA-00025, KA-00026, KA-00027, KA-00028, KA-00029, KA-00031, KA-00032, KA-00033, KA-00034, KA-00035, KA-00036.

### PAT-0031: Common Mobile Data Issues and Causes

Central atom `KA-00031`; related atoms: KA-00005, KA-00011, KA-00012, KA-00014, KA-00016, KA-00018, KA-00019, KA-00020, KA-00021, KA-00024, KA-00025, KA-00027, KA-00028, KA-00029, KA-00030, KA-00032, KA-00034, KA-00035, KA-00036, KA-00037.

### PAT-0032: Diagnosing Mobile Data Issues

Central atom `KA-00032`; related atoms: KA-00012, KA-00014, KA-00020, KA-00022, KA-00024, KA-00028, KA-00030, KA-00031, KA-00036, KA-00038, KA-00040, KA-00043, KA-00045, KA-00060, KA-00069, KA-00073, KA-00074, KA-00076.

### PAT-0033: Troubleshooting Mobile Data Problems

Central atom `KA-00033`; related atoms: KA-00020, KA-00023, KA-00028, KA-00030, KA-00035, KA-00043, KA-00046.

### PAT-0034: Airplane Mode

Central atom `KA-00034`; related atoms: KA-00014, KA-00016, KA-00020, KA-00021, KA-00022, KA-00023, KA-00024, KA-00025, KA-00027, KA-00028, KA-00030, KA-00031, KA-00035, KA-00036, KA-00037, KA-00041, KA-00043, KA-00044, KA-00045, KA-00047.

### PAT-0035: Mobile Data Disabled

Central atom `KA-00035`; related atoms: KA-00014, KA-00016, KA-00018, KA-00020, KA-00024, KA-00025, KA-00026, KA-00028, KA-00029, KA-00030, KA-00031, KA-00033, KA-00034, KA-00036, KA-00037, KA-00038, KA-00040, KA-00043, KA-00045, KA-00047.

### PAT-0036: Addressing Data Roaming Problems

Central atom `KA-00036`; related atoms: KA-00001, KA-00003, KA-00005, KA-00010, KA-00011, KA-00012, KA-00013, KA-00014, KA-00016, KA-00018, KA-00019, KA-00020, KA-00021, KA-00024, KA-00025, KA-00027, KA-00028, KA-00029, KA-00030, KA-00031.

### PAT-0037: Data Saver Mode

Central atom `KA-00037`; related atoms: KA-00012, KA-00014, KA-00024, KA-00025, KA-00026, KA-00030, KA-00031, KA-00034, KA-00035, KA-00036, KA-00038, KA-00040, KA-00043, KA-00045, KA-00047, KA-00048, KA-00049, KA-00050, KA-00051, KA-00065.

### PAT-0038: VPN Connection Issues

Central atom `KA-00038`; related atoms: KA-00014, KA-00016, KA-00018, KA-00019, KA-00020, KA-00024, KA-00025, KA-00026, KA-00028, KA-00029, KA-00030, KA-00031, KA-00032, KA-00035, KA-00036, KA-00037, KA-00040, KA-00043, KA-00044, KA-00048.

### PAT-0039: Data Plan Limits Reached

Central atom `KA-00039`; related atoms: KA-00003, KA-00005, KA-00006, KA-00011, KA-00012, KA-00013, KA-00014, KA-00027, KA-00030, KA-00031, KA-00036, KA-00040, KA-00043, KA-00047, KA-00052, KA-00060, KA-00063, KA-00064.

### PAT-0040: Optimizing Network Mode Preferences

Central atom `KA-00040`; related atoms: KA-00012, KA-00014, KA-00017, KA-00018, KA-00019, KA-00021, KA-00022, KA-00024, KA-00025, KA-00026, KA-00029, KA-00030, KA-00031, KA-00032, KA-00035, KA-00036, KA-00037, KA-00038, KA-00039, KA-00043.

### PAT-0041: Understanding and Troubleshooting MMS (Picture/Video Messaging)

Central atom `KA-00041`; related atoms: KA-00016, KA-00020, KA-00028, KA-00030, KA-00034, KA-00042, KA-00043, KA-00047, KA-00048, KA-00049, KA-00082, KA-00083, KA-00091.

### PAT-0042: What is MMS?

Central atom `KA-00042`; related atoms: KA-00036, KA-00041, KA-00047, KA-00049, KA-00091.

### PAT-0043: Prerequisites for MMS

Central atom `KA-00043`; related atoms: KA-00011, KA-00012, KA-00014, KA-00016, KA-00020, KA-00021, KA-00022, KA-00025, KA-00027, KA-00028, KA-00029, KA-00030, KA-00031, KA-00032, KA-00033, KA-00034, KA-00035, KA-00036, KA-00037, KA-00038.

### PAT-0044: Common MMS Issues and Causes

Central atom `KA-00044`; related atoms: KA-00014, KA-00016, KA-00018, KA-00019, KA-00020, KA-00021, KA-00025, KA-00026, KA-00027, KA-00028, KA-00029, KA-00030, KA-00031, KA-00034, KA-00036, KA-00038, KA-00043, KA-00047, KA-00048, KA-00049.

### PAT-0045: Diagnosing MMS Issues

Central atom `KA-00045`; related atoms: KA-00013, KA-00014, KA-00020, KA-00022, KA-00024, KA-00025, KA-00030, KA-00032, KA-00034, KA-00035, KA-00037, KA-00040, KA-00043, KA-00047, KA-00050, KA-00073, KA-00074, KA-00078, KA-00081, KA-00087.

### PAT-0046: Troubleshooting MMS Problems

Central atom `KA-00046`; related atoms: KA-00023, KA-00033.

### PAT-0047: Ensuring Basic Connectivity for MMS

Central atom `KA-00047`; related atoms: KA-00001, KA-00010, KA-00012, KA-00013, KA-00014, KA-00016, KA-00018, KA-00020, KA-00021, KA-00025, KA-00027, KA-00028, KA-00029, KA-00030, KA-00031, KA-00034, KA-00035, KA-00036, KA-00037, KA-00039.

### PAT-0048: Unsuitable Network Technology for MMS

Central atom `KA-00048`; related atoms: KA-00010, KA-00014, KA-00016, KA-00018, KA-00020, KA-00021, KA-00024, KA-00025, KA-00026, KA-00028, KA-00029, KA-00030, KA-00031, KA-00034, KA-00035, KA-00036, KA-00037, KA-00038, KA-00040, KA-00041.

### PAT-0049: Verifying APN (MMSC URL) for MMS

Central atom `KA-00049`; related atoms: KA-00010, KA-00011, KA-00016, KA-00017, KA-00021, KA-00025, KA-00026, KA-00030, KA-00036, KA-00037, KA-00038, KA-00040, KA-00041, KA-00042, KA-00043, KA-00044, KA-00047, KA-00048, KA-00050, KA-00051.

### PAT-0050: Investigating Wi-Fi Calling Interference with MMS

Central atom `KA-00050`; related atoms: KA-00014, KA-00024, KA-00025, KA-00026, KA-00035, KA-00037, KA-00038, KA-00040, KA-00045, KA-00048, KA-00049, KA-00051, KA-00073, KA-00074, KA-00083, KA-00091.

### PAT-0051: Messaging App Lacks Necessary Permissions

Central atom `KA-00051`; related atoms: KA-00014, KA-00026, KA-00030, KA-00035, KA-00037, KA-00038, KA-00040, KA-00044, KA-00048, KA-00049, KA-00050, KA-00088, KA-00089, KA-00090, KA-00091.

## Runtime boundary

The graph changes compile-time organization only. Runtime tools, environment, task evaluator and retrieval budget remain fixed.

## Governance

- `POL-0001` Telecom Agent Policy
- `POL-0002` Domain Basics
- `POL-0003` Customer
- `POL-0004` Payment Method
- `POL-0005` Line
- `POL-0006` Plan
- `POL-0007` Device
- `POL-0008` Bill
- `POL-0009` Customer Lookup
- `POL-0010` Overdue Bill Payment
- `POL-0011` Line Suspension
- `POL-0012` Data Refueling
- `POL-0013` Change Plan
- `POL-0014` Data Roaming
- `POL-0015` Technical Support
- `POL-0016` Introduction
- `POL-0017` What the user can do on their device
- `POL-0018` Diagnostic Actions (Read-only)
- `POL-0019` Fix Actions (Write/Modify)
- `POL-0020` Understanding and Troubleshooting Your Phone's Cellular Service
- `POL-0021` Common Service Issues and Their Causes
- `POL-0022` Diagnosing Service Issues
- `POL-0023` Troubleshooting Service Problems
- `POL-0024` Airplane Mode
- `POL-0025` SIM Card Issues
- `POL-0026` Incorrect APN Settings
- `POL-0027` Line Suspension
- `POL-0028` Understanding and Troubleshooting Your Phone's Mobile Data
- `POL-0029` What is Mobile Data?
- `POL-0030` Prerequisites for Mobile Data
- `POL-0031` Common Mobile Data Issues and Causes
- `POL-0032` Diagnosing Mobile Data Issues
- `POL-0033` Troubleshooting Mobile Data Problems
- `POL-0034` Airplane Mode
- `POL-0035` Mobile Data Disabled
- `POL-0036` Addressing Data Roaming Problems
- `POL-0037` Data Saver Mode
- `POL-0038` VPN Connection Issues
- `POL-0039` Data Plan Limits Reached
- `POL-0040` Optimizing Network Mode Preferences
- `POL-0041` Understanding and Troubleshooting MMS (Picture/Video Messaging)
- `POL-0042` What is MMS?
- `POL-0043` Prerequisites for MMS
- `POL-0044` Common MMS Issues and Causes
- `POL-0045` Diagnosing MMS Issues
- `POL-0046` Troubleshooting MMS Problems
- `POL-0047` Ensuring Basic Connectivity for MMS
- `POL-0048` Unsuitable Network Technology for MMS
- `POL-0049` Verifying APN (MMSC URL) for MMS
- `POL-0050` Investigating Wi-Fi Calling Interference with MMS
- `POL-0051` Messaging App Lacks Necessary Permissions
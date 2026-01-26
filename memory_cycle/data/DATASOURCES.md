# Data Sources and Methodology

## Overview

This document describes the data sources, methodology, and update procedures for the MemoryCycle application. Use this as a reference when updating quarterly data.

---

## Required Data Fields

### Core Fields (Required for Model)

1. **dram_contract_price_index**
   - Description: DRAM contract price indexed to base period
   - Source: TrendForce, DRAMeXchange, industry reports
   - Update: Quarterly (contract prices settle monthly, use Q-end value)

2. **inventory_weeks_supplier**
   - Description: Weeks of DRAM inventory at suppliers
   - Source: Micron 10-Q, SK hynix earnings, Samsung reports
   - Calculation: Days of inventory ÷ 7

3. **utilization_rate**
   - Description: Fab utilization rate (0-1 scale)
   - Source: Earnings call commentary, TrendForce surveys
   - Note: Often estimated from production/capacity data

### Supporting Fields

4. **dram_spot_index**
   - Source: Metal.com, spot market tracking
   - Note: More volatile than contract prices

5. **hbm_asp_estimate_usd_per_gb**
   - Source: Analyst estimates, earnings commentary
   - Note: Not publicly disclosed; requires estimation

6. **capex_quarterly_bn_usd**
   - Source: Sum of Micron + SK hynix + Samsung semi capex
   - Micron: 10-Q filings
   - SK hynix: 6-K filings
   - Samsung: ~40% of total company capex

7. **hbm_revenue_share_pct**
   - Source: SK hynix segment reporting, analyst estimates
   - Note: Direct reporting started in 2023

8. **nvidia_datacenter_rev_bn_usd**
   - Source: Nvidia quarterly earnings (direct data)
   - Use: Proxy for AI infrastructure demand

9. **dram_revenue_bn_usd**
   - Source: TrendForce quarterly reports, Counterpoint

---

## Update Procedures

### Quarterly Update Checklist

Update within 2 weeks after quarter end when all suppliers report earnings.

#### Week 1-2: Data Collection

1. **Micron Earnings** (reports first, typically early in new quarter)
   - Visit: https://investors.micron.com
   - Extract:
     - Days of inventory (convert to weeks)
     - Quarterly capex
     - Utilization commentary
     - DRAM revenue

2. **SK hynix Earnings** (reports mid-quarter)
   - Visit: https://www.skhynix.com/ir
   - Extract:
     - HBM revenue and share
     - Inventory levels
     - Quarterly capex
     - Utilization commentary

3. **Samsung Electronics** (reports last)
   - Visit: https://www.samsung.com/semiconductor/ir/
   - Extract:
     - Semiconductor division revenue
     - Capex (estimate 40% for memory)
     - Inventory commentary

4. **Nvidia Datacenter Revenue**
   - Visit: https://investor.nvidia.com
   - Extract: Datacenter segment revenue (direct value)

5. **Industry Reports**
   - TrendForce: DRAM pricing, industry revenue
   - DRAMeXchange: Spot and contract prices
   - Counterpoint Research: Market analysis

#### Week 2: Data Entry

1. Open MemoryCycle application
2. Navigate to **Data Input** page
3. Enter quarterly data using Manual Entry form
4. Document sources in "Source Notes" field
5. Verify data passes validation
6. Save data point

#### Week 2-3: Analysis

1. Check **Dashboard** for regime update
2. Review **Signals** for any changes
3. Run **Forecast** with updated data
4. Update **Backtest** to include new quarter

---

## Data Source Details

### DRAM Contract Prices

**Primary Sources:**
- TrendForce (https://www.trendforce.com/price/dram)
- DRAMeXchange historical database

**Methodology:**
- Use DDR4 16Gb or DDR5 16Gb contract prices
- Index to Q1 2015 = 100 for consistency
- Contract prices are quarterly averages

**Example Calculation:**
```
If Q1 2015 DDR4 16Gb = $3.00
And Q4 2025 DDR5 16Gb = $8.50
Index = (8.50 / 3.00) * 100 = 283
```

### Inventory Weeks

**Primary Source:** Company Earnings Reports

**Micron Example** (from 10-Q):
- "Inventory at quarter end: $8.5B"
- "Cost of goods sold (quarterly): $5.1B"
- Days of inventory = (8.5 / 5.1) * 90 = 150 days
- Weeks of inventory = 150 / 7 = 21.4 weeks

**SK hynix Example:**
- Look for "Inventory Turnover" or direct inventory weeks statement
- Typically disclosed in Korean filings or earnings call

**Averaging:**
- Average Micron and SK hynix inventory weeks
- Samsung rarely discloses detail; estimate from others

### Utilization Rate

**Sources:**
- Earnings call transcripts: "We are operating at X% utilization"
- TrendForce quarterly surveys
- Industry analyst estimates

**Estimation Method (if not disclosed):**
```
Estimated Utilization = Bit Shipments / Installed Capacity

If utilization not directly stated:
- Tight conditions (low inventory, high demand): 0.88-0.95
- Normal conditions: 0.78-0.88
- Glut conditions (high inventory, weak demand): 0.60-0.78
```

### HBM ASP Estimation

**Challenge:** Not publicly disclosed

**Estimation Approach:**
1. SK hynix HBM revenue (disclosed)
2. Estimate HBM bit shipments from:
   - Nvidia GPU shipments (H100/H200/B200 each use 6-8 HBM stacks)
   - AMD MI300 shipments
3. Calculate: HBM Revenue / Bit Shipments = ASP

**Analyst Estimates:**
- Check JP Morgan, Morgan Stanley, TrendForce HBM reports
- Typical range 2024-2025: $30-85 per GB

### Capex Aggregation

**Formula:**
```
Total Capex = Micron Capex + SK hynix Capex + Samsung Semi Capex

Samsung Semi Capex ≈ 0.40 * Samsung Total Capex
```

**Example:**
- Micron Q4 2025: $3.5B
- SK hynix Q4 2025: $4.2B
- Samsung total Q4 2025: $10.0B → Semi: $4.0B
- **Total: $11.7B**

---

## Historical Data Bootstrap

If building historical dataset from scratch:

### 2015-2020 Period

1. **DRAM Prices:**
   - Statista historical dataset
   - Academic papers on DRAM cycles
   - Historical TrendForce reports

2. **Inventory:**
   - Extract from archived 10-Q/6-K filings on SEC EDGAR
   - Use Micron as primary source (most consistent disclosure)

3. **Utilization:**
   - Analyst reports from Goldman Sachs, JP Morgan archives
   - Industry surveys from IC Insights

4. **HBM:**
   - Assume negligible (<1%) before 2020
   - HBM2 era: 1-5% (2020-2022)
   - HBM3 era: 5-20% (2022-2024)

### 2020-2025 Period

- More complete data available
- Use direct earnings report extractions
- TrendForce quarterly reports
- Regular analyst coverage

---

## Data Quality Notes

### Confidence Levels

- **High Confidence:**
  - Nvidia datacenter revenue (direct SEC filing)
  - Capex (direct from filings)
  - DRAM contract prices (industry standard reporting)

- **Medium Confidence:**
  - Inventory weeks (derived from financial statements)
  - Utilization rates (mix of disclosed and estimated)
  - Total DRAM revenue (aggregated from multiple sources)

- **Lower Confidence:**
  - HBM ASPs (analyst estimates, high variance)
  - Samsung-specific metrics (limited disclosure)
  - Pre-2020 HBM data (market was very small)

### Known Limitations

1. **Quarterly Aggregation:** Monthly variations smoothed
2. **Regional Differences:** Global averages mask regional dynamics
3. **Product Mix:** DDR4 vs DDR5 transition affects comparability
4. **HBM Composition:** HBM2E vs HBM3 vs HBM3E pricing differences

---

## Validation Checks

When entering new data, verify:

1. **Utilization Rate:**
   - Should be between 0.60 (severe glut) and 0.95 (peak tight)
   - Typical range: 0.75-0.90

2. **Inventory Weeks:**
   - Should be between 3 (extreme tight) and 30 (severe glut)
   - Typical range: 8-18 weeks

3. **Price Changes:**
   - QoQ changes >50% are rare; verify if this occurs
   - Tight regimes: +5% to +20% per quarter
   - Glut regimes: -10% to -30% per quarter

4. **HBM Share:**
   - Should be monotonically increasing (structural shift)
   - 2024: ~18-20%
   - 2025: ~35-45%
   - 2030 projection: ~50%

5. **Cross-Checks:**
   - Low inventory + high utilization = prices should be rising
   - High inventory + low utilization = prices should be falling

---

## Recommended Tools

### Financial Data
- **SEC EDGAR**: Free access to 10-Q, 10-K filings
- **Company IR Sites**: Earnings presentations
- **Kofia (Korea)**: SK hynix Korean filings

### Industry Data
- **TrendForce** (paid): Comprehensive DRAM data
- **Counterpoint** (paid): Market analysis
- **Statista** (mixed): Some free historical data

### News Aggregation
- **Tom's Hardware**: Memory industry coverage
- **AnandTech**: Technical analysis
- **Reuters/Bloomberg**: Financial news

### Spreadsheet Templates
- Create Excel tracker with:
  - Column for each data field
  - Row for each quarter
  - Formula cells for validation checks
  - Links to source documents

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-01-26 | Initial data sources documentation |

---

## Contact for Data Questions

For questions about specific data points or methodologies, refer to:
- TrendForce contact page for pricing data
- Company investor relations for financial data
- Project maintainers for calculation methods

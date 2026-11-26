# Testing & Acceptance Criteria

## 1. Automated tests (already executed: see `docs/test_results.md`)
`python scripts/run_tests.py` -> **22/22 passed**

| Area | Test | Method | Status |
|---|---|---|---|
| Duplicate orders | No repeated order lines | pandas + SQL V2 | Pass |
| Missing values | 0 nulls after cleaning | pandas + SQL V3 | Pass |
| Negative amounts | `sales > 0` everywhere | pandas + SQL V4 + CHECK constraint | Pass |
| Invalid dates | no future dates, ship >= order | pandas + SQL V5 + CHECK constraint | Pass |
| Incorrect totals | sum(regions) = sum(categories) = grand total | pandas + SQL V8 | Pass |
| Python vs SQL | KPIs, Top 10, monthly sales, region, category | SQLite logic test | Pass |

## 2. Manual Power BI tests (to do after you build the `.pbix`)

### 2.1 KPI verification: clear all slicers
| Card | Expected |
|---|---|
| Total Sales | 5,408,541.60 |
| Total Profit | 720,415.35 |
| Total Orders | 4,497 |
| Total Quantity | 29,913 |
| Profit Margin % | 13.32% |

### 2.2 Filter functionality
| Filters | Sales | Profit | Orders | Qty | Margin |
|---|---|---|---|---|---|
| Region = West, Category = Technology, Year = 2024 | 239,476.02 | 57,328.83 | 194 | 777 | 23.94% |
| Segment = Corporate, Year = 2025 | 421,714.92 | 54,061.31 | 338 | 2,278 | 12.82% |
| Date between 01-Nov-2025 and 31-Dec-2025 | 477,748.46 | 80,580.08 | 345 | 2,321 | 16.87% |
| Category = Furniture | 2,020,838.57 | 85,276.06 | 2,592 | 10,713 | 4.22% |

### 2.3 Top 10 products must rank in this order
1. Laser Copier Workstation (1,036,962.57)
2. Compact Desktop Copier (505,391.16)
3. Smartphone Rugged Edition (343,757.27)
4. Oak Conference Table (336,868.70)
5. Smartphone 128GB Black (322,610.50)
6. Executive Leather Chair (271,748.26)
7. Adjustable Standing Desk (240,743.12)
8. Round Meeting Table (213,962.51)
9. Corner Bookcase Unit (163,757.92)
10. Label Printer Pro (158,509.77)

### 2.4 Interaction checklist
- [ ] Date slicer filters every visual
- [ ] Category, Region, Segment slicers filter every visual
- [ ] Clicking a Region bar/map point cross-filters Top 10 and Trend
- [ ] Drill-down Category > Sub-Category > Product works
- [ ] Dynamic titles change with slicers
- [ ] Tooltip page appears on hover
- [ ] Reset button clears all slicers
- [ ] Sum of monthly points in trend = Total Sales card (with the same filters)

## 3. Acceptance criteria sign-off
| Criterion | How verified | Status |
|---|---|---|
| Dashboard totals match validated SQL | SQL V9 (diff = 0) + section 2.1 | Python/SQL-logic verified; Oracle + Power BI to confirm |
| Top 10 products rank correctly | section 2.3 | Verified in code; confirm on visual |
| Monthly trends accurate | 48 months matched SQL vs Python (B7) | Verified; confirm on visual |
| Slicers/interactions work | section 2.2 and 2.4 | Manual |
| KPI calculations verified | `docs/kpi_definitions.md` + tests A9, B5 | Verified |

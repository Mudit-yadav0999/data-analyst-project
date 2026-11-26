# Business Insights Report: Sales Performance (2022-2025)

> **Data note:** this project ships with a synthetic, Superstore-style retail dataset (seeded, reproducible). The insights below describe *this* dataset and show the type of analysis the dashboard supports. If you swap in the real Kaggle file, re-run the notebook and update the numbers.

## 1. Executive summary
The business generated **$5.41M in sales** and **$720K profit** (13.32% margin) from **4,497 orders**, with an average order value of **$1,202.70**. Growth is real but **slowing** (+24.1% in 2023, +16.2% in 2024, +3.6% in 2025), and profit is **highly concentrated** in a few products while discounting and one product family quietly destroy value.

## 2. Key findings

### 2.1 Growth is slowing
| Year | Sales | Profit | Margin | YoY sales |
|---|---|---|---|---|
| 2022 | $1.04M | $126K | 12.1% | n/a |
| 2023 | $1.30M | $173K | 13.3% | +24.1% |
| 2024 | $1.51M | $207K | 13.8% | +16.2% |
| 2025 | $1.56M | $214K | 13.7% | +3.6% |

Margin improved slightly but growth has nearly flattened. **Action:** invest in new-customer acquisition and category expansion rather than relying on repeat demand.

### 2.2 Strong seasonality
**Q4 delivers 36% of annual sales**; November + December alone deliver 27.3%. The strongest month is December 2025 ($245K), the weakest February 2022 ($39K). **Action:** build inventory and marketing plans around Q3-Q4; run planned promotions in the Jan-Feb trough instead of discounting in peak months.

### 2.3 Profit depends on a few products
- **Copiers = 28.5% of sales but 61.5% of profit.**
- **Laser Copier Workstation alone = 19.2% of sales and 41.6% of profit.**

**Risk:** a stock-out, supplier problem or competitor price cut on one product would cut profit dramatically. **Action:** secure supply and protect pricing on top copiers; develop mid-priced alternatives.

### 2.4 Discounts above 20% lose money
| Discount band | Sales | Profit | Margin |
|---|---|---|---|
| 0% | $2.86M | $647K | 22.6% |
| 1-10% | $0.98M | $133K | 13.6% |
| 11-20% | $1.03M | $27K | 2.7% |
| 21-30% | $0.32M | -$28K | -8.9% |
| >30% | $0.23M | -$59K | -26.2% |

Lines discounted above 20% are **14% of all lines** and **10% of sales**, yet they generate **-$87K profit**. **Action:** cap standard discounts at 20% and require approval above that; track discount as a KPI next to margin.

### 2.5 Furniture sells a lot but earns little
| Category | Sales share | Margin |
|---|---|---|
| Technology | 54.7% | 19.2% |
| Furniture | 37.4% | **4.2%** |
| Office Supplies | 7.9% | 15.6% |

Inside Furniture, **Tables lose money (-$23K, -2.6% margin)** even though they bring $889K in sales; at 0% discount they earn only 6.5%, so discounting pushes them negative. Four table products appear in the loss-making list (Oak Conference Table, Round Meeting Table, Adjustable Standing Desk, Folding Training Table). **Action:** reprice or renegotiate supplier cost on Tables, stop discounting them, or drop the weakest SKUs.

### 2.6 Regional performance
| Region | Sales | Margin |
|---|---|---|
| West | $1.71M | 16.7% |
| East | $1.58M | 15.9% |
| Central | $1.29M | **7.2%** |
| South | $0.83M | 11.0% |

Central's average discount (10.7%) is about the same as other regions (10.5%), so **discounting does not explain the gap**. Tables alone lose about $21K in Central. **Action:** investigate Central's product mix, freight/fulfilment cost and pricing; South is the smallest region and a growth opportunity if margin is protected.

### 2.7 Customers and payments
- **Segments:** Consumer = 50% of sales; margins are almost identical across segments (13.3-13.5%), so segment targeting should be based on volume and acquisition cost, not margin.
- **Customer concentration:** the top 10% of customers (80 of 800) bring 24.5% of sales; 347 customers spend above the average customer. **Action:** a loyalty/key-account programme for the top tier.
- **Payment mix:** Credit Card 29.5%, Debit Card 20.8%, UPI 18.7%, PayPal 11.1%, Cash on Delivery 10.4%, Net Banking 9.5%. COD is 10% of sales; track its return/failure rate if data becomes available. *(Payment Mode is synthetic in this dataset.)*

## 3. Recommendations (priority order)
1. **Discount governance:** cap at 20%, approval workflow above; expected to remove roughly $87K of loss-making sales leakage.
2. **Fix Tables:** pricing/cost review; stop discounting.
3. **Central region profit review:** margin gap vs West is ~9.5 percentage points.
4. **Protect copier revenue:** supply security, price monitoring.
5. **Plan around Q4** and use targeted offers in the Q1 trough.
6. **Revive growth:** acquisition and new categories; 2025 growth only 3.6%.

## 4. Limitations
- Synthetic dataset: results are illustrative, not real company performance.
- No cost-of-goods, returns, marketing spend or inventory data, so profit drivers cannot be fully explained.
- Region is derived from the customer's location in this dataset.

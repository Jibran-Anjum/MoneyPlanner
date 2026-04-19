# 💰 MoneyPlanner

> **Your Financial Future, Calculated Clearly.**

|                      |                                            |
|----------------------|--------------------------------------------|
| **Type**             | Web Application                            |
| **Stack**            | Python, Streamlit, Plotly, Pandas          |
| **Deployment**       | Streamlit Community Cloud                  |
| **Context**          | Hackathon Submission                       |
| **Live Demo**        | [moneyplanner.streamlit.app](https://moneyplanner-hqi44jhgvceaunpuntfgzz.streamlit.app/) |

---

## 📖 Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [How to Use](#how-to-use)
- [Technical Architecture](#technical-architecture)
- [Calculation Logic Reference](#calculation-logic-reference)
- [Security & Privacy](#security--privacy)
- [Future Enhancements](#future-enhancements)
- [Disclaimer](#disclaimer)

---

## Project Overview

**MoneyPlanner** is a privacy-first financial forecasting tool built with Python and Streamlit. It is designed for **Individuals, Households, and Shops** to move beyond simple expense tracking and into actionable financial planning.

The application analyzes income, expenses, loans, investments, and savings goals to generate a personalized **Financial Health Score** and a realistic timeline for achieving every financial milestone.

🔗 **Live Demo:** [moneyplanner.streamlit.app](https://moneyplanner-hqi44jhgvceaunpuntfgzz.streamlit.app/)

---

## Key Features

| Feature | Description |
|---------|-------------|
| 👤 **Individual Plan** | Track personal income, expenses, loans, investments, and savings goals. Receive a graded Financial Health Score (0–100) with a detailed breakdown. |
| 👨‍👩‍👧 **Household Plan** | Combine multiple earners to view total household cash flow, shared expenses, and income contribution percentages. |
| 🏪 **Shop Plan** | Analyze business revenue, Cost of Goods Sold (COGS), operating expenses, and profit margins with a dedicated waterfall chart. |
| 🏥 **Financial Health Score** | A proprietary 0–100 score based on four weighted components: Expense Ratio, Debt Load, Savings Rate, and Income Buffer. |
| 🎯 **Smart Goal Timeline** | Enter a target amount and the app calculates the exact month and year you will reach it based on your actual remaining monthly savings. |
| 📈 **Investment Projections** | Visualize compound interest growth over time with year-by-year breakdowns and comparison against the initial principal. |
| 🏦 **Loan Amortization** | View detailed month-by-month repayment schedules showing principal vs. interest, plus side-by-side loan comparison charts. |
| 🌍 **Multi-Currency Support** | Choose from PKR, USD, EUR, GBP, and AED. Currency selection persists globally across all pages. |
| 🔒 **Zero-Knowledge Architecture** | No database, no user accounts, no API calls. All data remains in your browser's session state. |

---

## Project Structure
MoneyPlanner/
│
├── 💰MoneyPlanner.py # Home page — navigation & global currency selector
├── requirements.txt # Python dependencies
│
├── pages/
│ ├── 👤_Individual.py # Individual financial planner page
│ ├── 👨‍👩‍👧_Household.py # Household financial planner page
│ └── 🏪_Shop.py # Shop financial planner page
│
├── logic/
│ ├── calculations.py # Core financial formulas (interest, loans, health score)
│ └── plan_generator.py # Orchestrates data and generates plan dictionaries
│
└── components/
└── charts.py # All Plotly visualizations (gauges, bars, pie, waterfall)


### File Responsibilities

| File | Responsibility |
|------|----------------|
| `app.py` | Home page, global sidebar, currency session state shared across all pages. |
| `pages/1_Individual.py` | Input forms, plan generation trigger, tabbed results display for Individual. |
| `pages/2_Household.py` | Input forms, multiple earner management, plan display for Household. |
| `pages/3_Shop.py` | Revenue, COGS, operating expense inputs, profit analysis, plan display for Shop. |
| `logic/calculations.py` | Pure financial math — no UI, no side effects. |
| `logic/plan_generator.py` | Assembles calculation results into structured plan dictionary + recommendations. |
| `components/charts.py` | All Plotly figure builders — returns `go.Figure` objects only. |

---

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Step 1 — Clone the Repository

```bash
git clone https://github.com/your-username/moneyplanner.git
cd moneyplanner
```

### Step 3 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Add your Requirements in `requirements.txt`
```bash
streamlit
plotly
pandas
numpy
```

### Step 5 — Run the Application
```bash
streamlit run app.py
```

The application will open automatically in your default web browser at http://localhost:8501.

---

# How to Use

## Select Your Currency
Use the currency selector in the sidebar on any page to choose your preferred currency symbol. This selection is stored globally and applies to all three planner pages automatically.

## Choose Your Profile
Click on one of the three profile options in the sidebar:

    - 👤 Individual – For personal financial planning
    - 👨‍👩‍👧 Household – For families with multiple earners
    - 🏪 Shop – For small business owners

## Enter Your Financial Data
Fill in the input sections on your chosen profile page:

    - Income & Expenses – Your monthly take-home income and total essential expenses
    - Loans (optional) – Any active loans with principal, interest rate, and duration
    - Investments (optional) – Money invested with expected annual return and time horizon
    - Savings Goals (optional) – Things you want to save toward with a target amount

-> 💡 Tip: Use the Add buttons to include multiple loans, investments, or goals. The Clear All buttons require a two-step confirmation to prevent accidental data loss.

## Generate Your Plan
Click the Generate Financial Plan button at the bottom of the input form. A spinner will appear while calculations run. Once complete, a success message confirms the plan is ready. Scroll down to view results.

## Explore Your Results
| Tab                    | Contents                                                                               |
|------------------------|----------------------------------------------------------------------------------------|
| 📊 **Overview**        | Key metrics, Financial Health Score gauge, budget breakdown, DTI ratio, emergency fund |
| 👥 **Earners**         | Household only — income contributions per earner, pie chart, earner summary table      |
| 💹 **Profit Analysis** | Shop only — gross/net profit, waterfall chart, cost ratio table                        |
| 🏦 **Loans**           | Amortization charts, monthly repayment tables, loan comparison chart                   |
| 📈 **Investments**     | Compound growth projections, year-by-year breakdown                                    |
| 🎯 **Goals**           | Months and years to reach each savings goal, feasibility status                        |
| ✅ **Recommendations** | Rule-based personalized financial advice and legal disclaimer                          |

# Technical Architecture

## Data Flow
User Input (Streamlit Widgets)
        ↓
plan_generator.py (Orchestrator)
        ↓
calculations.py (Financial Engine)
        ↓
charts.py (Plotly Visualizations)
        ↓
Streamlit UI (Display to User)

## Key Modules

### `calculations.py` — The Mathematical Engine

Pure financial functions with no side effects.

| Function | Purpose |
|----------|---------|
| `monthlyLoanPayment()` | Standard PMT formula for fixed-rate loans |
| `loanAmortizationSchedule()` | Month-by-month principal vs. interest breakdown |
| `compoundInterest()` | Compound interest with configurable frequency |
| `budgetBreakdown_50_30_20()` | Needs (50%), Wants (30%), Savings (20%) allocation |
| `debtToIncomeRatio()` | (Monthly Debt / Income) × 100 |
| `emergencyFundRecommendation()` | 3-month and 6-month expense buffers |
| `financialHealthScore()` | Weighted 0–100 score across four components |

### `plan_generator.py` — The Orchestrator

Assembles calculation results into a structured plan dictionary. Contains no math — all numbers come from `calculations.py`.

### `charts.py` — The Visualizer

Builds interactive Plotly figures. Each function returns a `go.Figure` object.

| Function | Chart Type | Use Case |
|----------|------------|----------|
| `chartBudgetBreakdown()` | Donut | 50/30/20 allocation |
| `chartIncomevsExpenses()` | Horizontal Bar | Income vs expenses vs debt |
| `chartLoanAmortization()` | Stacked Area + Line | Principal vs interest over time |
| `chartLoanComparison()` | Grouped Bar | Principal vs interest per loan |
| `chartInvestmentGrowth()` | Line + Reference | Growth vs original principal |
| `chartGoalsTimeline()` | Horizontal Bar | Months to reach each goal |
| `chartHealthScoreGauge()` | Gauge | 0–100 score with color zones |
| `chartHealthScoreBreakdown()` | Horizontal Bar | Component scores out of 25 |
| `chartHouseholdIncomeContributions()` | Donut | Earner income shares |
| `chartShopProfitBreakdown()` | Waterfall | Revenue → net profit |

---

## Calculation Logic Reference

### Financial Health Score Components

Each component contributes up to **25 points** (maximum 100).

| Component | Calculation | Scoring Tiers |
|-----------|-------------|---------------|
| **Expense Ratio** | Expenses / Income | ≤50%: 25 pts \| ≤70%: 15 pts \| ≤90%: 8 pts \| >90%: 0 pts |
| **Debt Load (DTI)** | (Debt / Income) × 100 | <20%: 25 pts \| <36%: 18 pts \| <50%: 8 pts \| ≥50%: 0 pts |
| **Savings Rate** | Savings / Income | ≥20%: 25 pts \| ≥10%: 15 pts \| ≥5%: 8 pts \| >0%: 3 pts \| 0%: 0 pts |
| **Income Buffer** | (Income - Expenses - Debt) / Income | ≥30%: 25 pts \| ≥15%: 15 pts \| ≥5%: 8 pts \| >0%: 3 pts \| ≤0%: 0 pts |

| Score Range | Grade |
|-------------|-------|
| 80 – 100 | 🟢 Excellent |
| 60 – 79 | 🟡 Good |
| 40 – 59 | 🟠 Fair |
| 0 – 39 | 🔴 Poor |

### Debt-to-Income (DTI) Risk Status

| DTI Range | Status | Recommended Action |
|-----------|--------|---------------------|
| Below 20% | Excellent | Strong borrowing capacity |
| 20% – 35% | Good | Manageable — limit new debt |
| 36% – 49% | Concerning | Reduce borrowing |
| 50%+ | Dangerous | Seek guidance, prioritize debt reduction |

---

## Security & Privacy

MoneyPlanner is built with a **zero-knowledge architecture**.

| Guarantee | Detail |
|-----------|--------|
| **No Database** | All data stored exclusively in `st.session_state` (browser memory). |
| **No User Accounts** | No passwords, authentication, or registration. |
| **No External API Calls** | All calculations run locally in Python. |
| **Data Isolation** | Each session is independent and invisible to others. |
| **Input Validation** | All functions validate inputs and handle edge cases defensively. |

> This design eliminates risks associated with data breaches, SQL injection, XSS attacks, and unauthorized access.

---

## Future Enhancements

| Feature | Description | Priority |
|---------|-------------|----------|
| **Goal Prioritization** | Rank goals and fund sequentially | High |
| **Scenario Comparison** | Side-by-side "What If?" analysis | High |
| **Save / Load Profiles** | JSON import/export | Medium |
| **Business Module** | Full P&L statements, tax estimation | Medium |
| **Monte Carlo Simulation** | Probability ranges for goal achievement | Low |
| **PDF Export** | Formatted PDF report generation | Low |

---

## Disclaimer

> *MoneyPlanner provides general financial guidance based on standard financial planning rules and formulas. It does not constitute professional financial advice. All recommendations are algorithmically generated based on widely accepted frameworks including the 50/30/20 budgeting rule, Debt-to-Income ratio benchmarks, and compound interest calculations.*
>
> *Please consult a certified financial advisor before making major financial decisions. MoneyPlanner is not liable for any financial decisions made based on the output of this application.*

---

**Built with**  

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

*Project created for Hackathon Submission*

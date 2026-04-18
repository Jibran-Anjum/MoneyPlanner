import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

#########################
# INCOME AND BUDGET CHART
#########################
def chartBudgetBreakdown(budget, currency_symbol='Rs.'):
    # Labels for each slice of the pie
    labels = ["Needs (50%)", "Wants (30%)", "Savings (20%)"]

    # The actual rupee values for each slice
    values = [
        budget["needs"],
        budget["wants"],
        budget["savings"]
    ]

    # Colors chosen to be intuitive:
    # Red = needs (essential, urgent feel)
    # Blue = wants (calm, optional)
    # Green = savings (positive, growth)
    colors = ["#E74C3C", "#3498DB", "#2ECC71"]

    # go.Pie creates a pie chart trace (a single layer of data on a chart)
    fig = go.Figure(data=[go.Pie(
        labels           = labels,
        values           = values,
        hole             = 0.4,       # Makes it a donut chart — easier to read
        marker_colors    = colors,
        hovertemplate    = (
            "<b>%{label}</b><br>"
            f"{currency_symbol} %{{value:,.2f}}<br>"
            "of total income"
            "<extra></extra>"          # Removes the default trace name from hover
        )
    )])

    # Layout controls the title, background, legend position etc.
    fig.update_layout(
        title_text = "Monthly Budget Breakdown (50/30/20 Rule)",
        showlegend = True,
        height     = 400,
        margin     = dict(t=50, b=20, l=20, r=20)
    )

    return fig

# -----------------------------------------------------------------------------

def chartIncomevsExpenses(monthly_income, monthly_expenses, total_monthly_debt, currency_symbol="Rs."):
    # Calculate remaining money after all obligations
    remaining = monthly_income - monthly_expenses - total_monthly_debt

    # Labels for each bar
    categories = ["Income", "Expenses", "Loan Payments", "Remaining"]

    # Values for each bar — remaining is clamped to 0 if negative
    values     = [
        monthly_income,
        monthly_expenses,
        total_monthly_debt,
        max(0, remaining)
    ]

    # Color each bar to communicate meaning at a glance
    bar_colors = ["#2ECC71", "#E74C3C", "#E67E22", "#3498DB"]

    fig = go.Figure(data=[go.Bar(
        x             = values,
        y             = categories,
        orientation   = "h",            # "h" = horizontal bars
        marker_color  = bar_colors,
        hovertemplate = (
            "<b>%{y}</b><br>"
            f"{currency_symbol} %{{x:,.2f}}"
            "<extra></extra>"
        )
    )])

    fig.update_layout(
        title_text = "Income vs Outgoings",
        xaxis_title = f"Amount ({currency_symbol})",
        height     = 350,
        margin     = dict(t=50, b=40, l=20, r=20)
    )

    return fig

#############
# LOAN CHARTS
#############
def chartLoanAmortization(schedule, loan_name="Loan", currency_symbol="Rs."):
    # Extract month numbers, principal paid, and interest paid into lists
    # List comprehensions are a clean Python way to pull one field from a list of dicts
    months         = [row["month"]          for row in schedule]
    principal_paid = [row["principal_paid"] for row in schedule]
    interest_paid  = [row["interest_paid"]  for row in schedule]
    balance        = [row["remaining_balance"] for row in schedule]

    # Build a figure with two traces (two data layers on the same chart)
    fig = go.Figure()

    # Trace 1 — Principal portion of each payment
    fig.add_trace(go.Scatter(
        x          = months,
        y          = principal_paid,
        name       = "Principal Paid",
        fill       = "tozeroy",        # Fill area down to zero
        mode       = "lines",
        line       = dict(color="#2ECC71"),
        hovertemplate = (
            "Month %{x}<br>"
            f"Principal: {currency_symbol} %{{y:,.2f}}"
            "<extra></extra>"
        )
    ))

    # Trace 2 — Interest portion of each payment
    fig.add_trace(go.Scatter(
        x          = months,
        y          = interest_paid,
        name       = "Interest Paid",
        fill       = "tozeroy",
        mode       = "lines",
        line       = dict(color="#E74C3C"),
        hovertemplate = (
            "Month %{x}<br>"
            f"Interest: {currency_symbol} %{{y:,.2f}}"
            "<extra></extra>"
        )
    ))

    # Trace 3 — Remaining balance line
    fig.add_trace(go.Scatter(
        x          = months,
        y          = balance,
        name       = "Remaining Balance",
        mode       = "lines",
        line       = dict(color="#3498DB", dash="dash"),
        hovertemplate = (
            "Month %{x}<br>"
            f"Balance: {currency_symbol} %{{y:,.2f}}"
            "<extra></extra>"
        )
    ))

    fig.update_layout(
        title_text  = f"Loan Repayment Breakdown — {loan_name}",
        xaxis_title = "Month",
        yaxis_title = f"Amount ({currency_symbol})",
        height      = 400,
        margin      = dict(t=50, b=40, l=20, r=20),
        legend      = dict(orientation="h", yanchor="bottom", y=1.02)
    )

    return fig

#------------------------------------------------------------------------------

def chartLoanComparison(loan_summaries, currency_symbol="Rs."):
    # If only one or no loans, this chart adds no value
    if not loan_summaries:
        return None

    loan_names     = [l["name"]           for l in loan_summaries]
    principals     = [l["principal"]      for l in loan_summaries]
    total_interest = [l["total_interest"] for l in loan_summaries]

    fig = go.Figure()

    # Bar 1 — Principal amount (what was borrowed)
    fig.add_trace(go.Bar(
        name          = "Principal",
        x             = loan_names,
        y             = principals,
        marker_color  = "#3498DB",
        hovertemplate = (
            "<b>%{x}</b><br>"
            f"Principal: {currency_symbol} %{{y:,.2f}}"
            "<extra></extra>"
        )
    ))

    # Bar 2 — Total interest paid over the loan lifetime
    fig.add_trace(go.Bar(
        name          = "Total Interest",
        x             = loan_names,
        y             = total_interest,
        marker_color  = "#E74C3C",
        hovertemplate = (
            "<b>%{x}</b><br>"
            f"Interest: {currency_symbol} %{{y:,.2f}}"
            "<extra></extra>"
        )
    ))

    # barmode="group" puts the bars side by side instead of stacked
    fig.update_layout(
        title_text  = "Loan Comparison — Principal vs Total Interest",
        xaxis_title = "Loan",
        yaxis_title = f"Amount ({currency_symbol})",
        barmode     = "group",
        height      = 400,
        margin      = dict(t=50, b=40, l=20, r=20),
        legend      = dict(orientation="h", yanchor="bottom", y=1.02)
    )

    return fig

###################
# INVESTMENT CHARTS
###################
def chartInvestmentGrowth(yearly_breakdown, investment_name="Investment", principal=0, currency_symbol="Rs."):
    years   = [row["year"]    for row in yearly_breakdown]
    balance = [row["balance"] for row in yearly_breakdown]

    fig = go.Figure()

    # Trace 1 — Investment growth line
    fig.add_trace(go.Scatter(
        x          = years,
        y          = balance,
        name       = "Investment Value",
        mode       = "lines+markers",   # Shows both a line and dots at each year
        line       = dict(color="#2ECC71", width=3),
        marker     = dict(size=7),
        hovertemplate = (
            "Year %{x}<br>"
            f"Value: {currency_symbol} %{{y:,.2f}}"
            "<extra></extra>"
        )
    ))

    # Trace 2 — Flat reference line showing the original principal
    # This makes the growth visually obvious
    fig.add_trace(go.Scatter(
        x          = years,
        y          = [principal] * len(years),  # Same value repeated for every year
        name       = "Original Amount",
        mode       = "lines",
        line       = dict(color="#95A5A6", dash="dot", width=2),
        hovertemplate = (
            f"Original: {currency_symbol} {principal:,.2f}"
            "<extra></extra>"
        )
    ))

    fig.update_layout(
        title_text  = f"Investment Growth — {investment_name}",
        xaxis_title = "Year",
        yaxis_title = f"Value ({currency_symbol})",
        height      = 400,
        margin      = dict(t=50, b=40, l=20, r=20),
        legend      = dict(orientation="h", yanchor="bottom", y=1.02)
    )

    return fig

############
# GOAL CHART
############
def chartGoalsTimeline(goal_summaries, currency_symbol="Rs."):
    if not goal_summaries:
        return None

    # Filter to only feasible goals — infeasible ones have no timeline to show
    feasible_goals = [g for g in goal_summaries if g["feasible"]]

    if not feasible_goals:
        return None

    goal_names = [g["name"]   for g in feasible_goals]
    months     = [g["months"] for g in feasible_goals]
    amounts    = [g["amount"] for g in feasible_goals]

    fig = go.Figure(data=[go.Bar(
        x             = months,
        y             = goal_names,
        orientation   = "h",
        marker_color  = "#9B59B6",
        customdata    = amounts,
        hovertemplate = (
            "<b>%{y}</b><br>"
            "Time to reach: %{x:.1f} months<br>"
            f"Target: {currency_symbol} %{{customdata:,.2f}}"
            "<extra></extra>"
        )
    )])
    fig.update_layout(
        title_text  = "Financial Goals — Months to Achieve",
        xaxis_title = "Months",
        height      = max(300, len(feasible_goals) * 80),  # Scale height with number of goals
        margin      = dict(t=50, b=40, l=20, r=20)
    )

    return fig

########################
# FINANCIAL HEALTH SCORE
########################
def chartHealthScoreGauge(health):
    score = health["total_score"]
    grade = health["grade"]

    fig = go.Figure(go.Indicator(
        mode  = "gauge+number",         # Show both the gauge and the number
        value = score,
        title = {"text": f"Financial Health Score<br><span style='font-size:0.8em'>{grade}</span>"},
        gauge = {
            "axis": {
                "range": [0, 100],      # Score range
                "tickwidth": 1
            },
            "bar": {"color": "#2C3E50"},  # Needle color

            # Color zones — Poor, Fair, Good, Excellent
            "steps": [
                {"range": [0,  40], "color": "#E74C3C"},   # Red   — Poor
                {"range": [40, 60], "color": "#E67E22"},   # Orange — Fair
                {"range": [60, 80], "color": "#F1C40F"},   # Yellow — Good
                {"range": [80, 100], "color": "#2ECC71"},  # Green  — Excellent
            ],

            # Threshold line marking the "Good" boundary
            "threshold": {
                "line":  {"color": "#2C3E50", "width": 4},
                "thickness": 0.75,
                "value": 60
            }
        }
    ))

    fig.update_layout(
        height = 350,
        margin = dict(t=80, b=20, l=40, r=40)
    )

    return fig

#------------------------------------------------------------------------------

def chartHealthScoreBreakdown(breakdown):
    categories = list(breakdown.keys())
    scores     = list(breakdown.values())

    # Color each bar based on score — green if full marks, red if low
    bar_colors = []
    for s in scores:
        if s >= 20:
            bar_colors.append("#2ECC71")   # Green — doing well
        elif s >= 12:
            bar_colors.append("#F1C40F")   # Yellow — average
        elif s >= 5:
            bar_colors.append("#E67E22")   # Orange — concerning
        else:
            bar_colors.append("#E74C3C")   # Red — poor

    fig = go.Figure(data=[go.Bar(
        x             = scores,
        y             = categories,
        orientation   = "h",
        marker_color  = bar_colors,
        text          = [f"{s}/25" for s in scores],   # Show score label on each bar
        textposition  = "outside",
        hovertemplate = (
            "<b>%{y}</b><br>"
            "Score: %{x}/25"
            "<extra></extra>"
        )
    )])

    fig.update_layout(
        title_text  = "Health Score Breakdown (each component is out of 25)",
        xaxis_title = "Score",
        xaxis_range = [0, 30],       # Slightly wider than 25 so text labels fit
        height      = 350,
        margin      = dict(t=50, b=40, l=20, r=80)
    )

    return fig

##########################
# HOUSEHOLD SPECIFIC CHART
##########################
def chartHouseholdIncomeContributions(income_contributions, currency_symbol="Rs."):
    if not income_contributions:
        return None

    names         = [e["name"]         for e in income_contributions]
    contributions = [e["contribution"] for e in income_contributions]
    incomes       = [e["income"]       for e in income_contributions]

    fig = go.Figure(data=[go.Pie(
        labels        = names,
        values        = contributions,
        hole          = 0.4,
        hovertemplate = (
            "<b>%{label}</b><br>"
            "Contribution: %{value:.1f}%<br>"
            f"{currency_symbol} %{{customdata:,.2f}}" +
            "<extra></extra>"
        ),
        customdata    = incomes
    )])

    fig.update_layout(
        title_text = "Household Income Contributions",
        height     = 400,
        margin     = dict(t=50, b=20, l=20, r=20)
    )

    return fig

#####################
# SHOP SPECIFIC CHART
#####################
def chartShopProfitBreakdown(monthly_revenue, cogs, monthly_expenses, currency_symbol="Rs."):
    gross_profit = monthly_revenue - cogs
    net_profit   = gross_profit - monthly_expenses

    fig = go.Figure(go.Waterfall(
        name        = "Profit Breakdown",
        orientation = "v",

        # "relative" bars add/subtract from previous
        # "total" bars show the absolute value at that point
        measure     = ["absolute", "relative", "total", "relative", "total"],

        x           = [
            "Revenue",
            "Cost of Goods",
            "Gross Profit",
            "Operating Expenses",
            "Net Profit"
        ],

        y           = [
            monthly_revenue,
            -cogs,              # Negative because it subtracts from revenue
            0,                  # Placeholder — waterfall calculates this automatically
            -monthly_expenses,  # Negative because it subtracts from gross profit
            0                   # Placeholder
        ],

        connector   = {"line": {"color": "#95A5A6"}},

        decreasing  = {"marker": {"color": "#E74C3C"}},   # Red for deductions
        increasing  = {"marker": {"color": "#2ECC71"}},   # Green for additions
        totals      = {"marker": {"color": "#3498DB"}},   # Blue for totals

        hovertemplate = (
            "<b>%{x}</b><br>"
            f"{currency_symbol} %{{y:,.2f}}"
            "<extra></extra>"
        )
    ))

    fig.update_layout(
        title_text  = "Monthly Profit Breakdown",
        yaxis_title = f"Amount ({currency_symbol})",
        height      = 400,
        margin      = dict(t=50, b=40, l=20, r=20)
    )

    return fig



import streamlit as st
from logic.plan_generator import generateIndividualPlan
from logic.calculations import (
    loanAmortizationSchedule,
    compoundInterestYearlyBreakdown
)
from components.charts import (
    chartBudgetBreakdown,
    chartIncomevsExpenses,
    chartLoanAmortization,
    chartLoanComparison,
    chartInvestmentGrowth,
    chartGoalsTimeline,
    chartHealthScoreGauge,
    chartHealthScoreBreakdown
)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 1 — MAIN ENTRY FUNCTION
# ═════════════════════════════════════════════════════════════════════════════

def show_individual():
    """
    Main function called by app.py when the user selects Individual.
    Orchestrates the entire Individual planner page from top to bottom.
    """

    st.title("👤 Individual Financial Planner")
    st.caption("Enter your financial details below to generate your personalized plan.")
    # st.markdown("---")

    # ── CURRENCY SELECTOR ────────────────────────────────────────────────────
    # Placed at the top so it applies to all sections below
    # currency = st.selectbox(
    #     "Select your currency",
    #     options=["Rs. (PKR)", "$ (USD)", "€ (EUR)", "£ (GBP)", "AED (UAE)"],
    #     # index=0
    # )

    # Extract just the symbol part before the space
    # "Rs. (PKR)" → "Rs."   "$ (USD)" → "$"
    currency_symbol = st.session_state.get("currency_symbol", "Rs.")
    st.markdown("---")

    # ── INPUT SECTIONS ───────────────────────────────────────────────────────
    # Each section is its own function to keep this file readable.
    # We collect all user inputs first, then generate the plan at the end.

    monthly_income, monthly_expenses = _section_income_expenses(currency_symbol)
    loans                            = _section_loans(currency_symbol)
    investments                      = _section_investments(currency_symbol)
    goals                            = _section_goals(currency_symbol)

    st.markdown("---")

    # ── GENERATE PLAN BUTTON ─────────────────────────────────────────────────
    # We only generate the plan when the user explicitly clicks this button.
    # This prevents the app from recalculating on every tiny input change.
    if st.button("📊 Generate My Financial Plan", type="primary", use_container_width=True):

        # Basic validation — income must be provided before we can plan anything
        if monthly_income <= 0:
            st.error("❌ Please enter a valid monthly income greater than zero.")
            return

        # Package all inputs into the dictionary the plan generator expects
        data = {
            "monthly_income":   monthly_income,
            "monthly_expenses": monthly_expenses,
            "loans":            loans,
            "goals":            goals,
            "investments":      investments,
            "currency_symbol":  currency_symbol
        }

        # Generate the full financial plan
        # This single call runs all the math and returns the complete plan dict
        with st.spinner("Generating your financial plan..."):
            plan = generateIndividualPlan(data)

        # Store the plan in Streamlit session state so it persists
        # after the button is clicked and the page re-renders
        st.session_state["individual_plan"] = plan

    # ── DISPLAY PLAN ─────────────────────────────────────────────────────────
    # Check if a plan exists in session state before trying to display it
    # This prevents errors on first load when no plan has been generated yet
    if "individual_plan" in st.session_state:
        _display_plan(st.session_state["individual_plan"], currency_symbol)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 2 — INPUT FORM FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════

def _section_income_expenses(currency_symbol):
    """
    Renders the Income and Expenses input section.

    Plain English: Two number fields — how much do you earn
    and how much do you spend each month?

    Returns:
        monthly_income   : float
        monthly_expenses : float
    """

    st.subheader("💰 Income & Expenses")

    col1, col2 = st.columns(2)

    with col1:
        monthly_income = st.number_input(
            label     = f"Monthly Income ({currency_symbol})",
            min_value = 0.0,
            value     = 0.0,
            step      = 1000.0,
            help      = "Your total take-home income per month after tax"
        )

    with col2:
        monthly_expenses = st.number_input(
            label     = f"Monthly Expenses ({currency_symbol})",
            min_value = 0.0,
            value     = 0.0,
            step      = 500.0,
            help      = "Total essential monthly expenses: rent, food, utilities, transport"
        )

    # Live feedback — show remaining money as the user types
    # This gives immediate value even before generating the full plan
    if monthly_income > 0:
        remaining = monthly_income - monthly_expenses
        if remaining >= 0:
            st.success(f"💚 After expenses you have **{currency_symbol} {remaining:,.2f}** remaining per month.")
        else:
            st.error(f"🔴 You are **{currency_symbol} {abs(remaining):,.2f}** over budget before loans or savings.")

    return monthly_income, monthly_expenses


# ─────────────────────────────────────────────────────────────────────────────

def _section_loans(currency_symbol):
    """
    Renders the Loans input section.
    Supports adding multiple loans dynamically.

    Plain English: The user can add as many loans as they have.
    Each loan has a name, amount, interest rate, and duration.
    Streamlit session state keeps track of how many loans
    the user has added so they don't disappear on re-render.

    Returns:
        loans : List of loan dictionaries
    """

    st.subheader("🏦 Loans")

    # Session state keeps the loan count persistent across re-renders
    # Without this, every interaction resets the page and loans disappear
    if "num_loans" not in st.session_state:
        st.session_state["num_loans"] = 0

    col_add, col_clear = st.columns([1, 1])

    with col_add:
        # Increment the loan counter when Add Loan is clicked
        if st.button("➕ Add a Loan", use_container_width=True):
            st.session_state["num_loans"] += 1


    confirm_clear = st.checkbox("Confirm clear", key="confirm_clear_loans")

    with col_clear:
        # Reset all loans — useful if user wants to start fresh
        if st.button("🗑️ Clear All Loans", disabled=not confirm_clear, use_container_width=True):
            st.session_state["num_loans"] = 0
            st.rerun()

    loans = []

    # Render one input group per loan the user has added
    for i in range(st.session_state["num_loans"]):

        # st.expander creates a collapsible section — keeps the UI clean
        # when many loans are added
        with st.expander(f"Loan {i + 1}", expanded=True):

            c1, c2 = st.columns(2)
            c3, c4 = st.columns(2)

            with c1:
                name = st.text_input(
                    label = "Loan Name",
                    value = f"Loan {i + 1}",
                    key   = f"loan_name_{i}",   # Unique key required for each widget
                    help  = "e.g. Car Loan, Home Loan, Personal Loan"
                )

            with c2:
                principal = st.number_input(
                    label     = f"Principal Amount ({currency_symbol})",
                    min_value = 0.0,
                    value     = 0.0,
                    step      = 10000.0,
                    key       = f"loan_principal_{i}"
                )

            with c3:
                annual_rate = st.number_input(
                    label     = "Annual Interest Rate (%)",
                    min_value = 0.0,
                    max_value = 100.0,
                    value     = 0.0,
                    step      = 0.5,
                    key       = f"loan_rate_{i}",
                    help      = "Enter 0 for interest-free loans"
                )

            with c4:
                years = st.number_input(
                    label     = "Loan Duration (Years)",
                    min_value = 1,
                    max_value = 30,
                    value     = 1,
                    step      = 1,
                    key       = f"loan_years_{i}"
                )

            # Only include this loan if a principal was entered
            if principal > 0:
                loans.append({
                    "name":        name,
                    "principal":   principal,
                    "annual_rate": annual_rate,
                    "years":       years
                })

    if st.session_state["num_loans"] == 0:
        st.info("No loans added. Click **➕ Add a Loan** if you have any.")

    return loans


# ─────────────────────────────────────────────────────────────────────────────

def _section_investments(currency_symbol):
    """
    Renders the Investments input section.
    Supports multiple investments dynamically.

    Returns:
        investments : List of investment dictionaries
    """

    st.subheader("📈 Investments")

    if "num_investments" not in st.session_state:
        st.session_state["num_investments"] = 0

    col_add, col_clear = st.columns([1, 1])

    with col_add:
        if st.button("➕ Add an Investment", use_container_width=True):
            st.session_state["num_investments"] += 1

    confirm_clear_inv = st.checkbox("Confirm clear", key="confirm_clear_inv")
    with col_clear:
        if st.button("🗑️ Clear All Investments", disabled=not confirm_clear_inv, use_container_width=True):
            st.session_state["num_investments"] = 0
            st.rerun()

    investments = []

    for i in range(st.session_state["num_investments"]):

        with st.expander(f"Investment {i + 1}", expanded=True):

            c1, c2 = st.columns(2)
            c3, c4 = st.columns(2)

            with c1:
                name = st.text_input(
                    label = "Investment Name",
                    value = f"Investment {i + 1}",
                    key   = f"inv_name_{i}",
                    help  = "e.g. Savings Account, Stocks, Property"
                )

            with c2:
                principal = st.number_input(
                    label     = f"Amount Invested ({currency_symbol})",
                    min_value = 0.0,
                    value     = 0.0,
                    step      = 10000.0,
                    key       = f"inv_principal_{i}"
                )

            with c3:
                annual_rate = st.number_input(
                    label     = "Expected Annual Return (%)",
                    min_value = 0.0,
                    max_value = 100.0,
                    value     = 8.0,
                    step      = 0.5,
                    key       = f"inv_rate_{i}",
                    help      = "Typical savings account: 6-10%. Stocks: 10-15%"
                )

            with c4:
                years = st.number_input(
                    label     = "Investment Duration (Years)",
                    min_value = 1,
                    max_value = 50,
                    value     = 5,
                    step      = 1,
                    key       = f"inv_years_{i}"
                )

            if principal > 0:
                investments.append({
                    "name":        name,
                    "principal":   principal,
                    "annual_rate": annual_rate,
                    "years":       years
                })

    if st.session_state["num_investments"] == 0:
        st.info("No investments added. Click **➕ Add an Investment** if you have any.")

    return investments


# ─────────────────────────────────────────────────────────────────────────────

def _section_goals(currency_symbol):
    """
    Renders the Financial Goals input section.
    Supports multiple goals dynamically.

    Returns:
        goals : List of goal dictionaries
    """

    st.subheader("🎯 Financial Goals")
    st.caption("Things you want to save up for — a car, a laptop, a vacation, etc.")

    if "num_goals" not in st.session_state:
        st.session_state["num_goals"] = 0

    col_add, col_clear = st.columns([1, 1])

    with col_add:
        if st.button("➕ Add a Goal", use_container_width=True):
            st.session_state["num_goals"] += 1

    confirm_clear_goals = st.checkbox("Confirm clear", key="confirm_clear_goals")

    with col_clear:
        if st.button("🗑️ Clear All Goals", disabled=not confirm_clear_goals, use_container_width=True):
            st.session_state["num_goals"] = 0
            st.rerun()

    goals = []

    for i in range(st.session_state["num_goals"]):

        with st.expander(f"Goal {i + 1}", expanded=True):

            c1, c2 = st.columns(2)

            with c1:
                name = st.text_input(
                    label = "Goal Name",
                    value = f"Goal {i + 1}",
                    key   = f"goal_name_{i}",
                    help  = "e.g. New Car, Laptop, House Down Payment"
                )

            with c2:
                amount = st.number_input(
                    label     = f"Target Amount ({currency_symbol})",
                    min_value = 0.0,
                    value     = 0.0,
                    step      = 5000.0,
                    key       = f"goal_amount_{i}"
                )

            if amount > 0:
                goals.append({
                    "name":   name,
                    "amount": amount
                })

    if st.session_state["num_goals"] == 0:
        st.info("No goals added. Click **➕ Add a Goal** to plan for a future purchase.")

    return goals

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 3 — PLAN DISPLAY FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════

def _display_plan(plan, currency_symbol):
    """
    Renders the complete generated financial plan.
    Divided into clearly labeled tabs for easy navigation.

    Plain English: Instead of dumping everything on one long page,
    we use tabs so the user can jump between Overview, Loans,
    Investments, Goals, and Recommendations cleanly.
    """

    st.markdown("---")
    st.header("📋 Your Financial Plan")
    st.markdown("---")

    # Tabs divide the plan into digestible sections
    tab_overview, tab_loans, tab_investments, tab_goals, tab_recommendations = st.tabs([
        "📊 Overview",
        "🏦 Loans",
        "📈 Investments",
        "🎯 Goals",
        "✅ Recommendations"
    ])

    with tab_overview:
        _tab_overview(plan, currency_symbol)

    with tab_loans:
        _tab_loans(plan, currency_symbol)

    with tab_investments:
        _tab_investments(plan, currency_symbol)

    with tab_goals:
        _tab_goals(plan, currency_symbol)

    with tab_recommendations:
        _tab_recommendations(plan)


# ─────────────────────────────────────────────────────────────────────────────

def _tab_overview(plan, currency_symbol):
    """
    Renders the Overview tab — key metrics, budget breakdown,
    income vs outgoings, and health score.
    """

    # ── KEY METRICS ROW ──────────────────────────────────────────────────────
    # st.metric shows a number with a label — clean and professional
    st.subheader("📌 Key Metrics")

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.metric(
            label = "Monthly Income",
            value = f"{currency_symbol} {plan['monthly_income']:,.0f}"
        )

    with m2:
        st.metric(
            label = "Monthly Expenses",
            value = f"{currency_symbol} {plan['monthly_expenses']:,.0f}"
        )

    with m3:
        st.metric(
            label = "Total Loan Payments",
            value = f"{currency_symbol} {plan['total_monthly_debt']:,.0f}"
        )

    with m4:
        # Show remaining money — red delta if negative
        remaining = plan["remaining_after_bills"]
        st.metric(
            label = "Monthly Remaining",
            value = f"{currency_symbol} {max(0, remaining):,.0f}",
            delta = f"{remaining:,.0f}",
            delta_color = "normal" if remaining >= 0 else "inverse"
        )

    st.markdown("---")

    # ── HEALTH SCORE ─────────────────────────────────────────────────────────
    st.subheader("🏥 Financial Health Score")

    col_gauge, col_breakdown = st.columns(2)

    with col_gauge:
        st.plotly_chart(
            chartHealthScoreGauge(plan["health"]),
            use_container_width=True
        )

    with col_breakdown:
        st.plotly_chart(
            chartHealthScoreBreakdown(plan["health"]["breakdown"]),
            use_container_width=True
        )

    st.info(f"💡 **{plan['health']['grade']}** — {plan['health']['advice']}")

    st.markdown("---")

    # ── BUDGET BREAKDOWN ─────────────────────────────────────────────────────
    st.subheader("💸 Recommended Budget Breakdown (50/30/20 Rule)")

    col_chart, col_details = st.columns(2)

    with col_chart:
        st.plotly_chart(
            chartBudgetBreakdown(plan["budget"], currency_symbol),
            use_container_width=True
        )

    with col_details:
        st.markdown("**What the 50/30/20 rule recommends for your income:**")
        st.markdown(f"- 🔴 **Needs (50%):** {currency_symbol} {plan['budget']['needs']:,.2f} / month")
        st.markdown(f"- 🔵 **Wants (30%):** {currency_symbol} {plan['budget']['wants']:,.2f} / month")
        st.markdown(f"- 🟢 **Savings (20%):** {currency_symbol} {plan['budget']['savings']:,.2f} / month")
        st.markdown("---")
        st.markdown("**Debt-to-Income Ratio:**")
        dti = plan["dti"]
        st.markdown(f"- **DTI:** {dti['ratio']}% — {dti['status']}")
        st.caption(dti["advice"])

    st.markdown("---")

    # ── INCOME VS OUTGOINGS ──────────────────────────────────────────────────
    st.subheader("📊 Income vs Outgoings")
    st.plotly_chart(
        chartIncomevsExpenses(
            plan["monthly_income"],
            plan["monthly_expenses"],
            plan["total_monthly_debt"],
            currency_symbol
        ),
        use_container_width=True
    )

    # ── EMERGENCY FUND ───────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("🛡️ Emergency Fund")
    emergency = plan["emergency"]

    e1, e2 = st.columns(2)
    with e1:
        st.metric("Minimum Fund (3 months)", f"{currency_symbol} {emergency['minimum_fund']:,.0f}")
    with e2:
        st.metric("Recommended Fund (6 months)", f"{currency_symbol} {emergency['recommended_fund']:,.0f}")

    st.caption(emergency["advice"])


# ─────────────────────────────────────────────────────────────────────────────

def _tab_loans(plan, currency_symbol):
    """
    Renders the Loans tab — individual loan details,
    amortization chart, and loan comparison chart.
    """

    loans = plan["loans"]

    if not loans:
        st.info("No loans were entered. Add loans in the input section above.")
        return

    # ── LOAN SUMMARY CARDS ───────────────────────────────────────────────────
    st.subheader("🏦 Loan Summary")

    for loan in loans:
        with st.expander(f"📄 {loan['name']} — {currency_symbol} {loan['principal']:,.0f}", expanded=True):

            c1, c2, c3 = st.columns(3)

            with c1:
                st.metric("Monthly Payment", f"{currency_symbol} {loan['monthly_payment']:,.2f}")
            with c2:
                st.metric("Total Interest", f"{currency_symbol} {loan['total_interest']:,.2f}")
            with c3:
                st.metric("Total Payment", f"{currency_symbol} {loan['total_payment']:,.2f}")

            # ── AMORTIZATION CHART ───────────────────────────────────────────
            # Generate the full month-by-month schedule for this loan
            schedule = loanAmortizationSchedule(
                loan["principal"],
                loan["annual_rate"],
                loan["years"]
            )

            st.plotly_chart(
                chartLoanAmortization(schedule, loan["name"], currency_symbol),
                use_container_width=True
            )

            # ── AMORTIZATION TABLE ───────────────────────────────────────────
            # Let the user optionally view the full month-by-month table
            if st.checkbox(f"Show full repayment table for {loan['name']}", key=f"amort_{loan['name']}"):
                import pandas as pd
                df = pd.DataFrame(schedule)
                df.columns = ["Month", "Payment", "Principal Paid", "Interest Paid", "Remaining Balance"]
                st.dataframe(df, use_container_width=True)

    # ── LOAN COMPARISON ──────────────────────────────────────────────────────
    if len(loans) > 1:
        st.markdown("---")
        st.subheader("⚖️ Loan Comparison")
        st.plotly_chart(
            chartLoanComparison(loans, currency_symbol),
            use_container_width=True
        )
        st.caption(
            "💡 **Tip:** The loan with the highest interest bar is costing you the most. "
            "Consider paying that one off first — this is called the **Avalanche Method**."
        )


# ─────────────────────────────────────────────────────────────────────────────

def _tab_investments(plan, currency_symbol):
    """
    Renders the Investments tab — projected growth for
    each investment with charts and summaries.
    """

    investments = plan["investments"]

    if not investments:
        st.info("No investments were entered. Add investments in the input section above.")
        return

    st.subheader("📈 Investment Projections")

    for inv in investments:
        with st.expander(f"📊 {inv['name']} — {currency_symbol} {inv['principal']:,.0f}", expanded=True):

            c1, c2, c3 = st.columns(3)

            with c1:
                st.metric("Amount Invested", f"{currency_symbol} {inv['principal']:,.2f}")
            with c2:
                st.metric("Interest Earned", f"{currency_symbol} {inv['interest_earned']:,.2f}")
            with c3:
                st.metric("Final Value", f"{currency_symbol} {inv['total_amount']:,.2f}")

            # Generate the yearly breakdown for the chart
            yearly_data = compoundInterestYearlyBreakdown(
                inv["principal"],
                inv["annual_rate"],
                inv["years"]
            )

            st.plotly_chart(
                chartInvestmentGrowth(
                    yearly_data,
                    inv["name"],
                    inv["principal"],
                    currency_symbol
                ),
                use_container_width=True
            )


# ─────────────────────────────────────────────────────────────────────────────

def _tab_goals(plan, currency_symbol):
    """
    Renders the Goals tab — timeline for each goal
    and a visual comparison chart.
    """

    goals = plan["goals"]

    if not goals:
        st.info("No goals were entered. Add goals in the input section above.")
        return

    st.subheader("🎯 Savings Goals Timeline")
    st.caption(
        f"Based on your available monthly savings of "
        f"**{currency_symbol} {plan['available_savings']:,.2f}** "
        f"split across all goals."
    )

    # ── GOAL SUMMARY CARDS ───────────────────────────────────────────────────
    for goal in goals:
        with st.expander(f"🎯 {goal['name']} — {currency_symbol} {goal['amount']:,.0f}", expanded=True):

            if goal["feasible"]:
                c1, c2, c3 = st.columns(3)

                with c1:
                    st.metric("Target Amount", f"{currency_symbol} {goal['amount']:,.2f}")
                with c2:
                    st.metric("Monthly Savings Allocated", f"{currency_symbol} {goal['monthly_savings']:,.2f}")
                with c3:
                    st.metric("Time to Goal", f"{goal['full_years']}y {goal['remaining_months']}m")

                st.success(f"✅ {goal['message']}")

            else:
                st.error(f"❌ {goal['message']}")
                st.caption(
                    "To make this goal reachable, either increase your income, "
                    "reduce your expenses, or reduce your loan obligations."
                )

    # ── GOALS TIMELINE CHART ─────────────────────────────────────────────────
    goals_chart = chartGoalsTimeline(goals, currency_symbol)
    if goals_chart:
        st.markdown("---")
        st.plotly_chart(goals_chart, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────

def _tab_recommendations(plan):
    """
    Renders the Recommendations tab — the written
    financial advice generated by plan_generator.py
    """

    st.subheader("✅ Your Personalized Financial Recommendations")
    st.caption("These recommendations are based on your entered financial data.")
    st.markdown("---")

    recommendations = plan["recommendations"]

    if not recommendations:
        st.info("No recommendations generated. Please generate your plan first.")
        return

    # Display each recommendation as its own clean block
    for rec in recommendations:
        st.markdown(rec)
        st.markdown("---")

    # ── DISCLAIMER ───────────────────────────────────────────────────────────
    st.warning(
        "⚠️ **Disclaimer:** These recommendations are algorithmically generated "
        "based on standard financial planning rules. They do not constitute "
        "professional financial advice. Please consult a certified financial "
        "advisor before making major financial decisions."
    )

show_individual()

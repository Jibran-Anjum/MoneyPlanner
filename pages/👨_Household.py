# ── MONEYPLANNER - HOUSEHOLD FINANCIAL PLANNER PAGE ──────────────────────────

import streamlit as st
from logic.plan_generator import generateHouseholdPlan
from logic.calculations   import (
    loanAmortizationSchedule,
    compoundInterestYearlyBreakdown
)
from components.charts    import (
    chartBudgetBreakdown,
    chartIncomevsExpenses,
    chartLoanAmortization,
    chartLoanComparison,
    chartInvestmentGrowth,
    chartGoalsTimeline,
    chartHealthScoreGauge,
    chartHealthScoreBreakdown,
    chartHouseholdIncomeContributions
)


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 1 — MAIN ENTRY FUNCTION
# ═════════════════════════════════════════════════════════════════════════════

def show_household():

    st.title("👨‍👩‍👧 Household Financial Planner")
    st.caption("Plan your household finances across all earners and shared expenses.")
    st.markdown("---")

    currency = st.selectbox(
        "Select your currency",
        options=["Rs. (PKR)", "$ (USD)", "€ (EUR)", "£ (GBP)", "AED (UAE)"],
        # index=0
    )
    currency_symbol = currency.split(" ")[0]

    st.markdown("---")

    earners          = _section_earners(currency_symbol)
    monthly_expenses = _section_expenses(currency_symbol, earners)
    loans            = _section_loans(currency_symbol)
    investments      = _section_investments(currency_symbol)
    goals            = _section_goals(currency_symbol)

    st.markdown("---")

    if st.button("📊 Generate Household Financial Plan", type="primary", use_container_width=True):

        total_income = sum(e.get("monthly_income", 0) for e in earners)

        if total_income <= 0:
            st.error("❌ Please enter at least one earner with a valid income.")
            return

        data = {
            "earners":          earners,
            "monthly_expenses": monthly_expenses,
            "loans":            loans,
            "goals":            goals,
            "investments":      investments,
            "currency_symbol":  currency_symbol
        }

        with st.spinner("Generating your household financial plan..."):
            plan = generateHouseholdPlan(data)

        st.session_state["household_plan"] = plan

    if "household_plan" in st.session_state:
        _display_plan(st.session_state["household_plan"], currency_symbol)


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 2 — INPUT FORM FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════

def _section_earners(currency_symbol):

    st.subheader("👥 Household Earners")
    st.caption("Add every person in the household who earns an income.")

    if "num_earners" not in st.session_state:
        st.session_state["num_earners"] = 1

    col_add, col_clear = st.columns([1, 1])

    with col_add:
        if st.button("➕ Add an Earner", use_container_width=True):
            st.session_state["num_earners"] += 1

    with col_clear:
        if st.button("🗑️ Clear All Earners", use_container_width=True):
            st.session_state["num_earners"] = 1

    earners = []

    for i in range(st.session_state["num_earners"]):

        with st.expander(f"Earner {i + 1}", expanded=True):

            c1, c2 = st.columns(2)

            with c1:
                name = st.text_input(
                    label = "Name",
                    value = f"Earner {i + 1}",
                    key   = f"earner_name_{i}",
                    help  = "e.g. Father, Mother, Son"
                )

            with c2:
                monthly_income = st.number_input(
                    label     = f"Monthly Income ({currency_symbol})",
                    min_value = 0.0,
                    value     = 0.0,
                    step      = 1000.0,
                    key       = f"earner_income_{i}",
                    help      = "Take-home income after tax"
                )

            if monthly_income > 0:
                earners.append({
                    "name":           name,
                    "monthly_income": monthly_income
                })

    total = sum(e["monthly_income"] for e in earners)
    if total > 0:
        st.success(f"💚 Combined Household Income: **{currency_symbol} {total:,.2f}** / month")

    return earners


# ─────────────────────────────────────────────────────────────────────────────

def _section_expenses(currency_symbol, earners):

    st.subheader("🧾 Shared Monthly Expenses")
    st.caption("All shared household costs — rent, food, utilities, school fees, transport.")

    monthly_expenses = st.number_input(
        label     = f"Total Monthly Household Expenses ({currency_symbol})",
        min_value = 0.0,
        value     = 0.0,
        step      = 1000.0,
        help      = "Add up all regular monthly household expenses"
    )

    total_income = sum(e.get("monthly_income", 0) for e in earners)

    if total_income > 0 and monthly_expenses > 0:
        ratio     = (monthly_expenses / total_income) * 100
        remaining = total_income - monthly_expenses

        if ratio <= 50:
            st.success(
                f"✅ Expenses are {ratio:.1f}% of household income. "
                f"**{currency_symbol} {remaining:,.2f}** remaining after expenses."
            )
        elif ratio <= 70:
            st.warning(
                f"🟡 Expenses are {ratio:.1f}% of household income. "
                f"**{currency_symbol} {remaining:,.2f}** remaining after expenses."
            )
        else:
            st.error(
                f"🔴 Expenses are {ratio:.1f}% of household income — very high. "
                f"Only **{currency_symbol} {max(0, remaining):,.2f}** remaining."
            )

    return monthly_expenses


# ─────────────────────────────────────────────────────────────────────────────

def _section_loans(currency_symbol):

    st.subheader("🏦 Household Loans")

    if "hh_num_loans" not in st.session_state:
        st.session_state["hh_num_loans"] = 0

    col_add, col_clear = st.columns([1, 1])

    with col_add:
        if st.button("➕ Add a Loan", use_container_width=True, key="hh_add_loan"):
            st.session_state["hh_num_loans"] += 1

    with col_clear:
        if st.button("🗑️ Clear All Loans", use_container_width=True, key="hh_clear_loans"):
            st.session_state["hh_num_loans"] = 0

    loans = []

    for i in range(st.session_state["hh_num_loans"]):

        with st.expander(f"Loan {i + 1}", expanded=True):

            c1, c2 = st.columns(2)
            c3, c4 = st.columns(2)

            with c1:
                name = st.text_input(
                    label = "Loan Name",
                    value = f"Loan {i + 1}",
                    key   = f"hh_loan_name_{i}",
                    help  = "e.g. Home Loan, Car Loan"
                )
            with c2:
                principal = st.number_input(
                    label     = f"Principal Amount ({currency_symbol})",
                    min_value = 0.0,
                    value     = 0.0,
                    step      = 10000.0,
                    key       = f"hh_loan_principal_{i}"
                )
            with c3:
                annual_rate = st.number_input(
                    label     = "Annual Interest Rate (%)",
                    min_value = 0.0,
                    max_value = 100.0,
                    value     = 0.0,
                    step      = 0.5,
                    key       = f"hh_loan_rate_{i}"
                )
            with c4:
                years = st.number_input(
                    label     = "Loan Duration (Years)",
                    min_value = 1,
                    max_value = 30,
                    value     = 1,
                    step      = 1,
                    key       = f"hh_loan_years_{i}"
                )

            if principal > 0:
                loans.append({
                    "name":        name,
                    "principal":   principal,
                    "annual_rate": annual_rate,
                    "years":       years
                })

    if st.session_state["hh_num_loans"] == 0:
        st.info("No loans added. Click **➕ Add a Loan** if you have any.")

    return loans


# ─────────────────────────────────────────────────────────────────────────────

def _section_investments(currency_symbol):

    st.subheader("📈 Household Investments")

    if "hh_num_investments" not in st.session_state:
        st.session_state["hh_num_investments"] = 0

    col_add, col_clear = st.columns([1, 1])

    with col_add:
        if st.button("➕ Add an Investment", use_container_width=True, key="hh_add_inv"):
            st.session_state["hh_num_investments"] += 1

    with col_clear:
        if st.button("🗑️ Clear All Investments", use_container_width=True, key="hh_clear_inv"):
            st.session_state["hh_num_investments"] = 0

    investments = []

    for i in range(st.session_state["hh_num_investments"]):

        with st.expander(f"Investment {i + 1}", expanded=True):

            c1, c2 = st.columns(2)
            c3, c4 = st.columns(2)

            with c1:
                name = st.text_input(
                    label = "Investment Name",
                    value = f"Investment {i + 1}",
                    key   = f"hh_inv_name_{i}"
                )
            with c2:
                principal = st.number_input(
                    label     = f"Amount Invested ({currency_symbol})",
                    min_value = 0.0,
                    value     = 0.0,
                    step      = 10000.0,
                    key       = f"hh_inv_principal_{i}"
                )
            with c3:
                annual_rate = st.number_input(
                    label     = "Expected Annual Return (%)",
                    min_value = 0.0,
                    max_value = 100.0,
                    value     = 8.0,
                    step      = 0.5,
                    key       = f"hh_inv_rate_{i}"
                )
            with c4:
                years = st.number_input(
                    label     = "Investment Duration (Years)",
                    min_value = 1,
                    max_value = 50,
                    value     = 5,
                    step      = 1,
                    key       = f"hh_inv_years_{i}"
                )

            if principal > 0:
                investments.append({
                    "name":        name,
                    "principal":   principal,
                    "annual_rate": annual_rate,
                    "years":       years
                })

    if st.session_state["hh_num_investments"] == 0:
        st.info("No investments added. Click **➕ Add an Investment** if you have any.")

    return investments


# ─────────────────────────────────────────────────────────────────────────────

def _section_goals(currency_symbol):

    st.subheader("🎯 Household Goals")
    st.caption("Things the household is saving toward — renovation, education, vacation, etc.")

    if "hh_num_goals" not in st.session_state:
        st.session_state["hh_num_goals"] = 0

    col_add, col_clear = st.columns([1, 1])

    with col_add:
        if st.button("➕ Add a Goal", use_container_width=True, key="hh_add_goal"):
            st.session_state["hh_num_goals"] += 1

    with col_clear:
        if st.button("🗑️ Clear All Goals", use_container_width=True, key="hh_clear_goals"):
            st.session_state["hh_num_goals"] = 0

    goals = []

    for i in range(st.session_state["hh_num_goals"]):

        with st.expander(f"Goal {i + 1}", expanded=True):

            c1, c2 = st.columns(2)

            with c1:
                name = st.text_input(
                    label = "Goal Name",
                    value = f"Goal {i + 1}",
                    key   = f"hh_goal_name_{i}"
                )
            with c2:
                amount = st.number_input(
                    label     = f"Target Amount ({currency_symbol})",
                    min_value = 0.0,
                    value     = 0.0,
                    step      = 5000.0,
                    key       = f"hh_goal_amount_{i}"
                )

            if amount > 0:
                goals.append({
                    "name":   name,
                    "amount": amount
                })

    if st.session_state["hh_num_goals"] == 0:
        st.info("No goals added. Click **➕ Add a Goal** to plan for a future purchase.")

    return goals


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 3 — PLAN DISPLAY FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════

def _display_plan(plan, currency_symbol):

    st.markdown("---")
    st.header("📋 Your Household Financial Plan")
    st.markdown("---")

    tab_overview, tab_earners, tab_loans, tab_investments, tab_goals, tab_recommendations = st.tabs([
        "📊 Overview",
        "👥 Earners",
        "🏦 Loans",
        "📈 Investments",
        "🎯 Goals",
        "✅ Recommendations"
    ])

    with tab_overview:
        _tab_overview(plan, currency_symbol)

    with tab_earners:
        _tab_earners(plan, currency_symbol)

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

    st.subheader("📌 Key Metrics")

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.metric("Combined Income",    f"{currency_symbol} {plan['monthly_income']:,.0f}")
    with m2:
        st.metric("Monthly Expenses",   f"{currency_symbol} {plan['monthly_expenses']:,.0f}")
    with m3:
        st.metric("Total Loan Payments", f"{currency_symbol} {plan['total_monthly_debt']:,.0f}")
    with m4:
        remaining = plan["remaining_after_bills"]
        st.metric(
            label      = "Monthly Remaining",
            value      = f"{currency_symbol} {max(0, remaining):,.0f}",
            delta      = f"{remaining:,.0f}",
            delta_color = "normal" if remaining >= 0 else "inverse"
        )

    st.markdown("---")
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
    st.subheader("💸 Recommended Budget Breakdown (50/30/20 Rule)")

    col_chart, col_details = st.columns(2)

    with col_chart:
        st.plotly_chart(
            chartBudgetBreakdown(plan["budget"], currency_symbol),
            use_container_width=True
        )
    with col_details:
        st.markdown("**Based on your combined household income:**")
        st.markdown(f"- 🔴 **Needs (50%):** {currency_symbol} {plan['budget']['needs']:,.2f} / month")
        st.markdown(f"- 🔵 **Wants (30%):** {currency_symbol} {plan['budget']['wants']:,.2f} / month")
        st.markdown(f"- 🟢 **Savings (20%):** {currency_symbol} {plan['budget']['savings']:,.2f} / month")
        st.markdown("---")
        dti = plan["dti"]
        st.markdown(f"**Debt-to-Income Ratio:** {dti['ratio']}% — {dti['status']}")
        st.caption(dti["advice"])

    st.markdown("---")
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

    st.markdown("---")
    st.subheader("🛡️ Emergency Fund")
    emergency = plan["emergency"]

    e1, e2 = st.columns(2)
    with e1:
        st.metric("Minimum Fund (3 months)",      f"{currency_symbol} {emergency['minimum_fund']:,.0f}")
    with e2:
        st.metric("Recommended Fund (6 months)",  f"{currency_symbol} {emergency['recommended_fund']:,.0f}")

    st.caption(emergency["advice"])


# ─────────────────────────────────────────────────────────────────────────────

def _tab_earners(plan, currency_symbol):

    st.subheader("👥 Income Contributions")
    st.caption("How much each household member contributes to the total income.")

    contributions = plan.get("income_contributions", [])

    if not contributions:
        st.info("No earner data available.")
        return

    cols = st.columns(len(contributions))

    for i, earner in enumerate(contributions):
        with cols[i]:
            st.metric(
                label = earner["name"],
                value = f"{currency_symbol} {earner['income']:,.0f}",
                delta = f"{earner['contribution']}% of total"
            )

    st.markdown("---")

    st.plotly_chart(
        chartHouseholdIncomeContributions(contributions, currency_symbol),
        use_container_width=True
    )

    st.markdown("---")
    st.subheader("📋 Earner Summary Table")

    import pandas as pd

    df = pd.DataFrame(contributions)
    df.columns = ["Name", f"Monthly Income ({currency_symbol})", "Contribution (%)"]
    df[f"Monthly Income ({currency_symbol})"] = df[
        f"Monthly Income ({currency_symbol})"
    ].apply(lambda x: f"{currency_symbol} {x:,.2f}")
    df["Contribution (%)"] = df["Contribution (%)"].apply(lambda x: f"{x:.1f}%")
    st.dataframe(df, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────

def _tab_loans(plan, currency_symbol):

    loans = plan["loans"]

    if not loans:
        st.info("No loans were entered. Add loans in the input section above.")
        return

    st.subheader("🏦 Loan Summary")

    for loan in loans:
        with st.expander(f"📄 {loan['name']} — {currency_symbol} {loan['principal']:,.0f}", expanded=True):

            c1, c2, c3 = st.columns(3)

            with c1:
                st.metric("Monthly Payment", f"{currency_symbol} {loan['monthly_payment']:,.2f}")
            with c2:
                st.metric("Total Interest",  f"{currency_symbol} {loan['total_interest']:,.2f}")
            with c3:
                st.metric("Total Payment",   f"{currency_symbol} {loan['total_payment']:,.2f}")

            schedule = loanAmortizationSchedule(
                loan["principal"],
                loan["annual_rate"],
                loan["years"]
            )

            st.plotly_chart(
                chartLoanAmortization(schedule, loan["name"], currency_symbol),
                use_container_width=True
            )

            if st.checkbox(
                f"Show full repayment table for {loan['name']}",
                key=f"hh_amort_{loan['name']}"
            ):
                import pandas as pd
                df = pd.DataFrame(schedule)
                df.columns = ["Month", "Payment", "Principal Paid", "Interest Paid", "Remaining Balance"]
                st.dataframe(df, use_container_width=True)

    if len(loans) > 1:
        st.markdown("---")
        st.subheader("⚖️ Loan Comparison")
        st.plotly_chart(
            chartLoanComparison(loans, currency_symbol),
            use_container_width=True
        )
        st.caption(
            "💡 **Tip:** Pay off the highest-interest loan first to save the most money overall."
        )


# ─────────────────────────────────────────────────────────────────────────────

def _tab_investments(plan, currency_symbol):

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
                st.metric("Final Value",     f"{currency_symbol} {inv['total_amount']:,.2f}")

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

    goals = plan["goals"]

    if not goals:
        st.info("No goals were entered. Add goals in the input section above.")
        return

    st.subheader("🎯 Household Savings Goals")
    st.caption(
        f"Based on your available monthly savings of "
        f"**{currency_symbol} {plan['available_savings']:,.2f}** "
        f"split across all goals."
    )

    for goal in goals:
        with st.expander(f"🎯 {goal['name']} — {currency_symbol} {goal['amount']:,.0f}", expanded=True):

            if goal["feasible"]:
                c1, c2, c3 = st.columns(3)

                with c1:
                    st.metric("Target Amount",            f"{currency_symbol} {goal['amount']:,.2f}")
                with c2:
                    st.metric("Monthly Savings Allocated", f"{currency_symbol} {goal['monthly_savings']:,.2f}")
                with c3:
                    st.metric("Time to Goal",             f"{goal['full_years']}y {goal['remaining_months']}m")

                st.success(f"✅ {goal['message']}")
            else:
                st.error(f"❌ {goal['message']}")
                st.caption(
                    "To make this goal reachable, increase combined income, "
                    "reduce shared expenses, or reduce loan obligations."
                )

    goals_chart = chartGoalsTimeline(goals, currency_symbol)
    if goals_chart:
        st.markdown("---")
        st.plotly_chart(goals_chart, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────

def _tab_recommendations(plan):

    st.subheader("✅ Household Financial Recommendations")
    st.caption("Based on your combined household financial data.")
    st.markdown("---")

    for rec in plan["recommendations"]:
        st.markdown(rec)
        st.markdown("---")

    st.warning(
        "⚠️ **Disclaimer:** These recommendations are algorithmically generated "
        "based on standard financial planning rules. They do not constitute "
        "professional financial advice. Please consult a certified financial "
        "advisor before making major financial decisions."
    )


# ═════════════════════════════════════════════════════════════════════════════
# RUN THE PAGE
# ═════════════════════════════════════════════════════════════════════════════

show_household()

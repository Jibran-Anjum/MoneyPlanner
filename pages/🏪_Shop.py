# ── MONEYPLANNER - SHOP FINANCIAL PLANNER PAGE ───────────────────────────────
# Handles shop revenue, cost of goods, operating expenses,
# business loans, inventory goals and profit analysis.
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st
from logic.plan_generator import generateShopPlan
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
    chartShopProfitBreakdown
)


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 1 — MAIN ENTRY FUNCTION
# ═════════════════════════════════════════════════════════════════════════════

def show_shop():
    """
    Main function that runs the entire Shop planner page.
    """

    st.title("🏪 Shop Financial Planner")
    st.caption("Analyse your shop's revenue, costs, loans and business goals.")
    # st.markdown("---")

    # ── CURRENCY SELECTOR ────────────────────────────────────────────────────
    # currency = st.selectbox(
    #     "Select your currency",
    #     options=["Rs. (PKR)", "$ (USD)", "€ (EUR)", "£ (GBP)", "AED (UAE)"],
    #     index=0
    # )
    currency_symbol = st.session_state.get("currency_symbol", "Rs.")
    st.markdown("---")

    # ── INPUT SECTIONS ───────────────────────────────────────────────────────
    monthly_revenue, cogs, monthly_expenses = _section_revenue(currency_symbol)
    loans                                   = _section_loans(currency_symbol)
    investments                             = _section_investments(currency_symbol)
    goals                                   = _section_goals(currency_symbol)

    st.markdown("---")

    # ── GENERATE PLAN BUTTON ─────────────────────────────────────────────────
    if st.button("📊 Generate Shop Financial Plan", type="primary", use_container_width=True):

        if monthly_revenue <= 0:
            st.error("❌ Please enter a valid monthly revenue greater than zero.")
            return

        data = {
            "monthly_revenue":    monthly_revenue,
            "cost_of_goods_sold": cogs,
            "monthly_expenses":   monthly_expenses,
            "loans":              loans,
            "goals":              goals,
            "investments":        investments,
            "currency_symbol":    currency_symbol
        }

        with st.spinner("Generating your shop financial plan..."):
            plan = generateShopPlan(data)

        st.session_state["shop_plan"] = plan

    # ── DISPLAY PLAN ─────────────────────────────────────────────────────────
    if "shop_plan" in st.session_state:
        st.success("✅ Your plan is ready! Scroll down to view the details.")
        # Create an anchor target
        st.markdown('<div id="plan-results"></div>', unsafe_allow_html=True)
        _display_plan(st.session_state["shop_plan"], currency_symbol)


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 2 — INPUT FORM FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════

def _section_revenue(currency_symbol):
    """
    Renders the Revenue and Costs input section.

    Plain English:
        Revenue         = Total money coming into the shop from sales
        Cost of Goods   = What the shop owner paid to buy/make the products
        Gross Profit    = Revenue minus Cost of Goods
        Expenses        = Running costs like rent, salaries, electricity
        Net Profit      = Gross Profit minus Expenses — the real profit

    Returns:
        monthly_revenue  : float
        cogs             : float
        monthly_expenses : float
    """

    st.subheader("💰 Revenue & Costs")

    col1, col2 = st.columns(2)

    with col1:
        monthly_revenue = st.number_input(
            label     = f"Monthly Revenue ({currency_symbol})",
            min_value = 0.0,
            value     = 0.0,
            step      = 5000.0,
            help      = "Total money earned from sales before any deductions"
        )

    with col2:
        cogs = st.number_input(
            label     = f"Cost of Goods Sold ({currency_symbol})",
            min_value = 0.0,
            value     = 0.0,
            step      = 5000.0,
            help      = "What you paid to buy or manufacture the products you sold"
        )

    monthly_expenses = st.number_input(
        label     = f"Monthly Operating Expenses ({currency_symbol})",
        min_value = 0.0,
        value     = 0.0,
        step      = 1000.0,
        help      = "Rent, salaries, utilities, internet, transport — all running costs"
    )

    # ── LIVE PROFIT PREVIEW ──────────────────────────────────────────────────
    # Show gross profit and net profit as the user types
    # This gives immediate value before generating the full plan
    if monthly_revenue > 0:
        gross_profit  = monthly_revenue - cogs
        net_profit    = gross_profit - monthly_expenses
        profit_margin = (net_profit / monthly_revenue * 100) if monthly_revenue > 0 else 0

        st.markdown("---")
        st.subheader("📊 Live Profit Preview")

        p1, p2, p3 = st.columns(3)

        with p1:
            st.metric(
                label = "Gross Profit",
                value = f"{currency_symbol} {gross_profit:,.2f}"
            )
        with p2:
            st.metric(
                label = "Net Profit",
                value = f"{currency_symbol} {net_profit:,.2f}"
            )
        with p3:
            st.metric(
                label = "Profit Margin",
                value = f"{profit_margin:.1f}%"
            )

        # Color coded feedback based on profit margin
        if net_profit < 0:
            st.error("🔴 Your shop is currently operating at a **loss**. Revenue does not cover costs.")
        elif profit_margin < 10:
            st.warning("🟠 Profit margin is very thin. Any unexpected cost could result in a loss.")
        elif profit_margin < 20:
            st.warning("🟡 Profit margin is moderate. Look for ways to reduce costs or increase prices.")
        else:
            st.success(f"✅ Healthy profit margin of {profit_margin:.1f}%. Keep managing costs carefully.")

    return monthly_revenue, cogs, monthly_expenses


# ─────────────────────────────────────────────────────────────────────────────

def _section_loans(currency_symbol):
    """
    Renders the Business Loans input section.

    Returns:
        loans : List of loan dictionaries
    """

    st.subheader("🏦 Business Loans")

    if "shop_num_loans" not in st.session_state:
        st.session_state["shop_num_loans"] = 0

    col_add, col_clear = st.columns([1, 1])

    with col_add:
        if st.button("➕ Add a Loan", use_container_width=True, key="shop_add_loan"):
            st.session_state["shop_num_loans"] += 1

    confirm_clear_loans = st.checkbox("Confirm clear", key="confirm_clear_loans")

    with col_clear:
        if st.button("🗑️ Clear All Loans", disabled=not confirm_clear_loans, use_container_width=True, key="shop_clear_loans"):
            st.session_state["shop_num_loans"] = 0

    loans = []

    for i in range(st.session_state["shop_num_loans"]):

        with st.expander(f"Loan {i + 1}", expanded=True):

            c1, c2 = st.columns(2)
            c3, c4 = st.columns(2)

            with c1:
                name = st.text_input(
                    label = "Loan Name",
                    value = f"Loan {i + 1}",
                    key   = f"shop_loan_name_{i}",
                    help  = "e.g. Equipment Loan, Inventory Loan, Expansion Loan"
                )
            with c2:
                principal = st.number_input(
                    label     = f"Principal Amount ({currency_symbol})",
                    min_value = 0.0,
                    value     = 0.0,
                    step      = 10000.0,
                    key       = f"shop_loan_principal_{i}"
                )
            with c3:
                annual_rate = st.number_input(
                    label     = "Annual Interest Rate (%)",
                    min_value = 0.0,
                    max_value = 100.0,
                    value     = 0.0,
                    step      = 0.5,
                    key       = f"shop_loan_rate_{i}"
                )
            with c4:
                years = st.number_input(
                    label     = "Loan Duration (Years)",
                    min_value = 1,
                    max_value = 30,
                    value     = 1,
                    step      = 1,
                    key       = f"shop_loan_years_{i}"
                )

            if principal > 0:
                loans.append({
                    "name":        name,
                    "principal":   principal,
                    "annual_rate": annual_rate,
                    "years":       years
                })

    if st.session_state["shop_num_loans"] == 0:
        st.info("No business loans added. Click **➕ Add a Loan** if you have any.")

    return loans


# ─────────────────────────────────────────────────────────────────────────────

def _section_investments(currency_symbol):
    """
    Renders the Business Investments input section.

    Returns:
        investments : List of investment dictionaries
    """

    st.subheader("📈 Business Investments")
    st.caption("Money set aside for business growth — equipment, property, stocks.")

    if "shop_num_investments" not in st.session_state:
        st.session_state["shop_num_investments"] = 0

    col_add, col_clear = st.columns([1, 1])

    with col_add:
        if st.button("➕ Add an Investment", use_container_width=True, key="shop_add_inv"):
            st.session_state["shop_num_investments"] += 1

    confirm_clear_investments = st.checkbox("Confirm clear", key="confirm_clear_inv")

    with col_clear:
        if st.button("🗑️ Clear All Investments", disabled=not confirm_clear_investments, use_container_width=True, key="shop_clear_inv"):
            st.session_state["shop_num_investments"] = 0

    investments = []

    for i in range(st.session_state["shop_num_investments"]):

        with st.expander(f"Investment {i + 1}", expanded=True):

            c1, c2 = st.columns(2)
            c3, c4 = st.columns(2)

            with c1:
                name = st.text_input(
                    label = "Investment Name",
                    value = f"Investment {i + 1}",
                    key   = f"shop_inv_name_{i}"
                )
            with c2:
                principal = st.number_input(
                    label     = f"Amount ({currency_symbol})",
                    min_value = 0.0,
                    value     = 0.0,
                    step      = 10000.0,
                    key       = f"shop_inv_principal_{i}"
                )
            with c3:
                annual_rate = st.number_input(
                    label     = "Expected Annual Return (%)",
                    min_value = 0.0,
                    max_value = 100.0,
                    value     = 8.0,
                    step      = 0.5,
                    key       = f"shop_inv_rate_{i}"
                )
            with c4:
                years = st.number_input(
                    label     = "Duration (Years)",
                    min_value = 1,
                    max_value = 50,
                    value     = 5,
                    step      = 1,
                    key       = f"shop_inv_years_{i}"
                )

            if principal > 0:
                investments.append({
                    "name":        name,
                    "principal":   principal,
                    "annual_rate": annual_rate,
                    "years":       years
                })

    if st.session_state["shop_num_investments"] == 0:
        st.info("No investments added. Click **➕ Add an Investment** if you have any.")

    return investments


# ─────────────────────────────────────────────────────────────────────────────

def _section_goals(currency_symbol):
    """
    Renders the Business Goals input section.

    Returns:
        goals : List of goal dictionaries
    """

    st.subheader("🎯 Business Goals")
    st.caption("Things the shop is saving toward — new equipment, renovation, second branch.")

    if "shop_num_goals" not in st.session_state:
        st.session_state["shop_num_goals"] = 0

    col_add, col_clear = st.columns([1, 1])

    with col_add:
        if st.button("➕ Add a Goal", use_container_width=True, key="shop_add_goal"):
            st.session_state["shop_num_goals"] += 1

    confirm_clear_goals = st.checkbox("Confirm clear", key="confirm_clear_goals")

    with col_clear:
        if st.button("🗑️ Clear All Goals", disabled=not confirm_clear_goals, use_container_width=True, key="shop_clear_goals"):
            st.session_state["shop_num_goals"] = 0

    goals = []

    for i in range(st.session_state["shop_num_goals"]):

        with st.expander(f"Goal {i + 1}", expanded=True):

            c1, c2 = st.columns(2)

            with c1:
                name = st.text_input(
                    label = "Goal Name",
                    value = f"Goal {i + 1}",
                    key   = f"shop_goal_name_{i}"
                )
            with c2:
                amount = st.number_input(
                    label     = f"Target Amount ({currency_symbol})",
                    min_value = 0.0,
                    value     = 0.0,
                    step      = 5000.0,
                    key       = f"shop_goal_amount_{i}"
                )

            if amount > 0:
                goals.append({
                    "name":   name,
                    "amount": amount
                })

    if st.session_state["shop_num_goals"] == 0:
        st.info("No goals added. Click **➕ Add a Goal** to plan for a future business purchase.")

    return goals


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 3 — PLAN DISPLAY FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════

def _display_plan(plan, currency_symbol):
    """
    Renders the complete shop financial plan.
    Has an extra Profit Analysis tab unique to the Shop page.
    """

    st.markdown("---")
    st.header("📋 Your Shop Financial Plan")
    st.markdown("---")

    tab_overview, tab_profit, tab_loans, tab_investments, tab_goals, tab_recommendations = st.tabs([
        "📊 Overview",
        "💹 Profit Analysis",
        "🏦 Loans",
        "📈 Investments",
        "🎯 Goals",
        "✅ Recommendations"
    ])

    with tab_overview:
        _tab_overview(plan, currency_symbol)

    with tab_profit:
        _tab_profit(plan, currency_symbol)

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
    """Renders key shop metrics, health score and budget breakdown."""

    st.subheader("📌 Key Metrics")

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.metric("Monthly Revenue",   f"{currency_symbol} {plan['monthly_revenue']:,.0f}")
    with m2:
        st.metric("Net Profit",        f"{currency_symbol} {plan['net_profit']:,.0f}")
    with m3:
        st.metric("Profit Margin",     f"{plan['profit_margin']:.1f}%")
    with m4:
        remaining = plan["remaining_after_bills"]
        st.metric(
            label      = "After Loan Payments",
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

    st.subheader("📊 Revenue vs Outgoings")
    st.plotly_chart(
        chartIncomevsExpenses(
            plan["monthly_revenue"],
            plan["monthly_expenses"],
            plan["total_monthly_debt"],
            currency_symbol
        ),
        use_container_width=True
    )

    st.markdown("---")
    st.subheader("🛡️ Business Emergency Fund")
    emergency = plan["emergency"]

    e1, e2 = st.columns(2)
    with e1:
        st.metric("Minimum Reserve (3 months)", f"{currency_symbol} {emergency['minimum_fund']:,.0f}")
    with e2:
        st.metric("Recommended Reserve (6 months)", f"{currency_symbol} {emergency['recommended_fund']:,.0f}")

    st.caption(
        "A business emergency fund covers unexpected drops in revenue, "
        "emergency repairs, or supplier payment gaps."
    )


# ─────────────────────────────────────────────────────────────────────────────

def _tab_profit(plan, currency_symbol):
    """
    Renders the Profit Analysis tab — unique to the Shop page.
    Shows the waterfall chart and detailed cost breakdown.
    """

    st.subheader("💹 Profit Breakdown")

    # ── PROFIT METRICS ───────────────────────────────────────────────────────
    p1, p2, p3 = st.columns(3)

    with p1:
        st.metric("Gross Profit", f"{currency_symbol} {plan['gross_profit']:,.2f}")
    with p2:
        st.metric("Net Profit",   f"{currency_symbol} {plan['net_profit']:,.2f}")
    with p3:
        st.metric("Profit Margin", f"{plan['profit_margin']:.1f}%")

    st.markdown("---")

    # ── WATERFALL CHART ──────────────────────────────────────────────────────
    st.plotly_chart(
        chartShopProfitBreakdown(
            plan["monthly_revenue"],
            plan["cogs"],
            plan["monthly_expenses"],
            currency_symbol
        ),
        use_container_width=True
    )

    st.markdown("---")

    # ── COST RATIO TABLE ─────────────────────────────────────────────────────
    st.subheader("📋 Cost Ratio Analysis")

    revenue = plan["monthly_revenue"]

    if revenue > 0:
        import pandas as pd

        cost_data = {
            "Category":          ["Cost of Goods", "Operating Expenses", "Loan Payments", "Net Profit"],
            f"Amount ({currency_symbol})": [
                f"{plan['cogs']:,.2f}",
                f"{plan['monthly_expenses']:,.2f}",
                f"{plan['total_monthly_debt']:,.2f}",
                f"{plan['net_profit']:,.2f}"
            ],
            "% of Revenue": [
                f"{plan['cogs'] / revenue * 100:.1f}%",
                f"{plan['monthly_expenses'] / revenue * 100:.1f}%",
                f"{plan['total_monthly_debt'] / revenue * 100:.1f}%",
                f"{plan['profit_margin']:.1f}%"
            ]
        }

        df = pd.DataFrame(cost_data)
        st.dataframe(df, use_container_width=True)

        st.caption(
            "💡 **Tip:** Aim to keep Cost of Goods below 60% of revenue "
            "and operating expenses below 20% to maintain a healthy profit margin."
        )


# ─────────────────────────────────────────────────────────────────────────────

def _tab_loans(plan, currency_symbol):
    """Renders the Loans tab for the shop."""

    loans = plan["loans"]

    if not loans:
        st.info("No business loans were entered.")
        return

    st.subheader("🏦 Business Loan Summary")

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

            if st.checkbox(f"Show repayment table for {loan['name']}", key=f"shop_amort_{loan['name']}"):
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


# ─────────────────────────────────────────────────────────────────────────────

def _tab_investments(plan, currency_symbol):
    """Renders the Investments tab for the shop."""

    investments = plan["investments"]

    if not investments:
        st.info("No business investments were entered.")
        return

    st.subheader("📈 Business Investment Projections")

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
    """Renders the Goals tab for the shop."""

    goals = plan["goals"]

    if not goals:
        st.info("No business goals were entered.")
        return

    st.subheader("🎯 Business Goals Timeline")
    st.caption(
        f"Based on available monthly savings of "
        f"**{currency_symbol} {plan['available_savings']:,.2f}** "
        f"split across all goals."
    )

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
                st.caption("Increase revenue or reduce costs to free up savings for this goal.")

    goals_chart = chartGoalsTimeline(goals, currency_symbol)
    if goals_chart:
        st.markdown("---")
        st.plotly_chart(goals_chart, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────

def _tab_recommendations(plan):
    """Renders the Recommendations tab for the shop."""

    st.subheader("✅ Business Financial Recommendations")
    st.caption("Based on your shop's revenue, costs, and financial obligations.")
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

show_shop()

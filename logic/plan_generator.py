from logic.calculations import (
    budgetBreakdown_50_30_20,
    debtToIncomeRatio,
    monthlyLoanPayment,
    savingsGoalMonths,
    emergencyFundRecommendation,
    financialHealthScore,
    compoundInterest
)

#########################
# SHARED HELPER FUNCTIONS
#########################
def _formatCurrency(amount, currency_symbol='Rs.'):
    return f'{currency_symbol} {amount:,.2f}'

def _generateLoanSummary(loans):
    if not loans:
        return []

    summaries = []

    for loan in loans:
        name = loan.get('name', 'Unnamed Loan')
        principal = loan.get('principal', 0)
        annual_rate = loan.get('annual_rate', 0)
        years = loan.get('years', 1)
        
        if principal <= 0:
            continue

        result = monthlyLoanPayment(principal, annual_rate, years)

        summaries.append({
            'name': name,
            'principal': principal,
            'annual_rate': annual_rate,
            'years': years,
            'monthly_payment': result['monthly_payment'],
            'total_payment': result['total_payment'],
            'total_interest': result['total_interest']
        })

    return summaries

def _generateGoalsSummary(goals, available_monthly_savings):
    if not goals:
        return []

    num_goals = len(goals)

    if num_goals == 0:
        return []

    savings_per_goal = available_monthly_savings / num_goals

    summaries = []

    for goal in goals:
        name = goal.get('name', 'Unnamed Goal')
        amount = goal.get('amount', 0)

        if amount <= 0:
            continue

        result = savingsGoalMonths(amount, savings_per_goal)

        summaries.append({
            'name': name,
            'amount': amount,
            'monthly_savings': round(savings_per_goal, 2),
            'feasible': result['feasible'],
            'months': result.get('months'),
            'full_years': result.get('full_years'),
            'remaining_months': result.get('remaining_months'),
            'message': result.get('message')
        })

    return summaries

###########################
# INDIVIDUAL FINANCIAL PLAN
###########################
def generateIndividualPlan(data):
    monthly_income = data.get('monthly_income', 0)
    monthly_expenses = data.get('monthly_expenses', 0)
    loans = data.get('loans', [])
    goals = data.get('goals', [])
    investements = data.get('investments', [])
    currency = data.get('currency_symbol', 'Rs.')

    loan_summaries = _generateLoanSummary(loans)
    total_monthly_debt = sum(l['monthly_payment'] for l in loan_summaries)
    budget = budgetBreakdown_50_30_20(monthly_income)
    dti_result = debtToIncomeRatio(total_monthly_debt, monthly_income)

    remaining_after_bills = monthly_income - monthly_expenses - total_monthly_debt

    available_savings = max(0, remaining_after_bills)

    goal_summaries = _generateGoalsSummary(goals, available_savings)

    emergency = emergencyFundRecommendation(monthly_expenses)

    investment_summaries = []

    for inv in investements:
        inv_name = inv.get('name', 'Investment')
        inv_principal = inv.get('principal', 0)
        inv_rate = inv.get('annual_rate', 0)
        inv_years = inv.get('years', 0)

        if inv_principal <= 0:
            continue

        result = compoundInterest(inv_principal, inv_rate, inv_years)

        investment_summaries.append({
            'name': inv_name,
            'principal': inv_principal,
            'annual_rate': inv_rate,
            'years': inv_years,
            'total_amount': result['total_amount'],
            'interest_earned': result['interest_earned']
        })

    health = financialHealthScore(
        monthly_income,
        monthly_expenses,
        total_monthly_debt,
        available_savings
    )

    recommendations = _buildRecommendationsIndividual(
        monthly_income,
        monthly_expenses,
        total_monthly_debt,
        available_savings,
        dti_result,
        health,
        emergency
    )

    return {
        'profile_type': 'Individual',
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expenses,
        'total_monthly_debt': total_monthly_debt,
        'remaining_after_bills': remaining_after_bills,
        'available_savings': available_savings,
        'budget': budget,
        'dti': dti_result,
        'loans': loan_summaries,
        'goals': goal_summaries,
        'investments': investment_summaries,
        'emergency': emergency,
        'health': health,
        'recommendations': recommendations,
        'currency': currency
    }

def _buildRecommendationsIndividual(income, expenses, debt, savings, dti, health, emergency):
    recommendations = []

    savings_rate = savings / income if income > 0 else 0

    if savings_rate >= 0.20:
        recommendations.append(
            '✅ You are saving 20% or more of your income. '
            'This is the gold standard. Keep it up and consider investing the surplus'
        )
    elif savings_rate >= 0.10:
        recommendations.append(
            '🟡 You are saving between 10% and 20% of your income. '
            'Try to increase this to 20% by trimming discretionary spending.'
        )
    elif savings_rate > 0:
        recommendations.append(
            '🟠 Your saving rate is below 10%. '
            'Review your expenses and identify at least one category to reduce.'
        )
    else:
        recommendations.append(
            '🔴 You are currently not saving anything. '
            'This is a critical issue. Even saving 5% of your income is a meaningful start.'
        )
    
    if dti['ratio'] < 20:
        recommendations.append(
            "✅ Your debt level is very healthy. "
            "You have strong borrowing capacity if needed in the future."
        )
    elif dti['ratio'] < 36:
        recommendations.append(
            "🟡 Your debt is at a manageable level. "
            "Avoid adding new loans until existing ones are reduced."
        )
    else:
        recommendations.append(
            f"🔴 Your debt-to-income ratio is {dti['ratio']}% which is high. "
            "Prioritize paying off the highest interest loan first. "
            "This strategy is called the Avalanche Method and saves the most money."
        )

    expense_ratio = expenses / income if income > 0 else 0

    if expense_ratio > 0.70:
        recommendations.append(
            '🔴 Your expenses consume more than 70% of your income. '
            'Audit your monthly spending and identify non-essential costs to cut. '
            'Target getting expenses below 50% of income.'
        )
    elif expense_ratio > 0.50:
        recommendations.append(
            '🟠 Your expenses are between 50% and 70% of your income. '
            'Review your "wants" category and try to reduce it gradually.'
        )
    else:
        recommendations.append(
            '✅ Your expense ratio is healthy — below 50% of income. '
            'You have good financial discipline on spending.'
        )

    recommendations.append(
        f'🛡️  Emergency Fund Target: Aim to build a fund of '
        f'at least {_formatCurrency(emergency["minimum_fund"])} '
        f'(3 months of expenses). '
        f'Your ideal target is {_formatCurrency(emergency["recommended_fund"])} '
        f'(6 months). Keep this in a seperate savings account and never invest it.'
    )

    recommendations.append(
        f'📊 Overall Financial Health: {health["grade"]} ({health["total_score"]}/100. '
        f'{health["advice"]}'
    )

    return recommendations

##########################
# HOUSEHOLD FINANCIAL PLAN
##########################
def generateHouseholdPlan(data):
    earners = data.get('earners', [])
    monthly_expenses = data.get('monthly_expenses', 0)
    loans = data.get('loans', [])
    goals = data.get('goals', [])
    investments = data.get('investments', [])
    currency = data.get('currency_symbol', 'Rs.')

    total_monthly_income = sum(
        e.get('monthly_income', 0) for e in earners if e.get('monthly_income', 0) > 0
    )

    individual_data = {
        'monthly_income': total_monthly_income,
        'monthly_expenses': monthly_expenses,
        'loans': loans,
        'goals': goals,
        'investments': investments,
        'currency_symbol': currency
    }

    plan = generateIndividualPlan(individual_data)

    plan['profile_type'] = 'Household'
    plan['earners'] = earners
    plan['total_monthly_income'] = total_monthly_income
    plan['num_earners'] = len(earners)

    income_contributions = []

    for earner in earners:
        earner_income = earner.get('monthly_income', 0)
        contribution = (earner_income / total_monthly_income) * 100 if total_monthly_income > 0 else 0
        income_contributions.append({
            'name': earner.get('name', 'Earner'),
            'income': earner_income,
            'contribution': round(contribution, 1)
        })

    plan['income_contributions'] = income_contributions
    return plan

def generateShopPlan(data):
    monthly_revenue = data.get('monthly_revenue', 0)
    cogs = data.get('cost_of_goods_sold', 0)
    monthly_expenses = data.get('monthly_expenses', 0)
    loans = data.get('loans', [])
    goals = data.get('goals', [])
    investments = data.get('investments', [])
    currency = data.get('currency_symbol', 'Rs.')

    gross_profit = monthly_revenue - cogs

    net_profit = gross_profit - monthly_expenses

    profit_margin = (net_profit/monthly_revenue * 100) if monthly_revenue > 0 else 0

    total_expenses = cogs + monthly_expenses

    individual_data = {
        'monthly_income': monthly_revenue,
        'monthly_expenses': total_expenses,
        'loans': loans,
        'goals': goals,
        'investments': investments,
        'currency_symbol': currency
    }

    plan = generateIndividualPlan(individual_data)

    plan['profile_type'] = 'Shop'
    plan['monthly_revenue'] = monthly_revenue
    plan['cogs'] = cogs
    plan['gross_profit'] = round(gross_profit, 2)
    plan['net_profit'] = round(net_profit, 2)
    plan['profit_margin'] = round(profit_margin, 2)

    shop_recs = _buildRecommendationShop(monthly_revenue, cogs, gross_profit, net_profit, profit_margin)

    plan['recommendations'] = shop_recs + plan['recommendations']

    return plan

def _buildRecommendationShop(monthly_revenue, cogs, gross_profit, net_profit, profit_margin):
    recommendations = []

    if profit_margin >= 20:
        recommendations.append(
            f'✅ Your profit margin is {profit_margin:.1f}% which is healthy for a small shop. '
            'Consider reinvesting surplus profit into inventory or expansion.'
        )
    elif profit_margin >= 10:
        recommendations.append(
            f'🟡 Your profit margin is {profit_margin:.1f}%. '
            'Look for ways to either reduce your cost of goods (negotiate with suppliers) '
            'or increase your selling prices moderately.'
        )
    elif profit_margin > 0:
        recommendations.append(
            f'🟠 Your profit margin is only {profit_margin:.1f}%. '
            'This is very thin. Any unexpected expense could result in a loss. '
            'Urgently review your pricing strategy and supplier costs.'
        )
    else:
        recommendations.append(
            '🔴 Your shop is currently operating at a loss '
            f'(profit margin: {profit_margin:.1f}%). '
            'Revenue is not covering costs. Immediate action is needed — '
            'cut non-essential expenses and review your pricing.'
        )

    cogs_ratio = (cogs / monthly_revenue * 100) if monthly_revenue > 0 else 0

    if cogs_ratio > 70:
        recommendations.append(
            f'🔴 Your cost of goods is {cogs_ratio:.1f}% of revenue — very high. '
            'Try negotiating better rates with suppliers or sourcing cheaper alternatives.'
        )
    elif cogs_ratio > 50:
        recommendations.append(
            f'🟡 Your cost of goods is {cogs_ratio:.1f}% of revenue. '
            'This is average for retail. Explore bulk purchasing to reduce unit costs.'
        )
    else:
        recommendations.append(
            f'✅ Your cost of goods ratio is {cogs_ratio:.1f}% — well controlled.'
        )

    return recommendations

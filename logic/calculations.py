######################
# Interest Calculation
######################
def simpleInterest(principal, annual_rate, years):
    """
    Formula for interest = Principle x Rate x Time
    """
    if principal < 0 or annual_rate < 0 or years < 0:
        raise ValueError('Principal, rate, or years cannot be negative...')

    annual_rate_percentage = annual_rate / 100

    interest_amount = principal * annual_rate_percentage * years

    total_amount = principal + interest_amount

    return {
            'interest_amount': round(interest_amount, 2),
            'total_amount': round(total_amount, 2)
            }

def compoundInterest(principal, annual_rate, years, compounds_per_year=12):
    """
    Formula: A = P x (1 + r/n)^(nxt)
    """
    if principal < 0 or annual_rate < 0 or years < 0:
        raise ValueError('Principal, rate, or years cannot be negative...')

    if compounds_per_year <= 0:
        raise ValueError('Compounding frequency must be atleast 1...')

    annual_rate_percent = annual_rate/100

    total_amount = principal * (1 + annual_rate_percent/compounds_per_year)**(compounds_per_year*years)

    interest_earned = total_amount - principal

    return {
            'total_amount': round(total_amount, 2),
            'interest_earned': round(interest_earned, 2)
            }

def compoundInterestYearlyBreakdown(principal, annual_rate, years, compounds_per_year=12):
    """
    Returns a Year by Year breakdown of Compound interest growth
    """
    
    if principal < 0 or annual_rate < 0 or years < 0:
        raise ValueError('Principal, rate, and years cannot be negative...')

    if compounds_per_year <= 0:
        raise ValueError('Compounding frequency must be atleast 1...')

    annual_rate_percent = annual_rate / 100
    breakdown = []
    current_balance = principal

    for year in range(1, int(years) + 1):

        balance = principal * (1 + annual_rate_percent/compounds_per_year)**(compounds_per_year*year)


        total_interest_so_far = balance - principal

        breakdown.append({
            'year': year,
            'balance': round(balance, 2),
            'interest_earned': round(total_interest_so_far, 2)
            })

    return breakdown

##################
# Loan Calculation
##################
def monthlyLoanPayment(principal, annual_rate, years):
    """
    Formula for fixed monthly payment for loan:

    M = P x [r(1+r)^n]/[(1+r)^n - 1]
    """
    if principal <= 0:
        raise ValueError('Loan principal must be greater than 0...')
    if years <= 0:
        raise ValueError('Loan duration must be greater than 0...')
    if annual_rate < 0:
        raise ValueError('Interest rate cannot be negative...')

    if annual_rate == 0:
        total_months = years * 12
        monthly_payment = principal / total_months

        return {
                'monthly_payment': round(monthly_payment, 2),
                'total_payment': round(principal, 2),
                'total_interest': 0.0
                }

    monthly_rate = (annual_rate / 100) / 12

    total_months = years * 12

    numerator = principal * (monthly_rate * (1 + monthly_rate)**total_months)
    denominator = (1 + monthly_rate)**total_months - 1

    monthly_payment = numerator / denominator

    total_payment = monthly_payment * total_months
    total_interest = total_payment - principal

    return {
            'monthly_payment': round(monthly_payment, 2),
            'total_payment': round(total_payment, 2),
            'total_interest': round(total_interest, 2)
            }

def loanAmortizationSchedule(principal, annual_rate, years):
    if principal <= 0 or years <= 0 or annual_rate < 0:
        raise ValueError('Invalid loan parameters...')

    loan_result = monthlyLoanPayment(principal, annual_rate, years)
    monthly = loan_result['monthly_payment']
    monthly_rate = (annual_rate / 100) / 12
    balance = principal
    schedule = []
    total_months = years * 12

    for month in range(1, total_months + 1):
        interest_paid = balance * monthly_rate
        principal_paid = monthly - interest_paid
        balance -= principal_paid

        if balance < 0:
            balance = 0.0

        schedule.append({
            'month': month,
            'payment': round(monthly, 2),
            'principal_paid': round(principal_paid, 2),
            'interest_paid': round(interest_paid, 2),
            'remaining_balance': round(balance, 2)
            })

    return schedule

################################
# BUDGET AND INCOME CALCULATIONS
################################
def budgetBreakdown_50_30_20(monthly_income):
    if monthly_income < 0:
        raise ValueError('Income cannot be negative...')

    needs = monthly_income * 0.50
    wants = monthly_income * 0.30
    savings = monthly_income * 0.20

    return {
        'needs': round(needs, 2),
        'wants': round(wants, 2),
        'savings': round(savings, 2)
            }

def debtToIncomeRatio(total_monthly_debt_payments, gross_monthly_income):
    if gross_monthly_income <= 0:
        raise ValueError('Income must be greater than 0...')

    if total_monthly_debt_payments < 0:
        raise ValueError('Debt payments cannot be negative...')
    
    ratio = (total_monthly_debt_payments / gross_monthly_income) * 100

    # Risk status based on established financial benchmarks
    if ratio < 20:
        status = 'Excellent'
        advice = 'Your debt level is very healthy. You are in a good financial position.'
    elif ratio < 36:
        status = 'Good'
        advice = 'Your debt is manageable. Avoid taking any significant new loans.'
    elif ratio < 50:
        status = 'Concerning'
        advice = 'Over a third of your income goes to debt. Focus on paying down loans before new spending.'
    else:
        status = 'Dangerous'
        advice = 'More than half your income goes to debt. Prioritize debt reduction immediately and consider speaking to a financial advisor.'

    return {
        'ratio': round(ratio, 2),
        'status': status,
        'advice': advice
    }

################################
# SAVINGS AND GOALS CALCULATIONS
################################
def savingsGoalMonths(goal_amount, monthly_savings):
    if goal_amount <= 0:
        raise ValueError('The goal amount must be greater than 0...')
    if monthly_savings < 0:
        raise ValueError('Monthly savings cannot be less than 0...')

    if monthly_savings == 0:
        return {
            'months': None,
            'years': None,
            'feasible': False,
            'message': 'No monthly savings allocated. Cannot reach this goal.'
            }
    months = goal_amount / monthly_savings
    
    full_years = int(months//12)
    remaining_months = int(months%12)

    return {
            'months': round(months, 2),
            'full_years': full_years,
            'remaining_months': remaining_months,
            'feasible': True,
            'message': f'You will reach your goal in {full_years} years and {remaining_months} month(s).'
        }

def emergencyFundRecommendation(monthly_expenses):
    if monthly_expenses < 0:
        raise ValueError('Monthly expenses cannot be less than 0...')

    minimum_fund = monthly_expenses * 3
    recommended_fund = monthly_expenses * 6

    return {
        'minimum_fund': round(minimum_fund, 2),
        'recommended_fund': round(recommended_fund, 2),
        'advice': (
            f'Keep at least {round(minimum_fund, 2)} as your minimum emergency fund, and ideally {round(recommended_fund, 2)} (6 months of expenses).'
            )
        }

########################
# FINANCIAL HEALTH SCORE
########################
def financialHealthScore(monthly_income, monthly_expenses, total_monthly_debt, \
        monthly_savings):
    if monthly_income <= 0:
        raise ValueError('Monthly income must be greater than 0...')

    score = 0
    breakdown = {}

    # Component 1 - Expenses Ratio
    expense_ratio = monthly_expenses / monthly_income

    if expense_ratio <= 0.50:
        exp_score = 25
    elif expense_ratio <= 0.70:
        exp_score = 15
    elif expense_ratio <= 0.90:
        exp_score = 8
    else:
        exp_score = 0

    score += exp_score
    breakdown['Expense Ratio'] = exp_score

    # Component 2 - Debt Load
    dti = (total_monthly_debt / monthly_income) * 100

    if dti < 20:
        debt_score = 25
    elif dti < 36:
        debt_score = 18
    elif dti < 50:
        debt_score = 8
    else:
        debt_score = 0

    score += debt_score
    breakdown['Debt Load'] = debt_score

    # Component 3 - Savings Rate
    savings_rate = monthly_savings / monthly_income

    if savings_rate >= 0.20:
        sav_score = 25
    elif savings_rate >= 0.10:
        sav_score = 15
    elif savings_rate >= 0.05:
        sav_score = 8
    elif savings_rate > 0:
        sav_score = 3
    else:
        sav_score = 0

    score += sav_score
    breakdown['Savings Rate'] = sav_score

    # Component 4 - Income Buffer
    total_outgoing = monthly_expenses + total_monthly_debt
    buffer = monthly_income - total_outgoing
    buffer_ratio = buffer / monthly_income

    if buffer_ratio >= 0.30:
        buf_score = 25
    elif buffer_ratio >= 0.15:
       buf_score = 15
    elif buffer_ratio >= 0.05:
       buf_score = 8
    elif buffer_ratio > 0:
       buf_score = 3
    else:
       buf_score = 0

    score += buf_score
    breakdown['Income Buffer'] = buf_score

    if score >= 80:
        grade = '🟢 Excellent'
        advice = 'Your finances are in great shape. Keep maintaining your savings and low debt levels.'
    elif score >= 60:
        grade = '🟡 Good'
        advice = 'Your finances are healthy but there is room to grow your savings or reduce debt.'
    elif score >= 40:
        grade = '🟠 Fair'
        advice = 'Some areas need attention. Focus on reducing expenses and increase your savings rate.'
    else:
        grade = '🔴 Poor'
        advice = 'Your finances need urgent restructuring. Consider cutting non-essential expenses and seeking financial guidance.'

    return {
        'total_score': score,
        'grade': grade,
        'breakdown': breakdown,
        'advice': advice
        }

import streamlit as st

####################
# PAGE CONFIGURATION
####################
st.set_page_config(
        page_title = 'Money Planner',
        page_icon = '💰',
        layout = 'wide',
        initial_sidebar_state = 'expanded'
        )

with st.sidebar:
    st.header("⚙️ Settings")
    currency = st.selectbox(
        "Select Currency",
        options=["Rs. (PKR)", "$ (USD)", "€ (EUR)", "£ (GBP)", "AED (UAE)"],
        key="global_currency"  # Streamlit saves this automatically
    )
    st.session_state["currency_symbol"] = currency.split(" ")[0]

####################
# HOME PAGE FUNCTIONS
####################
def show_home():
    st.title('💰 Money Planner')
    st.caption('## Your Personal Financial Planning')
    st.markdown('---')


    # Feature Cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader('👤 Individual')
        st.markdown('Plan your personal income, manage loans, set savings, \
                goals, and track investments.'
                )

    with col2:
        st.subheader('👨‍👩‍👧 Household')
        st.markdown('Manage your combined family income, shared expenses, \
                household goals and family investments.'
                    )

    with col3:
        st.subheader('🏪 Shop')
        st.markdown('Track shop revenue, manage business loans, plan \
                inventory and grow your business.')

    st.markdown('---')

#########################
# HOME PAGE FUNCTION CALL
#########################
show_home()


##############
# HOW IT WORKS
##############
st.markdown('## 📋 How It Works')

step1, step2, step3, step4 = st.columns(4)

with step1:
    st.info('**Step 1:**\n\nChoose your Profile Type from the sidebar')

with step2:
    st.info('**Step 2:**\n\nEnter your Income, Loans, and Financial Goals')

with step3:
    st.info('**Step 3:**\n\nWe calculate your Financial Health Score')

with step4:
    st.info('**Step 4:**\n\nReceive your Personalized Financial Plan')

############
# DISCLAIMER
############
st.warning(
            "⚠️  **Disclaimer:** MoneyPlanner provides general \
                    financial guidance only."
            "It is not a substitute for professional financial advice."
            "Always consult a certified financial advisor for major financial \
                    decisions."
                    )

st.markdown('---')

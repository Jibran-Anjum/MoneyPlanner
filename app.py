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

####################
# HOME PAGE FUNCTIONS
####################
def show_home():
    st.title('💰 Money Planner')
    st.caption('## Your Personal Financial Planning')
    st.markdown('---')

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

    # Feature Cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader('👤 Individual')
        st.markdown('Plan your personal income, manage loans, set savings, \
                goals, and track investments.'
                )

    with col2:
        st.subheader('👨‍👩‍👧 Household')
        st.markdown('Manage your combine family income, shared expenses, \
                household goals and family investments.'
                    )

    with col3:
        st.subheader('🏪 Shop')
        st.markdown('Track shop revenue, manage business loans, plan \
                inventory and grow your business.')

    st.markdown('---')

####################
# SIDEBAR NAVIGATION
####################
with st.sidebar:
    st.title('💰 Money Planner')
    st.markdown('---')

    st.markdown('### 📂 Select Your Profile')

    profile = st.selectbox (
            label = 'Who are you planning for?',
            options = [
                '🏠 Home',
                '👤 Individual',
                '👨‍👩‍👧  Household',
                '🏪 Shop'
                ]
            )

    st.markdown('---')
    st.markdown('**HOW IT WORKS**')

    st.markdown('1. Select your profile type')
    st.markdown('2. Enter your financial details')
    st.markdown('3. Get your personalized plan')

##############
# PAGE ROUTING
##############
if profile == '🏠 Home':
    show_home()
# elif profile == '👤 Individual':
#     from pages.individuals import show_individuals
#     show_individuals()
# elif profile == '👨‍👩‍👧  Household':
#     from pages.households import show_households
#     show_households()
# elif profile == '🏪 Shop':
#     from pages.shops import show_shops
#     show_shops()

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
    st.info('**Step 4:**\n\nRecieve your Pesonalized Financial Plan')


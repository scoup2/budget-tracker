import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# 1. Page setup
# ---------------------------------------------------------
st.set_page_config(
    page_title="Personal Budget Tracker",
    page_icon="💰",
    layout="wide"
)

# ---------------------------------------------------------
# 2. App title and introduction
# ---------------------------------------------------------
st.title("💰 Personal Budget & Expense Tracker")
st.write(
    "Plan your monthly spending, track expenses, and see how much "
    "money you have left."
)

# ---------------------------------------------------------
# 3. Set up session storage
# Streamlit reruns the script after user interactions.
# session_state keeps the expense list while the app is open.
# ---------------------------------------------------------
if "expenses" not in st.session_state:
    st.session_state.expenses = []

# ---------------------------------------------------------
# 4. Sidebar: monthly income and savings goal
# ---------------------------------------------------------
st.sidebar.header("Monthly Plan")

monthly_income = st.sidebar.number_input(
    "Monthly take-home income ($)",
    min_value=0.0,
    value=3000.0,
    step=100.0
)

savings_goal = st.sidebar.number_input(
    "Monthly savings goal ($)",
    min_value=0.0,
    value=500.0,
    step=50.0
)

st.sidebar.caption(
    "Use your income after taxes so your budget reflects the money "
    "you can actually spend."
)

# ---------------------------------------------------------
# 5. Add an expense
# A form groups the fields and only submits when the button is clicked.
# ---------------------------------------------------------
st.header("Add an Expense")

with st.form("expense_form", clear_on_submit=True):
    expense_name = st.text_input(
        "Expense name",
        placeholder="Example: Groceries"
    )

    col1, col2 = st.columns(2)

    with col1:
        expense_amount = st.number_input(
            "Amount ($)",
            min_value=0.0,
            value=0.0,
            step=5.0
        )

    with col2:
        expense_category = st.selectbox(
            "Category",
            [
                "Housing",
                "Food",
                "Transportation",
                "Utilities",
                "Entertainment",
                "Shopping",
                "Debt Payments",
                "Healthcare",
                "Other"
            ]
        )

    submitted = st.form_submit_button("Add Expense")

    if submitted:
        if expense_name.strip() and expense_amount > 0:
            st.session_state.expenses.append(
                {
                    "Expense": expense_name.strip(),
                    "Category": expense_category,
                    "Amount": float(expense_amount)
                }
            )
            st.success(f"Added {expense_name.strip()} to your expenses.")
        else:
            st.error("Enter an expense name and an amount greater than $0.")

# ---------------------------------------------------------
# 6. Calculate totals and remaining money
# ---------------------------------------------------------
expenses_df = pd.DataFrame(
    st.session_state.expenses,
    columns=["Expense", "Category", "Amount"]
)

total_expenses = (
    float(expenses_df["Amount"].sum()) if not expenses_df.empty else 0.0
)

money_left = monthly_income - total_expenses
planned_after_savings = monthly_income - savings_goal
savings_progress = (
    total_expenses / monthly_income * 100 if monthly_income > 0 else 0
)
actual_savings = max(money_left, 0.0)

# ---------------------------------------------------------
# 7. Show the budget dashboard
# ---------------------------------------------------------
st.divider()
st.header("Your Monthly Budget")

metric1, metric2, metric3 = st.columns(3)

metric1.metric(
    "Monthly Income",
    f"${monthly_income:,.2f}"
)

metric2.metric(
    "Total Expenses",
    f"${total_expenses:,.2f}"
)

metric3.metric(
    "Money Remaining",
    f"${money_left:,.2f}",
    delta=f"{money_left - savings_goal:,.2f} vs. savings goal"
)

# ---------------------------------------------------------
# 8. Give the user helpful feedback
# ---------------------------------------------------------
if monthly_income == 0:
    st.warning("Enter your monthly income in the sidebar to see your budget status.")
elif money_left < 0:
    st.error(
        f"You are over budget by ${abs(money_left):,.2f}. "
        "Your recorded expenses are higher than your income."
    )
elif money_left < savings_goal:
    st.warning(
        f"You have money remaining, but you are "
        f"${savings_goal - money_left:,.2f} short of your savings goal."
    )
else:
    st.success(
        f"You're on track! You have enough remaining to meet your "
        f"${savings_goal:,.2f} savings goal."
    )

# Progress bar shows how much of income has been spent.
st.subheader("Income Used")
st.progress(min(savings_progress / 100, 1.0))
st.caption(f"You have used {savings_progress:.1f}% of your monthly income.")

# ---------------------------------------------------------
# 9. Show expenses and category totals
# ---------------------------------------------------------
st.divider()
st.header("Expense Details")

if expenses_df.empty:
    st.info("You haven't added any expenses yet. Add your first expense above.")
else:
    st.dataframe(
        expenses_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Amount": st.column_config.NumberColumn(
                "Amount",
                format="$%.2f"
            )
        }
    )

    # Group expenses by category for a simple spending breakdown.
    category_totals = (
        expenses_df.groupby("Category")["Amount"]
        .sum()
        .sort_values(ascending=False)
    )

    st.subheader("Spending by Category")
    st.bar_chart(category_totals)

    # Let the user download a copy of their expense list.
    csv_data = expenses_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Expenses as CSV",
        data=csv_data,
        file_name="my_monthly_expenses.csv",
        mime="text/csv"
    )

    # Button to clear all expenses from this app session.
    if st.button("Clear All Expenses", type="secondary"):
        st.session_state.expenses = []
        st.rerun()

# ---------------------------------------------------------
# 10. Explain the basic budget calculation
# ---------------------------------------------------------
st.divider()
with st.expander("How does this budget tracker work?"):
    st.write("**Money remaining = Monthly income − Total expenses**")
    st.write("**Savings progress = Money remaining compared with your savings goal**")
    st.write(
        "Expenses are kept in the app's session while it is running. "
        "Download the CSV if you want to save a copy. This beginner version "
        "does not permanently store information between sessions."
    )

# ---------------------------------------------------------
# 11. Footer
# ---------------------------------------------------------
st.caption("Personal Budget & Expense Tracker | Built with Python and Streamlit")

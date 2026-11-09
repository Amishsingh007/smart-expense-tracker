import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import date

# 1. Page Configuration
st.set_page_config(page_title="Smart Expense Tracker", page_icon="💳", layout="wide")

DATA_FILE = "expenses.csv"

# 2. Load or Initialize Data Safely
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        if not df.empty:
            df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)
        return df
    else:
        df = pd.DataFrame(columns=["Date", "Category", "Description", "Amount"])
        df.to_csv(DATA_FILE, index=False)
        return df

df = load_data()

# 3. Left Sidebar: Monthly Budget & Quick Add Form
with st.sidebar:
    st.header("⚙️ Budget Settings")
    monthly_budget = st.number_input("Set Monthly Budget (₹)", min_value=500.0, value=5000.0, step=500.0)
    st.divider()

    st.header("➕ Add New Expense")
    with st.form("expense_form", clear_on_submit=True):
        exp_date = st.date_input("Date", date.today())
        category = st.selectbox(
            "Category",
            ["🍔 Food", "🚌 Transport", "📚 Books & Study", "🎬 Entertainment", "💡 Utilities", "🛍️ Shopping", "📦 Other"]
        )
        description = st.text_input("Description", placeholder="e.g., Canteen Lunch, Metro Card")
        amount = st.number_input("Amount (₹)", min_value=1.0, step=10.0)

        submitted = st.form_submit_button("Add Expense", use_container_width=True, type="primary")

        if submitted:
            if description.strip() == "":
                st.warning("Please enter a valid description!")
            else:
                new_row = pd.DataFrame([[str(exp_date), category, description.strip(), float(amount)]], columns=df.columns)
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(DATA_FILE, index=False)
                st.success(f"Added ₹{amount:,.2f}!")
                st.rerun()

# 4. Main Screen Header & Top KPI Cards
st.title("💳 Smart Personal Expense Tracker")
st.caption("Track your daily spending, edit entries directly, and analyze your budget with interactive charts.")

total_spent = df["Amount"].sum() if not df.empty else 0.0
remaining_budget = monthly_budget - total_spent
top_category = df.groupby("Category")["Amount"].sum().idxmax() if not df.empty else "None"

col1, col2, col3 = st.columns(3)
col1.metric("💸 Total Spent", f"₹{total_spent:,.2f}")
col2.metric("💰 Remaining Budget", f"₹{remaining_budget:,.2f}", delta=f"{remaining_budget:,.0f} left")
col3.metric("🔥 Top Category", top_category)

# Budget Progress Bar
st.subheader("📊 Monthly Budget Usage")
progress_ratio = min(total_spent / monthly_budget, 1.0) if monthly_budget > 0 else 0.0
st.progress(progress_ratio)
if total_spent > monthly_budget:
    st.error(f"⚠️ Alert: You have exceeded your monthly budget by ₹{total_spent - monthly_budget:,.2f}!")
else:
    st.info(f"You have used {(total_spent / monthly_budget) * 100:.1f}% of your ₹{monthly_budget:,.2f} budget.")

st.divider()

# 5. Interactive Tabs for Analytics, Direct Editing & Filtering
tab1, tab2, tab3 = st.tabs(["📊 Analytics & Charts", "📝 Edit & Delete Expenses", "🔍 Filter & Export"])

with tab1:
    if df.empty:
        st.info("No expenses added yet. Use the left sidebar to add your first expense!")
    else:
        cat_summary = df.groupby("Category")["Amount"].sum().reset_index().sort_values(by="Amount", ascending=False)
        
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.subheader("🍩 Spending Share (Donut Chart)")
            fig_pie = px.pie(cat_summary, values="Amount", names="Category", hole=0.45, color_discrete_sequence=px.colors.qualitative.Set2)
            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with chart_col2:
            st.subheader("📊 Category Comparison (Bar Chart)")
            fig_bar = px.bar(cat_summary, x="Category", y="Amount", color="Category", text_auto=".2s", color_discrete_sequence=px.colors.qualitative.Set2)
            fig_bar.update_layout(showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)

        st.subheader("📈 Daily Spending Trend")
        daily_summary = df.groupby("Date")["Amount"].sum().reset_index().sort_values(by="Date")
        fig_line = px.area(daily_summary, x="Date", y="Amount", markers=True, color_discrete_sequence=["#00B4D8"])
        st.plotly_chart(fig_line, use_container_width=True)

with tab2:
    st.subheader("Edit or Delete Any Entry Directly")
    st.caption("Double-click any cell to edit values, or select rows on the left and press Delete on your keyboard, then click Save Changes.")
    if df.empty:
        st.info("Your expense table is currently empty.")
    else:
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Amount": st.column_config.NumberColumn("Amount (₹)", min_value=0.0, format="₹%.2f"),
                "Category": st.column_config.SelectboxColumn(
                    "Category",
                    options=["🍔 Food", "🚌 Transport", "📚 Books & Study", "🎬 Entertainment", "💡 Utilities", "🛍️ Shopping", "📦 Other"]
                )
            }
        )
        if st.button("💾 Save Changes", type="primary"):
            edited_df.to_csv(DATA_FILE, index=False)
            st.success("All changes saved successfully!")
            st.rerun()

with tab3:
    st.subheader("Filter & Download Report")
    if df.empty:
        st.info("Add some expenses first to filter or export reports.")
    else:
        categories = ["All"] + list(df["Category"].unique())
        selected_cat = st.selectbox("Filter by Category", categories)
        filtered_df = df if selected_cat == "All" else df[df["Category"] == selected_cat]
        
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        
        csv_data = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Report as CSV",
            data=csv_data,
            file_name="expense_report.csv",
            mime="text/csv"
        )
        # 6. Developer Credit Footer & Sidebar Badge
with st.sidebar:
    st.divider()
    st.markdown("### 👨‍💻 Developer Info")
    st.info("**Created by:** Amish\n\n**Course:** BCA 2nd Year\n\n**Tech Stack:** Python, Streamlit, Pandas & Plotly")

st.divider()
st.caption("© 2026 Smart Personal Expense Tracker | Designed & Developed by **Amish singh** (BCA 2nd Year Project)")

import streamlit as st
import plotly.graph_objects as go
from model_loader import load_customer_data


def render():
    st.title("Customer Lookup")
    st.markdown("Search any customer by ID to see their full profile and recommended action.")

    df = load_customer_data()

    customer_id = st.number_input(
        "Enter Customer ID",
        min_value=int(df['CustomerID'].min()),
        max_value=int(df['CustomerID'].max()),
        value=int(df['CustomerID'].iloc[0]),
        step=1
    )

    customer = df[df['CustomerID'] == customer_id]

    if customer.empty:
        st.warning(f"Customer {customer_id} not found in the dataset.")
        return

    row = customer.iloc[0]

    st.divider()

    # --- Profile tiles ---
    st.subheader(f"Customer {int(row['CustomerID'])} — {row['Cluster_Name']}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("CLTV",        f"£{row['CLTV']:,.0f}")
    c2.metric("Churn risk",  f"{row['Churn_Probability']*100:.1f}%")
    c3.metric("Cluster",     row['Cluster_Name'])
    c4.metric("RFM Segment", row['Segment'])

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Behavioural metrics")
        st.markdown(f"- **Recency:** {int(row['Recency'])} days since last order")
        st.markdown(f"- **Frequency:** {int(row['Frequency'])} orders")
        st.markdown(f"- **Monetary:** £{row['Monetary']:,.2f} total spend")
        st.markdown(f"- **AOV:** £{row['AOV']:,.2f} average order")
        st.markdown(f"- **Unique products:** {int(row['UniqueProducts'])}")
        st.markdown(f"- **Customer lifespan:** {int(row['Lifespan'])} days")
        st.markdown(f"- **RFM score:** {int(row['RFM_Score'])} / 15")

    with col2:
        # RFM score gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=row['RFM_Score'],
            title={'text': "RFM Score (3–15)"},
            gauge={
                'axis': {'range': [3, 15]},
                'bar': {'color': '#3498db'},
                'steps': [
                    {'range': [3, 6],  'color': '#e74c3c'},
                    {'range': [6, 10], 'color': '#f39c12'},
                    {'range': [10, 15],'color': '#2ecc71'},
                ],
            }
        ))
        fig.update_layout(height=280, margin=dict(t=40, b=10, l=10, r=10))
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # --- Recommended action ---
    churn_risk = row['Churn_Risk']
    cluster    = row['Cluster_Name']

    actions = {
        ('High Value', 'Low'):    "🟢 **Protect.** Enrol in loyalty programme. Offer early product access.",
        ('High Value', 'Medium'): "🟡 **Monitor.** Send personalised retention offer within 14 days.",
        ('High Value', 'High'):   "🔴 **Rescue immediately.** Personal outreach within 7 days. Strong incentive.",
        ('Mid Value',  'Low'):    "🔵 **Nurture.** Upsell campaign to grow toward High Value.",
        ('Mid Value',  'Medium'): "🟡 **Re-engage.** Send limited-time offer email.",
        ('Mid Value',  'High'):   "🟠 **Win-back.** One campaign with discount. Archive if no response in 30 days.",
        ('Low Value',  'Low'):    "🔵 **Develop.** Include in broad campaigns only.",
        ('Low Value',  'Medium'): "⚪ **Low priority.** Batch re-engagement only.",
        ('Low Value',  'High'):   "⚫ **Monitor.** Minimal spend. One final email then archive.",
    }

    action = actions.get(
        (cluster, churn_risk),
        "ℹ️ Review manually — unusual combination."
    )
    st.subheader("Recommended action")
    st.info(action)
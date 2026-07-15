import streamlit as st
import sys
import os

# Add app directory to path so page imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pages import prediction, analytics, customer_lookup, model_insights


def load_css():
    css_path = os.path.join(os.path.dirname(__file__), 'style.css')
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_title="CLTV Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    load_css()

    # Sidebar navigation
    with st.sidebar:
        st.title("📊 CLTV Dashboard")
        st.markdown("---")

        page = st.radio(
            "Navigate to",
            options=[
                "🔮 Predict",
                "📈 Analytics",
                "🔍 Customer Lookup",
                "🧠 Model Insights"
            ],
            label_visibility="collapsed"
        )

        st.markdown("---")
        st.caption("Customer Lifetime Value Project")

    # Route to selected page
    if page == "🔮 Predict":
        prediction.render()
    elif page == "📈 Analytics":
        analytics.render()
    elif page == "🔍 Customer Lookup":
        customer_lookup.render()
    elif page == "🧠 Model Insights":
        model_insights.render()


if __name__ == "__main__":
    main()
import streamlit as st

st.set_page_config(page_title="Slide 2 - Reports", page_icon="📝", layout="wide")

st.title("📝 Slide 2: Data & Reports Workspace")
st.markdown("When you tell Jarvis to output long research or tables, it will be stored here.")

st.markdown("---")

# Mock layout for Data/Reports
st.subheader("Generated Report: US Market Analysis")
st.write("""
1. **Tech Sector:** Showing strong resilience in Q3.
2. **Energy Sector:** Fluctuating based on global oil prices.
3. **Healthcare:** Steady growth observed over the last 6 months.

*(In Step 2 and 3, this text will be generated live by the AI based on your text prompts!)*
""")
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Slide 2", layout="wide")

st.title("📊 Slide 2 Workspace")
st.markdown("---")

col_slide, col_chat = st.columns([2, 1], gap="large")

with col_slide:
    st.markdown("### Content")
    st.markdown(st.session_state.get("slide2_text", "Empty."))
    if st.session_state.get("slide2_chart") is not None:
        st.bar_chart(st.session_state.slide2_chart)

with col_chat:
    st.markdown("### Terminal")
    chat_box = st.container(height=400, border=True)
    with chat_box:
        for msg in st.session_state.get("messages", []):
            if msg["role"] != "system":
                with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Ask Jarvis..."):
    st.info("Please return to Home to enter new commands. This ensures graphs render perfectly.")

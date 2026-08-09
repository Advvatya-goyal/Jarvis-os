import streamlit as st
import pandas as pd
import json
import re
from groq import Groq

# --- Page Configuration ---
st.set_page_config(page_title="Jarvis Workspace", page_icon="✨", layout="wide", initial_sidebar_state="expanded")

# --- Initialize Groq Client ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- Clean Light Theme CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .stApp { background-color: #f8fafc; color: #0f172a; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e2e8f0; }
    h1, h2, h3 { color: #0f172a !important; font-weight: 700 !important; letter-spacing: -0.5px; }
    .stMarkdown p { color: #334155 !important; font-size: 15px; }
    div[data-testid="stVerticalBlock"] > div { background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; padding: 16px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05); }
    div[data-testid="stChatInput"] { background-color: #ffffff !important; border: 1.5px solid #cbd5e1 !important; border-radius: 12px !important; box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.05) !important; }
    div[data-testid="stChatInput"] textarea { color: #000000 !important; -webkit-text-fill-color: #000000 !important; font-size: 16px !important; font-weight: 500 !important; background-color: transparent !important; }
    .stButton > button { background-color: #2563eb; color: #ffffff !important; border: none; border-radius: 8px; padding: 0.5rem 1rem; font-weight: 600; transition: all 0.2s ease; }
    .stButton > button:hover { background-color: #1d4ed8; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25); }
    [data-testid="stSidebar"] .stButton > button { background-color: #f1f5f9; color: #0f172a !important; border: 1px solid #cbd5e1; }
    [data-testid="stSidebar"] .stButton > button:hover { background-color: #ef4444; color: #ffffff !important; border-color: #ef4444; }
    </style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "full_chat" 

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello. I am Jarvis, running on Groq. Ask me to compare data or show a graph, and I will generate it dynamically!"}
    ]

# Default empty data for graphs
if "chart_data" not in st.session_state:
    st.session_state.chart_data = pd.DataFrame()
if "metrics_data" not in st.session_state:
    st.session_state.metrics_data = pd.DataFrame()

def toggle_view():
    st.session_state.view_mode = "split" if st.session_state.view_mode == "full_chat" else "full_chat"

# --- Sidebar Controls ---
with st.sidebar:
    st.markdown("## ✨ Jarvis Network")
    st.markdown("---")
    st.caption("🟢 SYSTEM STATUS: ONLINE")
    st.write("Powered by ultra-fast Groq AI.")
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = [{"role": "assistant", "content": "Workspace memory cleared. How can I assist you today?"}]
        st.session_state.chart_data = pd.DataFrame()
        st.session_state.metrics_data = pd.DataFrame()
        st.session_state.view_mode = "full_chat"
        st.rerun()

# --- Main Header & Controls ---
col_head1, col_head2 = st.columns([4, 1])
with col_head1:
    st.title("Jarvis AI Terminal")
with col_head2:
    st.write("") 
    btn_text = "⛶ Open Analytics" if st.session_state.view_mode == "full_chat" else "🗖 Close Analytics"
    st.button(btn_text, on_click=toggle_view, use_container_width=True)

st.markdown("---")

# --- Dynamic Layout Engine ---
if st.session_state.view_mode == "split":
    chat_col, graph_col = st.columns([1.2, 1], gap="large")
else:
    chat_col = st.container()
    graph_col = None

# --- Chat Interface ---
with chat_col:
    chat_container = st.container(height=520, border=False) 
    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] != "system":
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

# --- Right Area: Dynamic Visualizations ---
if graph_col is not None:
    with graph_col:
        st.subheader("Data Analytics")
        tab1, tab2 = st.tabs(["Slide 1: Graph", "Slide 2: Metrics Table"])
        
        with tab1:
            st.caption("Dynamic Visualization based on prompt.")
            if not st.session_state.chart_data.empty:
                # Streamlit automatically turns this into a nice chart
                st.bar_chart(st.session_state.chart_data)
            else:
                st.info("Ask Jarvis to generate a chart (e.g., 'Show me a graph of smartphone sales').")
                
        with tab2:
            st.caption("Dynamic Data Table.")
            if not st.session_state.metrics_data.empty:
                st.dataframe(st.session_state.metrics_data, use_container_width=True, hide_index=True)
            else:
                st.info("No table data generated yet.")

# --- Groq Fallback Engine ---
def get_groq_response(messages):
    fallback_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
    last_error = None
    for model_name in fallback_models:
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.5, # Lower temperature for better JSON formatting
                max_tokens=2048
            )
            return completion.choices[0].message.content
        except Exception as e:
            last_error = str(e)
            continue
    raise Exception(f"All Groq models failed. Last error: {last_error}")

# --- Chat Input & AI Logic ---
if prompt := st.chat_input("Message Jarvis..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                # Highly specific prompt instructing the AI to create JSON data for charts
                system_instruction = """
                You are Jarvis. You are helpful and polite. 
                If the user asks for data, a chart, a graph, analytics, or a table, you MUST invent/provide the data in JSON format enclosed in <CHART> and </CHART> tags at the VERY END of your response.
                
                FORMAT EXACTLY LIKE THIS:
                <CHART>
                {
                  "chart_data": {"Item A": [10, 20, 30], "Item B": [15, 25, 35]},
                  "metrics_data": [{"Category": "Item A", "Status": "Growing", "Total": 60}, {"Category": "Item B", "Status": "Stable", "Total": 75}]
                }
                </CHART>
                Do not use markdown blocks inside the <CHART> tags. The chart_data should contain numerical arrays of equal length.
                """
                
                formatted_messages = [{"role": "system", "content": system_instruction}]
                
                for m in st.session_state.messages:
                    if m["role"] in ["user", "assistant"]:
                        formatted_messages.append({"role": m["role"], "content": m["content"]})

                # Call Groq
                raw_reply = get_groq_response(formatted_messages)
                
                # --- PARSE THE DYNAMIC DATA ---
                display_text = raw_reply
                chart_match = re.search(r"<CHART>(.*?)</CHART>", raw_reply, re.DOTALL)
                
                if chart_match:
                    try:
                        # Extract the JSON part
                        json_str = chart_match.group(1).strip()
                        data = json.loads(json_str)
                        
                        # Update the graphs dynamically
                        if "chart_data" in data:
                            st.session_state.chart_data = pd.DataFrame(data["chart_data"])
                        if "metrics_data" in data:
                            st.session_state.metrics_data = pd.DataFrame(data["metrics_data"])
                            
                        # Automatically pop open the analytics window!
                        st.session_state.view_mode = "split"
                        
                        # Remove the ugly JSON text from the user's view
                        display_text = re.sub(r"<CHART>.*?</CHART>", "", raw_reply, flags=re.DOTALL).strip()
                        
                    except Exception as e:
                        print("Failed to parse AI JSON:", e) # Fails silently for the user

                # Display the clean text to the user
                st.markdown(display_text)
                st.session_state.messages.append({"role": "assistant", "content": display_text})

            except Exception as e:
                error_msg = f"**System Error:** `{str(e)}`"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

    st.rerun()

import streamlit as st
import pandas as pd
import numpy as np
from google import genai

# --- Page Configuration ---
st.set_page_config(page_title="Jarvis Workspace", page_icon="✨", layout="wide", initial_sidebar_state="expanded")

# --- Initialize Gemini Client ---
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# --- Clean Light Theme CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Main Background & Text - Clean White Setup */
    .stApp { 
        background-color: #f8fafc; 
        color: #0f172a; 
        font-family: 'Inter', sans-serif;
    }
    
    /* Clean Light Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0;
    }

    /* Crisp High-Contrast Headers */
    h1, h2, h3 { 
        color: #0f172a !important; 
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    
    /* Paragraph & Message Text */
    .stMarkdown p {
        color: #334155 !important;
        font-size: 15px;
    }

    /* Sleek Cards/Containers */
    div[data-testid="stVerticalBlock"] > div { 
        background: #ffffff; 
        border-radius: 12px; 
        border: 1px solid #e2e8f0; 
        padding: 16px; 
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    /* --- FIX: Chat Input Box & Typed Text in Pure Black --- */
    div[data-testid="stChatInput"] { 
        background-color: #ffffff !important; 
        border: 1.5px solid #cbd5e1 !important; 
        border-radius: 12px !important; 
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.05) !important; 
    }
    
    /* Pure Black text while typing */
    div[data-testid="stChatInput"] textarea { 
        color: #000000 !important; 
        -webkit-text-fill-color: #000000 !important; 
        font-size: 16px !important; 
        font-weight: 500 !important;
        background-color: transparent !important; 
    }

    /* Modern Primary Buttons */
    .stButton > button { 
        background-color: #2563eb; 
        color: #ffffff !important; 
        border: none; 
        border-radius: 8px; 
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.2s ease; 
    }
    .stButton > button:hover { 
        background-color: #1d4ed8; 
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25); 
    }
    
    /* Sidebar Delete/Clear Button Styling */
    [data-testid="stSidebar"] .stButton > button {
        background-color: #f1f5f9;
        color: #0f172a !important;
        border: 1px solid #cbd5e1;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #ef4444;
        color: #ffffff !important;
        border-color: #ef4444;
    }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Controls ---
with st.sidebar:
    st.markdown("## ✨ Jarvis Network")
    st.markdown("---")
    st.caption("🟢 SYSTEM STATUS: ONLINE")
    st.write("Clean high-contrast workspace interface.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "Workspace memory cleared. How can I assist you today?"}
        ]
        st.rerun()

# --- Session State Initialization ---
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "full_chat" 

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello. I am Jarvis. How can I assist you today? (Tip: Mention **chart** or **analytics** to open split-screen mode)."}
    ]

def toggle_view():
    st.session_state.view_mode = "split" if st.session_state.view_mode == "full_chat" else "full_chat"

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
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

# --- Right Area: Visualizations ---
if graph_col is not None:
    with graph_col:
        st.subheader("Data Analytics")
        tab1, tab2 = st.tabs(["Visualization", "Metrics Table"])
        
        with tab1:
            st.caption("Real-time metric projections.")
            chart_data = pd.DataFrame(np.random.randn(20, 3), columns=['Alpha', 'Beta', 'Gamma'])
            st.area_chart(chart_data, color=["#2563eb", "#7c3aed", "#059669"])
            
        with tab2:
            st.caption("Live system status.")
            st.dataframe(pd.DataFrame({
                "Sector": ["Alpha (Tech)", "Beta (Defense)", "Gamma (Energy)"],
                "Status": ["Optimal", "Review Needed", "Stable"]
            }), use_container_width=True, hide_index=True)

# --- Chat Input & Gemini Logic ---
if prompt := st.chat_input("Message Jarvis..."):
    # Append User Prompt
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Trigger Split-Screen if analytics words are present
    if any(word in prompt.lower() for word in ["chart", "plot", "graph", "visual", "analytics", "data"]):
        st.session_state.view_mode = "split"

    # Render Immediately
    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate Response using standard Gemini Model
        with st.chat_message("assistant"):
            try:
                formatted_contents = []
                for m in st.session_state.messages:
                    role = "user" if m["role"] == "user" else "model"
                    formatted_contents.append({"role": role, "parts": [{"text": m["content"]}]})

                # Verified compatible model string for Google Gen AI SDK
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=formatted_contents
                )
                
                ai_reply = response.text
                st.markdown(ai_reply)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})

            except Exception as e:
                error_msg = f"**System Error:** `{str(e)}`"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

    st.rerun()

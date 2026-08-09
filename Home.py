import streamlit as st
import pandas as pd
import numpy as np
from google import genai

# --- Page Configuration ---
st.set_page_config(page_title="Jarvis Premium", page_icon="✨", layout="wide", initial_sidebar_state="expanded")

# --- Initialize Gemini Client ---
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# --- Premium UI Custom CSS ---
st.markdown("""
    <style>
    /* Import Premium Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');

    /* Main Background & Text - Sleek Slate Gradient */
    .stApp { 
        background: linear-gradient(135deg, #0f172a 0%, #020617 100%);
        color: #f8fafc; 
        font-family: 'Inter', sans-serif;
    }
    
    /* Clean Sidebar */
    [data-testid="stSidebar"] {
        background-color: #020617 !important;
        border-right: 1px solid #1e293b;
    }

    /* Premium Headers */
    h1, h2, h3 { 
        color: #f1f5f9 !important; 
        font-weight: 600 !important;
        letter-spacing: -0.5px;
    }
    
    /* Subtitles & Captions */
    .stMarkdown p {
        color: #cbd5e1 !important;
    }

    /* Glassmorphism Containers (Cards) */
    div[data-testid="stVerticalBlock"] > div { 
        background: rgba(30, 41, 59, 0.4); 
        border-radius: 12px; 
        border: 1px solid rgba(255, 255, 255, 0.05); 
        padding: 15px; 
        backdrop-filter: blur(10px);
    }
    
    /* --- FIX: Perfect High-Contrast Chat Input --- */
    div[data-testid="stChatInput"] { 
        background-color: #1e293b !important; 
        border: 1px solid #334155 !important; 
        border-radius: 12px !important; 
        box-shadow: 0px 8px 24px rgba(0, 0, 0, 0.2) !important; 
    }
    
    /* The text you type */
    div[data-testid="stChatInput"] textarea { 
        color: #ffffff !important; 
        -webkit-text-fill-color: #ffffff !important; 
        font-size: 16px !important; 
        background-color: transparent !important; 
    }

    /* Modern Premium Buttons */
    .stButton > button { 
        background-color: #0ea5e9; 
        color: #ffffff !important; 
        border: none; 
        border-radius: 8px; 
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s ease; 
    }
    .stButton > button:hover { 
        background-color: #0284c7; 
        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.4); 
        transform: translateY(-2px);
    }
    
    /* Secondary/Sidebar Button Styling */
    [data-testid="stSidebar"] .stButton > button {
        background-color: #1e293b;
        border: 1px solid #334155;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #ef4444; /* Red hover for delete/clear */
        border-color: #ef4444;
    }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Controls ---
with st.sidebar:
    st.markdown("## ✨ Jarvis Workspace")
    st.markdown("---")
    st.caption("🟢 SYSTEM STATUS: OPTIMAL")
    st.write("Welcome to your intelligent workspace. Seamlessly chat, analyze data, and generate insights.")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "Workspace cleared. How can I assist you today?"}
        ]
        st.rerun()

# --- Session State Initialization ---
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "full_chat" 

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello. I am Jarvis. How can I assist you today? (Tip: Ask me to show a **chart** to see the split-screen)."}
    ]

def toggle_view():
    st.session_state.view_mode = "split" if st.session_state.view_mode == "full_chat" else "full_chat"

# --- Main Header & Controls ---
col_head1, col_head2 = st.columns([4, 1])
with col_head1:
    st.title("Jarvis AI Terminal")
with col_head2:
    st.write("") # Spacing alignment
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
    chat_container = st.container(height=550, border=False) 
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

# --- Right Area: Visualizations ---
if graph_col is not None:
    with graph_col:
        st.subheader("Data Analytics")
        tab1, tab2 = st.tabs(["Visualization", "Raw Data"])
        
        with tab1:
            st.caption("Real-time metric projections.")
            # Softer, premium colors for the chart
            chart_data = pd.DataFrame(np.random.randn(20, 3), columns=['Alpha', 'Beta', 'Gamma'])
            st.area_chart(chart_data, color=["#0ea5e9", "#8b5cf6", "#10b981"])
            
        with tab2:
            st.caption("Live system metrics.")
            st.dataframe(pd.DataFrame({
                "Sector": ["Alpha (Tech)", "Beta (Defense)", "Gamma (Energy)"],
                "Status": ["Optimal", "Review Needed", "Stable"]
            }), use_container_width=True, hide_index=True)

# --- Chat Input & Gemini Logic ---
if prompt := st.chat_input("Message Jarvis..."):
    # Append User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Check for Split-Screen Triggers
    if any(word in prompt.lower() for word in ["chart", "plot", "graph", "visual", "analytics", "data"]):
        st.session_state.view_mode = "split"

    # Display User Message
    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate AI Response
        with st.chat_message("assistant"):
            try:
                # Format conversation history for Gemini API
                formatted_contents = []
                for m in st.session_state.messages:
                    role = "user" if m["role"] == "user" else "model"
                    formatted_contents.append({"role": role, "parts": [{"text": m["content"]}]})

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

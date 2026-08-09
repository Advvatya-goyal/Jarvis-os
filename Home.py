import streamlit as st
import pandas as pd
import numpy as np
from openai import OpenAI

# --- Page Configuration ---
st.set_page_config(page_title="Jarvis OS", page_icon="🧿", layout="wide", initial_sidebar_state="expanded")

# --- Initialize OpenAI Client ---
# Note: Removed the trailing space from secrets key name to prevent KeyError
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- Futuristic Custom CSS ---
st.markdown("""
    <style>
    /* Main Background & Text */
    .stApp {
        background-color: #0a0e17;
        color: #e0e6ed;
    }
    
    /* Glowing Headers */
    h1, h2, h3 {
        color: #00F0FF !important;
        text-shadow: 0px 0px 10px rgba(0, 240, 255, 0.5);
        font-family: 'Courier New', Courier, monospace;
    }
    
    /* Glassmorphism Containers */
    div[data-testid="stVerticalBlock"] > div {
        background: rgba(15, 22, 36, 0.6);
        border-radius: 10px;
        border: 1px solid rgba(0, 240, 255, 0.1);
        padding: 10px;
    }
    
    /* Chat Input Visibility and Size */
    div[data-testid="stChatInput"] {
        background-color: #0a0e17 !important;
        border: 1px solid #00F0FF !important;
        border-radius: 15px !important;
        box-shadow: 0px 0px 15px rgba(0, 240, 255, 0.2) !important;
    }
    
    div[data-testid="stChatInput"] textarea {
        color: #00F0FF !important; 
        -webkit-text-fill-color: #00F0FF !important;
        font-size: 20px !important;
        font-weight: bold !important;
        background-color: transparent !important;
    }
    
    /* Futuristic Buttons */
    .stButton > button {
        background: transparent;
        color: #00F0FF;
        border: 1px solid #00F0FF;
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background: #00F0FF;
        color: #0a0e17;
        box-shadow: 0px 0px 15px #00F0FF;
    }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Controls ---
with st.sidebar:
    st.markdown("## 🌐 Jarvis Network")
    st.markdown("---")
    st.caption("SYSTEM STATUS: ONLINE 🟢")
    
    # Button to clear history and reset memory
    if st.button("🗑️ Clear Conversation Memory", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "System Memory Flushed. Jarvis at your service. Ask me a question, or tell me to generate a **chart**."}
        ]
        st.rerun()

# --- Session State Initialization ---
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "full_chat" 

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "System Online. Jarvis at your service. Ask me a question, or tell me to generate a **chart**."}
    ]

def toggle_view():
    if st.session_state.view_mode == "full_chat":
        st.session_state.view_mode = "split"
    else:
        st.session_state.view_mode = "full_chat"

# --- Main Header & Controls ---
col_head1, col_head2 = st.columns([4, 1])
with col_head1:
    st.title("🧿 JARVIS CORE // Main Terminal")
with col_head2:
    btn_text = "⛶ Enter Split-Screen" if st.session_state.view_mode == "full_chat" else "🗖 Full Chat Mode"
    st.button(btn_text, on_click=toggle_view, use_container_width=True)

st.markdown("---")

# --- Dynamic Layout Engine ---
if st.session_state.view_mode == "split":
    chat_col, graph_col = st.columns([1.5, 1])
else:
    chat_col = st.container()
    graph_col = None

# --- Left / Main Area: Chat Interface ---
with chat_col:
    st.subheader("💬 Comm-Link")
    chat_container = st.container(height=500) 
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

# --- Right Area: Visualizations (Split mode only) ---
if graph_col is not None:
    with graph_col:
        st.subheader("📊 Visual Projection")
        tab1, tab2 = st.tabs(["Data Chart", "Raw Analysis"])
        
        with tab1:
            st.caption("Auto-generated visual interface.")
            chart_data = pd.DataFrame(np.random.randn(20, 3), columns=['Tech', 'Defense', 'Energy'])
            st.area_chart(chart_data, color=["#00F0FF", "#FF0055", "#00FF66"])
            
        with tab2:
            st.caption("Live system metrics.")
            st.dataframe(pd.DataFrame({
                "Sector": ["Tech", "Defense", "Energy"],
                "Status": ["Optimal", "Elevated", "Stable"]
            }), use_container_width=True)

# --- Chat Input & AI Response Generation ---
if prompt := st.chat_input("Enter command for Jarvis..."):
    # 1. Append user prompt to session state history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 2. Check for visualization trigger words
    trigger_words = ["chart", "plot", "graph", "visual", "draw"]
    if any(word in prompt.lower() for word in trigger_words):
        st.session_state.view_mode = "split"

    # 3. Display user message immediately in chat container
    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)

        # 4. Generate response using OpenAI API with full conversation memory
        with st.chat_message("assistant"):
            try:
                # Prepare message history for the LLM
                api_messages = [
                    {"role": "system", "content": "You are Jarvis, an advanced futuristic AI system assistant. Speak clearly, concisely, and stay in character."}
                ]
                
                # Append all existing history so the AI remembers context
                for m in st.session_state.messages:
                    api_messages.append({"role": m["role"], "content": m["content"]})

                # Stream or generate completion
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=api_messages
                )
                
                ai_reply = response.choices[0].message.content
                st.markdown(ai_reply)
                
                # Save assistant response to session state history
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})

            except Exception as e:
                error_msg = f"**System Error:** Failed to process query. Details: `{str(e)}`"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

    st.rerun()

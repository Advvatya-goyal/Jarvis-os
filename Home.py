import streamlit as st
import pandas as pd
import numpy as np
from groq import Groq

# --- Page Configuration ---
st.set_page_config(page_title="Jarvis Workspace", page_icon="✨", layout="wide", initial_sidebar_state="expanded")

# --- Initialize Groq Client ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- Clean Light Theme CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    .stApp { 
        background-color: #f8fafc; 
        color: #0f172a; 
        font-family: 'Inter', sans-serif;
    }
    
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0;
    }

    h1, h2, h3 { 
        color: #0f172a !important; 
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    
    .stMarkdown p {
        color: #334155 !important;
        font-size: 15px;
    }

    div[data-testid="stVerticalBlock"] > div { 
        background: #ffffff; 
        border-radius: 12px; 
        border: 1px solid #e2e8f0; 
        padding: 16px; 
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    div[data-testid="stChatInput"] { 
        background-color: #ffffff !important; 
        border: 1.5px solid #cbd5e1 !important; 
        border-radius: 12px !important; 
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.05) !important; 
    }
    
    div[data-testid="stChatInput"] textarea { 
        color: #000000 !important; 
        -webkit-text-fill-color: #000000 !important; 
        font-size: 16px !important; 
        font-weight: 500 !important;
        background-color: transparent !important; 
    }

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
    st.write("Powered by ultra-fast Groq AI models.")
    
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
        {"role": "assistant", "content": "Hello. I am Jarvis, running on Groq. How can I assist you today? (Tip: Mention **chart** or **analytics** to open split-screen mode)."}
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


# --- Groq Fallback Engine ---
def get_groq_response(messages):
    """
    Tries multiple Groq models. If the first one fails or hits a rate limit, 
    it automatically falls back to the next one.
    """
    fallback_models = [
        "llama-3.3-70b-versatile", # Primary: Smartest
        "llama-3.1-8b-instant",    # Backup 1: Very fast and reliable
        "mixtral-8x7b-32768"       # Backup 2: Great fallback alternative
    ]
    
    last_error = None
    for model_name in fallback_models:
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=1024
            )
            return completion.choices[0].message.content
        except Exception as e:
            last_error = str(e)
            # Silently catch the error and try the next model in the list
            continue
            
    # If all models fail, raise the final error
    raise Exception(f"All Groq models failed. Last error: {last_error}")


# --- Chat Input & AI Logic ---
if prompt := st.chat_input("Message Jarvis..."):
    # Append user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Check for analytics trigger words
    if any(word in prompt.lower() for word in ["chart", "plot", "graph", "visual", "analytics", "data"]):
        st.session_state.view_mode = "split"

    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                # Format messages for Groq API (including a system prompt for persona)
                formatted_messages = [
                    {"role": "system", "content": "You are Jarvis, a highly intelligent and polite AI assistant. Keep responses helpful and concise."}
                ]
                
                # Add conversation history
                for m in st.session_state.messages:
                    if m["role"] in ["user", "assistant"]:
                        formatted_messages.append({"role": m["role"], "content": m["content"]})

                # Call the Fallback Engine
                ai_reply = get_groq_response(formatted_messages)
                
                st.markdown(ai_reply)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})

            except Exception as e:
                error_msg = f"**System Error:** `{str(e)}`"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

    st.rerun()

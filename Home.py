import streamlit as st
import pandas as pd
import json
import re
from groq import Groq

# --- Page Configuration ---
st.set_page_config(page_title="Jarvis Workspace", page_icon="✨", layout="wide", initial_sidebar_state="expanded")

# --- Initialize Groq Client ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- Custom Styling ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .stApp { background-color: #f8fafc; color: #0f172a; font-family: 'Inter', sans-serif; }
    .slide-container { background: #ffffff; border-radius: 8px; padding: 20px; border: 1px solid #e2e8f0; min-height: 50vh; overflow-y: auto; }
    </style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if "view_mode" not in st.session_state: st.session_state.view_mode = "full_chat" 
if "messages" not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "System Online. Tell me what to put on Home, Slide 1, and Slide 2."}]
if "slide1_text" not in st.session_state: st.session_state.slide1_text = "*Slide 1 is empty.*"
if "slide2_text" not in st.session_state: st.session_state.slide2_text = "*Slide 2 is empty.*"
if "slide1_chart" not in st.session_state: st.session_state.slide1_chart = None
if "slide2_chart" not in st.session_state: st.session_state.slide2_chart = None

def toggle_view():
    st.session_state.view_mode = "split" if st.session_state.view_mode == "full_chat" else "full_chat"

# --- Sidebar Controls ---
with st.sidebar:
    st.markdown("## ✨ Jarvis Network")
    st.caption("🟢 SYSTEM STATUS: ONLINE")
    if st.button("🗑️ Clear Workspace", use_container_width=True):
        st.session_state.messages = [{"role": "assistant", "content": "Workspace cleared."}]
        st.session_state.slide1_text = "*Slide 1 is empty.*"
        st.session_state.slide2_text = "*Slide 2 is empty.*"
        st.session_state.slide1_chart = None
        st.session_state.slide2_chart = None
        st.session_state.view_mode = "full_chat"
        st.rerun()

# --- Main Header ---
col1, col2 = st.columns([4, 1])
with col1: st.title("Jarvis AI Terminal")
with col2:
    st.write("") 
    st.button("⛶ Toggle Split Screen", on_click=toggle_view, use_container_width=True)
st.markdown("---")

# --- Dynamic Layout Engine ---
if st.session_state.view_mode == "split":
    chat_col, slide_col = st.columns([1, 1.5], gap="large")
else:
    chat_col = st.container()
    slide_col = None

# --- Chat Interface (Left Side) ---
with chat_col:
    chat_container = st.container(height=600, border=False) 
    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] != "system":
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

# --- Right Area: Dynamic Slides/Tabs ---
if slide_col is not None:
    with slide_col:
        tab1, tab2 = st.tabs(["Slide 1", "Slide 2"])
        
        with tab1:
            st.markdown('<div class="slide-container">', unsafe_allow_html=True)
            st.markdown(st.session_state.slide1_text)
            if st.session_state.slide1_chart is not None:
                st.bar_chart(st.session_state.slide1_chart)
            st.markdown('</div>', unsafe_allow_html=True)
                
        with tab2:
            st.markdown('<div class="slide-container">', unsafe_allow_html=True)
            st.markdown(st.session_state.slide2_text)
            if st.session_state.slide2_chart is not None:
                st.bar_chart(st.session_state.slide2_chart)
            st.markdown('</div>', unsafe_allow_html=True)

# --- Groq Logic & Parsing ---
def process_prompt(prompt):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with chat_container:
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            system_instruction = """
            You are Jarvis, managing a 3-part UI: Home, Slide 1, and Slide 2.
            You MUST follow these strict XML tags to place content:
            
            <HOME> Put your conversational reply and main text here. </HOME>
            <SLIDE1> Put text, code, or markdown meant for Slide 1 here. </SLIDE1>
            <SLIDE2> Put text, code, or markdown meant for Slide 2 here. </SLIDE2>
            
            If asked for a GRAPH/CHART in Slide 1, output pure JSON data here:
            <CHART1>{"Item A": 10, "Item B": 20}</CHART1>
            If asked for a GRAPH in Slide 2, use:
            <CHART2>{"Item C": 30, "Item D": 40}</CHART2>
            
            Example rule: If user asks for movie names on Home, graph on Slide 1, and actors on Slide 2, you MUST separate them perfectly into <HOME>, <SLIDE1>+<CHART1>, and <SLIDE2>.
            """
            
            msgs = [{"role": "system", "content": system_instruction}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            
            try:
                response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=msgs, temperature=0.3)
                raw_text = response.choices[0].message.content
                
                # --- PARSING LOGIC ---
                cleaned_text = raw_text
                
                s1 = re.search(r"<SLIDE1>(.*?)</SLIDE1>", raw_text, re.DOTALL)
                if s1:
                    st.session_state.slide1_text = s1.group(1).strip()
                    cleaned_text = cleaned_text.replace(s1.group(0), "")
                    st.session_state.view_mode = "split"
                
                s2 = re.search(r"<SLIDE2>(.*?)</SLIDE2>", raw_text, re.DOTALL)
                if s2:
                    st.session_state.slide2_text = s2.group(1).strip()
                    cleaned_text = cleaned_text.replace(s2.group(0), "")
                    st.session_state.view_mode = "split"
                    
                c1 = re.search(r"<CHART1>(.*?)</CHART1>", raw_text, re.DOTALL)
                if c1:
                    try:
                        st.session_state.slide1_chart = pd.Series(json.loads(c1.group(1)))
                        cleaned_text = cleaned_text.replace(c1.group(0), "")
                        st.session_state.view_mode = "split"
                    except: pass
                    
                c2 = re.search(r"<CHART2>(.*?)</CHART2>", raw_text, re.DOTALL)
                if c2:
                    try:
                        st.session_state.slide2_chart = pd.Series(json.loads(c2.group(1)))
                        cleaned_text = cleaned_text.replace(c2.group(0), "")
                        st.session_state.view_mode = "split"
                    except: pass

                h_match = re.search(r"<HOME>(.*?)</HOME>", cleaned_text, re.DOTALL)
                home_text = h_match.group(1).strip() if h_match else cleaned_text.strip()
                if not home_text: home_text = "Workspace updated as requested."

                st.markdown(home_text)
                st.session_state.messages.append({"role": "assistant", "content": home_text})

            except Exception as e:
                st.error(f"Error: {str(e)}")
    st.rerun()

if prompt := st.chat_input("Message Jarvis..."):
    process_prompt(prompt)

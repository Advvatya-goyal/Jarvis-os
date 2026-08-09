import streamlit as st
import re
from groq import Groq

# --- Page Configuration ---
st.set_page_config(page_title="Jarvis Workspace", page_icon="✨", layout="wide", initial_sidebar_state="expanded")

# --- Initialize Groq Client ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- Clean UI CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .stApp { background-color: #f8fafc; color: #0f172a; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e2e8f0; }
    h1, h2, h3 { color: #0f172a !important; font-weight: 700 !important; letter-spacing: -0.5px; }
    div[data-testid="stChatInput"] { background-color: #ffffff !important; border: 1.5px solid #cbd5e1 !important; border-radius: 12px !important; }
    div[data-testid="stChatInput"] textarea { color: #000000 !important; font-size: 16px !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { padding-top: 10px; padding-bottom: 10px; border-radius: 4px 4px 0 0; }
    .slide-container { background: #ffffff; border-radius: 8px; padding: 20px; border: 1px solid #e2e8f0; min-height: 60vh; overflow-y: auto; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "full_chat" 

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello. I am Jarvis. I can now open tabs just like a browser! Ask me a question and say **'Show this in Slide 1'** or **'Put the code in Slide 2'**."}
    ]

# Store content for the slides/tabs
if "slide_1_content" not in st.session_state:
    st.session_state.slide_1_content = "*Slide 1 is currently empty. Ask Jarvis to put something here.*"
if "slide_2_content" not in st.session_state:
    st.session_state.slide_2_content = "*Slide 2 is currently empty. Ask Jarvis to put something here.*"

def toggle_view():
    st.session_state.view_mode = "split" if st.session_state.view_mode == "full_chat" else "full_chat"

# --- Sidebar Controls ---
with st.sidebar:
    st.markdown("## ✨ Jarvis Network")
    st.markdown("---")
    st.caption("🟢 SYSTEM STATUS: ONLINE")
    st.write("Dynamic Workspace Tabs Active.")
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️ Clear Workspace", use_container_width=True):
        st.session_state.messages = [{"role": "assistant", "content": "Workspace cleared."}]
        st.session_state.slide_1_content = "*Slide 1 is currently empty.*"
        st.session_state.slide_2_content = "*Slide 2 is currently empty.*"
        st.session_state.view_mode = "full_chat"
        st.rerun()

# --- Main Header & Controls ---
col_head1, col_head2 = st.columns([4, 1])
with col_head1:
    st.title("Jarvis AI Terminal")
with col_head2:
    st.write("") 
    btn_text = "⛶ Open Split Screen" if st.session_state.view_mode == "full_chat" else "🗖 Close Split Screen"
    st.button(btn_text, on_click=toggle_view, use_container_width=True)

st.markdown("---")

# --- Dynamic Layout Engine ---
if st.session_state.view_mode == "split":
    chat_col, slide_col = st.columns([1.2, 1.5], gap="large") # Adjust width ratio here
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
        st.subheader("Workspace Tabs")
        tab1, tab2 = st.tabs(["Slide 1", "Slide 2"])
        
        with tab1:
            st.markdown('<div class="slide-container">', unsafe_allow_html=True)
            st.markdown(st.session_state.slide_1_content)
            st.markdown('</div>', unsafe_allow_html=True)
                
        with tab2:
            st.markdown('<div class="slide-container">', unsafe_allow_html=True)
            st.markdown(st.session_state.slide_2_content)
            st.markdown('</div>', unsafe_allow_html=True)

# --- Groq Engine ---
def get_groq_response(messages):
    fallback_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
    for model_name in fallback_models:
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=3000
            )
            return completion.choices[0].message.content
        except Exception:
            continue
    return "Error: Could not connect to Groq AI."

# --- Chat Input & AI Logic ---
if prompt := st.chat_input("Message Jarvis..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                # The "Brain" instruction: Tells AI how to use the slides
                system_instruction = """
                You are Jarvis, an advanced AI with a split-screen workspace interface.
                The user has a chat on the left, and two browser-like tabs on the right called 'Slide 1' and 'Slide 2'.
                
                If the user explicitly asks you to show, put, or display something in Slide 1, you MUST wrap that specific content inside <SLIDE1> and </SLIDE1> tags.
                If they ask for Slide 2, wrap the content in <SLIDE2> and </SLIDE2> tags.
                
                Whatever is inside those tags will physically render in the user's right-side panels. 
                You can put explanations, bullet points, Markdown, Python code, HTML, etc., inside the tags.
                
                Example:
                User: Write a python script for a calculator and put it in Slide 1.
                Jarvis: Sure, I have placed the calculator code in Slide 1.
                <SLIDE1>
                Here is the code you requested:
                ```python
                def add(a, b): return a + b
                ```
                </SLIDE1>
                """
                
                formatted_messages = [{"role": "system", "content": system_instruction}]
                
                for m in st.session_state.messages:
                    if m["role"] in ["user", "assistant"]:
                        formatted_messages.append({"role": m["role"], "content": m["content"]})

                # Call Groq
                raw_reply = get_groq_response(formatted_messages)
                
                # --- PARSE THE DYNAMIC CONTENT ---
                display_text = raw_reply
                
                # Check for Slide 1 content
                slide1_match = re.search(r"<SLIDE1>(.*?)</SLIDE1>", raw_reply, re.DOTALL)
                if slide1_match:
                    st.session_state.slide_1_content = slide1_match.group(1).strip()
                    st.session_state.view_mode = "split" # Auto-open split screen
                    display_text = display_text.replace(slide1_match.group(0), "").strip()
                
                # Check for Slide 2 content
                slide2_match = re.search(r"<SLIDE2>(.*?)</SLIDE2>", raw_reply, re.DOTALL)
                if slide2_match:
                    st.session_state.slide_2_content = slide2_match.group(1).strip()
                    st.session_state.view_mode = "split" # Auto-open split screen
                    display_text = display_text.replace(slide2_match.group(0), "").strip()

                # If display text is empty after removing tags, add a default message
                if not display_text:
                    display_text = "I have updated the slides as requested."

                # Display the conversational text in chat
                st.markdown(display_text)
                st.session_state.messages.append({"role": "assistant", "content": display_text})

            except Exception as e:
                st.error(f"Error: {str(e)}")

    st.rerun()

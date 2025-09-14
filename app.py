# pip install openai streamlit python-dotenv
import os
import time
import openai
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
st.set_page_config(page_title="AI Debate Bot", page_icon="🤖")

# Load CSS Styling
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Title and description
st.title("🧠 AI Debate Bot")
st.write("Enter a topic below and let two AI bots argue it out!")

# Generate Argument
def generate_argument(role, topic, prev_response):
    prompt = f"""
    You are a skilled debater on the {'PRO' if role == 'pro' else 'CON'} side of the topic: "{topic}". 
    {'Your opponent said: ' + prev_response if prev_response else ''} 
    Reply with a strong, persuasive, and respectful argument (max 1 sentence).
    """
    response = openai.chat.completions.create(
        model="gpt-4o-mini", 
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def generate_debate(topic, rounds):
    prev = None
    for i in range(rounds):
        st.markdown(f"### 🔁 Round {i + 1}")

        pro = generate_argument("pro", topic, prev)
        st.session_state.chat_history.append(("pro", pro))
        type_writer(pro, role="pro") 
        prev = pro

        con = generate_argument("con", topic, prev)
        st.session_state.chat_history.append(("con", con))
        type_writer(con, role="con")  
        prev = con

def type_writer(text, role, delay=0.05):
    placeholder = st.empty()
    full_text = ""

    if role == 'pro':
        background_color = '#e0ffe0' 
        alignment = 'flex-start' 
        avatar = "🟢🤖"
    else:
        background_color = '#ffe0e0' 
        alignment = 'flex-end'
        avatar = "🔴🦊"

    chat_container = f'<div class="chat-row" style="display: flex; justify-content: {alignment};">'
    chat_bubble = f'<div class="avatar">{avatar}</div><div class="chat-bubble" style="background-color:{background_color};">'
    
    for word in text.split():
        full_text += word + " "
        placeholder.markdown(
            f'{chat_container}{chat_bubble}{full_text}</div></div>',
            unsafe_allow_html=True
        )
        time.sleep(delay)
    return full_text.strip()

def initialize_session_state():
    st.session_state.setdefault("debate_history", [])
    st.session_state.setdefault("debate_started", False)
    st.session_state.setdefault("chat_history", [])
    st.session_state.setdefault("ui_interacted", False)

def display_chat_history(chat_placeholder):
    with chat_placeholder.container():
        for role, text in st.session_state.chat_history:
            if role == 'pro':
                st.markdown(f'<div class="chat-row" style="display: flex; justify-content: flex-start;">'
                            f'<div class="avatar">🟢🤖</div><div class="chat-bubble" style="background-color:#e0ffe0;">{text}</div></div>', 
                            unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-row" style="display: flex; justify-content: flex-end;">'
                            f'<div class="avatar">🔴🦊</div><div class="chat-bubble" style="background-color:#ffe0e0;">{text}</div></div>', 
                            unsafe_allow_html=True)

def show_vote_options(vote_placeholder):
    winner = vote_placeholder.radio("🏁 Who won the debate?", ["🟢 PRO", "🔴 CON"], index=None)
    
    if winner:
        st.success(f"🎉 You voted: {winner}")

def show_download_button():
    debate_text = "\n\n".join([f"PRO: {text}" if role == 'pro' else f"CON: {text}" 
                                for role, text in st.session_state.chat_history])
    st.download_button("📄 Download Debate (TXT)", debate_text, file_name="debate.txt")

def reset_debate_if_topic_changes(topic):
    if topic != st.session_state.get("last_topic", ""):
        st.session_state.debate_started = False
        st.session_state.debate_history = []
        st.session_state.chat_history = []
        st.session_state.last_topic = topic
        st.session_state.ui_interacted = False

def main():
    initialize_session_state()

    # Get user input
    topic = st.text_input("🎯 Debate Topic", "Gen AI is important topic for student.")
    rounds = st.slider("🌀 Number of Debate Rounds", 1, 5, 2)

    # Reset debet
    reset_debate_if_topic_changes(topic)

    if st.button("🗣️ Start Debate") and topic and not st.session_state.debate_started:
        st.session_state.debate_started = True
        generate_debate(topic, rounds)

    # UI interaction handling
    chat_placeholder = st.empty()
    vote_placeholder = st.empty()

    if st.session_state.debate_started:
        show_vote_options(vote_placeholder)

        if st.session_state.ui_interacted:
            display_chat_history(chat_placeholder)
        st.session_state.ui_interacted = True

        # Debate download button
        show_download_button()
    
    st.write("Created with ❤️ by Ameen YouTube🔔 : Coder Ameen")

if __name__ == "__main__":
    # streamlit run app.py
    main()
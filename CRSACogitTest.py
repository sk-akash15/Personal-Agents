import streamlit as st
import google.generativeai as genai
import json
import os
from fpdf import FPDF
from datetime import datetime

# === CONFIG ===
genai.configure(api_key="AIzaSyA4hVbpZeQL0-VoqUj6tPlj92py8lCS7II")  # Replace with actual key
llm = genai.GenerativeModel("gemini-1.5-pro")

# === Constants ===
HISTORY_FILE = "chat_sessions.json"

# === CSS Styling
st.set_page_config(page_title="CogitX CPRS", layout="wide")
st.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            background-color: #d6b4fc !important;
            color: black !important;
        }
        .stSidebar .stButton>button,
        .stSidebar .stDownloadButton>button {
            background-color: #ee82ee !important;
            color: black !important;
            border-radius: 6px;
        }
        .stApp {
            background-color: #000000;
            color: white;
            font-family: 'Poppins', sans-serif;
        }
        .stChatMessage {
            background-color: #1a1a1a;
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 10px;
        }
        .stTextInput>div>input {
            background-color: #1e1e1e;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# === Utilities
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_session_to_history():
    history = load_history()
    if st.session_state.chat_history:
        history.append({
            "id": st.session_state.session_id,
            "messages": st.session_state.chat_history
        })
    history = history[-5:]
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def export_conversation_as_pdf(messages):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for msg in messages:
        pdf.multi_cell(0, 10, f"You: {msg['user']}")
        pdf.multi_cell(0, 10, f"Assistant: {msg['assistant']}")
        pdf.ln(5)
    pdf_path = "session_chat.pdf"
    pdf.output(pdf_path)
    return pdf_path

# === Session State Setup
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "session_id" not in st.session_state:
    st.session_state.session_id = datetime.now().strftime("%Y%m%d%H%M%S")

if "chat_session" not in st.session_state:
    st.session_state.chat_session = llm.start_chat(history=[
        {"role": "user", "parts": msg["user"]} if i % 2 == 0 else {"role": "model", "parts": msg["assistant"]}
        for i, msg in enumerate(st.session_state.chat_history)
    ])

# === Sidebar
with st.sidebar:
    st.title("🧠 CPRS Cogit")

    if st.button("🔄 New Session"):
        save_session_to_history()
        st.session_state.chat_history = []
        st.session_state.session_id = datetime.now().strftime("%Y%m%d%H%M%S")
        st.session_state.chat_session = llm.start_chat()
        st.rerun()

    if st.button("🕓 Show History"):
        for session in load_history()[-5:][::-1]:
            with st.expander(f"🗂 {session['id']}"):
                for msg in session['messages']:
                    st.markdown(f"**👤 You:** {msg['user']}")
                    st.markdown(f"**🤖 Assistant:** {msg['assistant']}")

    st.markdown("---")
    if st.session_state.chat_history:
        json_str = json.dumps(st.session_state.chat_history, indent=2)
        st.download_button(
            label="💾 Save Current Chat",
            data=json_str,
            file_name="current_session.json",
            mime="application/json"
        )


# === Main Title & Subheader
st.title("📊 Know Your Prospect!")
st.subheader("Co-thinker for smarter outreach and quicker research that can help you with quick briefs, call prep and current news about your prospect")

# === Initial Prompt
system_prompt = """# Role and Objective
You are a Sales + Customer Research Assistant designed to help sales professionals and startup founders understand prospective customers quickly and clearly. Your job is to interactively gather minimal inputs and generate actionable profiles, company summaries, recent news, AI maturity insights, and financial information—fast, sharp, and with swagger.

# Instructions
- Maintain a tone that’s **casual, consultative, and smartly corporate**—think “sales-savvy strategist with a LinkedIn addiction.”
- Keep the interaction **lightweight**: only ask for essential info. If the user gives just a company name or job title, run with it.
- Wait for user input before each major step, but never bog them down with a questionnaire vibe.
- Simulate or summarize **real-world information** such as:
  - Company size, revenue estimates, and funding
  - Recent company news and strategic shifts
  - Product offerings and positioning
  - AI maturity and relevant use cases
  - Key customer challenges or needs
- Always generate output in a mix of:
  - **Narrative summaries** (1–3 short paragraphs)
  - **Clean, clear tables** for quick scanning
  - **Concise bullet points** for key takeaways
- Support recurring prompts like:
  - “Give me a quick brief on [company]”
  - “Help me prep for a call with [prospect]”
  - “Give me current news and AI maturity for [company]”
- Add optional flair (e.g., insights, a strategic suggestion, or a fun closer) to make it feel like a teammate, not a tool.
- Avoid sounding robotic, overly verbose, or too “analyst” in tone. Aim for speed + clarity + vibe.

# Reasoning Steps / Workflow
1. Greet the user in a crisp, upbeat tone. Ask what company or contact they want to look into.
2. If the user only gives a name, begin research-style simulation with smart assumptions. If they give more context (industry, region, product fit), tailor accordingly.
3. Deliver a structured response including:
   - High-level narrative summary of the company
   - Snapshot table with size, revenue, funding, headcount, HQ, etc.
   - Bullet list of AI maturity, recent news, and potential needs
4. Ask if the user wants more depth (e.g., exec team, org structure, product analysis, or objections handling).
5. End with a consultative call-prep tip or insight, casually phrased.

# Output Format
Each output should include:
- **Narrative summary** (2–3 short paragraphs, easy to skim)
- **Snapshot table**:
  | Metric | Value |
  |--------|-------|
  | HQ | ... |
  | Revenue | ... |
  | Headcount | ... |
  | Funding | ... |
- **Bullet list** of:
  - Recent news and moves
  - AI maturity and pain points
  - Strategic opportunities or red flags
- Optionally: a **“One-liner to use in your call”** or **call prep note** with swagger

# Examples
**User**: Give me a quick brief on SynthoTech AI

**Assistant**:
Alright, here’s the 60-second download on SynthoTech AI 👇

SynthoTech AI is a fast-growing Dutch startup in synthetic data. They're riding the GenAI hype with a niche B2B product targeted at enterprise compliance teams. They recently raised a $20M Series A and are aggressively hiring in Germany and the Nordics. Expect a tech-forward but risk-averse buyer persona.

| Metric | Value |
|--------|-------|
| HQ | Amsterdam, NL |
| Revenue | ~$8M (est) |
| Headcount | 55 |
| Funding | $24M (Series A) |

- **Recent News**: Closed Series A (Jan 2025), announced Azure integration.
- **AI Maturity**: Very high – core product is AI-based; CTO speaks at industry events.
- **Pain Points**: Scaling sales ops, differentiation in crowded space, enterprise onboarding friction.

💡 **Call Tip**: Mention regulatory frameworks—they’ll bite. Ask how they’re navigating AI compliance in France.""" 

# === Initial Assistant Message
if len(st.session_state.chat_history) == 0:
    st.chat_message("assistant").markdown("👋 Who are you researching today? Company, role, or region?")

# === Chat Input + Contextual Memory
user_input = st.chat_input("Enter company name, title, or sales question...")
if user_input:
    st.chat_message("user").markdown(user_input)

    full_prompt = user_input if st.session_state.chat_history else f"{system_prompt}\n\nUser Query: {user_input}"
    response = st.session_state.chat_session.send_message(full_prompt)

    st.chat_message("assistant").markdown(response.text + "\n\n💬 Want to dive deeper?")

    st.session_state.chat_history.append({
        "user": user_input,
        "assistant": response.text
    })

import streamlit as st
import google.generativeai as genai
import json
import os
from fpdf import FPDF

# ✅ Configure your Gemini API key
genai.configure(api_key="AIzaSyA4hVbpZeQL0-VoqUj6tPlj92py8lCS7II")

# ✅ Initialize Gemini Pro 1.5
llm = genai.GenerativeModel("gemini-1.5-pro")
chat = llm.start_chat()

# ✅ System behavior instructions (core)
system_prompt = """

# Role and Objective
You are a hilariously witty and quirky Personal Travel Assistant. Your mission is to help users plan unforgettable trips by asking smart, relevant questions and delivering crystal-clear travel recommendations, itineraries, and rough budgets. You specialize in weekend city breaks, honeymoons, solo backpacking adventures, couple escapes, family vacations, and office getaways—anywhere in the world.

# Instructions
- Maintain a **funny, quirky, and clever** tone at all times. Think "sarcastic travel blogger meets personal concierge."
- Always wait for user input before proceeding to the next planning stage—**no jumping ahead**.
- Support **global destinations** and adapt your advice based on what users tell you.
- When possible, base suggestions on popular sources like Google Maps and Skyscanner. If live data isn’t available, give plausible general advice.
- Always present results in **conversational form AND tables** (avoid bullet points).
- Provide **rough budget estimates** using the user’s local currency. Clarify that prices are approximate.
- Be curious! Ask the right follow-up questions to refine travel plans: interests, vibe, budget, travel dates, group type, etc.
- Include options and comparisons when appropriate (e.g., two itinerary routes, budget vs. splurge).
- If users are vague, be charmingly nosy to get more details.
- Provide responses keeping in context the previous conversation.
- Always present 3 itinerary options after receiving all the inputs from the user.
- Offer to be a decision assitant - compare the itinerary options if the user seems to be confused. 
- Translate the user query into English if the user input's in any other language, and respond back in the user-native language.


# Reasoning Steps / Workflow
1. Greet the user with humor and ask what kind of trip they’re planning.
2. Gather details step-by-step:
   - Type of trip (weekend, honeymoon, etc.)
   - Destination (or help pick one)
   - Dates and duration
   - Number of travelers and group type
   - Interests (food, adventure, museums, vibes, etc.)
   - Budget
3. Based on their answers, suggest:
   - Destinations (if undecided)
   - Travel logistics (flights, transport)
   - Lodging options
   - Sample itinerary (day-by-day)
   - Rough budget breakdown (in table)
4. Ask if they want to tweak or refine anything.
5. End with a humorous sign-off or bonus tip.

# Output Format
Always include:
- A **chatty explanation** ("Okay, here’s your budget bonanza breakdown, hold onto your flip-flops…")
- A **clean table** summarizing:
   - Itemized itinerary (per day or section)
   - Budget estimate by category (flights, hotel, food, activities, etc.)
   - Optional: comparison tables (e.g. budget vs. luxury)

# Examples
**User**: I want to plan a honeymoon in Italy for 10 days.

**Assistant**:
Ooh la la, amore in the land of pasta and passion! 🍝💋  
Before I book your Vespa and matching sunhats, tell me:
- When are you thinking of going?
- Are you more of a "sip wine in Tuscany" or "take selfies at the Colosseum" couple?
- And what's the vibe—luxury, mid-range, or "we just spent it all on the wedding"?

(Once info is in, return an itinerary + budget table with a cheeky outro.)



"""


# ✅ UI Styling
st.set_page_config(page_title="✈️ Trip Assistant", layout="centered")

st.markdown("""
    <style>
        body {
            background-color: #0b1c2c;
            color: white;
            font-family: 'Poppins', sans-serif;
        }
        .css-18e3th9 {
            background-color: #0b1c2c;
        }
        .stButton>button {
            background-color: #2f9e44 !important;
            color: white !important;
            border-radius: 6px;
        }
        .stDownloadButton>button {
            background-color: #2f9e44 !important;
            color: white !important;
        }
        .stTextInput>div>input {
            background-color: #13293d;
            color: white;
        }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;500&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# ✅ Reset chat state on app launch
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ✅ Header
st.title("🌍 Personal Travel Assistant")
col1, col2 = st.columns([1, 1])

# ✅ Session Control
with col1:
    if st.button("🔄 New Session"):
        st.session_state.chat_history = []
        st.rerun()

with col2:
    if st.session_state.chat_history:
        def export_last_response_as_pdf(text):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font("Arial", size=12)
            for line in text.split('\n'):
                pdf.multi_cell(0, 10, line)
            pdf_path = "last_response.pdf"
            pdf.output(pdf_path)
            return pdf_path

        if st.button("📄 Export Last Response as PDF"):
            last_response = st.session_state.chat_history[-1]["assistant"]
            pdf_file = export_last_response_as_pdf(last_response)
            with open(pdf_file, "rb") as f:
                st.download_button("⬇️ Download PDF", f, file_name="travel_plan.pdf", mime="application/pdf")

# ✅ Display chat history
for entry in st.session_state.chat_history:
    st.chat_message("user").markdown(entry["user"])
    st.chat_message("assistant").markdown(entry["assistant"])

# ✅ Initial Greeting
if len(st.session_state.chat_history) == 0:
    st.chat_message("assistant").markdown("🌴 Hey there! Where are we off to today?")

# ✅ Chat Input
user_input = st.chat_input("Type your travel question or destination...")
if user_input:
    st.chat_message("user").markdown(user_input)

    if len(st.session_state.chat_history) == 0:
        full_prompt = f"{system_prompt}\n\nUser Query: {user_input}"
    else:
        full_prompt = user_input

    response = chat.send_message(full_prompt)
    assistant_reply = f"{response.text}\n\n🧭 Anything else you'd like help with?"

    st.chat_message("assistant").markdown(assistant_reply)
    st.session_state.chat_history.append({
        "user": user_input,
        "assistant": response.text
    })





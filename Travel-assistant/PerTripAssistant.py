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
You are a Personal Travel Assistant chatbot with expert-level knowledge of global travel and tourism. Your primary goal is to help users plan and enjoy their trips by providing accurate, up-to-date, and personalized travel advice. You should:

1. Ask clarifying questions, one by one, to understand the user’s preferences, needs, and constraints (example: destination, budget, travel dates, interests, group size).

2. Suggest destinations, itineraries, and activities after gathering all the input provided by the user, highlighting unique experiences, must-see attractions, and local culture.

3. Provide practical information such as visa requirements, safety tips, best times to visit, transportation options, accommodation recommendations, and packing tips.

4. Recommend best websites to book flights, hotels, tours, and activities.

5. Share insider tips and lesser-known recommendations to enhance the travel experience.

Communicate in a friendly, engaging, and professional tone. Be positive, helpful, and enthusiastic about travel. Adapt your responses to the user’s knowledge level and travel experience, providing more detail or simplifying explanations as needed. Stay up-to-date with global travel trends, restrictions, and safety advisories. Always prioritize the user’s preferences and safety. If you are unsure about something, recommend consulting official sources or local authorities.

Example User Request:
“I want to plan a 10-day trip to Japan in April. I love food, culture, and nature. Can you help me with an itinerary?”

Example Assistant Response:
“Absolutely! April is a beautiful time to visit Japan, especially for cherry blossoms. Based on your interests in food, culture, and nature, I recommend starting in Tokyo for its vibrant food scene, then heading to Kyoto for temples and traditional culture, and finishing in Hakone or the Japanese Alps for stunning natural scenery. Would you like a detailed day-by-day itinerary or suggestions for each city?”

Additional guidelines:
1. Translate the user query into English if the user input's in any other language.
2. Generate the output in a very strucutred format, keep the responses very succinct throught the conversation. 
3. Do no overwhelm the user with long and complex responses. 
4. If the user wants a nicely curated itinerary, generate a simple table accordingly.
4. Keep the language super friendly, funny and quirky. 
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
st.title("🌍 Your Travel Assistant")
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




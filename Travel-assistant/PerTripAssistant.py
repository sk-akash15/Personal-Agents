# streamlit_app.py
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

# ✅ System behavior instructions (included only once)
system_prompt = """
You are a Personal Travel Assistant chatbot with expert-level knowledge of global travel and tourism. Your primary goal is to help users plan and enjoy their trips by providing accurate, up-to-date, and personalized travel advice. You should:

Ask clarifying questions to understand the user’s preferences, needs, and constraints (e.g., destination, budget, travel dates, interests, group size).

Suggest destinations, itineraries, and activities based on user input, highlighting unique experiences, must-see attractions, and local culture.

Provide practical information such as visa requirements, safety tips, best times to visit, transportation options, accommodation recommendations, and packing tips.

Offer booking assistance for flights, hotels, tours, and activities, or direct users to trusted platforms.

Share insider tips and lesser-known recommendations to enhance the travel experience.

Communicate in a friendly, engaging, and professional tone. Be positive, helpful, and enthusiastic about travel.

Adapt your responses to the user’s knowledge level and travel experience, providing more detail or simplifying explanations as needed.

Stay up-to-date with global travel trends, restrictions, and safety advisories.

Always prioritize the user’s preferences and safety. If you are unsure about something, recommend consulting official sources or local authorities.

Example User Request:
“I want to plan a 10-day trip to Japan in April. I love food, culture, and nature. Can you help me with an itinerary?”

Example Assistant Response:
“Absolutely! April is a beautiful time to visit Japan, especially for cherry blossoms. Based on your interests in food, culture, and nature, I recommend starting in Tokyo for its vibrant food scene, then heading to Kyoto for temples and traditional culture, and finishing in Hakone or the Japanese Alps for stunning natural scenery. Would you like a detailed day-by-day itinerary or suggestions for each city?”

Additional guidelines:
1. Translate the user query into English if the user input's in any other language.
2. Generate the output in a very strucutred format. 
3. If the user wants a nicely curated itinerary and generate a table accordingly.
4. Keep the language super friendly, funny and quirky. 
"""

# Load or initialize chat history
HISTORY_FILE = "chat_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

history = load_history()

st.set_page_config(page_title="One place to plan your trips", layout="centered")
st.title("Trip Assistant")
col1, col2 = st.columns([1, 1])

with col1:
    if st.button("🔄 Reset Chat"):
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        st.rerun()

with col2:
    if history:
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
            last_response = history[-1]["assistant"]
            pdf_file = export_last_response_as_pdf(last_response)
            with open(pdf_file, "rb") as f:
                st.download_button("⬇️ Download PDF", f, file_name="recipe.pdf", mime="application/pdf")


# Display history
for entry in history:
    st.chat_message("user").markdown(entry["user"])
    st.chat_message("assistant").markdown(entry["assistant"])

# Initial assistant greeting
if len(history) == 0:
    st.chat_message("assistant").markdown("👋 Where do you want to travel?")

# User input
user_input = st.chat_input("Enter your message")
if user_input:
    st.chat_message("user").markdown(user_input)

    if len(history) == 0:
        full_prompt = f"{system_prompt}\n\nUser Query: {user_input}"
    else:
        full_prompt = user_input

    response = chat.send_message(full_prompt)
    follow_up = "Do you want to ask anything more?"
    st.chat_message("assistant").markdown(f"{response.text}\n\n{follow_up}")

    history.append({"user": user_input, "assistant": response.text})
    save_history(history)

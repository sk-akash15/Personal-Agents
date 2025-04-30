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
You are an expert chef who has mastered Indian cuisines and understands all Indian languages. 
You are now serving as a recipe and ingredients curator.

Your tasks:
1. Translate the user query into English if needed.
2. Generate a recipe for one person that includes:
   - Mandatory items: macro ingredients (>50g or 200ml) with quantities. Use 'edible oil' if oil is mentioned. Replace 'all-purpose flour' with 'flour'.
   - Optional items: micro ingredients with quantities.
3. Respond only in plain English text.
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

st.set_page_config(page_title="Personal Recipe Assist", layout="centered")
st.title("🧑‍🍳 Personal Recipe Assistant")
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
    st.chat_message("assistant").markdown("👋 What would you like to cook today?")

# User input
user_input = st.chat_input("Enter your message")
if user_input:
    st.chat_message("user").markdown(user_input)

    if len(history) == 0:
        full_prompt = f"{system_prompt}\n\nUser Query: {user_input}"
    else:
        full_prompt = user_input

    response = chat.send_message(full_prompt)
    follow_up = "🧑‍🍳 Do you want to ask anything more?"
    st.chat_message("assistant").markdown(f"{response.text}\n\n{follow_up}")

    history.append({"user": user_input, "assistant": response.text})
    save_history(history)

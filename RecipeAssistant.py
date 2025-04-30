
import requests
import json
import time
import numpy as np
import html
from bs4 import BeautifulSoup

import google.generativeai as genai

# Set your API key
genai.configure(api_key="AIzaSyA4hVbpZeQL0-VoqUj6tPlj92py8lCS7II")

# Initialize the model (Gemini Pro)
llm = genai.GenerativeModel("gemini-1.5-pro")


# System behavior embedded into the prompt
system_prompt = """
You are an expert chef who has mastered Indian cuisines and understands all Indian languages. 
You are now serving as an expert recipe and ingredients curator.

Your tasks are:
1. Translate the user query into English if needed.
2. Generate a recipe for one person that includes:
   - Mandatory items: macro ingredients (>50g or 200ml) with quantities. Use 'edible oil' if oil is mentioned. Replace 'all-purpose flour' with 'flour'.
   - Optional items: micro ingredients with quantities.
3. Respond in plain English text only.
"""

# ✅ Start a chat session with Gemini
chat = llm.start_chat()

# 👋 Initial assistant greeting
print("\n🤖 RecipeAssist: What would you like to cook today?")
first_user_input = input("👤 You: ")

# 🔁 Send system prompt + first query in one combined message
initial_message = f"{system_prompt}\n\nUser Query: {first_user_input}"
response = chat.send_message(initial_message)
print("\n🤖 RecipeAssist:", response.text)

# 🔁 Multi-turn chat loop
while True:
    user_input = input("\n👤 You: ")
    if user_input.lower() in ["exit", "quit"]:
        print("🔚 Ending chat. Have a delicious day! 👋")
        break
    response = chat.send_message(user_input)
    print("\n🤖 RecipeAssist:", response.text)


# Anything below is single turn only
# User query
#query = "give me the recipe for coconut rice"

# Combine system prompt and user message into one string
#full_prompt = f"{system_prompt}\n\nUser Query: {query}"

# Generate the response one time
#response = llm.generate_content(full_prompt)

# Chat like turns - multi turn
#chat = llm.start_chat()
#response = chat.send_message(full_prompt)

# Print the result
#print(response.text)
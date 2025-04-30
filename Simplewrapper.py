import google.generativeai as genai

# Set your API key
genai.configure(api_key="AIzaSyA4hVbpZeQL0-VoqUj6tPlj92py8lCS7II")

# Initialize the model (Gemini Pro)
model = genai.GenerativeModel("gemini-1.5-pro")

# Generate a response
response = model.generate_content("Explain quantum physics in simple terms.")

# Print the result
print(response.text)


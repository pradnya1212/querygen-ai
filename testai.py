from google import genai

client = genai.Client(api_key="AIzaSyBV6BlguVL4Uzmd3W55O6FgE3FYncdVuGA")

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Say hello"
)

print(response.text)
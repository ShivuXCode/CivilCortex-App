import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()

try:
    llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0.1)
    print("3.6-flash: ", llm.invoke("Hello").content)
except Exception as e:
    print(f"Error 3.6-flash: {e}")

try:
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.1)
    print("2.5-pro: ", llm.invoke("Hello").content)
except Exception as e:
    print(f"Error 2.5-pro: {e}")

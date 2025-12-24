import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
import PyPDF2

from groq import Groq

load_dotenv()

CONSTITUTION_PATH = os.path.join(os.path.dirname(__file__), "..", "Documentation", "Constitution_of_India_2024_EnglishVersion.pdf")

_constitution_text = None

def get_constitution_text():
    global _constitution_text
    if _constitution_text is None:
        if os.path.exists(CONSTITUTION_PATH):
            try:
                with open(CONSTITUTION_PATH, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    # Extracting first 50 pages for faster loading and to stay safe with context
                    num_pages = min(50, len(reader.pages))
                    for i in range(num_pages):
                        page_text = reader.pages[i].extract_text()
                        if page_text:
                            text += page_text + "\n"
                    _constitution_text = text
            except Exception as e:
                print(f"Error reading constitution: {e}")
                _constitution_text = ""
        else:
            print(f"Constitution not found at {CONSTITUTION_PATH}")
            _constitution_text = ""
    return _constitution_text

def chat_with_groq_stream(message, history=None, system_instruction=""):
    api_key = os.environ.get("GROQ_KEY")
    if not api_key:
        yield "Error: Groq API key (GROQ_KEY) not found in environment."
        return

    client = Groq(api_key=api_key)
    
    messages = [{"role": "system", "content": system_instruction}]
    if history:
        for msg in history:
            role = "user" if msg.get('role') == 'user' else "assistant"
            messages.append({"role": role, "content": msg.get('content', '')})
    
    messages.append({"role": "user", "content": message})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            stream=True,
        )
        for chunk in completion:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        yield f"Error calling Groq API: {str(e)}"

def chat_with_gemini_stream(message, history=None):
    api_key = os.environ.get("GAISTUDIO_KEY")
    
    keywords = ["legal", "right", "law", "constitution", "article", "illegal", "allowed", "permit", "my right", "is it legal"]
    is_legal_query = any(keyword in message.lower() for keyword in keywords)
    
    system_instruction = """
    You are LegalClauseAI, a helpful legal assistant for Indian citizens. 
    Your goal is to simplify legal concepts and provide guidance.
    If the user asks about their rights or whether something is legal, you MUST refer to the Indian Constitution.
    Always provide the specific Article number if applicable.
    Keep your answers concise, professional, and easy to understand for a layperson.
    """
    
    if is_legal_query:
        constitution_context = get_constitution_text()
        if constitution_context:
            system_instruction += f"\n\nREFERENCE MATERIAL (Constitution of India):\n{constitution_context[:15000]}"

    # Try Gemini first
    if api_key:
        try:
            client = genai.Client(api_key=api_key)
            contents = []
            if history:
                for msg in history:
                    role = "user" if msg.get('role') == 'user' else "model"
                    contents.append(types.Content(
                        role=role,
                        parts=[types.Part(text=msg.get('content', ''))]
                    ))
            
            contents.append(types.Content(
                role="user",
                parts=[types.Part(text=message)]
            ))

            # Using gemini-2.0-flash-exp
            for chunk in client.models.generate_content_stream(
                model="gemini-2.0-flash-exp",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction
                )
            ):
                if chunk.candidates:
                    part = chunk.candidates[0].content.parts[0]
                    if part.text:
                        yield part.text
            return # Success, exit
        except Exception as e:
            print(f"Gemini failed, falling back to Groq: {e}")
            # If Gemini fails, we fall through to Groq
    
    # Fallback to Groq
    yield from chat_with_groq_stream(message, history, system_instruction)

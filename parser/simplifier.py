import os
from google import genai
from google.genai import types
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

# Prevent 'proxies' error in Gemini SDK
for var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
    os.environ.pop(var, None)

def simplify_text_stream(text):
    """
    Simplify legal text using Google Gemini with Groq fallback.
    """
    gemini_key = os.environ.get("GAISTUDIO_KEY")
    groq_key = os.environ.get("GROQ_KEY")

    # Truncate text to stay within token limits (approx 30,000 characters)
    # This avoids the "Request too large" error on Groq's free tier.
    truncated_text = text[:30000]

    prompt = f"""
You are an expert legal simplifier. Your task is to summarize the provided legal document into a short, easy-to-read guide for a layperson.

**Goal:** Reduce the document to its absolute essentials. The user will NOT read a long output.

**Structure the output exactly as follows:**

# [Title of the Document/Scheme]

**🔍 What is this?**
[1-2 sentences explaining the core purpose.]

**👥 Who is it for?**
*   [Bullet points of eligibility or target audience]

**✅ Key Benefits / Obligations**
*   [Bullet points of what the user gets or must do]

**❌ Exclusions / Risks**
*   [Bullet points of who is excluded or what to watch out for]

**📝 How to Proceed**
*   [Simple steps to apply or comply]

**📅 Important Dates**
*   [Deadlines or timelines, if any]

**Rules:**
1.  **Be extremely concise.** Use short sentences.
2.  **No filler.** Do not say "The document states that...". Just state the fact.
3.  **No legal jargon.** Use plain English (e.g., use "agreement" instead of "indenture").
4.  **Skip procedural minutiae** (like internal office procedures) unless it affects the user directly.
5.  **Maximum Length:** Keep the total output under 400 words if possible, unless the document is massive and complex.

Legal Text to Simplify:
{truncated_text}
"""

    # Try Gemini first
    if gemini_key:
        try:
            client = genai.Client(api_key=gemini_key)
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part(text=prompt)]
                )
            ]

            for chunk in client.models.generate_content_stream(
                model="gemini-1.5-flash",
                contents=contents,
            ):
                if chunk.candidates:
                    candidate = chunk.candidates[0]
                    if candidate.content and candidate.content.parts:
                        part = candidate.content.parts[0]
                        if part.text:
                            yield part.text
            return # Success
        except Exception as e:
            print(f"Gemini simplification failed, falling back to Groq: {e}")

    # Fallback to Groq
    if groq_key:
        try:
            client = Groq(api_key=groq_key)
            # Using llama-3.1-8b-instant for fallback as it has higher rate limits
            # but llama-3.3-70b-versatile is also fine if we truncate.
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                stream=True,
            )
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"Error calling Groq API: {str(e)}"
    else:
        yield "Error: No API keys found for Gemini or Groq."

def simplify_text(text):
    """
    Wrapper for non-streaming usage.
    """
    return "".join(simplify_text_stream(text))


if __name__ == "__main__":
    sample_text = """
    THIS AGREEMENT is made between the parties herein and sets forth the obligations and liabilities.
    """
    simplified = simplify_text(sample_text)
    print("Simplified Text:\n", simplified)
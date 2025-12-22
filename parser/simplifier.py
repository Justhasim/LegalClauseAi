import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
load_dotenv()

def simplify_text_stream(text):
    """
    Simplify legal text using Google Gemini, yielding chunks of text.
    """
    client = genai.Client(
        api_key=os.environ.get("GAISTUDIO_KEY")
    )

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
{text}
"""

    contents = [
        types.Content(
            role="user",
            parts=[types.Part(text=prompt)]
        )
    ]

    # Generate content stream
    for chunk in client.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents=contents,
    ):
        if chunk.candidates is None:
            continue
        candidate = chunk.candidates[0]
        if candidate.content and candidate.content.parts:
            part = candidate.content.parts[0]
            if part.text:
                yield part.text

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
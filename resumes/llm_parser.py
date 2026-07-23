import json
from django.conf import settings
from groq import Groq

client = Groq(api_key=settings.GROQ_API_KEY)

PARSE_PROMPT = """You are given raw text extracted from a resume PDF/DOCX.
Extract the following fields and return ONLY valid JSON, no preamble, no markdown fences, no explanation:

{
  "name": string or null,
  "email": string or null,
  "phone": string or null,
  "skills": [list of strings],
  "education": [{"degree": string, "institution": string, "year": string}],
  "projects": [{"title": string, "description": string, "tech_stack": [strings]}],
  "experience_years": number or null
}

Resume text:
---
RESUME_TEXT_PLACEHOLDER
---"""


def parse_resume_text(resume_text):
    """
    Sends extracted resume text to Groq's LLM to structure it into JSON.
    Uses llama-3.1-8b-instant — fast, free, and accurate enough for
    resume field extraction. Returns a Python dict.
    Raises ValueError if the model response isn't valid JSON.
    """
    prompt = PARSE_PROMPT.replace('RESUME_TEXT_PLACEHOLDER', resume_text[:6000])

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
        temperature=0.1,  # low temperature = more deterministic JSON output
    )

    raw_text = response.choices[0].message.content.strip()

    # Defensive cleanup in case the model wraps output in ```json fences
    if raw_text.startswith('```'):
        lines = raw_text.split('\n')
        lines = [l for l in lines if not l.strip().startswith('```')]
        raw_text = '\n'.join(lines).strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM did not return valid JSON: {e}\nRaw: {raw_text[:500]}")
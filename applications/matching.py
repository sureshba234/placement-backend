import json
from django.conf import settings
from groq import Groq

client = Groq(api_key=settings.GROQ_API_KEY)

MATCH_PROMPT = """You are a resume-JD matching expert.

Given a resume and a job description, return ONLY valid JSON with no preamble or markdown:

{
  "match_score": number between 0 and 100,
  "missing_skills": [list of skills in the JD but missing from the resume]
}

Resume:
---
RESUME_PLACEHOLDER
---

Job Description:
---
JD_PLACEHOLDER
---"""


def compute_match(resume_text: str, jd_text: str) -> dict:
    """
    Uses Groq LLM to compute a match score and missing skills
    between a resume and job description.
    Returns dict with match_score (float) and missing_skills (list).
    """
    prompt = MATCH_PROMPT\
        .replace('RESUME_PLACEHOLDER', resume_text[:4000])\
        .replace('JD_PLACEHOLDER', jd_text[:2000])

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.1,
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown fences if present
    if raw.startswith('```'):
        lines = raw.split('\n')
        lines = [l for l in lines if not l.strip().startswith('```')]
        raw = '\n'.join(lines).strip()

    try:
        result = json.loads(raw)
        return {
            'match_score': float(result.get('match_score', 0)),
            'missing_skills': result.get('missing_skills', []),
        }
    except json.JSONDecodeError as e:
        raise ValueError(f"Groq did not return valid JSON: {e}\nRaw: {raw[:300]}")

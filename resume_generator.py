"""
Resume Generator - Format resume text into professional structured JSON
"""

import json
from typing import Dict, Optional, Any
from openai import OpenAI


class ResumeGenerator:
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def _chat_completion_json(self, system_prompt: str, user_prompt: str, max_tokens: int = 3000) -> Any:
        """Helper to call the Chat Completions API and parse JSON content."""
        try:
            print(f"[DEBUG] Calling OpenAI API with model: {self.model}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_completion_tokens=max_tokens,
                response_format={"type": "json_object"},
            )
            print(f"[DEBUG] API call successful. Response received.")

            # Defensive extraction of the message content
            content = None
            try:
                choice0 = response.choices[0]
            except Exception:
                choice0 = None

            if choice0 is not None:
                # If the choice is a mapping (dict-like), use dict access
                if isinstance(choice0, dict):
                    content = choice0.get('message', {}).get('content')
                else:
                    # Try attribute access for different client shapes
                    msg = getattr(choice0, 'message', None)
                    if msg is not None:
                        if isinstance(msg, dict):
                            content = msg.get('content')
                        else:
                            content = getattr(msg, 'content', None)

            if content is None or not isinstance(content, str) or not content.strip():
                # Include a short summary of the raw response to help debugging
                raw_summary = None
                try:
                    # Limit length to avoid huge dumps
                    raw_summary = str(response)[:1000]
                except Exception:
                    raw_summary = '<unavailable>'
                raise ValueError(f"OpenAI API returned empty or non-text content. Raw response summary: {raw_summary}")

            # Attempt to parse JSON and provide clearer error messages on failure
            text = content.strip()
            try:
                return json.loads(text)
            except json.JSONDecodeError as jde:
                preview = text[:1000].replace('\n', '\\n')
                raise ValueError(f"Failed to parse JSON from model response: {str(jde)}. Response preview: {preview}")
        except Exception as e:
            print(f"[ERROR] OpenAI API call failed: {str(e)}")
            raise
    
    def format_resume(self, resume_text: str) -> Dict:
        """Format and structure resume text into professional JSON format."""
        
        user_prompt = f"""Parse the following resume text and classify each existing section without altering the wording.

**RESUME TEXT:**
{resume_text}

**INSTRUCTIONS:**
- Identify sections such as contact info, professional summary, skills, experience, education, certifications, and projects based on headings or content.
- NEVER rewrite, rephrase, summarise, improve, or modify any word. Copy every field value VERBATIM from the input.
- Preserve the exact wording, capitalisation, punctuation, and numbers from the original text.
- Preserve all bullets and formatting from the input within each section's value.
- If a section is missing, the corresponding JSON field should be empty or omitted.
- Return only valid JSON.

**REQUIRED JSON STRUCTURE:**
{{
  "contact_info": {{
    "name": "Full Name",
    "email": "email@example.com",
    "phone": "phone number",
    "location": "City, State/Country",
    "linkedin": "linkedin url (optional)",
    "website": "personal website (optional)"
  }},
  "professional_summary": "professional summary text exactly as input",
  "skills": {{
    "technical_skills": ["skill1", "skill2"],
    "tools_technologies": ["tool1", "tool2"],
    "methodologies": ["method1", "method2"]
  }},
  "experience": [
    {{
      "job_title": "Job Title text from resume",
      "company": "Company text from resume",
      "location": "Location text from resume",
      "dates": "Dates text from resume",
      "achievements": ["Each bullet or line under the experience entry, unchanged"]
    }}
  ],
  "education": [
    {{
      "degree": "Degree text",
      "institution": "Institution text",
      "location": "Location text",
      "graduation_date": "Graduation date text",
      "gpa": "GPA text"
    }}
  ],
  "certifications": ["Full certification lines as they appear"],
  "projects": [
    {{
      "project_name": "Project name text",
      "description": "Description text",
      "technologies": ["tech list if present"],
      "bullets": ["Each bullet line unchanged"]
    }}
  ]
}}"""
        
        resume_data = self._chat_completion_json(
            system_prompt="You are a resume parser. Your only job is to read the resume text and assign each piece of text to the correct JSON field WITHOUT changing, rewording, summarising, or improving anything. Copy text verbatim. Return only valid JSON.",
            user_prompt=user_prompt,
            max_tokens=3000,
        )
        
        return resume_data
    
    def validate_resume_data(self, resume_data: Dict) -> bool:
        """Validate that resume data has required fields."""
        required_fields = ['professional_summary', 'contact_info', 'experience', 'skills', 'education']
        for field in required_fields:
            if field not in resume_data:
                return False
        if 'name' not in resume_data.get('contact_info', {}):
            return False
        if not isinstance(resume_data.get('experience'), list) or len(resume_data['experience']) == 0:
            return False
        return True

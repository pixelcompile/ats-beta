"""
Resume Generator - Single LLM call to optimize resume and optional cover letter/Q&A generation.
"""

import json
from typing import Dict, Optional, Any
from openai import OpenAI
from prompt_config import SYSTEM_PROMPT, get_optimization_prompt, get_cover_letter_and_qa_prompt


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
    
    def generate_optimized_resume(
        self,
        resume_text: str,
        job_description: str,
        company_info: Optional[str] = None,
        company_name: Optional[str] = None,
        target_role: Optional[str] = None,
    ) -> Dict:

        user_prompt = get_optimization_prompt(
            resume_text=resume_text,
            job_description=job_description,
            company_info=company_info or "",
            company_name=company_name or "",
            target_role=target_role or "",
        )
        
        resume_data = self._chat_completion_json(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            max_tokens=3000,
        )

        # Persist targeting metadata so downstream logic (e.g., file naming)
        # can use the explicit company/role even if they are not reflected in
        # the structured experience data yet.
        target_block = {}
        if company_name:
            target_block["company_name"] = company_name
        if target_role:
            target_block["role_title"] = target_role
        if target_block:
            resume_data.setdefault("target", {}).update(target_block)

        return resume_data
    
    def format_resume(self, resume_text: str) -> Dict:
        """Format and structure resume text into professional JSON format without optimization."""
        
        user_prompt = f"""Parse and structure the following resume text into a clean, professional JSON format.

**RESUME TEXT:**
{resume_text}

**INSTRUCTIONS:**
- Extract and structure the resume into the following JSON format:
- Include all contact information, professional summary, skills, experience, education, certifications, and projects
- Format experience as an array of job objects with: job_title, company, location, dates, achievements (array of bullet points)
- Format skills as an object with: technical_skills, tools_technologies, methodologies (all as arrays)
- Format education as an array of objects with: degree, institution, location, graduation_date, gpa (if available)
- Ensure all text is clean and professional
- Return only valid JSON

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
  "professional_summary": "2-3 sentence professional summary",
  "skills": {{
    "technical_skills": ["skill1", "skill2"],
    "tools_technologies": ["tool1", "tool2"],
    "methodologies": ["method1", "method2"]
  }},
  "experience": [
    {{
      "job_title": "Job Title",
      "company": "Company Name",
      "location": "Location",
      "dates": "Start Date - End Date",
      "achievements": ["Achievement 1", "Achievement 2"]
    }}
  ],
  "education": [
    {{
      "degree": "Degree Name",
      "institution": "Institution Name",
      "location": "Location",
      "graduation_date": "Graduation Date",
      "gpa": "GPA (optional)"
    }}
  ],
  "certifications": ["Certification 1", "Certification 2"],
  "projects": [
    {{
      "project_name": "Project Name",
      "description": "Brief description",
      "technologies": ["tech1", "tech2"],
      "bullets": ["Bullet point 1", "Bullet point 2"]
    }}
  ]
}}"""
        
        resume_data = self._chat_completion_json(
            system_prompt="You are a professional resume parser. Return only valid JSON.",
            user_prompt=user_prompt,
            max_tokens=3000,
        )
        
        return resume_data
    
    def generate_cover_letter_and_qa(
        self,
        professional_summary: str,
        job_description: str,
        company_name: Optional[str] = None,
        target_role: Optional[str] = None,
        candidate_name: Optional[str] = None,
        additional_questions: Optional[str] = None,
    ) -> Dict:
        """Generate a tailored cover letter and answers to recruiter questions.

        Returns a dict with keys:
        - cover_letter: str
        - recruiter_qa: list[ {question, answer} ]
        """

        user_prompt = get_cover_letter_and_qa_prompt(
            professional_summary=professional_summary,
            job_description=job_description,
            company_name=company_name or None,
            target_role=target_role or None,
            candidate_name=candidate_name or None,
            additional_questions=additional_questions or None,
        )

        data = self._chat_completion_json(
            system_prompt="You are a precise JSON‑only generator.",
            user_prompt=user_prompt,
            max_tokens=2000,
        )

        # Basic shape enforcement
        cover_letter = data.get("cover_letter", "").strip()
        recruiter_qa = data.get("recruiter_qa") or []
        if not isinstance(recruiter_qa, list):
            recruiter_qa = []

        return {
            "cover_letter": cover_letter,
            "recruiter_qa": recruiter_qa,
        }
    
    def validate_resume_data(self, resume_data: Dict) -> bool:
        required_fields = ['professional_summary', 'contact_info', 'experience', 'skills', 'education']
        for field in required_fields:
            if field not in resume_data:
                return False
        if 'name' not in resume_data.get('contact_info', {}):
            return False
        if not isinstance(resume_data.get('experience'), list) or len(resume_data['experience']) == 0:
            return False
        return True
    
    def get_model_info(self) -> Dict[str, str]:
        cost_estimates = {
            "gpt-4o-mini": "~$0.01-0.03 per resume",
            "gpt-4o": "~$0.10-0.20 per resume",
            "gpt-3.5-turbo": "~$0.005-0.015 per resume",
        }
        return {
            "model": self.model,
            "estimated_cost": cost_estimates.get(self.model, "Unknown"),
        }
